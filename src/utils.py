#!/usr/bin/env python3
"""
Common Utility Functions Library
Provides frequently used helper functions across the project
"""

import time
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
import threading


# ============================================================================
# Time-related utilities
# ============================================================================

def timestamp_now() -> float:
    """Get current timestamp (seconds)"""
    return time.time()


def timestamp_to_datetime(timestamp: float) -> datetime:
    """Convert timestamp to datetime object"""
    return datetime.fromtimestamp(timestamp)


def datetime_to_str(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime to string"""
    return dt.strftime(fmt)


def str_to_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Convert string to datetime"""
    return datetime.strptime(dt_str, fmt)


def time_ago(timestamp: float) -> str:
    """
    Convert timestamp to "time ago" description
    
    Examples:
    - just now
    - 5 minutes ago
    - 2 hours ago
    - 3 days ago
    """
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif diff < 2592000:
        weeks = int(diff / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        months = int(diff / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"


# ============================================================================
# String processing utilities
# ============================================================================

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string
    
    Args:
        text: Original text
        max_length: Maximum length
        suffix: Suffix to append
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """Clean extra whitespace characters"""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing spaces
    return text.strip()


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from Markdown text
    
    Returns:
        [{"language": "python", "code": "print('hello')"}]
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    return [
        {"language": lang or "text", "code": code.strip()}
        for lang, code in matches
    ]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing illegal characters
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename
    """
    # Remove illegal characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:max_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name
    
    return filename


# ============================================================================
# Data processing utilities
# ============================================================================

def deep_get(data: Dict, key_path: str, default: Any = None) -> Any:
    """
    Safely get value from nested dictionary
    
    Example: deep_get({"a": {"b": {"c": 1}}}, "a.b.c") -> 1
    
    Args:
        data: Dictionary data
        key_path: Dot-separated path
        default: Default value
    
    Returns:
        Value or default
    """
    keys = key_path.split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def merge_dicts(base: Dict, *overrides: Dict) -> Dict:
    """
    Deep merge multiple dictionaries
    
    Args:
        base: Base dictionary
        *overrides: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for override in overrides:
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    
    return result


def calculate_hash(data: str, algorithm: str = "md5") -> str:
    """
    Calculate hash value of string
    
    Args:
        data: Data to hash
        algorithm: Algorithm (md5, sha1, sha256)
    
    Returns:
        Hexadecimal hash value
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


# ============================================================================
# File processing utilities
# ============================================================================

def read_json_file(file_path: str, default: Any = None) -> Any:
    """
    Safely read JSON file
    
    Args:
        file_path: File path
        default: Default value on read failure
    
    Returns:
        JSON data or default value
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def write_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Write JSON file
    
    Args:
        file_path: File path
        data: Data to write
        indent: Indentation spaces
    
    Returns:
        Success status
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        return False


# ============================================================================
# Decorator utilities
# ============================================================================

def timing_decorator(func: Callable) -> Callable:
    """
    Timing decorator - record function execution time
    
    Usage example:
        @timing_decorator
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"⏱️  {func.__name__} execution time: {duration:.2f}ms")
        return result
    return wrapper


def retry_decorator(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator - automatically retry on failure
    
    Args:
        max_retries: Maximum retry attempts
        delay: Initial delay (seconds)
        backoff: Delay multiplier
    
    Usage example:
        @retry_decorator(max_retries=3, delay=1.0)
        def unstable_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries}), retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


def thread_safe(func: Callable) -> Callable:
    """
    Thread-safe decorator
    
    Usage example:
        @thread_safe
        def critical_section():
            pass
    """
    lock = threading.Lock()
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return wrapper


# ============================================================================
# Validation utilities
# ============================================================================

def validate_api_key(api_key: str, provider: str = "openai") -> bool:
    """
    Validate API key format
    
    Args:
        api_key: API key
        provider: Provider
    
    Returns:
        Validity status
    """
    if not api_key:
        return False
    
    patterns = {
        "openai": r"^sk-[a-zA-Z0-9]{32,}$",
        "anthropic": r"^sk-ant-[a-zA-Z0-9\-]{20,}$",
        "google": r"^AIza[a-zA-Z0-9\-_]{35}$",
    }
    
    pattern = patterns.get(provider)
    if not pattern:
        return len(api_key) > 10  # Simple validation
    
    return bool(re.match(pattern, api_key))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


# ============================================================================
# Cache utilities
# ============================================================================

class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self, ttl: int = 3600):
        """
        Args:
            ttl: Cache expiration time (seconds)
        """
        self.cache = {}
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value"""
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear cache"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        with self.lock:
            return len(self.cache)


# Usage example
if __name__ == "__main__":
    print("🛠️ Utility Functions Test")
    print("=" * 70)
    
    # Time utilities
    print("\n1️⃣ Time utilities:")
    now = timestamp_now()
    print(f"  Current timestamp: {now}")
    print(f"  Time ago: {time_ago(now - 3600)}")
    
    # String utilities
    print("\n2️⃣ String utilities:")
    long_text = "This is a very long string" * 10
    print(f"  Truncated: {truncate_string(long_text, 30)}")
    
    # Data processing
    print("\n3️⃣ Data processing:")
    nested = {"a": {"b": {"c": 123}}}
    print(f"  Deep get: {deep_get(nested, 'a.b.c')}")
    
    # Hash calculation
    print("\n4️⃣ Hash calculation:")
    print(f"  MD5: {calculate_hash('hello world', 'md5')}")
    
    # Validation utilities
    print("\n5️⃣ Validation utilities:")
    print(f"  URL validation: {validate_url('https://example.com')}")
    
    # Cache test
    print("\n6️⃣ Cache test:")
    cache = SimpleCache(ttl=60)
    cache.set("key1", "value1")
    print(f"  Cache get: {cache.get('key1')}")
    print(f"  Cache size: {cache.size()}")
    
    print("\n" + "=" * 70)
