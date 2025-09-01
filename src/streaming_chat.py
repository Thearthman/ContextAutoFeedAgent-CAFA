#!/usr/bin/env python3
"""
Streaming command-line chat interface for Gemma-3-12B with token-by-token output.
"""

from transformers import AutoProcessor, Gemma3ForConditionalGeneration, TextIteratorStreamer, BitsAndBytesConfig
import torch
import threading
import sys

def main():
    print("Loading Gemma-3-12B model with 8-bit quantization...")
    
    # Use the exact working configuration from debug test
    model_id = "google/gemma-3-12b-it"
    
    # RTX 5090 supports bfloat16, so use it for best performance
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_compute_dtype=torch.bfloat16  # Your GPU supports this
    )
    
    print("Loading model... this may take a few minutes")
    model = Gemma3ForConditionalGeneration.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=quantization_config,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    ).eval()
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Ensure tokenizer has proper pad token
    if processor.tokenizer.pad_token is None:
        processor.tokenizer.pad_token = processor.tokenizer.eos_token
    
    print("✅ Model loaded successfully with 8-bit quantization!")
    
    # Show memory usage info
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        allocated_memory = torch.cuda.memory_allocated() / 1e9
        print(f"💾 GPU Memory: {allocated_memory:.1f}GB / {gpu_memory:.1f}GB used")
        print(f"🚀 8-bit quantization reduces memory usage by ~50%")
    
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
            
            # Build messages for this turn
            messages = [
                {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant."}]}
            ]
            
            # Add conversation history
            for turn in conversation:
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
                
                # Use the working parameters from debug test
                generation_kwargs = {
                    **inputs,
                    "max_new_tokens": 200,
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50,
                    "repetition_penalty": 1.1,
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
