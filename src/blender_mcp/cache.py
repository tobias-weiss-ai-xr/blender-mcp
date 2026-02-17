"""
TTL-based caching layer for Blender MCP.
Provides thread-safe caching with automatic expiration.
"""

import time
import threading
from functools import wraps
from typing import Any, Optional, Callable, Dict


class CacheManager:
    """Thread-safe cache with TTL expiration.

    Uses a singleton pattern to ensure a single global cache instance.

    Attributes:
        _cache: Dictionary storing cached values with their expiration times
        _stats: Dictionary tracking cache hits and misses
        _lock: Threading lock for thread-safe operations
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache: Dict[str, tuple] = {}
                    cls._instance._stats = {"hits": 0, "misses": 0}
                    cls._instance._cache_lock = threading.Lock()
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """Get value if exists and not expired.

        Args:
            key: The cache key to look up

        Returns:
            The cached value if found and not expired, None otherwise
        """
        with self._cache_lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._stats["hits"] += 1
                    return value
                else:
                    # Expired, remove it
                    del self._cache[key]
            self._stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value with TTL in seconds.

        Args:
            key: The cache key
            value: The value to cache (must be serializable)
            ttl: Time-to-live in seconds (default: 300)
        """
        with self._cache_lock:
            expiry = time.time() + ttl
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """Delete a cached value.

        Args:
            key: The cache key to delete

        Returns:
            True if the key existed and was deleted, False otherwise
        """
        with self._cache_lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all cached values.

        Returns:
            The number of entries cleared
        """
        with self._cache_lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def cache_info(self) -> dict:
        """Return cache statistics.

        Returns:
            Dictionary with keys: hits, misses, size, hit_rate
        """
        with self._cache_lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0.0
            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "size": len(self._cache),
                "hit_rate": round(hit_rate, 2),
            }

    def cleanup_expired(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            The number of expired entries removed
        """
        with self._cache_lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, expiry) in self._cache.items()
                if current_time >= expiry
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)


def cached(ttl: int = 300):
    """Decorator to cache function results.

    The cache key is generated from the function name and arguments.
    Only works with JSON-serializable arguments.

    Args:
        ttl: Time-to-live in seconds (default: 300)

    Returns:
        Decorator function

    Example:
        @cached(ttl=60)
        def expensive_operation(arg1, arg2):
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = _make_cache_key(func.__name__, args, kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


def _make_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function name and arguments.

    Args:
        func_name: Name of the function
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        A string cache key
    """
    # Convert args and kwargs to a stable string representation
    key_parts = [func_name]

    for arg in args:
        key_parts.append(str(arg))

    for k in sorted(kwargs.keys()):
        key_parts.append(f"{k}={kwargs[k]}")

    return ":".join(key_parts)


# Global cache instance
cache = CacheManager()
