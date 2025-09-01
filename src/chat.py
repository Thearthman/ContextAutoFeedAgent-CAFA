#!/usr/bin/env python3
"""
Simple command-line chat interface for Gemma-3-12B text-only conversations.
"""

from transformers import AutoProcessor, Gemma3ForConditionalGeneration
import torch
import sys

class GemmaChat:
    def __init__(self, model_id="google/gemma-3-12b-it"):
        print("Loading Gemma model... This may take a few minutes.")
        
        self.model = Gemma3ForConditionalGeneration.from_pretrained(
            model_id, device_map="auto"
        ).eval()
        
        self.processor = AutoProcessor.from_pretrained(model_id)
        
        # Initialize conversation with system prompt
        self.conversation_history = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."}]
            }
        ]
        
        print("Model loaded successfully!")
        print("You can start chatting now. Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'clear' to clear the conversation history.")
        print("-" * 50)
    
    def generate_response(self, user_input, max_new_tokens=256):
        """Generate a response to user input."""
        # Add user message to conversation
        user_message = {
            "role": "user",
            "content": [{"type": "text", "text": user_input}]
        }
        
        # Create temporary conversation including the new message
        temp_conversation = self.conversation_history + [user_message]
        
        try:
            # Apply chat template
            inputs = self.processor.apply_chat_template(
                temp_conversation, 
                add_generation_prompt=True, 
                tokenize=True,
                return_dict=True, 
                return_tensors="pt"
            ).to(self.model.device, dtype=torch.bfloat16)
            
            input_len = inputs["input_ids"].shape[-1]
            
            # Generate response
            with torch.inference_mode():
                generation = self.model.generate(
                    **inputs, 
                    max_new_tokens=max_new_tokens, 
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
                generation = generation[0][input_len:]
            
            # Decode response
            response = self.processor.decode(generation, skip_special_tokens=True)
            
            # Add both user message and assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": [{"type": "text", "text": response}]
            }
            
            self.conversation_history.extend([user_message, assistant_message])
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history except system prompt."""
        self.conversation_history = [self.conversation_history[0]]  # Keep system prompt
        print("Conversation history cleared.")
    
    def show_stats(self):
        """Show conversation statistics."""
        total_messages = len(self.conversation_history) - 1  # Exclude system prompt
        user_messages = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        
        print(f"Conversation stats: {user_messages} user messages, {assistant_messages} assistant responses")
    
    def chat_loop(self):
        """Main chat loop."""
        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                elif user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                elif not user_input:
                    continue
                
                # Generate and display response
                print("Assistant: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(response)
                
        except KeyboardInterrupt:
            print("\n\nChat interrupted. Goodbye!")
        except Exception as e:
            print(f"\nError: {e}")

def main():
    """Main function."""
    print("Gemma-3-12B Command Line Chat Interface")
    print("=" * 50)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name()}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("Using CPU (will be much slower)")
    
    print()
    
    try:
        # Initialize chat
        chat = GemmaChat()
        
        # Start chat loop
        chat.chat_loop()
        
    except Exception as e:
        print(f"Failed to initialize chat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
