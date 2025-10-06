#!/usr/bin/env python3
"""
Object-oriented Gemma-3-27B Q4 streaming chat interface.
Designed for extensibility and future feature additions.
"""

from transformers import AutoProcessor, Gemma3ForConditionalGeneration, TextIteratorStreamer, BitsAndBytesConfig
import torch
import threading
import sys
from typing import List, Dict, Optional, Any


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
        
        print(f"🚀 Initializing Gemma-3-27B Q4 Streaming Chat...")
        self._optimize_loading_environment()
        self._load_model()
        self._show_system_info()
    
    def _load_model(self) -> None:
        """Load the Gemma model with optimal 4-bit quantization and fast loading optimizations."""
        print("Loading model with 4-bit quantization and fast loading optimizations...")
        print("📊 Expected memory usage: ~7-10GB (vs ~54GB full precision)")
        
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
        compiled_model = torch.compile(model)
        
        # Optimized loading parameters for faster initialization
        self.model = compiled_model.eval()
        
        # Load processor
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        
        # Ensure proper tokenizer configuration
        if self.processor.tokenizer.pad_token is None:
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
        
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
            
            print("⚡ CUDA optimizations enabled for faster loading")
        
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
            print(f"🚀 4-bit quantization: ~75% memory reduction!")
        
        print(f"🎯 Ready for high-quality conversations!")
        print(f"📝 System prompt: {self.system_prompt[:60]}...")
    
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
            
            # Create streamer for real-time output
            streamer = TextIteratorStreamer(
                self.processor.tokenizer,
                timeout=40.0,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            # Generation parameters
            generation_kwargs = {
                **inputs,
                "max_new_tokens": max_new_tokens,
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repetition_penalty": 1.05,
                "pad_token_id": self.processor.tokenizer.eos_token_id,
                "eos_token_id": self.processor.tokenizer.eos_token_id,
                "streamer": streamer,
            }
            
            print("Assistant: ", end="", flush=True)
            
            # Start generation in background thread
            generation_thread = threading.Thread(
                target=lambda: self.model.generate(**generation_kwargs)
            )
            generation_thread.start()
            
            # Stream tokens as they're generated
            generated_text = ""
            for new_text in streamer:
                if new_text is not None:
                    print(new_text, end="", flush=True)
                    generated_text += new_text
            
            generation_thread.join()
            # A delay happened before this
            print("end of response")  # New line after response 
            
            # Update conversation history
            self._update_conversation_history(user_input, generated_text.strip())
            
            # Update statistics
            self.total_tokens_generated += len(self.processor.tokenizer.encode(generated_text))
            
            return generated_text.strip()
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"\n{error_msg}")
            return error_msg
    
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
        
        print("🧹 Conversation history cleared.")
    
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
        print(f"🎯 System prompt updated: {new_prompt[:60]}...")
    
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
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.clear_conversation_history()
                    continue
                elif user_input.lower() == 'stats':
                    stats = self.get_conversation_stats()
                    print(f"📊 Stats: {stats['total_turns']} turns, {stats['total_tokens_generated']} tokens, {stats['conversation_sessions']} sessions")
                    continue
                elif user_input.startswith('prompt '):
                    new_prompt = user_input[7:].strip()
                    if new_prompt:
                        self.set_system_prompt(new_prompt)
                    continue
                
                # Generate response
                self.generate_response(user_input)
                
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted. Goodbye!")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
        finally:
            # Cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


def main():
    """Main function to run the streaming chat interface."""
    try:
        # Initialize chat system
        chat = GemmaStreamingChat()
        
        # Start interactive chat
        chat.chat_loop()
        
    except Exception as e:
        print(f"Failed to initialize chat system: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
