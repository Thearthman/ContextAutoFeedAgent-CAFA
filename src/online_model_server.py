#!/usr/bin/env python3
"""
Online LLM Model Server
Supports multiple online LLM APIs without requiring local GPU and model downloads

Supported APIs:
- OpenAI GPT-4/GPT-3.5
- Anthropic Claude
- Google Gemini
- Qwen (Tongyi Qianwen)
- ERNIE Bot (Wenxin Yiyan)
- Custom API

Usage:
    python src/online_model_server.py
"""

import sys
import os
import json
import time
import requests
from typing import Dict, Any, Optional, Generator
from threading import Lock
from flask import Flask, request, jsonify, Response

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)

# Global configuration
config = {
    "provider": "openai",  # openai, anthropic, google, qwen, wenxin, custom
    "api_key": None,
    "base_url": None,
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": True
}

# Conversation history
conversation_history = []
model_lock = Lock()

# Statistics
total_tokens_generated = 0
conversation_count = 0

def load_config():
    """Load API configuration from environment variables or config file"""
    global config
    
    # Read configuration from environment variables
    config["provider"] = os.getenv("LLM_PROVIDER", "openai")
    config["api_key"] = os.getenv("LLM_API_KEY")
    config["base_url"] = os.getenv("LLM_BASE_URL")
    config["model"] = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # If no API Key, try reading from file
    if not config["api_key"]:
        try:
            with open("api_config.json", "r", encoding="utf-8") as f:
                file_config = json.load(f)
                config.update(file_config)
        except FileNotFoundError:
            pass
    
    print(f"🔧 Configuration loaded:")
    print(f"   Provider: {config['provider']}")
    print(f"   Model: {config['model']}")
    print(f"   API Key: {'Set' if config['api_key'] else 'Not set'}")

def initialize_server():
    """Initialize server"""
    print("=" * 70)
    print("🌐 Starting Online LLM Model Server...")
    print("=" * 70)
    
    load_config()
    
    if not config["api_key"]:
        print("⚠️  Warning: API Key not set, please set environment variable or create api_config.json")
        print("   Example: export LLM_API_KEY='your-api-key'")
    
    print(f"🌐 Server ready, listening on http://localhost:5000")
    print("=" * 70)

class OnlineLLMClient:
    """Online LLM API Client"""
    
    def __init__(self, provider: str, api_key: str, base_url: str = None):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url or self._get_default_base_url()
        
    def _get_default_base_url(self) -> str:
        """Get default API base URL"""
        urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "google": "https://generativelanguage.googleapis.com/v1beta",
            "qwen": "https://dashscope.aliyuncs.com/api/v1",
            "wenxin": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"
        }
        return urls.get(self.provider, "https://api.openai.com/v1")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response"""
        if self.provider == "openai":
            return self._call_openai(prompt, **kwargs)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, **kwargs)
        elif self.provider == "google":
            return self._call_google(prompt, **kwargs)
        elif self.provider == "qwen":
            return self._call_qwen(prompt, **kwargs)
        elif self.provider == "wenxin":
            return self._call_wenxin(prompt, **kwargs)
        else:
            return self._call_custom(prompt, **kwargs)
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Generate streaming response"""
        if self.provider == "openai":
            yield from self._call_openai_stream(prompt, **kwargs)
        elif self.provider == "anthropic":
            yield from self._call_anthropic_stream(prompt, **kwargs)
        else:
            # For APIs that don't support streaming, return complete response
            response = self.generate_response(prompt, **kwargs)
            for char in response:
                yield char
                time.sleep(0.01)  # Simulate streaming output
    
    def _call_openai(self, prompt: str, **kwargs) -> str:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", config["model"]),
            "messages": self._build_messages(prompt),
            "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "top_p": kwargs.get("top_p", config["top_p"]),
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def _call_openai_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Call OpenAI streaming API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", config["model"]),
            "messages": self._build_messages(prompt),
            "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "top_p": kwargs.get("top_p", config["top_p"]),
            "stream": True
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        else:
            yield f"Error: {response.status_code} - {response.text}"
    
    def _call_anthropic(self, prompt: str, **kwargs) -> str:
        """Call Anthropic Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": kwargs.get("model", "claude-3-sonnet-20240229"),
            "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "messages": self._build_messages(prompt)
        }
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"]
        else:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    def _call_anthropic_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Call Anthropic streaming API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": kwargs.get("model", "claude-3-sonnet-20240229"),
            "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "messages": self._build_messages(prompt),
            "stream": True
        }
        
        response = requests.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=data,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get('type') == 'content_block_delta':
                                yield data.get('delta', {}).get('text', '')
                        except json.JSONDecodeError:
                            continue
        else:
            yield f"Error: {response.status_code} - {response.text}"
    
    def _call_google(self, prompt: str, **kwargs) -> str:
        """Call Google Gemini API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", config["max_tokens"]),
                "temperature": kwargs.get("temperature", config["temperature"]),
                "topP": kwargs.get("top_p", config["top_p"])
            }
        }
        
        response = requests.post(
            f"{self.base_url}/models/{kwargs.get('model', 'gemini-pro')}:generateContent?key={self.api_key}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Google API error: {response.status_code} - {response.text}")
    
    def _call_qwen(self, prompt: str, **kwargs) -> str:
        """Call Qwen (Tongyi Qianwen) API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", "qwen-turbo"),
            "input": {
                "messages": self._build_messages(prompt)
            },
            "parameters": {
                "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
                "temperature": kwargs.get("temperature", config["temperature"]),
                "top_p": kwargs.get("top_p", config["top_p"])
            }
        }
        
        response = requests.post(
            f"{self.base_url}/services/aigc/text-generation/generation",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["output"]["text"]
        else:
            raise Exception(f"Qwen API error: {response.status_code} - {response.text}")
    
    def _call_wenxin(self, prompt: str, **kwargs) -> str:
        """Call ERNIE Bot (Wenxin Yiyan) API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": self._build_messages(prompt),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "top_p": kwargs.get("top_p", config["top_p"]),
            "penalty_score": 1.0,
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions?access_token={self.api_key}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["result"]
        else:
            raise Exception(f"ERNIE Bot API error: {response.status_code} - {response.text}")
    
    def _call_custom(self, prompt: str, **kwargs) -> str:
        """Call custom API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", config["max_tokens"]),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "top_p": kwargs.get("top_p", config["top_p"])
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", result.get("text", "No response"))
        else:
            raise Exception(f"Custom API error: {response.status_code} - {response.text}")
    
    def _build_messages(self, prompt: str) -> list:
        """Build message list"""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": "You are a helpful AI assistant."
        })
        
        # Add conversation history
        messages.extend(conversation_history[-10:])  # Keep only last 10 turns
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages

# Global LLM client
llm_client = None

def initialize_llm_client():
    """Initialize LLM client"""
    global llm_client
    
    if not config["api_key"]:
        raise Exception("API Key not set")
    
    llm_client = OnlineLLMClient(
        provider=config["provider"],
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    
    print(f"✅ LLM client initialized: {config['provider']} - {config['model']}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if llm_client is None:
        return jsonify({"status": "initializing"}), 503
    
    return jsonify({
        "status": "healthy",
        "provider": config["provider"],
        "model": config["model"],
        "total_conversations": conversation_count + 1,
        "total_tokens_generated": total_tokens_generated
    })

@app.route('/generate', methods=['POST'])
def generate():
    """Generate response"""
    if llm_client is None:
        return jsonify({"error": "LLM client not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' parameter"}), 400
        
        # Optional parameters
        max_tokens = data.get('max_new_tokens', config["max_tokens"])
        temperature = data.get('temperature', config["temperature"])
        top_p = data.get('top_p', config["top_p"])
        
        print(f"\n📨 Request received: {prompt[:50]}...")
        
        # Generate response
        with model_lock:
            response = llm_client.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Update statistics
        global total_tokens_generated
        total_tokens_generated += len(response.split())
        
        return jsonify({
            "response": response,
            "prompt": prompt,
            "timestamp": time.time(),
            "provider": config["provider"],
            "model": config["model"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_stream', methods=['POST'])
def generate_stream():
    """Generate streaming response"""
    if llm_client is None:
        return jsonify({"error": "LLM client not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' parameter"}), 400
        
        def generate_sse():
            """Generate Server-Sent Events"""
            try:
                print(f"\n📨 Streaming request: {prompt[:50]}...")
                
                full_response = ""
                
                # Streaming生成
                with model_lock:
                    for token in llm_client.generate_stream(
                        prompt=prompt,
                        max_tokens=data.get('max_new_tokens', config["max_tokens"]),
                        temperature=data.get('temperature', config["temperature"]),
                        top_p=data.get('top_p', config["top_p"])
                    ):
                        full_response += token
                        yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                
                # Update conversation history
                conversation_history.append({"role": "user", "content": prompt})
                conversation_history.append({"role": "assistant", "content": full_response})
                
                # Update statistics
                global total_tokens_generated
                total_tokens_generated += len(full_response.split())
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate_sse(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history, conversation_count
    
    with model_lock:
        conversation_history = []
        conversation_count += 1
    
    return jsonify({"message": "Conversation history cleared"})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    return jsonify({
        "total_conversations": conversation_count + 1,
        "total_tokens_generated": total_tokens_generated,
        "provider": config["provider"],
        "model": config["model"],
        "conversation_history_length": len(conversation_history)
    })

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "provider": config["provider"],
        "model": config["model"],
        "max_tokens": config["max_tokens"],
        "temperature": config["temperature"],
        "top_p": config["top_p"],
        "api_key_set": bool(config["api_key"])
    })

@app.route('/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.json
        
        # Update configuration
        if 'provider' in data:
            config['provider'] = data['provider']
        if 'model' in data:
            config['model'] = data['model']
        if 'max_tokens' in data:
            config['max_tokens'] = data['max_tokens']
        if 'temperature' in data:
            config['temperature'] = data['temperature']
        if 'top_p' in data:
            config['top_p'] = data['top_p']
        
        # Reinitialize client
        if 'api_key' in data:
            config['api_key'] = data['api_key']
            initialize_llm_client()
        
        return jsonify({"message": "Configuration updated"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown server"""
    print("\n🛑 Shutdown request received...")
    return jsonify({"message": "Server shutting down..."})

if __name__ == "__main__":
    # Initialize server
    initialize_server()
    
    # Initialize LLM client
    try:
        initialize_llm_client()
    except Exception as e:
        print(f"⚠️  LLM client initialization failed: {e}")
        print("   Server will still start, but API Key needs to be configured manually")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
