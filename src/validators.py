#!/usr/bin/env python3
"""
Data Validation Module
Provides validation functionality for input/output data
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Callable
from src.exceptions import ValidationError, MissingFieldError, InvalidFieldError


class Validator:
    """Generic validator"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """
        Validate required field
        
        Args:
            value: Field value
            field_name: Field name
        
        Raises:
            MissingFieldError: Field is missing
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise MissingFieldError(field_name)
    
    @staticmethod
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        """
        Validate type
        
        Args:
            value: Field value
            expected_type: Expected type
            field_name: Field name
        
        Raises:
            InvalidFieldError: Type mismatch
        """
        if not isinstance(value, expected_type):
            raise InvalidFieldError(
                field_name,
                f"Expected type {expected_type.__name__}, got {type(value).__name__}"
            )
    
    @staticmethod
    def validate_range(
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "value"
    ) -> None:
        """
        Validate numeric range
        
        Args:
            value: Numeric value
            min_value: Minimum value
            max_value: Maximum value
            field_name: Field name
        
        Raises:
            InvalidFieldError: Out of range
        """
        if min_value is not None and value < min_value:
            raise InvalidFieldError(
                field_name,
                f"Value {value} is less than minimum {min_value}"
            )
        
        if max_value is not None and value > max_value:
            raise InvalidFieldError(
                field_name,
                f"Value {value} is greater than maximum {max_value}"
            )
    
    @staticmethod
    def validate_length(
        text: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        field_name: str = "text"
    ) -> None:
        """
        Validate string length
        
        Args:
            text: Text
            min_length: Minimum length
            max_length: Maximum length
            field_name: Field name
        
        Raises:
            InvalidFieldError: Length mismatch
        """
        length = len(text)
        
        if min_length is not None and length < min_length:
            raise InvalidFieldError(
                field_name,
                f"Length {length} is less than minimum {min_length}"
            )
        
        if max_length is not None and length > max_length:
            raise InvalidFieldError(
                field_name,
                f"Length {length} is greater than maximum {max_length}"
            )
    
    @staticmethod
    def validate_enum(
        value: Any,
        allowed_values: List[Any],
        field_name: str = "value"
    ) -> None:
        """
        Validate enum value
        
        Args:
            value: Value
            allowed_values: List of allowed values
            field_name: Field name
        
        Raises:
            InvalidFieldError: Not in allowed values
        """
        if value not in allowed_values:
            raise InvalidFieldError(
                field_name,
                f"Value '{value}' not in allowed list: {allowed_values}"
            )
    
    @staticmethod
    def validate_pattern(
        text: str,
        pattern: str,
        field_name: str = "text",
        pattern_description: str = "specified format"
    ) -> None:
        """
        Validate regex pattern
        
        Args:
            text: Text
            pattern: Regex pattern
            field_name: Field name
            pattern_description: Pattern description
        
        Raises:
            InvalidFieldError: Pattern mismatch
        """
        if not re.match(pattern, text):
            raise InvalidFieldError(
                field_name,
                f"Does not match {pattern_description}"
            )


class LLMRequestValidator:
    """LLM request validator"""
    
    @staticmethod
    def validate_chat_request(data: Dict) -> None:
        """
        Validate chat request
        
        Args:
            data: Request data
        
        Raises:
            ValidationError: Validation failed
        """
        # Validate prompt or message field
        prompt = data.get('prompt') or data.get('message')
        Validator.validate_required(prompt, 'prompt/message')
        Validator.validate_type(prompt, str, 'prompt/message')
        Validator.validate_length(prompt, min_length=1, max_length=100000, field_name='prompt')
        
        # Validate optional parameters
        if 'max_new_tokens' in data:
            max_tokens = data['max_new_tokens']
            Validator.validate_type(max_tokens, int, 'max_new_tokens')
            Validator.validate_range(max_tokens, 1, 10000, 'max_new_tokens')
        
        if 'temperature' in data:
            temperature = data['temperature']
            Validator.validate_type(temperature, (int, float), 'temperature')
            Validator.validate_range(temperature, 0.0, 2.0, 'temperature')
        
        if 'top_p' in data:
            top_p = data['top_p']
            Validator.validate_type(top_p, (int, float), 'top_p')
            Validator.validate_range(top_p, 0.0, 1.0, 'top_p')
        
        if 'top_k' in data:
            top_k = data['top_k']
            Validator.validate_type(top_k, int, 'top_k')
            Validator.validate_range(top_k, 1, 1000, 'top_k')


class MemoryRequestValidator:
    """Memory request validator"""
    
    @staticmethod
    def validate_store_request(data: Dict) -> None:
        """
        Validate memory store request
        
        Args:
            data: Request data
        
        Raises:
            ValidationError: Validation failed
        """
        # Validate text field
        text = data.get('text')
        Validator.validate_required(text, 'text')
        Validator.validate_type(text, str, 'text')
        Validator.validate_length(text, min_length=1, max_length=50000, field_name='text')
        
        # Validate importance field (optional)
        if 'importance' in data:
            importance = data['importance']
            Validator.validate_type(importance, (int, float), 'importance')
            Validator.validate_range(importance, 0.0, 1.0, 'importance')
        
        # Validate tags field (optional)
        if 'tags' in data:
            tags = data['tags']
            Validator.validate_type(tags, list, 'tags')
            for tag in tags:
                Validator.validate_type(tag, str, 'tag')
    
    @staticmethod
    def validate_recall_request(data: Dict) -> None:
        """
        Validate memory recall request
        
        Args:
            data: Request data
        
        Raises:
            ValidationError: Validation failed
        """
        # Validate query field
        query = data.get('query')
        Validator.validate_required(query, 'query')
        Validator.validate_type(query, str, 'query')
        Validator.validate_length(query, min_length=1, max_length=10000, field_name='query')
        
        # Validate top_k field (optional)
        if 'top_k' in data:
            top_k = data['top_k']
            Validator.validate_type(top_k, int, 'top_k')
            Validator.validate_range(top_k, 1, 100, 'top_k')
        
        # Validate min_similarity field (optional)
        if 'min_similarity' in data:
            min_sim = data['min_similarity']
            Validator.validate_type(min_sim, (int, float), 'min_similarity')
            Validator.validate_range(min_sim, 0.0, 1.0, 'min_similarity')


class APIKeyValidator:
    """API key validator"""
    
    # API Key format patterns
    PATTERNS = {
        "openai": r"^sk-[a-zA-Z0-9]{32,}$",
        "anthropic": r"^sk-ant-[a-zA-Z0-9\-]{20,}$",
        "google": r"^AIza[a-zA-Z0-9\-_]{35}$",
        "qwen": r".{20,}",  # Qwen key format is more flexible
    }
    
    @staticmethod
    def validate(api_key: str, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Validate API key format
        
        Args:
            api_key: API key
            provider: Provider name
        
        Returns:
            (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, "API Key cannot be empty"
        
        pattern = APIKeyValidator.PATTERNS.get(provider.lower())
        
        if not pattern:
            # Unknown provider, use basic validation
            if len(api_key) < 10:
                return False, f"API Key too short (provider: {provider})"
            return True, None
        
        if not re.match(pattern, api_key):
            return False, f"API Key format does not match {provider} requirements"
        
        return True, None


class ConfigValidator:
    """Configuration validator"""
    
    @staticmethod
    def validate_server_config(config: Dict) -> List[str]:
        """
        Validate server configuration
        
        Args:
            config: Configuration dictionary
        
        Returns:
            List of error messages (empty list means validation passed)
        """
        errors = []
        
        # Validate LLM configuration
        if 'llm' in config:
            llm_config = config['llm']
            
            # Validate URLs
            for url_key in ['local_model_url', 'online_model_url']:
                if url_key in llm_config:
                    url = llm_config[url_key]
                    if not ConfigValidator._is_valid_url(url):
                        errors.append(f"Invalid URL: {url_key} = {url}")
            
            # Validate parameter ranges
            if 'temperature' in llm_config:
                temp = llm_config['temperature']
                if not (0 <= temp <= 2):
                    errors.append(f"temperature should be between 0-2, current value: {temp}")
            
            if 'top_p' in llm_config:
                top_p = llm_config['top_p']
                if not (0 <= top_p <= 1):
                    errors.append(f"top_p should be between 0-1, current value: {top_p}")
        
        # Validate memory configuration
        if 'memory' in config:
            memory_config = config['memory']
            
            if 'api_url' in memory_config:
                url = memory_config['api_url']
                if not ConfigValidator._is_valid_url(url):
                    errors.append(f"Invalid memory service URL: {url}")
        
        return errors
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?://[\w\-\.]+(:\d+)?(/.*)?$'
        return bool(re.match(pattern, url))


# Usage example
if __name__ == "__main__":
    print("✅ Data Validation Module Test")
    print("=" * 70)
    
    # Test LLM request validation
    print("\n1️⃣ LLM request validation:")
    try:
        LLMRequestValidator.validate_chat_request({
            "prompt": "Hello",
            "temperature": 0.7,
            "max_new_tokens": 1000
        })
        print("  ✅ Validation passed")
    except ValidationError as e:
        print(f"  ❌ {e}")
    
    # Test invalid parameters
    print("\n2️⃣ Invalid parameter validation:")
    try:
        LLMRequestValidator.validate_chat_request({
            "prompt": "Hello",
            "temperature": 3.0  # Out of range
        })
        print("  ✅ Validation passed")
    except ValidationError as e:
        print(f"  ❌ {e}")
    
    # Test memory request validation
    print("\n3️⃣ Memory request validation:")
    try:
        MemoryRequestValidator.validate_store_request({
            "text": "This is a memory",
            "importance": 0.8
        })
        print("  ✅ Validation passed")
    except ValidationError as e:
        print(f"  ❌ {e}")
    
    # Test API Key validation
    print("\n4️⃣ API Key validation:")
    test_keys = [
        ("sk-1234567890123456789012345678901234567890", "openai"),
        ("invalid-key", "openai"),
        ("AIzaSyC1234567890123456789012345678901234", "google"),
    ]
    
    for key, provider in test_keys:
        is_valid, error = APIKeyValidator.validate(key, provider)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {provider}: {key[:20]}... - {error or 'valid'}")
    
    # Test configuration validation
    print("\n5️⃣ Configuration validation:")
    test_config = {
        "llm": {
            "local_model_url": "http://localhost:5000",
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    
    errors = ConfigValidator.validate_server_config(test_config)
    if not errors:
        print("  ✅ Configuration validation passed")
    else:
        print("  ❌ Configuration errors:")
        for error in errors:
            print(f"    • {error}")
    
    print("\n" + "=" * 70)
