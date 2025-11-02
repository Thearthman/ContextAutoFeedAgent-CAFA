#!/usr/bin/env python3
"""
CAFA Main Module - Complete Integrated System
ContextAutoFeedAgent-CAFA (Context Auto Feed Agent)

This module provides:
1. GemmaStreamingChat - Basic local LLM chat (used by model_server.py)
2. CAFAIntegratedSystem - Complete system with memory, config, logging, etc.

Features:
- Smart memory retrieval before response generation
- Automatic memory storage after conversations
- Unified configuration management
- Comprehensive logging
- Support for both local and online LLMs
"""

from transformers import AutoProcessor, Gemma3ForConditionalGeneration, TextIteratorStreamer, BitsAndBytesConfig
from transformers.generation.stopping_criteria import StoppingCriteria, StoppingCriteriaList
import torch
import threading
import sys
import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime

# Import CAFA modules
try:
    from config_manager import ConfigManager
    from logger import get_logger
    from memory_tool.enhanced_memory_store import EnhancedMemoryStore
    from api_key_detector import APIKeyDetector
    from performance import get_monitor, RequestTimer
    from cache import get_response_cache, get_embedding_cache
    from validators import LLMRequestValidator, MemoryRequestValidator
except ImportError:
    # Try relative imports
    try:
        from src.config_manager import ConfigManager
        from src.logger import get_logger
        from src.memory_tool.enhanced_memory_store import EnhancedMemoryStore
        from src.api_key_detector import APIKeyDetector
        from src.performance import get_monitor, RequestTimer
        from src.cache import get_response_cache, get_embedding_cache
        from src.validators import LLMRequestValidator, MemoryRequestValidator
    except ImportError:
        print("[WARNING] CAFA modules not found. Running in basic mode.")
        ConfigManager = None
        get_logger = None
        EnhancedMemoryStore = None
        APIKeyDetector = None
        get_monitor = None
        RequestTimer = None
        get_response_cache = None
        get_embedding_cache = None
        LLMRequestValidator = None
        MemoryRequestValidator = None


class StopOnTokens(StoppingCriteria):
    """Custom stopping criteria to stop on specific tokens like <end_of_turn>"""
    def __init__(self, stop_token_ids: List[int]):
        self.stop_token_ids = stop_token_ids
    
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        # Check if the last generated token is a stop token
        for stop_id in self.stop_token_ids:
            if input_ids[0, -1] == stop_id:
                return True
        return False


class GemmaStreamingChat:
    """
    Advanced streaming chat interface for Gemma-3-27B with 4-bit quantization.
    
    Features:
    - Real-time token streaming
    - Conversation history management
    - Memory optimization
    - Extensible architecture for future enhancements
    """
    
    def __init__(
        self, 
        model_id: str = "google/gemma-3-12b-it",
        max_history_turns: int = 30,
        system_prompt: str = """You are a highly knowledgeable personal AI assistant with expertise across many domains. 
        Provide accurate, thoughtful responses as short and concise as possible."""
    ):
        """
        Initialize the Gemma streaming chat system.
        
        Args:
            model_id: HuggingFace model identifier
            max_history_turns: Maximum conversation turns to keep in memory
            system_prompt: System prompt for the AI assistant
        """
        self.model_id = model_id
        self.max_history_turns = max_history_turns
        self.system_prompt = system_prompt
        
        # Model components
        self.model = None
        self.processor = None
        
        # Conversation state
        self.conversation_history = []
        
        # Performance tracking
        self.total_tokens_generated = 0
        self.conversation_count = 0
        
        print(f"[INFO] Initializing Gemma-3-27B Q4 Streaming Chat...")
        self._optimize_loading_environment()
        self._load_model()
        self._show_system_info()
    
    def _load_model(self) -> None:
        """Load the Gemma model with optimal 4-bit quantization and fast loading optimizations."""
        print("Loading model with 4-bit quantization and fast loading optimizations...")
        print("[INFO] Expected memory usage: ~7-10GB (vs ~54GB full precision)")
        
        # Optimal 4-bit quantization configuration
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        model = Gemma3ForConditionalGeneration.from_pretrained(
            self.model_id,
            device_map="auto",
            quantization_config=quantization_config,
            dtype=torch.bfloat16,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            # Fast loading optimizations
            use_safetensors=True,           # Use safetensors format (faster than pickle)
            local_files_only=True,        # Allow cached files
            # offload_folder=None,         # Don't use disk offload unless necessary
            max_memory=None,               # Let auto device mapping handle memory
        )
        
        # Use model directly without torch.compile() to avoid delays with quantized models
        # torch.compile() causes graph breaks and recompilations during streaming
        self.model = model.eval()
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        # Ensure proper tokenizer configuration
        if self.processor.tokenizer.pad_token is None:
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
        
        # DEBUG: Print EOS token info and find stop tokens
        print(f"[DEBUG] EOS token ID: {self.processor.tokenizer.eos_token_id}")
        print(f"[DEBUG] EOS token: '{self.processor.tokenizer.eos_token}'")
        
        # Get stop token IDs for Gemma (including <end_of_turn>)
        self.stop_token_ids = []
        if self.processor.tokenizer.eos_token_id:
            self.stop_token_ids.append(self.processor.tokenizer.eos_token_id)
        
        # Try to find <end_of_turn> token ID
        end_of_turn_token = "<end_of_turn>"
        try:
            end_of_turn_id = self.processor.tokenizer.convert_tokens_to_ids(end_of_turn_token)
            if end_of_turn_id != self.processor.tokenizer.unk_token_id:
                self.stop_token_ids.append(end_of_turn_id)
                print(f"[DEBUG] Found <end_of_turn> token ID: {end_of_turn_id}")
        except:
            pass
        
        print(f"[DEBUG] Stop token IDs: {self.stop_token_ids}")
        
        print("✅ Model loaded successfully!")
    
    def _optimize_loading_environment(self) -> None:
        """Optimize the environment for faster model loading."""
        # Enable optimized attention and faster inference
        import os
        
        # Enable optimized CUDA operations
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            
            # Set memory management for faster loading
            torch.cuda.empty_cache()
            
            print("[INFO] CUDA optimizations enabled for faster loading")
        
        # Optimize CPU operations for model loading
        torch.set_num_threads(min(8, torch.get_num_threads()))  # Optimal thread count
        
        # Set environment variables for faster loading
        os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid tokenizer warnings
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        
        # Pre-warm JIT compilation if available
        if hasattr(torch.jit, 'set_fusion_strategy'):
            torch.jit.set_fusion_strategy([('STATIC', 2), ('DYNAMIC', 2)])
    
    def _show_system_info(self) -> None:
        """Display system and model information."""
        if torch.cuda.is_available():
            gpu_props = torch.cuda.get_device_properties(0)
            gpu_memory = gpu_props.total_memory / 1e9
            allocated_memory = torch.cuda.memory_allocated() / 1e9
            
            print(f"🖥️  GPU: {gpu_props.name}")
            print(f"💾 Memory: {allocated_memory:.1f}GB / {gpu_memory:.1f}GB used ({allocated_memory/gpu_memory*100:.1f}%)")
            print(f"[INFO] 4-bit quantization: ~75% memory reduction!")
        
        print(f"[SUCCESS] Ready for high-quality conversations!")
        print(f"[INFO] System prompt: {self.system_prompt[:60]}...")
    
    def _build_conversation_context(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Build the conversation context for model input.
        
        Args:
            user_input: Current user message
            
        Returns:
            Formatted conversation context
        """
        messages = [
            {
                "role": "system", 
                "content": [{"type": "text", "text": self.system_prompt}]
            }
        ]
        
        # Add recent conversation history (limited for memory efficiency)
        recent_history = self.conversation_history[-self.max_history_turns:] if len(self.conversation_history) > self.max_history_turns else self.conversation_history
        messages.extend(recent_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": user_input}]
        })
        
        return messages
    
    def generate_response(
        self, 
        user_input: str, 
        max_new_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40
    ) -> str:
        """
        Generate a streaming response to user input.
        
        Args:
            user_input: User's message
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated response text
        """
        # Build conversation context
        messages = self._build_conversation_context(user_input)
        
        try:
            # Prepare inputs
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            # Create streamer for real-time output with shorter timeout
            streamer = TextIteratorStreamer(
                self.processor.tokenizer,
                timeout=2.0,  # Reduced from 40s to break out faster if generation stalls
                skip_prompt=True,
                skip_special_tokens=True  # Skip special tokens for clean output
            )
            
            # Generation parameters with proper stop tokens for Gemma
            stop_criteria = StoppingCriteriaList([StopOnTokens(self.stop_token_ids)])
            
            generation_kwargs = {
                **inputs,
                "max_new_tokens": max_new_tokens,
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                # Removed repetition_penalty to avoid O(n²) logit recalculation
                "pad_token_id": self.processor.tokenizer.pad_token_id,
                "eos_token_id": self.processor.tokenizer.eos_token_id,
                "streamer": streamer,
                "stopping_criteria": stop_criteria,
            }
            
            print("Assistant: ", end="", flush=True)
            
            # Start generation in background thread (daemon=True means it won't block)
            generation_thread = threading.Thread(
                target=lambda: self.model.generate(**generation_kwargs),
                daemon=True
            )
            generation_thread.start()
            
            # Stream tokens as they're generated
            generated_text = ""
            for new_text in streamer:
                if new_text is not None:
                    print(new_text, end="", flush=True)
                    generated_text += new_text
            
            # Don't wait for thread - all tokens already received via streamer
            print()  # New line after response 
            
            # Update conversation history
            self._update_conversation_history(user_input, generated_text.strip())
            
            # Update statistics
            self.total_tokens_generated += len(self.processor.tokenizer.encode(generated_text))
            
            return generated_text.strip()
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"\n{error_msg}")
            return error_msg
    
    def generate_response_stream(
        self, 
        user_input: str, 
        max_new_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40
    ):
        """
        Generate a streaming response that yields tokens as they're generated.
        
        Args:
            user_input: User's message
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Yields:
            Individual tokens as they're generated
        """
        # Build conversation context
        messages = self._build_conversation_context(user_input)
        
        try:
            # Prepare inputs
            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            # Create streamer for real-time output with shorter timeout
            streamer = TextIteratorStreamer(
                self.processor.tokenizer,
                timeout=2.0,  # Reduced from 40s to break out faster if generation stalls
                skip_prompt=True,
                skip_special_tokens=True  # Skip special tokens for clean output
            )
            
            # Generation parameters with proper stop tokens for Gemma
            stop_criteria = StoppingCriteriaList([StopOnTokens(self.stop_token_ids)])
            
            generation_kwargs = {
                **inputs,
                "max_new_tokens": max_new_tokens,
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                # Removed repetition_penalty to avoid O(n²) logit recalculation
                "pad_token_id": self.processor.tokenizer.pad_token_id,
                "eos_token_id": self.processor.tokenizer.eos_token_id,
                "streamer": streamer,
                "stopping_criteria": stop_criteria,
            }
            
            # Start generation in background thread
            generation_thread = threading.Thread(
                target=lambda: self.model.generate(**generation_kwargs),
                daemon=True
            )
            generation_thread.start()
            
            # Yield tokens as they're generated with timing instrumentation
            generated_text = ""
            import time
            start_time = time.time()
            last_token_time = start_time
            token_count = 0
            
            # Gemma uses <end_of_turn> as stop token
            stop_strings = ["<end_of_turn>", "<eos>", "</s>", self.processor.tokenizer.eos_token]
            
            for new_text in streamer:
                if new_text is not None:
                    current_time = time.time()
                    time_since_last = current_time - last_token_time
                    
                    # Log if there's a significant delay between tokens (>1 second)
                    if time_since_last > 1.0:
                        print(f"\n[TIMING] Long delay: {time_since_last:.2f}s between tokens", flush=True)
                    
                    # Check if this contains any stop token
                    contains_stop = any(stop_str in new_text for stop_str in stop_strings if stop_str)
                    if contains_stop:
                        print(f"\n[DEBUG] Stop token detected in: '{new_text[:50]}...' Stopping generation.", flush=True)
                        # Don't yield the stop token
                        break
                    
                    generated_text += new_text
                    yield new_text
                    token_count += 1
                    last_token_time = current_time
            
            # Log final statistics
            total_time = time.time() - start_time
            if token_count > 0:
                avg_time_per_token = total_time / token_count
                print(f"\n[TIMING] Generation complete: {token_count} tokens in {total_time:.2f}s ({avg_time_per_token:.3f}s/token)", flush=True)
            
            # Update conversation history after streaming completes
            self._update_conversation_history(user_input, generated_text.strip())
            
            # Update statistics
            self.total_tokens_generated += len(self.processor.tokenizer.encode(generated_text))
            
        except Exception as e:
            yield f"Error: {e}"
    
    def _update_conversation_history(self, user_input: str, assistant_response: str) -> None:
        """Update the conversation history with new exchange."""
        self.conversation_history.extend([
            {"role": "user", "content": [{"type": "text", "text": user_input}]},
            {"role": "assistant", "content": [{"type": "text", "text": assistant_response}]}
        ])
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        self.conversation_count += 1
        
        # Optional: Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("[INFO] Conversation history cleared.")
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        return {
            "total_turns": len(self.conversation_history) // 2,
            "total_tokens_generated": self.total_tokens_generated,
            "conversation_sessions": self.conversation_count + 1,
            "model_id": self.model_id,
            "max_history_turns": self.max_history_turns
        }
    
    def set_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt."""
        self.system_prompt = new_prompt
        print(f"[INFO] System prompt updated: {new_prompt[:60]}...")
    
    def chat_loop(self) -> None:
        """Main interactive chat loop."""
        print("Commands:")
        print("  • 'quit' / 'exit' / 'bye' - Exit chat")
        print("  • 'clear' - Clear conversation history")
        print("  • 'stats' - Show conversation statistics")
        print("  • 'prompt <new_prompt>' - Update system prompt")
        print("-" * 60)
        
        try:
            while True:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("[INFO] Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.clear_conversation_history()
                    continue
                elif user_input.lower() == 'stats':
                    stats = self.get_conversation_stats()
                    print(f"[INFO] Stats: {stats['total_turns']} turns, {stats['total_tokens_generated']} tokens, {stats['conversation_sessions']} sessions")
                    continue
                elif user_input.startswith('prompt '):
                    new_prompt = user_input[7:].strip()
                    if new_prompt:
                        self.set_system_prompt(new_prompt)
                    continue
                
                # Generate response
                self.generate_response(user_input)
                
        except KeyboardInterrupt:
            print("\n[INFO] Chat interrupted. Goodbye!")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


class CAFAIntegratedSystem:
    """
    CAFA Complete Integrated System
    
    Integrates:
    - Configuration Management (ConfigManager)
    - Logging System (CAFALogger)
    - Memory System (EnhancedMemoryStore)
    - LLM System (GemmaStreamingChat or Online API)
    - Smart memory retrieval and storage
    
    Features:
    - Auto-retrieve relevant memories before generating responses
    - Auto-store important conversations in memory
    - Unified configuration
    - Comprehensive logging
    """
    
    def __init__(
        self,
        config_file: str = "api_config.json",
        use_memory: bool = True,
        use_local_llm: bool = True,
        model_id: str = "google/gemma-3-12b-it",
        enable_performance_monitor: bool = True,
        enable_cache: bool = True,
        enable_validation: bool = True
    ):
        """
        Initialize CAFA Integrated System
        
        Args:
            config_file: Configuration file path
            use_memory: Enable memory system
            use_local_llm: Use local LLM (if False, will use online API)
            model_id: Model identifier for local LLM
            enable_performance_monitor: Enable performance monitoring
            enable_cache: Enable response and embedding caching
            enable_validation: Enable input/output validation
        """
        print("=" * 70)
        print("🚀 Initializing CAFA Integrated System")
        print("=" * 70)
        
        # 1. Initialize configuration
        self.config = ConfigManager(config_file) if ConfigManager else None
        if self.config:
            print("✅ Configuration loaded")
            is_valid, errors = self.config.validate()
            if not is_valid:
                print("⚠️  Configuration validation errors:")
                for err in errors:
                    print(f"   • {err}")
        
        # 2. Initialize logger
        self.logger = get_logger("CAFA_Main", log_level="INFO") if get_logger else None
        if self.logger:
            self.logger.info("CAFA System initialization started")
            print("✅ Logging system initialized")
        
        # 3. Initialize memory system
        self.memory_enabled = use_memory and (EnhancedMemoryStore is not None)
        self.memory_store = None
        
        if self.memory_enabled:
            try:
                memory_path = self.config.get("memory.storage_path") if self.config else "memory_data.json"
                self.memory_store = EnhancedMemoryStore(path=memory_path)
                print(f"✅ Memory system initialized ({len(self.memory_store.memories)} memories loaded)")
                if self.logger:
                    self.logger.info(f"Memory system loaded: {len(self.memory_store.memories)} memories")
            except Exception as e:
                print(f"⚠️  Memory system initialization failed: {e}")
                self.memory_enabled = False
                if self.logger:
                    self.logger.error(f"Memory initialization failed: {e}")
        
        # 4. Initialize LLM
        self.use_local_llm = use_local_llm
        self.llm = None
        
        if use_local_llm:
            try:
                print("\n📦 Loading local LLM (this may take a while)...")
                system_prompt = self.config.get("llm.system_prompt") if self.config else None
                if not system_prompt:
                    system_prompt = """You are a highly knowledgeable personal AI assistant with expertise across many domains. 
                    Provide accurate, thoughtful responses as short and concise as possible."""
                
                self.llm = GemmaStreamingChat(
                    model_id=model_id,
                    max_history_turns=self.config.get("llm.max_history_turns", 30) if self.config else 30,
                    system_prompt=system_prompt
                )
                print("✅ Local LLM initialized")
                if self.logger:
                    self.logger.info(f"Local LLM initialized: {model_id}")
            except Exception as e:
                print(f"❌ Local LLM initialization failed: {e}")
                if self.logger:
                    self.logger.error(f"Local LLM initialization failed: {e}")
                raise
        else:
            print("ℹ️  Local LLM disabled (will use online API if configured)")
            # TODO: Add online API client integration
        
        # 5. API Key Detection
        if APIKeyDetector:
            detector = APIKeyDetector()
            detected_keys = detector.detect_from_env()
            if detected_keys:
                print(f"✅ Detected API keys: {', '.join([k['provider_display_name'] for k in detected_keys])}")
                if self.logger:
                    self.logger.info(f"API keys detected: {len(detected_keys)}")
        
        # 6. Initialize Performance Monitor
        self.perf_monitor_enabled = enable_performance_monitor and (get_monitor is not None)
        self.perf_monitor = None
        
        if self.perf_monitor_enabled:
            try:
                self.perf_monitor = get_monitor()
                self.perf_monitor.start_system_monitoring()
                print("✅ Performance monitoring initialized")
                if self.logger:
                    self.logger.info("Performance monitoring enabled")
            except Exception as e:
                print(f"⚠️  Performance monitor initialization failed: {e}")
                self.perf_monitor_enabled = False
                if self.logger:
                    self.logger.warning(f"Performance monitor initialization failed: {e}")
        
        # 7. Initialize Cache System
        self.cache_enabled = enable_cache and (get_response_cache is not None)
        self.response_cache = None
        self.embedding_cache = None
        
        if self.cache_enabled:
            try:
                self.response_cache = get_response_cache()
                self.embedding_cache = get_embedding_cache()
                print("✅ Cache system initialized (Response + Embedding)")
                if self.logger:
                    self.logger.info("Cache system enabled")
            except Exception as e:
                print(f"⚠️  Cache system initialization failed: {e}")
                self.cache_enabled = False
                if self.logger:
                    self.logger.warning(f"Cache system initialization failed: {e}")
        
        # 8. Initialize Validators
        self.validation_enabled = enable_validation and (LLMRequestValidator is not None)
        
        if self.validation_enabled:
            print("✅ Input validation enabled")
            if self.logger:
                self.logger.info("Input validation enabled")
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "memory_retrievals": 0,
            "memory_stores": 0,
            "context_enhanced_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "validation_errors": 0,
            "start_time": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 70)
        print("🎉 CAFA System initialized successfully!")
        print("=" * 70)
        if self.logger:
            self.logger.info("CAFA System initialization complete")
    
    def _retrieve_relevant_memories(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant memories for a query
        
        Args:
            query: User query
            top_k: Number of memories to retrieve
        
        Returns:
            List of relevant memories
        """
        if not self.memory_enabled or not self.memory_store:
            return []
        
        try:
            start_time = time.time()
            memories = self.memory_store.search(
                query=query,
                top_k=top_k,
                min_similarity=self.config.get("memory.similarity_threshold", 0.3) if self.config else 0.3,
                importance_boost=True
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if memories:
                self.stats["memory_retrievals"] += 1
                if self.logger:
                    self.logger.log_memory_operation("retrieve", len(memories), duration_ms)
            
            return memories
        except Exception as e:
            if self.logger:
                self.logger.error(f"Memory retrieval failed: {e}")
            return []
    
    def _build_context_with_memory(self, user_input: str, memories: List[Dict]) -> str:
        """
        Build enhanced context by combining user input with relevant memories
        
        Args:
            user_input: User's current input
            memories: Retrieved relevant memories
        
        Returns:
            Enhanced context string
        """
        if not memories:
            return user_input
        
        # Build context
        context_parts = []
        context_parts.append("=== Relevant Context from Memory ===")
        
        for i, mem in enumerate(memories, 1):
            context_parts.append(
                f"\n[Memory {i}] (similarity: {mem['similarity']:.2f}, importance: {mem['importance']:.2f})"
            )
            context_parts.append(f"{mem['text']}")
        
        context_parts.append("\n=== Current Question ===")
        context_parts.append(user_input)
        
        enhanced_context = "\n".join(context_parts)
        self.stats["context_enhanced_queries"] += 1
        
        if self.logger:
            self.logger.info(f"Context enhanced with {len(memories)} memories")
        
        return enhanced_context
    
    def _store_conversation_memory(self, user_input: str, assistant_response: str):
        """
        Store conversation in memory with smart weight evaluation
        
        Args:
            user_input: User's input
            assistant_response: Assistant's response
        """
        if not self.memory_enabled or not self.memory_store:
            return
        
        try:
            # Store user input
            user_memory = self.memory_store.add_memory(
                text=user_input,
                context={"role": "user"},
                auto_evaluate=True,
                tags=["conversation", "user_query"]
            )
            
            # Only store important assistant responses (avoid storing simple acknowledgments)
            if len(assistant_response) > 50:  # Minimum length threshold
                assistant_memory = self.memory_store.add_memory(
                    text=assistant_response,
                    context={"role": "assistant"},
                    auto_evaluate=True,
                    tags=["conversation", "assistant_response"]
                )
                
                # Log if user should be prompted about weight
                if user_memory['metadata']['should_prompt_user']:
                    print(f"\n💡 {user_memory['metadata']['prompt_message']}")
                
                if assistant_memory['metadata']['should_prompt_user']:
                    print(f"\n💡 {assistant_memory['metadata']['prompt_message']}")
            
            self.stats["memory_stores"] += 1
            
            if self.logger:
                self.logger.log_memory_operation("store", 1, 0)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Memory storage failed: {e}")
    
    def generate_response(
        self,
        user_input: str,
        use_memory: bool = True,
        store_conversation: bool = True,
        use_cache: bool = True,
        **generation_kwargs
    ) -> str:
        """
        Generate response with smart memory integration, caching, and validation
        
        Args:
            user_input: User's input
            use_memory: Whether to retrieve and use memories
            store_conversation: Whether to store this conversation
            use_cache: Whether to use cache for responses
            **generation_kwargs: Additional arguments for generation
        
        Returns:
            Generated response
        """
        self.stats["total_queries"] += 1
        
        # 0. Input Validation
        if self.validation_enabled and LLMRequestValidator:
            try:
                request_data = {
                    "prompt": user_input,
                    **generation_kwargs
                }
                LLMRequestValidator.validate_chat_request(request_data)
            except Exception as e:
                self.stats["validation_errors"] += 1
                if self.logger:
                    self.logger.warning(f"Input validation failed: {e}")
                # Continue anyway with warning
        
        # 1. Check cache first
        cached_response = None
        if use_cache and self.cache_enabled and self.response_cache:
            try:
                model = self.llm.model_id if self.llm else "default"
                temperature = generation_kwargs.get('temperature', 0.7)
                cached_response = self.response_cache.get_response(
                    prompt=user_input,
                    model=model,
                    temperature=temperature
                )
                
                if cached_response:
                    self.stats["cache_hits"] += 1
                    print("🎯 Using cached response")
                    if self.logger:
                        self.logger.info("Cache hit - returning cached response")
                    return cached_response
                else:
                    self.stats["cache_misses"] += 1
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Cache lookup failed: {e}")
        
        # 2. Retrieve relevant memories
        memories = []
        if use_memory and self.memory_enabled:
            memories = self._retrieve_relevant_memories(user_input)
            
            if memories:
                print(f"\n🧠 Retrieved {len(memories)} relevant memories:")
                for i, mem in enumerate(memories, 1):
                    print(f"   [{i}] ({mem['category']}) {mem['text'][:60]}...")
        
        # 3. Build enhanced context
        if memories:
            enhanced_input = self._build_context_with_memory(user_input, memories)
        else:
            enhanced_input = user_input
        
        # 4. Generate response with performance timing
        start_time = time.time()
        
        # Use RequestTimer if available
        if self.perf_monitor_enabled and self.perf_monitor and RequestTimer:
            with RequestTimer(self.perf_monitor.metrics, "llm_generate"):
                response = self._execute_llm_generation(enhanced_input, generation_kwargs)
        else:
            response = self._execute_llm_generation(enhanced_input, generation_kwargs)
        
        duration_s = time.time() - start_time
        
        # Log LLM call
        if self.logger:
            self.logger.log_llm_call(
                "local" if self.use_local_llm else "online",
                self.llm.model_id if self.llm else "unknown",
                len(response.split()),
                duration_s
            )
        
        # Record performance metrics
        if self.perf_monitor_enabled and self.perf_monitor:
            try:
                self.perf_monitor.record_llm_call(
                    provider="local" if self.use_local_llm else "online",
                    model=self.llm.model_id if self.llm else "unknown",
                    duration_s=duration_s,
                    tokens=len(response.split()),
                    success=True
                )
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Performance recording failed: {e}")
        
        # 5. Cache the response
        if use_cache and self.cache_enabled and self.response_cache and response:
            try:
                model = self.llm.model_id if self.llm else "default"
                temperature = generation_kwargs.get('temperature', 0.7)
                self.response_cache.set_response(
                    prompt=user_input,
                    model=model,
                    temperature=temperature,
                    response=response
                )
                if self.logger:
                    self.logger.debug("Response cached")
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Response caching failed: {e}")
        
        # 6. Store conversation in memory
        if store_conversation and self.memory_enabled:
            self._store_conversation_memory(user_input, response)
        
        return response
    
    def _execute_llm_generation(self, enhanced_input: str, generation_kwargs: dict) -> str:
        """
        Execute LLM generation (separated for cleaner code)
        
        Args:
            enhanced_input: Input text (possibly enhanced with memory context)
            generation_kwargs: Generation parameters
        
        Returns:
            Generated response
        """
        if self.use_local_llm and self.llm:
            return self.llm.generate_response(
                user_input=enhanced_input,
                **generation_kwargs
            )
        else:
            # TODO: Add online API support
            return "[Online API not implemented yet]"
    
    def generate_response_stream(
        self,
        user_input: str,
        use_memory: bool = True,
        store_conversation: bool = True,
        **generation_kwargs
    ):
        """
        Generate streaming response with memory integration
        
        Args:
            user_input: User's input
            use_memory: Whether to retrieve and use memories
            store_conversation: Whether to store this conversation
            **generation_kwargs: Additional arguments for generation
        
        Yields:
            Response tokens
        """
        self.stats["total_queries"] += 1
        
        # 1. Retrieve relevant memories
        memories = []
        if use_memory and self.memory_enabled:
            memories = self._retrieve_relevant_memories(user_input)
            
            if memories:
                yield f"\n🧠 Retrieved {len(memories)} relevant memories:\n"
                for i, mem in enumerate(memories, 1):
                    yield f"   [{i}] ({mem['category']}) {mem['text'][:60]}...\n"
                yield "\nAssistant: "
        
        # 2. Build enhanced context
        if memories:
            enhanced_input = self._build_context_with_memory(user_input, memories)
        else:
            enhanced_input = user_input
        
        # 3. Generate streaming response
        full_response = ""
        
        if self.use_local_llm and self.llm:
            for token in self.llm.generate_response_stream(
                user_input=enhanced_input,
                **generation_kwargs
            ):
                full_response += token
                yield token
        else:
            # TODO: Add online API streaming support
            yield "[Online API streaming not implemented yet]"
        
        # 4. Store conversation in memory
        if store_conversation and self.memory_enabled and full_response:
            self._store_conversation_memory(user_input, full_response)
    
    def chat_loop(self):
        """Interactive chat loop with full CAFA features"""
        print("\n" + "=" * 70)
        print("💬 CAFA Interactive Chat")
        print("=" * 70)
        print("\nCommands:")
        print("  • 'quit' / 'exit' / 'bye' - Exit chat")
        print("  • 'clear' - Clear conversation history")
        print("  • 'stats' - Show system statistics")
        print("  • 'memory search <query>' - Search memories")
        print("  • 'memory stats' - Show memory statistics")
        print("  • 'memory decay' - Trigger memory decay")
        print("  • 'config show' - Show current configuration")
        print("-" * 70)
        
        try:
            while True:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye!")
                    if self.logger:
                        self.logger.info("User exited chat")
                    break
                
                elif user_input.lower() == 'clear':
                    if self.llm:
                        self.llm.clear_conversation_history()
                    print("✅ Conversation history cleared")
                    continue
                
                elif user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                
                elif user_input.startswith('memory search '):
                    query = user_input[14:].strip()
                    self._search_memory_command(query)
                    continue
                
                elif user_input.lower() == 'memory stats':
                    self._show_memory_stats()
                    continue
                
                elif user_input.lower() == 'memory decay':
                    self._trigger_memory_decay()
                    continue
                
                elif user_input.lower() == 'config show':
                    self._show_config()
                    continue
                
                # Generate response
                self.generate_response(user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            if self.logger:
                self.logger.info("Chat interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if self.logger:
                self.logger.exception("Chat loop error")
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def _show_stats(self):
        """Show system statistics"""
        print("\n📊 System Statistics")
        print("=" * 70)
        print(f"Total Queries: {self.stats['total_queries']}")
        print(f"Memory Retrievals: {self.stats['memory_retrievals']}")
        print(f"Memory Stores: {self.stats['memory_stores']}")
        print(f"Context Enhanced Queries: {self.stats['context_enhanced_queries']}")
        
        # Cache statistics
        if self.cache_enabled:
            total_cache_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            hit_rate = (self.stats['cache_hits'] / total_cache_requests * 100) if total_cache_requests > 0 else 0
            print(f"\n💾 Cache Statistics:")
            print(f"  Cache Hits: {self.stats['cache_hits']}")
            print(f"  Cache Misses: {self.stats['cache_misses']}")
            print(f"  Hit Rate: {hit_rate:.1f}%")
            
            # Detailed cache stats
            if self.response_cache:
                try:
                    cache_stats = self.response_cache.get_stats()
                    print(f"  Cache Size: {cache_stats.get('size', 0)} items")
                except:
                    pass
        
        # Validation statistics
        if self.validation_enabled and self.stats['validation_errors'] > 0:
            print(f"\n⚠️  Validation Errors: {self.stats['validation_errors']}")
        
        # LLM statistics
        if self.llm:
            llm_stats = self.llm.get_conversation_stats()
            print(f"\n🤖 LLM Statistics:")
            print(f"  Conversation Turns: {llm_stats['total_turns']}")
            print(f"  Tokens Generated: {llm_stats['total_tokens_generated']}")
            print(f"  Sessions: {llm_stats['conversation_sessions']}")
        
        # Performance statistics
        if self.perf_monitor_enabled and self.perf_monitor:
            try:
                summary = self.perf_monitor.get_summary()
                print(f"\n⚡ Performance Metrics:")
                print(f"  Total Requests: {summary.get('total_requests', 0)}")
                print(f"  Avg LLM Duration: {summary.get('avg_llm_duration_s', 0):.2f}s")
                print(f"  Success Rate: {summary.get('llm_success_rate', 0):.1f}%")
                
                # Get detailed LLM metrics
                llm_stats = self.perf_monitor.metrics.get_stats("llm_generate")
                if llm_stats:
                    print(f"  LLM P50: {llm_stats.get('p50', 0):.2f}ms")
                    print(f"  LLM P95: {llm_stats.get('p95', 0):.2f}ms")
                    print(f"  LLM P99: {llm_stats.get('p99', 0):.2f}ms")
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Failed to get performance stats: {e}")
    
    def _show_memory_stats(self):
        """Show memory statistics"""
        if not self.memory_enabled:
            print("⚠️  Memory system not enabled")
            return
        
        stats = self.memory_store.get_stats()
        print("\n🧠 Memory Statistics")
        print("=" * 70)
        print(f"Total Memories: {stats['total_memories']}")
        print(f"High Importance: {stats['high_importance_count']}")
        print(f"Average Importance: {stats['avg_importance']:.2f}")
        print(f"\nCategories:")
        for category, count in stats['categories'].items():
            print(f"  • {category}: {count}")
    
    def _search_memory_command(self, query: str):
        """Search memory command"""
        if not self.memory_enabled:
            print("⚠️  Memory system not enabled")
            return
        
        memories = self.memory_store.search(query, top_k=5)
        if memories:
            print(f"\n🔍 Found {len(memories)} memories:")
            for i, mem in enumerate(memories, 1):
                print(f"\n[{i}] Similarity: {mem['similarity']:.3f} | Importance: {mem['importance']:.2f}")
                print(f"    Category: {mem['category']}")
                print(f"    {mem['text']}")
        else:
            print("❌ No relevant memories found")
    
    def _trigger_memory_decay(self):
        """Trigger memory decay"""
        if not self.memory_enabled:
            print("⚠️  Memory system not enabled")
            return
        
        print("\n⏳ Triggering memory decay...")
        result = self.memory_store.adaptive_decay()
        print(f"✅ Updated {result['updated_count']} memories")
        print(f"   High importance remaining: {result['high_importance_remaining']}")
    
    def _show_config(self):
        """Show current configuration"""
        if not self.config:
            print("⚠️  Configuration system not available")
            return
        
        print("\n⚙️  Current Configuration")
        print("=" * 70)
        print(f"Memory Enabled: {self.memory_enabled}")
        print(f"Local LLM: {self.use_local_llm}")
        if self.config:
            print(f"LLM Temperature: {self.config.get('llm.temperature')}")
            print(f"Memory Threshold: {self.config.get('memory.similarity_threshold')}")


def main():
    """Main function to run the CAFA system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CAFA - Context Auto Feed Agent")
    parser.add_argument(
        "--mode",
        choices=["basic", "integrated"],
        default="integrated",
        help="Run mode: basic (Gemma only) or integrated (full CAFA system)"
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable memory system"
    )
    parser.add_argument(
        "--online-api",
        action="store_true",
        help="Use online API instead of local LLM"
    )
    parser.add_argument(
        "--model",
        default="google/gemma-3-12b-it",
        help="Model ID for local LLM"
    )
    parser.add_argument(
        "--config",
        default="api_config.json",
        help="Configuration file path"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable response caching"
    )
    parser.add_argument(
        "--no-perf-monitor",
        action="store_true",
        help="Disable performance monitoring"
    )
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Disable input validation"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "basic":
            # Basic mode - only Gemma chat
            print("🔧 Running in BASIC mode (Gemma only)")
            chat = GemmaStreamingChat(model_id=args.model)
            chat.chat_loop()
        else:
            # Integrated mode - full CAFA system
            print("🚀 Running in INTEGRATED mode (Full CAFA)")
            system = CAFAIntegratedSystem(
                config_file=args.config,
                use_memory=not args.no_memory,
                use_local_llm=not args.online_api,
                model_id=args.model,
                enable_performance_monitor=not args.no_perf_monitor,
                enable_cache=not args.no_cache,
                enable_validation=not args.no_validation
            )
            system.chat_loop()
        
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
