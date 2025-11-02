#!/usr/bin/env python3
"""
Unified Configuration Management Module
Manages configuration for all services, supports environment variables, config files, and dynamic updates
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Unified Configuration Manager"""
    
    # Default configuration
    DEFAULT_CONFIG = {
        # LLM service configuration
        "llm": {
            "local_model_url": "http://localhost:5000",
            "online_model_url": "http://localhost:5001",
            "default_provider": "local",  # local, openai, anthropic, etc.
            "model_name": "google/gemma-3-12b-it",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
        },
        
        # Memory service configuration
        "memory": {
            "enabled": True,
            "api_url": "http://localhost:8000",
            "storage_path": "memory_data.json",
            "enhanced_storage_path": "enhanced_memory_data.json",
            "embedding_model": "all-MiniLM-L6-v2",
            "auto_store": True,
            "similarity_threshold": 0.7,
            "decay_enabled": True,
            "default_half_life_days": 30,
        },
        
        # Integrated service configuration
        "integrated_service": {
            "enabled": True,
            "port": 6000,
            "host": "0.0.0.0",
            "use_local_memory": True,
            "auto_memory_fetch": True,
        },
        
        # UI configuration
        "ui": {
            "window_width": 450,
            "window_height": 700,
            "always_on_top": True,
            "theme": "dark",
        },
        
        # API key configuration (loaded from environment variables or config file)
        "api_keys": {
            "openai": None,
            "anthropic": None,
            "google": None,
            "qwen": None,
        },
        
        # Logging configuration
        "logging": {
            "enabled": True,
            "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            "log_dir": "logs",
            "max_log_size_mb": 10,
            "backup_count": 5,
        },
        
        # Performance configuration
        "performance": {
            "enable_caching": True,
            "cache_ttl_seconds": 3600,
            "max_concurrent_requests": 5,
            "request_timeout_seconds": 30,
        }
    }
    
    def __init__(self, config_file: str = "api_config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Configuration file path
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration (priority: environment variables > config file > defaults)"""
        config = self.DEFAULT_CONFIG.copy()
        
        # 1. Load from config file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config = self._deep_merge(config, file_config)
            except Exception as e:
                print(f"⚠️  Config file load failed: {e}, using defaults")
        
        # 2. Override from environment variables
        config = self._load_from_env(config)
        
        return config
    
    def _deep_merge(self, base: Dict, overlay: Dict) -> Dict:
        """Deep merge dictionaries"""
        result = base.copy()
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _load_from_env(self, config: Dict) -> Dict:
        """Load configuration from environment variables"""
        # API Keys
        if os.getenv("OPENAI_API_KEY"):
            config["api_keys"]["openai"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("ANTHROPIC_API_KEY"):
            config["api_keys"]["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
        if os.getenv("GOOGLE_API_KEY"):
            config["api_keys"]["google"] = os.getenv("GOOGLE_API_KEY")
        if os.getenv("QWEN_API_KEY"):
            config["api_keys"]["qwen"] = os.getenv("QWEN_API_KEY")
        
        # LLM configuration
        if os.getenv("LLM_PROVIDER"):
            config["llm"]["default_provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_MODEL"):
            config["llm"]["model_name"] = os.getenv("LLM_MODEL")
        
        # Memory configuration
        if os.getenv("MEMORY_ENABLED"):
            config["memory"]["enabled"] = os.getenv("MEMORY_ENABLED").lower() == "true"
        
        return config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value (supports dot-separated path)
        
        Example: get("llm.temperature") -> 0.7
        
        Args:
            key_path: Configuration path, separated by dots
            default: Default value
        
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key_path: Configuration path
            value: Configuration value
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(self.config_file) or '.', exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Configuration save failed: {e}")
    
    def reload(self) -> None:
        """Reload configuration"""
        self.config = self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        
        Returns:
            (is_valid, error_list)
        """
        errors = []
        
        # Validate ports
        ports = [
            self.get("llm.local_model_url"),
            self.get("llm.online_model_url"),
            self.get("memory.api_url"),
        ]
        
        # Validate paths
        storage_path = self.get("memory.storage_path")
        if storage_path and not os.path.isdir(os.path.dirname(storage_path) or '.'):
            errors.append(f"Storage path directory does not exist: {storage_path}")
        
        # Validate value ranges
        temperature = self.get("llm.temperature")
        if not (0 <= temperature <= 2):
            errors.append(f"temperature should be between 0-2, current value: {temperature}")
        
        top_p = self.get("llm.top_p")
        if not (0 <= top_p <= 1):
            errors.append(f"top_p should be between 0-1, current value: {top_p}")
        
        return len(errors) == 0, errors
    
    def export_template(self, output_file: str = "api_config.json.example") -> None:
        """Export configuration template"""
        template = self.DEFAULT_CONFIG.copy()
        # Hide sensitive information
        template["api_keys"] = {
            "openai": "your-openai-api-key",
            "anthropic": "your-anthropic-api-key",
            "google": "your-google-api-key",
            "qwen": "your-qwen-api-key",
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Configuration template exported to {output_file}")


# Global configuration instance
_global_config = None

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config


# Usage example
if __name__ == "__main__":
    print("🔧 Configuration Manager Test")
    print("=" * 70)
    
    # Create configuration manager
    config = ConfigManager()
    
    # Get configuration
    print("\n1️⃣ Get configuration:")
    print(f"  LLM Temperature: {config.get('llm.temperature')}")
    print(f"  Memory Enabled: {config.get('memory.enabled')}")
    print(f"  UI Theme: {config.get('ui.theme')}")
    
    # Set configuration
    print("\n2️⃣ Set configuration:")
    config.set('llm.temperature', 0.8)
    print(f"  New Temperature: {config.get('llm.temperature')}")
    
    # Validate configuration
    print("\n3️⃣ Validate configuration:")
    is_valid, errors = config.validate()
    if is_valid:
        print("  ✅ Configuration valid")
    else:
        print("  ❌ Configuration errors:")
        for error in errors:
            print(f"    • {error}")
    
    # Export template
    print("\n4️⃣ Export configuration template:")
    config.export_template()
    
    print("\n" + "=" * 70)
