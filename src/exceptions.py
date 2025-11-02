#!/usr/bin/env python3
"""
Unified Exception Definition Module
Provides structured exception handling for the project
"""

from typing import Optional, Dict, Any


class CAFAException(Exception):
    """CAFA base exception class"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize exception
        
        Args:
            message: Error message
            error_code: Error code
            details: Additional details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }
    
    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


# ============================================================================
# Configuration-related exceptions
# ============================================================================

class ConfigError(CAFAException):
    """Configuration error"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message,
            error_code="CONFIG_ERROR",
            details={"config_key": config_key} if config_key else {}
        )


class MissingConfigError(ConfigError):
    """Missing configuration"""
    
    def __init__(self, config_key: str):
        super().__init__(
            f"Missing required configuration: {config_key}",
            config_key=config_key
        )
        self.error_code = "MISSING_CONFIG"


class InvalidConfigError(ConfigError):
    """Invalid configuration"""
    
    def __init__(self, config_key: str, expected: str, actual: Any):
        super().__init__(
            f"Invalid configuration '{config_key}': expected {expected}, got {actual}",
            config_key=config_key
        )
        self.error_code = "INVALID_CONFIG"
        self.details["expected"] = expected
        self.details["actual"] = actual


# ============================================================================
# API-related exceptions
# ============================================================================

class APIError(CAFAException):
    """API error base class"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(
            message,
            error_code="API_ERROR",
            details={"status_code": status_code} if status_code else {}
        )
        self.status_code = status_code


class APIConnectionError(APIError):
    """API connection error"""
    
    def __init__(self, service_name: str, url: str):
        super().__init__(
            f"Cannot connect to {service_name} service: {url}",
            status_code=503
        )
        self.error_code = "API_CONNECTION_ERROR"
        self.details["service_name"] = service_name
        self.details["url"] = url


class APITimeoutError(APIError):
    """API timeout error"""
    
    def __init__(self, service_name: str, timeout: float):
        super().__init__(
            f"{service_name} request timeout (timeout: {timeout}s)",
            status_code=504
        )
        self.error_code = "API_TIMEOUT"
        self.details["timeout"] = timeout


class APIAuthenticationError(APIError):
    """API authentication error"""
    
    def __init__(self, provider: str):
        super().__init__(
            f"{provider} API authentication failed, please check API Key",
            status_code=401
        )
        self.error_code = "API_AUTH_ERROR"
        self.details["provider"] = provider


class APIRateLimitError(APIError):
    """API rate limit error"""
    
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        message = f"{provider} API rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        
        super().__init__(message, status_code=429)
        self.error_code = "API_RATE_LIMIT"
        self.details["provider"] = provider
        if retry_after:
            self.details["retry_after"] = retry_after


# ============================================================================
# LLM-related exceptions
# ============================================================================

class LLMError(CAFAException):
    """LLM error base class"""
    
    def __init__(self, message: str, provider: Optional[str] = None):
        super().__init__(
            message,
            error_code="LLM_ERROR",
            details={"provider": provider} if provider else {}
        )


class LLMGenerationError(LLMError):
    """LLM generation error"""
    
    def __init__(self, provider: str, reason: str):
        super().__init__(
            f"{provider} generation failed: {reason}",
            provider=provider
        )
        self.error_code = "LLM_GENERATION_ERROR"
        self.details["reason"] = reason


class ModelNotLoadedError(LLMError):
    """Model not loaded error"""
    
    def __init__(self, model_name: str):
        super().__init__(
            f"Model '{model_name}' not loaded",
            provider="local"
        )
        self.error_code = "MODEL_NOT_LOADED"
        self.details["model_name"] = model_name


class InvalidPromptError(LLMError):
    """Invalid prompt error"""
    
    def __init__(self, reason: str):
        super().__init__(
            f"Invalid prompt: {reason}",
            provider=None
        )
        self.error_code = "INVALID_PROMPT"


# ============================================================================
# Memory system-related exceptions
# ============================================================================

class MemoryError(CAFAException):
    """Memory system error base class"""
    
    def __init__(self, message: str):
        super().__init__(
            message,
            error_code="MEMORY_ERROR"
        )


class MemoryStorageError(MemoryError):
    """Memory storage error"""
    
    def __init__(self, reason: str):
        super().__init__(f"Memory storage failed: {reason}")
        self.error_code = "MEMORY_STORAGE_ERROR"


class MemoryRetrievalError(MemoryError):
    """Memory retrieval error"""
    
    def __init__(self, reason: str):
        super().__init__(f"Memory retrieval failed: {reason}")
        self.error_code = "MEMORY_RETRIEVAL_ERROR"


class EmbeddingError(MemoryError):
    """Embedding generation error"""
    
    def __init__(self, text_snippet: str):
        super().__init__(
            f"Embedding generation failed: '{text_snippet[:50]}...'"
        )
        self.error_code = "EMBEDDING_ERROR"
        self.details["text_snippet"] = text_snippet[:100]


# ============================================================================
# Validation-related exceptions
# ============================================================================

class ValidationError(CAFAException):
    """Validation error base class"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {}
        )


class MissingFieldError(ValidationError):
    """Missing field error"""
    
    def __init__(self, field: str):
        super().__init__(
            f"Missing required field: {field}",
            field=field
        )
        self.error_code = "MISSING_FIELD"


class InvalidFieldError(ValidationError):
    """Invalid field error"""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Field '{field}' invalid: {reason}",
            field=field
        )
        self.error_code = "INVALID_FIELD"
        self.details["reason"] = reason


# ============================================================================
# File handling-related exceptions
# ============================================================================

class FileError(CAFAException):
    """File error base class"""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(
            message,
            error_code="FILE_ERROR",
            details={"file_path": file_path} if file_path else {}
        )


class FileNotFoundError(FileError):
    """File not found error"""
    
    def __init__(self, file_path: str):
        super().__init__(
            f"File not found: {file_path}",
            file_path=file_path
        )
        self.error_code = "FILE_NOT_FOUND"


class FileReadError(FileError):
    """File read error"""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"File read failed ({file_path}): {reason}",
            file_path=file_path
        )
        self.error_code = "FILE_READ_ERROR"
        self.details["reason"] = reason


class FileWriteError(FileError):
    """File write error"""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"File write failed ({file_path}): {reason}",
            file_path=file_path
        )
        self.error_code = "FILE_WRITE_ERROR"
        self.details["reason"] = reason


# ============================================================================
# Exception handling helper functions
# ============================================================================

def handle_exception(exc: Exception, logger=None) -> Dict[str, Any]:
    """
    Unified exception handling, returns error info in standard format
    
    Args:
        exc: Exception object
        logger: Logger (optional)
    
    Returns:
        Error information dictionary
    """
    if isinstance(exc, CAFAException):
        error_info = exc.to_dict()
    else:
        error_info = {
            "error": exc.__class__.__name__,
            "message": str(exc),
            "error_code": "UNHANDLED_EXCEPTION"
        }
    
    if logger:
        logger.error(f"Exception: {error_info}")
    
    return error_info


# Usage example
if __name__ == "__main__":
    print("⚠️  Exception System Test")
    print("=" * 70)
    
    # Test configuration exceptions
    print("\n1️⃣ Configuration exceptions:")
    try:
        raise MissingConfigError("api_key")
    except CAFAException as e:
        print(f"  {e}")
        print(f"  Dict format: {e.to_dict()}")
    
    # Test API exceptions
    print("\n2️⃣ API exceptions:")
    try:
        raise APIConnectionError("OpenAI", "https://api.openai.com")
    except CAFAException as e:
        print(f"  {e}")
        print(f"  Status code: {e.status_code}")
    
    # Test LLM exceptions
    print("\n3️⃣ LLM exceptions:")
    try:
        raise LLMGenerationError("gemma", "Model not responding")
    except CAFAException as e:
        print(f"  {e}")
    
    # Test memory exceptions
    print("\n4️⃣ Memory exceptions:")
    try:
        raise EmbeddingError("This is a test text")
    except CAFAException as e:
        print(f"  {e}")
    
    # Test validation exceptions
    print("\n5️⃣ Validation exceptions:")
    try:
        raise InvalidFieldError("temperature", "Value must be between 0-2")
    except CAFAException as e:
        print(f"  {e}")
    
    print("\n" + "=" * 70)
