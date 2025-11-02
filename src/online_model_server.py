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
    
    # No longer automatically load API Key, wait for user input
    config["provider"] = os.getenv("LLM_PROVIDER", "openai")
    config["api_key"] = None  # Default None, requires user to set manually
    config["base_url"] = os.getenv("LLM_BASE_URL")
    config["model"] = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Can load other configs from file, but not API Key
    try:
        with open("api_config.json", "r", encoding="utf-8") as f:
            file_config = json.load(f)
            # Only load non-sensitive configs
            for key in ["model", "max_tokens", "temperature", "top_p"]:
                if key in file_config:
                    config[key] = file_config[key]
    except FileNotFoundError:
        pass
    
    print(f"[INFO] Configuration loaded:")
    print(f"   Provider: {config['provider']}")
    print(f"   Model: {config['model']}")
    print(f"   API Key: {'Not set - waiting for user input' if not config['api_key'] else 'Set'}")

def initialize_server():
    """Initialize server"""
    print("=" * 70)
    print("[INFO] Starting Online LLM Model Server...")
    print("=" * 70)
    
    load_config()
    
    if not config["api_key"]:
        print("⚠️  Warning: API Key not set, please set environment variable or create api_config.json")
        print("   Example: export LLM_API_KEY='your-api-key'")
    
    print(f"[INFO] Server ready, listening on http://localhost:5000")
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
            "wenxin": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
            "ollama": "http://localhost:11434"
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
        elif self.provider == "ollama":
            return self._call_ollama(prompt, **kwargs)
        else:
            return self._call_custom(prompt, **kwargs)
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Generate streaming response"""
        if self.provider == "openai":
            yield from self._call_openai_stream(prompt, **kwargs)
        elif self.provider == "anthropic":
            yield from self._call_anthropic_stream(prompt, **kwargs)
        elif self.provider == "ollama":
            yield from self._call_ollama_stream(prompt, **kwargs)
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
    
    def _call_ollama(self, prompt: str, **kwargs) -> str:
        """Call Ollama API (OpenAI-compatible format)"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", config["model"]),
            "messages": self._build_messages(prompt),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "stream": False
        }
        
        # Add optional parameters if provided
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        if "max_tokens" in kwargs:
            data["num_predict"] = kwargs["max_tokens"]
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # Ollama can be slower on first run
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    def _call_ollama_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Call Ollama streaming API (OpenAI-compatible format)"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", config["model"]),
            "messages": self._build_messages(prompt),
            "temperature": kwargs.get("temperature", config["temperature"]),
            "stream": True
        }
        
        # Add optional parameters if provided
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        if "max_tokens" in kwargs:
            data["num_predict"] = kwargs["max_tokens"]
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=60
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
    
    # Ollama doesn't need a real API key
    if not config["api_key"] and config["provider"] != "ollama":
        raise Exception("API Key not set")
    
    # For Ollama, use a dummy API key
    api_key = config["api_key"] if config["api_key"] else "ollama"
    
    llm_client = OnlineLLMClient(
        provider=config["provider"],
        api_key=api_key,
        base_url=config["base_url"]
    )
    
    print(f"[SUCCESS] LLM client initialized: {config['provider']} - {config['model']}")

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

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint (supports 'message' parameter)"""
    if llm_client is None:
        return jsonify({"error": "LLM client not initialized"}), 503
    
    try:
        data = request.json
        # Support both 'message' and 'prompt' parameters
        message = data.get('message') or data.get('prompt')
        
        if not message:
            return jsonify({"error": "Missing 'message' or 'prompt' parameter"}), 400
        
        # Optional parameters
        max_tokens = data.get('max_new_tokens', config["max_tokens"])
        temperature = data.get('temperature', config["temperature"])
        top_p = data.get('top_p', config["top_p"])
        
        print(f"\n[INFO] Chat request: {message[:50]}...")
        
        # Generate response
        with model_lock:
            response = llm_client.generate_response(
                prompt=message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Update statistics
        global total_tokens_generated
        total_tokens_generated += len(response.split())
        
        return jsonify({
            "response": response,
            "message": message,
            "timestamp": time.time(),
            "provider": config["provider"],
            "model": config["model"]
        })
        
    except Exception as e:
        print(f"[ERROR] Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
        
        print(f"\n[INFO] Request received: {prompt[:50]}...")
        
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
                print(f"\n[INFO] Streaming request: {prompt[:50]}...")
                
                full_response = ""
                
                # Streaming generation
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

@app.route('/api_key_status', methods=['GET'])
def api_key_status():
    """Check API key status"""
    return jsonify({
        "has_api_key": bool(config["api_key"]),
        "provider": config["provider"]
    })

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    """
    Set API key (enhanced version)
    Automatically detect provider and configure
    """
    try:
        # Import API key detector
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.api_key_detector import APIKeyDetector
        
        data = request.json
        api_key = data.get('api_key', '').strip()
        manual_provider = data.get('provider')  # User can manually specify provider
        manual_base_url = data.get('base_url')  # User can manually specify base_url
        
        if not api_key:
            return jsonify({"error": "API key cannot be empty"}), 400
        
        # Automatically detect provider
        detection_result = APIKeyDetector.validate_and_detect(api_key)
        
        if not detection_result["valid"]:
            return jsonify({"error": detection_result["error"]}), 400
        
        # Get detected provider info
        detected_provider = detection_result.get("provider")
        provider_info = detection_result.get("provider_info")
        confidence = detection_result.get("confidence", 0.0)
        
        # If user manually specified provider, use it
        if manual_provider:
            detected_provider = manual_provider
            provider_info = APIKeyDetector.get_provider_info(manual_provider)
        
        # Update configuration
        config['api_key'] = api_key
        config['provider'] = detected_provider
        
        # Set base_url and model
        if provider_info:
            if manual_base_url:
                config['base_url'] = manual_base_url
            elif provider_info.base_url:
                config['base_url'] = provider_info.base_url
            
            # For Ollama, try to detect available models
            if detected_provider == "ollama":
                try:
                    import requests
                    response = requests.get(f"{config.get('base_url', 'http://localhost:11434')}/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        if models:
                            # Use the first available model
                            config['model'] = models[0]['name']
                            print(f"[INFO] Auto-detected Ollama model: {config['model']}")
                        else:
                            config['model'] = provider_info.default_model
                    else:
                        config['model'] = provider_info.default_model
                except:
                    config['model'] = provider_info.default_model
            else:
                config['model'] = provider_info.default_model
        
        # Try to initialize client
        try:
            initialize_llm_client()
            
            response_data = {
                "success": True,
                "message": "API key set successfully",
                "provider": detected_provider,
                "confidence": confidence,
                "base_url": config.get('base_url'),
                "model": config.get('model')
            }
            
            if provider_info:
                response_data["provider_display_name"] = provider_info.display_name
                response_data["supported_models"] = provider_info.supported_models
                response_data["description"] = provider_info.description
            
            if "warning" in detection_result:
                response_data["warning"] = detection_result["warning"]
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                "error": f"Initialization failed: {str(e)}",
                "provider": detected_provider,
                "suggestion": "Please check if API key is correct, or manually specify provider"
            }), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_api_key', methods=['POST'])
def test_api_key():
    """
    Test API key (enhanced version)
    Automatically detect provider and validate
    """
    try:
        # Import API key detector
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.api_key_detector import APIKeyDetector
        
        data = request.json
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({"valid": False, "error": "API key cannot be empty"}), 400
        
        # Perform format detection first
        detection_result = APIKeyDetector.validate_and_detect(api_key)
        
        if not detection_result["valid"]:
            return jsonify({
                "valid": False,
                "error": detection_result["error"],
                "stage": "format_validation"
            }), 400
        
        # Get detection results
        detected_provider = detection_result.get("provider")
        provider_info = detection_result.get("provider_info")
        confidence = detection_result.get("confidence", 0.0)
        
        # Return detection results (without actually calling API)
        response_data = {
            "valid": True,
            "provider": detected_provider,
            "confidence": confidence,
            "stage": "format_validation"
        }
        
        if provider_info:
            response_data.update({
                "provider_display_name": provider_info.display_name,
                "base_url": provider_info.base_url,
                "default_model": provider_info.default_model,
                "supported_models": provider_info.supported_models,
                "description": provider_info.description
            })
        
        if "warning" in detection_result:
            response_data["warning"] = detection_result["warning"]
        
        if "message" in detection_result:
            response_data["message"] = detection_result["message"]
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown server"""
    print("\n[INFO] Shutdown request received...")
    return jsonify({"message": "Server shutting down..."})

if __name__ == "__main__":
    # Initialize server
    initialize_server()
    
    # No longer auto-initialize LLM client, wait for user to input API Key
    print("⚠️  Waiting for user to input API key...")
    print("   Please set API key via POST /set_api_key endpoint")
    print("   Or test API key format via POST /test_api_key endpoint")
    
    # Start Flask server on port 5001 to avoid conflict with local model server
    print(f"\n[INFO] Starting online API server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
