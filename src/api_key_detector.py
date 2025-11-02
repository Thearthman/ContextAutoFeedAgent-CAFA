#!/usr/bin/env python3
"""
API Key Auto-Detection Module
Automatically identify provider based on key format and provide corresponding configuration
"""

import re
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class ProviderInfo:
    """Provider information"""
    name: str
    display_name: str
    pattern: str
    base_url: str
    default_model: str
    supported_models: List[str]
    description: str


class APIKeyDetector:
    """API Key Detector - Automatically identify provider"""
    
    # Provider information database
    PROVIDERS = {
        "openai": ProviderInfo(
            name="openai",
            display_name="OpenAI",
            pattern=r"^sk-[a-zA-Z0-9]{32,}$",
            base_url="https://api.openai.com/v1",
            default_model="gpt-3.5-turbo",
            supported_models=[
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ],
            description="OpenAI GPT Series Models"
        ),
        
        "anthropic": ProviderInfo(
            name="anthropic",
            display_name="Anthropic",
            pattern=r"^sk-ant-[a-zA-Z0-9\-]{20,}$",
            base_url="https://api.anthropic.com/v1",
            default_model="claude-3-sonnet-20240229",
            supported_models=[
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0"
            ],
            description="Anthropic Claude Series Models"
        ),
        
        "google": ProviderInfo(
            name="google",
            display_name="Google",
            pattern=r"^AIza[a-zA-Z0-9\-_]{35}$",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            default_model="gemini-pro",
            supported_models=[
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-ultra"
            ],
            description="Google Gemini Series Models"
        ),
        
        "qwen": ProviderInfo(
            name="qwen",
            display_name="Tongyi Qwen (Qwen)",
            pattern=r"^sk-[a-f0-9]{32}$",
            base_url="https://dashscope.aliyuncs.com/api/v1",
            default_model="qwen-turbo",
            supported_models=[
                "qwen-turbo",
                "qwen-plus",
                "qwen-max"
            ],
            description="Alibaba Cloud Tongyi Qwen Series Models"
        ),
        
        "deepseek": ProviderInfo(
            name="deepseek",
            display_name="DeepSeek",
            pattern=r"^sk-[a-f0-9]{32}$",
            base_url="https://api.deepseek.com/v1",
            default_model="deepseek-chat",
            supported_models=[
                "deepseek-chat",
                "deepseek-coder"
            ],
            description="DeepSeek AI Models"
        ),
        
        "moonshot": ProviderInfo(
            name="moonshot",
            display_name="Moonshot AI (Kimi)",
            pattern=r"^sk-[a-zA-Z0-9]{32,}$",
            base_url="https://api.moonshot.cn/v1",
            default_model="moonshot-v1-8k",
            supported_models=[
                "moonshot-v1-8k",
                "moonshot-v1-32k",
                "moonshot-v1-128k"
            ],
            description="Moonshot Kimi Series Models"
        ),
        
        "zhipu": ProviderInfo(
            name="zhipu",
            display_name="Zhipu AI (GLM)",
            pattern=r"^[a-f0-9]{32}\.[a-zA-Z0-9]{6}$",
            base_url="https://open.bigmodel.cn/api/paas/v4",
            default_model="glm-4",
            supported_models=[
                "glm-4",
                "glm-3-turbo",
                "chatglm_turbo"
            ],
            description="Zhipu AI GLM Series Models"
        ),
        
        "ollama": ProviderInfo(
            name="ollama",
            display_name="Ollama (Local)",
            pattern=r"^ollama$|^OLLAMA$|^http://localhost:11434$",
            base_url="http://localhost:11434",
            default_model="llama2",
            supported_models=[
                "llama2",
                "llama3",
                "llama3:70b",
                "codellama",
                "mistral",
                "mixtral",
                "phi",
                "gemma",
                "qwen",
                "deepseek-coder"
            ],
            description="Ollama - Run LLMs locally (no API key required)"
        ),
        
        # Other providers compatible with OpenAI format
        "openai_compatible": ProviderInfo(
            name="openai_compatible",
            display_name="OpenAI Compatible API",
            pattern=r"^sk-.*",  # Loose matching
            base_url="",  # Need user to specify
            default_model="gpt-3.5-turbo",
            supported_models=[],
            description="Third-party API compatible with OpenAI format"
        ),
    }
    
    @classmethod
    def detect(cls, api_key: str) -> Tuple[Optional[str], Optional[ProviderInfo], float]:
        """
        Automatically detect API key provider
        
        Args:
            api_key: API key
        
        Returns:
            (provider_name, provider_info, confidence)
            confidence: 0.0-1.0, 1.0 means perfect match
        """
        if not api_key or not api_key.strip():
            return None, None, 0.0
        
        api_key = api_key.strip()
        
        # Try exact match for each provider pattern
        matches = []
        
        for provider_name, provider_info in cls.PROVIDERS.items():
            if provider_name == "openai_compatible":
                continue  # Skip compatible mode, check last
            
            if re.match(provider_info.pattern, api_key):
                # Calculate confidence
                confidence = cls._calculate_confidence(api_key, provider_info)
                matches.append((provider_name, provider_info, confidence))
        
        # Sort by confidence
        matches.sort(key=lambda x: x[2], reverse=True)
        
        if matches:
            # Return highest confidence match
            return matches[0]
        
        # If no exact match, check if OpenAI compatible format
        if api_key.startswith("sk-"):
            provider_info = cls.PROVIDERS["openai_compatible"]
            return "openai_compatible", provider_info, 0.5
        
        return None, None, 0.0
    
    @classmethod
    def _calculate_confidence(cls, api_key: str, provider_info: ProviderInfo) -> float:
        """
        Calculate match confidence
        
        Args:
            api_key: API key
            provider_info: Provider information
        
        Returns:
            confidence (0.0-1.0)
        """
        confidence = 0.8  # Base confidence
        
        # OpenAI: starts with sk-, followed by base64 characters
        if provider_info.name == "openai":
            if len(api_key) >= 40 and len(api_key) <= 60:
                confidence = 0.95
            elif len(api_key) > 60:
                confidence = 0.99  # New OpenAI keys are longer
        
        # Anthropic: starts with sk-ant-
        elif provider_info.name == "anthropic":
            if "ant" in api_key[:10]:
                confidence = 0.99
        
        # Google: starts with AIza, fixed length
        elif provider_info.name == "google":
            if len(api_key) == 39:
                confidence = 0.99
        
        # Zhipu: fixed format 32-char hex.6-char
        elif provider_info.name == "zhipu":
            if "." in api_key:
                parts = api_key.split(".")
                if len(parts) == 2 and len(parts[0]) == 32 and len(parts[1]) == 6:
                    confidence = 0.99
        
        # Ollama: special identifier
        elif provider_info.name == "ollama":
            if api_key.lower() == "ollama" or "localhost:11434" in api_key:
                confidence = 0.99
        
        return confidence
    
    @classmethod
    def get_provider_info(cls, provider_name: str) -> Optional[ProviderInfo]:
        """
        Get provider information
        
        Args:
            provider_name: Provider name
        
        Returns:
            Provider information
        """
        return cls.PROVIDERS.get(provider_name)
    
    @classmethod
    def get_all_providers(cls) -> Dict[str, ProviderInfo]:
        """Get all supported providers"""
        return {k: v for k, v in cls.PROVIDERS.items() if k != "openai_compatible"}
    
    @classmethod
    def validate_and_detect(cls, api_key: str) -> Dict:
        """
        Validate and detect API key
        
        Args:
            api_key: API key
        
        Returns:
            Dictionary containing detection results
        """
        if not api_key or not api_key.strip():
            return {
                "valid": False,
                "error": "API key cannot be empty",
                "provider": None,
                "confidence": 0.0
            }
        
        api_key = api_key.strip()
        
        # Special case for Ollama - skip length check
        if api_key.lower() == "ollama" or "localhost:11434" in api_key:
            provider_info = cls.PROVIDERS.get("ollama")
            return {
                "valid": True,
                "provider": "ollama",
                "provider_info": provider_info,
                "confidence": 1.0,
                "message": f"Detected {provider_info.display_name} - Local LLM service",
                "note": "Ollama runs locally and doesn't require an API key. Just enter 'ollama' to use it."
            }
        
        # Length check for other providers
        if len(api_key) < 10:
            return {
                "valid": False,
                "error": "API key too short",
                "provider": None,
                "confidence": 0.0
            }
        
        # Detect provider
        provider_name, provider_info, confidence = cls.detect(api_key)
        
        if provider_name is None:
            return {
                "valid": False,
                "error": "Unrecognized API key format",
                "provider": None,
                "confidence": 0.0
            }
        
        # Special handling for Ollama (no API key needed)
        if provider_name == "ollama":
            return {
                "valid": True,
                "provider": provider_name,
                "provider_info": provider_info,
                "confidence": confidence,
                "message": f"Detected {provider_info.display_name} - Local LLM service",
                "note": "Ollama runs locally and doesn't require an API key. Just enter 'ollama' to use it."
            }
        
        # If compatible mode, prompt user
        if provider_name == "openai_compatible":
            return {
                "valid": True,
                "provider": provider_name,
                "provider_info": provider_info,
                "confidence": confidence,
                "warning": "Detected OpenAI compatible format, but cannot determine specific provider, please verify manually"
            }
        
        return {
            "valid": True,
            "provider": provider_name,
            "provider_info": provider_info,
            "confidence": confidence,
            "message": f"Detected {provider_info.display_name} API key (confidence: {confidence:.0%})"
        }


# Usage example
if __name__ == "__main__":
    print("🔍 API Key Auto-Detection Test")
    print("=" * 70)
    
    # Test keys from different providers
    test_keys = [
        ("sk-1234567890abcdefghijklmnopqrstuvwxyz123456", "OpenAI"),
        ("sk-ant-api03-1234567890abcdefghijk", "Anthropic"),
        ("AIzaSyC1234567890abcdefghijklmnopqrstuv", "Google"),
        ("sk-abcdef1234567890abcdef1234567890", "Qwen/DeepSeek"),
        ("abcdef1234567890abcdef1234567890.ABC123", "Zhipu AI"),
        ("invalid-key-format", "Unknown"),
    ]
    
    for api_key, expected in test_keys:
        print(f"\nTesting key: {api_key[:20]}...")
        print(f"Expected: {expected}")
        
        result = APIKeyDetector.validate_and_detect(api_key)
        
        if result["valid"]:
            provider_info = result.get("provider_info")
            if provider_info:
                print(f"✅ {result.get('message', 'Detection successful')}")
                print(f"   Provider: {provider_info.display_name}")
                print(f"   Default model: {provider_info.default_model}")
                print(f"   API URL: {provider_info.base_url}")
            if "warning" in result:
                print(f"⚠️  {result['warning']}")
        else:
            print(f"❌ {result['error']}")
    
    # Display all supported providers
    print("\n" + "=" * 70)
    print("Supported Providers:")
    print("=" * 70)
    
    for name, info in APIKeyDetector.get_all_providers().items():
        print(f"\n{info.display_name} ({name})")
        print(f"  Description: {info.description}")
        print(f"  Default model: {info.default_model}")
        print(f"  Supported models: {', '.join(info.supported_models[:3])}")
        if len(info.supported_models) > 3:
            print(f"                    and {len(info.supported_models)} models total")
    
    print("\n" + "=" * 70)
