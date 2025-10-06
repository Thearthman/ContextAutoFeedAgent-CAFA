#!/usr/bin/env python3
"""
Client for Gemma Model Server
Send requests to the persistent model server without reloading the model.

Usage:
    python src/model_client.py

This script can be modified and rerun instantly - the model stays loaded in the server.
"""

import requests
import json
import sys
import os
from typing import Optional

class GemmaClient:
    """Client for interacting with the Gemma model server."""
    
    def __init__(self, server_url: str = "http://localhost:5000"):
        """
        Initialize the client.
        
        Args:
            server_url: URL of the model server
        """
        self.server_url = server_url
        self._check_server_health()
    
    def _check_server_health(self):
        """Check if the server is healthy."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connected to model server")
                print(f"   Model: {data.get('model_id')}")
                print(f"   Status: {data.get('status')}")
                print(f"   Total conversations: {data.get('total_conversations')}")
            else:
                print(f"⚠️  Server returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to model server!")
            print(f"   Make sure the server is running: python src/model_server.py")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")
            sys.exit(1)
    
    def generate(
        self, 
        prompt: str,
        max_new_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40
    ) -> Optional[str]:
        """
        Generate a response from the model.
        
        Args:
            prompt: User input prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated response text or None if error
        """
        try:
            payload = {
                "prompt": prompt,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
            
            print(f"\n📤 Sending: {prompt[:100]}...")
            
            response = requests.post(
                f"{self.server_url}/generate",
                json=payload,
                timeout=300  # 5 minutes timeout for generation
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response')
            else:
                print(f"❌ Server error: {response.status_code}")
                print(f"   {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def clear_history(self) -> bool:
        """Clear the conversation history."""
        try:
            response = requests.post(f"{self.server_url}/clear_history")
            if response.status_code == 200:
                print("🧹 Conversation history cleared")
                return True
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_stats(self) -> Optional[dict]:
        """Get conversation statistics."""
        try:
            response = requests.get(f"{self.server_url}/stats")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def update_system_prompt(self, new_prompt: str) -> bool:
        """Update the system prompt."""
        try:
            payload = {"system_prompt": new_prompt}
            response = requests.post(
                f"{self.server_url}/update_system_prompt",
                json=payload
            )
            if response.status_code == 200:
                print(f"🎯 System prompt updated")
                return True
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def shutdown_server(self) -> bool:
        """Shutdown the model server."""
        try:
            response = requests.post(f"{self.server_url}/shutdown")
            if response.status_code == 200:
                print("🛑 Server shutdown requested")
                return True
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def chat_loop(self):
        """Interactive chat loop."""
        print("\n" + "=" * 60)
        print("🎮 Gemma Client - Connected to Model Server")
        print("=" * 60)
        print("Commands:")
        print("  • Type normally to chat")
        print("  • 'quit' / 'exit' / 'bye' - Exit client (server keeps running)")
        print("  • 'clear' - Clear conversation history")
        print("  • 'stats' - Show conversation statistics")
        print("  • 'prompt <text>' - Update system prompt")
        print("  • 'shutdown' - Shutdown the model server")
        print("-" * 60)
        
        try:
            while True:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! (Server still running)")
                    break
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                elif user_input.lower() == 'stats':
                    stats = self.get_stats()
                    if stats:
                        print(f"📊 Stats: {stats['total_turns']} turns, "
                              f"{stats['total_tokens_generated']} tokens, "
                              f"{stats['conversation_sessions']} sessions")
                    continue
                elif user_input.lower().startswith('prompt '):
                    new_prompt = user_input[7:].strip()
                    if new_prompt:
                        self.update_system_prompt(new_prompt)
                    continue
                elif user_input.lower() == 'shutdown':
                    confirm = input("Are you sure you want to shutdown the server? (yes/no): ")
                    if confirm.lower() == 'yes':
                        self.shutdown_server()
                        break
                    continue
                
                # Generate response
                print("Assistant: ", end="", flush=True)
                response = self.generate(user_input)
                if response:
                    print(response)
                
        except KeyboardInterrupt:
            print("\n👋 Client interrupted. (Server still running)")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")


def main():
    """Main function for the client."""
    # Create client and start chat
    client = GemmaClient()
    client.chat_loop()


def quick_test():
    """Quick test function - modify this for rapid testing!"""
    client = GemmaClient()
    
    # Test different prompts quickly
    prompts = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about AI."
    ]
    
    for prompt in prompts:
        print(f"\n{'='*60}")
        print(f"Testing: {prompt}")
        print('='*60)
        response = client.generate(prompt, max_new_tokens=200)
        if response:
            print(f"\nResponse: {response}")
    
    # Get stats
    stats = client.get_stats()
    print(f"\n📊 Final Stats: {stats}")


if __name__ == "__main__":
    # Choose mode:
    # 1. Interactive chat loop
    main()
    
    # 2. Quick test mode (comment out main() above and uncomment below)
    # quick_test()

