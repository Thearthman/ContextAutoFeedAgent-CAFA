#!/usr/bin/env python3
"""
Cache Module
Provides various caching strategies to reduce redundant computations and API calls
"""

import time
import hashlib
import json
import threading
from typing import Any, Optional, Callable, Dict
from functools import wraps
from collections import OrderedDict


class CacheEntry:
    """Cache entry"""
    
    def __init__(self, value: Any, ttl: float):
        """
        Initialize cache entry
        
        Args:
            value: Cached value
            ttl: Time-to-live (seconds), 0 means never expires
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if expired"""
        if self.ttl == 0:
            return False
        return time.time() - self.created_at > self.ttl
    
    def access(self) -> Any:
        """Access cached value"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class LRUCache:
    """LRU (Least Recently Used) Cache"""
    
    def __init__(self, max_size: int = 100, ttl: float = 3600):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of cache entries
            ttl: Default time-to-live (seconds)
        """
        self.max_size = max_size
        self.default_ttl = ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            
            return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set cached value
        
        Args:
            key: Cache key
            value: Cached value
            ttl: Time-to-live (seconds), None means use default
        """
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]
            
            # Remove oldest entry if at capacity
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            # Add new entry
            entry = CacheEntry(value, ttl or self.default_ttl)
            self.cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry
        
        Args:
            key: Cache key
        
        Returns:
            Success status
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def size(self) -> int:
        """Get cache size"""
        with self.lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "total_requests": total
            }
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries
        
        Returns:
            Number of entries cleaned up
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)


class EmbeddingCache(LRUCache):
    """Specialized cache for embeddings"""
    
    def __init__(self, max_size: int = 1000, ttl: float = 86400):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of cache entries
            ttl: Default time-to-live (24 hours)
        """
        super().__init__(max_size, ttl)
    
    def get_embedding(self, text: str) -> Optional[Any]:
        """
        Get embedding for text
        
        Args:
            text: Text
        
        Returns:
            Embedding or None
        """
        key = self._text_to_key(text)
        return self.get(key)
    
    def set_embedding(self, text: str, embedding: Any) -> None:
        """
        Set embedding for text
        
        Args:
            text: Text
            embedding: Embedding
        """
        key = self._text_to_key(text)
        self.set(key, embedding)
    
    @staticmethod
    def _text_to_key(text: str) -> str:
        """Convert text to cache key"""
        # Use hash of text as key
        return hashlib.md5(text.encode('utf-8')).hexdigest()


class ResponseCache(LRUCache):
    """LLM response cache"""
    
    def __init__(self, max_size: int = 500, ttl: float = 3600):
        """
        Initialize response cache
        
        Args:
            max_size: Maximum number of cache entries
            ttl: Default time-to-live (1 hour)
        """
        super().__init__(max_size, ttl)
    
    def get_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        **kwargs
    ) -> Optional[str]:
        """
        Get cached response
        
        Args:
            prompt: Prompt
            model: Model
            temperature: Temperature
            **kwargs: Other parameters
        
        Returns:
            Cached response or None
        """
        key = self._create_key(prompt, model, temperature, **kwargs)
        return self.get(key)
    
    def set_response(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response: str,
        **kwargs
    ) -> None:
        """
        Set cached response
        
        Args:
            prompt: Prompt
            model: Model
            temperature: Temperature
            response: Response
            **kwargs: Other parameters
        """
        key = self._create_key(prompt, model, temperature, **kwargs)
        self.set(key, response)
    
    @staticmethod
    def _create_key(prompt: str, model: str, temperature: float, **kwargs) -> str:
        """Create cache key"""
        # Serialize all parameters as key
        key_data = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()


def cache_decorator(cache: LRUCache, key_func: Optional[Callable] = None):
    """
    Cache decorator
    
    Args:
        cache: Cache instance
        key_func: Key generation function (if None, use function name and arguments)
    
    Usage example:
        @cache_decorator(my_cache)
        def expensive_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key_data = {
                    "func": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                key_str = json.dumps(key_data, sort_keys=True, default=str)
                key = hashlib.md5(key_str.encode('utf-8')).hexdigest()
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache.set(key, result)
            
            return result
        
        return wrapper
    return decorator


# Global cache instances
_embedding_cache = EmbeddingCache()
_response_cache = ResponseCache()


def get_embedding_cache() -> EmbeddingCache:
    """Get global embedding cache"""
    return _embedding_cache


def get_response_cache() -> ResponseCache:
    """Get global response cache"""
    return _response_cache


# Usage example
if __name__ == "__main__":
    print("💾 Cache Module Test")
    print("=" * 70)
    
    # Test LRU cache
    print("\n1️⃣ LRU cache test:")
    cache = LRUCache(max_size=3, ttl=10)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    print(f"  Cache size: {cache.size()}")
    print(f"  Get key1: {cache.get('key1')}")
    
    # Add 4th entry, should remove oldest
    cache.set("key4", "value4")
    print(f"  After adding key4, is key2 still there: {cache.get('key2')}")
    
    # Test expiration
    print("\n2️⃣ Expiration test:")
    short_cache = LRUCache(max_size=10, ttl=0.1)
    short_cache.set("temp", "temporary value")
    print(f"  Get immediately after set: {short_cache.get('temp')}")
    time.sleep(0.2)
    print(f"  Get after 0.2s: {short_cache.get('temp')}")
    
    # Test embedding cache
    print("\n3️⃣ Embedding cache:")
    emb_cache = get_embedding_cache()
    
    text = "This is a test text"
    fake_embedding = [0.1, 0.2, 0.3]
    
    emb_cache.set_embedding(text, fake_embedding)
    cached_emb = emb_cache.get_embedding(text)
    print(f"  Cached embedding: {cached_emb}")
    
    # Test response cache
    print("\n4️⃣ Response cache:")
    resp_cache = get_response_cache()
    
    resp_cache.set_response(
        "Hello",
        "gpt-3.5-turbo",
        0.7,
        "Hi there!"
    )
    
    cached_resp = resp_cache.get_response("Hello", "gpt-3.5-turbo", 0.7)
    print(f"  Cached response: {cached_resp}")
    
    # Test cache decorator
    print("\n5️⃣ Cache decorator:")
    test_cache = LRUCache(max_size=10, ttl=60)
    
    @cache_decorator(test_cache)
    def slow_function(x, y):
        time.sleep(0.1)
        return x + y
    
    start = time.time()
    result1 = slow_function(1, 2)
    time1 = time.time() - start
    
    start = time.time()
    result2 = slow_function(1, 2)  # Should get from cache
    time2 = time.time() - start
    
    print(f"  First call: {time1:.3f}s")
    print(f"  Second call (cached): {time2:.3f}s")
    print(f"  Speedup: {time1/time2:.1f}x")
    
    # Test statistics
    print("\n6️⃣ Cache statistics:")
    stats = cache.get_stats()
    print(f"  Hit rate: {stats['hit_rate']:.2%}")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    
    print("\n" + "=" * 70)
