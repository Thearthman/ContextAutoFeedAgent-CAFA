#!/usr/bin/env python3
"""
Online LLM Model Server Test Script
Demonstrates how to use online LLM API
"""

import requests
import json
import time

def test_online_llm():
    """Test online LLM server"""
    base_url = "http://localhost:5000"
    
    print("🧪 Online LLM Model Server Test")
    print("=" * 50)
    
    # 1. Health check
    print("\n1️⃣ Health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Server status: {health['status']}")
            if health['status'] == 'healthy':
                print(f"   📊 Provider: {health['provider']}")
                print(f"   🤖 Model: {health['model']}")
            else:
                print("   ⚠️  Server initializing (needs API Key configuration)")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # 2. Get configuration
    print("\n2️⃣ Get configuration...")
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   📋 Provider: {config['provider']}")
            print(f"   🤖 Model: {config['model']}")
            print(f"   🔑 API Key: {'Set' if config['api_key_set'] else 'Not set'}")
            print(f"   🌡️  Temperature: {config['temperature']}")
            print(f"   📏 Max tokens: {config['max_tokens']}")
        else:
            print(f"   ❌ Get configuration failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Get configuration failed: {e}")
    
    # 3. Get statistics
    print("\n3️⃣ Get statistics...")
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   💬 Conversations: {stats['total_conversations']}")
            print(f"   📝 Tokens generated: {stats['total_tokens_generated']}")
            print(f"   📚 History length: {stats['conversation_history_length']}")
        else:
            print(f"   ❌ Get statistics failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Get statistics failed: {e}")
    
    # 4. Test generation (if API Key available)
    print("\n4️⃣ Test generation...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200 and response.json()['status'] == 'healthy':
            # Has API Key, can test generation
            test_prompt = "Hello, please introduce yourself briefly"
            print(f"   📨 Send test request: {test_prompt}")
            
            generate_response = requests.post(f"{base_url}/generate", json={
                "prompt": test_prompt,
                "max_new_tokens": 200,
                "temperature": 0.7
            })
            
            if generate_response.status_code == 200:
                result = generate_response.json()
                print(f"   ✅ Generation successful!")
                print(f"   🤖 Response: {result['response'][:100]}...")
                print(f"   ⏰ Timestamp: {result['timestamp']}")
            else:
                print(f"   ❌ Generation failed: {generate_response.status_code}")
                print(f"   📄 Error message: {generate_response.text}")
        else:
            print("   ⚠️  Skip generation test (needs API Key configuration)")
            print("   💡 Tip: Set environment variable LLM_API_KEY or create api_config.json")
    except Exception as e:
        print(f"   ❌ Generation test failed: {e}")
    
    # 5. Show usage instructions
    print("\n" + "=" * 50)
    print("📖 Usage Instructions:")
    print("=" * 50)
    print("1. Configure API Key:")
    print("   Windows: $env:LLM_API_KEY='your-api-key'")
    print("   Linux/Mac: export LLM_API_KEY='your-api-key'")
    print()
    print("2. Supported providers:")
    print("   • OpenAI (GPT-3.5, GPT-4)")
    print("   • Anthropic (Claude)")
    print("   • Google (Gemini)")
    print("   • Qwen (Tongyi Qianwen)")
    print("   • ERNIE Bot (Wenxin Yiyan)")
    print()
    print("3. Launch floating UI:")
    print("   python src/floating_ui.py")
    print()
    print("4. API documentation:")
    print("   http://localhost:5000/health")
    print("   http://localhost:5000/config")
    print("   http://localhost:5000/stats")
    print()
    print("🎉 Online LLM server running normally!")

def test_with_api_key():
    """Complete test using API Key"""
    print("\n🔑 Test with API Key")
    print("=" * 30)
    
    # Check if API Key available
    api_key = input("Please enter your API Key (or press Enter to skip): ").strip()
    if not api_key:
        print("⏭️  Skip API Key test")
        return
    
    provider = input("Choose provider (openai/anthropic/google/qwen/wenxin): ").strip() or "openai"
    
    # Update configuration
    base_url = "http://localhost:5000"
    try:
        response = requests.post(f"{base_url}/config", json={
            "provider": provider,
            "api_key": api_key
        })
        
        if response.status_code == 200:
            print("✅ Configuration updated successfully")
            
            # Wait for configuration to take effect
            time.sleep(2)
            
            # Test generation
            test_prompt = "Please briefly introduce the history of artificial intelligence development"
            print(f"\n📨 Test generation: {test_prompt}")
            
            generate_response = requests.post(f"{base_url}/generate", json={
                "prompt": test_prompt,
                "max_new_tokens": 300,
                "temperature": 0.7
            })
            
            if generate_response.status_code == 200:
                result = generate_response.json()
                print("✅ Generation successful!")
                print(f"🤖 Response:\n{result['response']}")
                print(f"\n📊 Provider: {result['provider']}")
                print(f"🤖 Model: {result['model']}")
            else:
                print(f"❌ Generation failed: {generate_response.text}")
        else:
            print(f"❌ Configuration update failed: {response.text}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_online_llm()
    
    # Ask if user wants to do API Key test
    choice = input("\nDo you want to do API Key test? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        test_with_api_key()
    
    print("\n🎯 Next steps:")
    print("1. Configure your API Key")
    print("2. Launch floating UI: python src/floating_ui.py")
    print("3. Enjoy AI conversation experience!")
