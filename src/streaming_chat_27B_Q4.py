#!/usr/bin/env python3
"""
Streaming command-line chat interface for Gemma-3-27B with 4-bit quantization.
Optimized for maximum memory efficiency while maintaining quality.
"""

from transformers import AutoProcessor, Gemma3ForConditionalGeneration, TextIteratorStreamer, BitsAndBytesConfig
import torch
import threading
import sys

def main():
    print("Loading Gemma-3-27B model with 4-bit quantization...")
    print("🔥 This will use ~75% less memory than full precision!")
    
    # Use 4-bit quantization for maximum memory efficiency
    model_id = "google/gemma-3-27b-it"
    
    # Optimal 4-bit quantization configuration for 27B model
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,                      # Enable 4-bit quantization
        bnb_4bit_compute_dtype=torch.bfloat16,  # Use bfloat16 for computation (RTX 5090 supports this)
        bnb_4bit_quant_type="nf4",             # Normal Float 4 - best for weights from normal distribution
        bnb_4bit_use_double_quant=True         # Nested quantization for additional memory savings
    )
    
    print("Loading model... this may take several minutes for 27B parameters")
    print("📊 Expected memory usage: ~7-10GB (vs ~54GB full precision)")
    
    model = Gemma3ForConditionalGeneration.from_pretrained(
        model_id,
        device_map="auto",                       # Automatically distribute across available GPUs
        quantization_config=quantization_config,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        low_cpu_mem_usage=True                   # Reduce CPU memory usage during loading
    ).eval()
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Ensure tokenizer has proper pad token
    if processor.tokenizer.pad_token is None:
        processor.tokenizer.pad_token = processor.tokenizer.eos_token
    
    print("✅ Gemma-3-27B loaded successfully with 4-bit quantization!")
    
    # Show detailed memory usage info
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        allocated_memory = torch.cuda.memory_allocated() / 1e9
        print(f"💾 GPU Memory: {allocated_memory:.1f}GB / {gpu_memory:.1f}GB used ({allocated_memory/gpu_memory*100:.1f}%)")
        print(f"🚀 4-bit quantization: ~75% memory reduction!")
        print(f"📈 Model size: 27B parameters → ~{allocated_memory:.1f}GB memory footprint")
    
    print("🎯 Ready for high-quality conversations with the larger model!")
    print("Type 'quit' to exit, 'clear' to reset conversation.\n")
    
    # Keep conversation history
    conversation = []
    
    try:
        while True:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                conversation = []
                print("Chat history cleared.")
                continue
                
            if not user_input:
                continue
            
            # Build messages for this turn - enhanced system prompt for 27B model
            messages = [
                {"role": "system", "content": [{"type": "text", "text": "You are a highly knowledgeable AI assistant with expertise across many domains. Provide detailed, accurate, and thoughtful responses. Use your extensive knowledge to give comprehensive answers while being clear and helpful."}]}
            ]
            
            # Add conversation history (limit to last 30 turns for 27B model)
            recent_conversation = conversation[-30:] if len(conversation) > 30 else conversation
            for turn in recent_conversation:
                messages.append(turn)
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": [{"type": "text", "text": user_input}]
            })
            
            # Generate streaming response
            try:
                inputs = processor.apply_chat_template(
                    messages, add_generation_prompt=True, tokenize=True,
                    return_dict=True, return_tensors="pt"
                ).to(model.device)
                
                # Create a text streamer
                streamer = TextIteratorStreamer(
                    processor.tokenizer,
                    timeout=30.0,
                    skip_prompt=True,
                    skip_special_tokens=True
                )
                
                # Optimized parameters for 27B model with 4-bit quantization
                generation_kwargs = {
                    **inputs,
                    "max_new_tokens": 1000,          # Longer responses for 27B capability
                    "do_sample": True,
                    "temperature": 0.8,             # Slightly higher for more creativity
                    "top_p": 0.9,
                    "top_k": 40,                    # Slightly lower for better quality
                    "repetition_penalty": 1.05,    # Lower penalty for more natural flow
                    "pad_token_id": processor.tokenizer.eos_token_id,
                    "eos_token_id": processor.tokenizer.eos_token_id,
                    "streamer": streamer,
                }
                
                print("Assistant: ", end="", flush=True)
                
                # Start generation in a separate thread
                generation_thread = threading.Thread(
                    target=lambda: model.generate(**generation_kwargs)
                )
                generation_thread.start()
                
                # Stream the tokens as they are generated
                generated_text = ""
                for new_text in streamer:
                    if new_text is not None:
                        print(new_text, end="", flush=True)
                        generated_text += new_text
                
                # Wait for generation to complete
                generation_thread.join()
                print()  # New line after response
                
                # Add to conversation history
                conversation.extend([
                    {"role": "user", "content": [{"type": "text", "text": user_input}]},
                    {"role": "assistant", "content": [{"type": "text", "text": generated_text.strip()}]}
                ])
                
            except Exception as e:
                print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
