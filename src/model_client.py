#!/usr/bin/env python3
"""
Model Client for Gemma Model Server
Command-line client for interacting with the model server
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

class GemmaClient:
    """Client for interacting with the Gemma model server."""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        """
        Initialize the client.
        
        Args:
            server_url: URL of the model server
        """
        self.server_url = server_url
        self.conversation_history = []
        
    def health_check(self) -> bool:
        """Check if the server is healthy."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, max_new_tokens: int = 1000, 
                 temperature: float = 0.7, top_p: float = 0.9, 
                 top_k: int = 40) -> str:
        """
        Generate a response to a prompt.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated response text
        """
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/generate",
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_stream(self, prompt: str, max_new_tokens: int = 1000,
                       temperature: float = 0.7, top_p: float = 0.9,
                       top_k: int = 40):
        """
        Generate a streaming response.
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Yields:
            Individual tokens as they're generated
        """
        payload = {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/generate_stream",
                json=payload,
                timeout=300,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data = json.loads(line_str[6:])
                            
                            if 'error' in data:
                                yield f"Error: {data['error']}"
                                break
                            
                            token = data.get('token', '')
                            is_done = data.get('done', False)
                            
                            if token:
                                yield token
                            
                            if is_done:
                                break
            else:
                yield f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history."""
        try:
            response = requests.post(f"{self.server_url}/clear_history")
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        try:
            response = requests.get(f"{self.server_url}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except:
            return {}
    
    def update_system_prompt(self, system_prompt: str) -> bool:
        """Update the system prompt."""
        try:
            payload = {"system_prompt": system_prompt}
            response = requests.post(
                f"{self.server_url}/update_system_prompt",
                json=payload
            )
            return response.status_code == 200
        except:
            return False
    
    def shutdown_server(self) -> bool:
        """Shutdown the server."""
        try:
            response = requests.post(f"{self.server_url}/shutdown")
            return response.status_code == 200
        except:
            return False

def quick_test():
    """Quick test function for rapid iteration."""
    client = GemmaClient()
    
    if not client.health_check():
        print("Error: Cannot connect to server. Make sure it's running.")
        return
    
    # Test prompts
    prompts = [
        "What is machine learning?",
        "Explain neural networks in simple terms",
        "What is a transformer in AI?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Prompt: {prompt}")
        print("Response: ", end="", flush=True)
        
        # Use streaming for real-time output
        for token in client.generate_stream(prompt, max_new_tokens=200):
            print(token, end="", flush=True)
        print()

def main():
    """Main interactive chat loop."""
    client = GemmaClient()
    
    # Check server health
    if not client.health_check():
        print("Error: Cannot connect to server.")
        print("Please start the server first:")
        print("  python src/model_server.py")
        print("  or")
        print("  python src/online_model_server.py")
        return
    
    print("Connected to server successfully!")
    print("Commands:")
    print("  • 'quit' / 'exit' / 'bye' - Exit chat")
    print("  • 'clear' - Clear conversation history")
    print("  • 'stats' - Show conversation statistics")
    print("  • 'prompt <text>' - Update system prompt")
    print("  • 'shutdown' - Shutdown the server")
    print("-" * 60)
    
    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'clear':
                if client.clear_history():
                    print("Conversation history cleared.")
                else:
                    print("Failed to clear history.")
                continue
            elif user_input.lower() == 'stats':
                stats = client.get_stats()
                print(f"Stats: {stats}")
                continue
            elif user_input.startswith('prompt '):
                new_prompt = user_input[7:].strip()
                if new_prompt:
                    if client.update_system_prompt(new_prompt):
                        print(f"System prompt updated: {new_prompt[:60]}...")
                    else:
                        print("Failed to update system prompt.")
                continue
            elif user_input.lower() == 'shutdown':
                confirm = input("Are you sure you want to shutdown the server? (y/n): ")
                if confirm.lower() in ['y', 'yes']:
                    if client.shutdown_server():
                        print("Server shutdown requested.")
                        break
                    else:
                        print("Failed to shutdown server.")
                continue
            
            # Generate response
            print("Assistant: ", end="", flush=True)
            
            # Use streaming for real-time output
            for token in client.generate_stream(user_input):
                print(token, end="", flush=True)
            print()
            
    except KeyboardInterrupt:
        print("\nChat interrupted. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test()
    else:
        main()
