"""
Tests for the TTL-based caching layer.

This module tests:
- CacheManager: Thread-safe cache with TTL expiration
- @cached decorator: Function result caching
- _make_cache_key: Cache key generation
"""

import time
import threading
import pytest
from unittest.mock import patch, MagicMock

from blender_mcp.cache import CacheManager, cached, _make_cache_key


class TestCacheManagerSingleton:
    """Tests for CacheManager singleton pattern."""

    def test_singleton_returns_same_instance(self):
        """Verify CacheManager returns the same instance."""
        # Clear the singleton for this test
        CacheManager._instance = None

        instance1 = CacheManager()
        instance2 = CacheManager()

        assert instance1 is instance2

    def test_singleton_thread_safety(self):
        """Verify singleton is thread-safe."""
        CacheManager._instance = None
        instances = []

        def create_instance():
            instances.append(CacheManager())

        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same
        assert all(inst is instances[0] for inst in instances)


class TestCacheManagerGetSet:
    """Tests for CacheManager get and set operations."""

    def setup_method(self):
        """Clear cache before each test."""
        # Create fresh instance
        CacheManager._instance = None
        self.cache = CacheManager()

    def test_set_and_get_value(self):
        """Test basic set and get operations."""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        assert result == "test_value"

    def test_set_with_custom_ttl(self):
        """Test set with custom TTL."""
        self.cache.set("key", "value", ttl=60)
        result = self.cache.get("key")
        assert result == "value"

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        result = self.cache.get("nonexistent")
        assert result is None

    def test_get_expired_key(self):
        """Test getting an expired key returns None and removes it."""
        # Set with very short TTL
        self.cache.set("expiring_key", "value", ttl=0.01)

        # Wait for expiration
        time.sleep(0.02)

        result = self.cache.get("expiring_key")
        assert result is None

        # Verify it was removed from cache
        info = self.cache.cache_info()
        assert info["size"] == 0

    def test_get_tracks_hits_and_misses(self):
        """Test that get correctly tracks hits and misses."""
        self.cache.set("key1", "value1")

        # Hit
        self.cache.get("key1")
        # Miss
        self.cache.get("nonexistent")

        info = self.cache.cache_info()
        assert info["hits"] == 1
        assert info["misses"] == 1

    def test_set_overwrites_existing_key(self):
        """Test that set overwrites an existing key."""
        self.cache.set("key", "value1")
        self.cache.set("key", "value2")

        result = self.cache.get("key")
        assert result == "value2"

    def test_set_stores_complex_value(self):
        """Test that set can store complex values like dicts."""
        complex_value = {"name": "test", "items": [1, 2, 3], "nested": {"a": 1}}
        self.cache.set("complex", complex_value)

        result = self.cache.get("complex")
        assert result == complex_value


class TestCacheManagerDelete:
    """Tests for CacheManager delete operation."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager._instance = None
        self.cache = CacheManager()

    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        self.cache.set("key", "value")
        result = self.cache.delete("key")

        assert result is True
        assert self.cache.get("key") is None

    def test_delete_nonexistent_key(self):
        """Test deleting a key that doesn't exist."""
        result = self.cache.delete("nonexistent")
        assert result is False


class TestCacheManagerClear:
    """Tests for CacheManager clear operation."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager._instance = None
        self.cache = CacheManager()

    def test_clear_returns_count(self):
        """Test clear returns the number of entries cleared."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")

        count = self.cache.clear()
        assert count == 3

    def test_clear_empties_cache(self):
        """Test clear removes all entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        self.cache.clear()

        info = self.cache.cache_info()
        assert info["size"] == 0

    def test_clear_empty_cache(self):
        """Test clear on empty cache returns 0."""
        count = self.cache.clear()
        assert count == 0


class TestCacheManagerCacheInfo:
    """Tests for CacheManager cache_info operation."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager._instance = None
        self.cache = CacheManager()

    def test_cache_info_returns_correct_structure(self):
        """Test cache_info returns correct dictionary structure."""
        info = self.cache.cache_info()

        assert "hits" in info
        assert "misses" in info
        assert "size" in info
        assert "hit_rate" in info

    def test_cache_info_hit_rate_calculation(self):
        """Test hit rate is calculated correctly."""
        self.cache.set("key", "value")

        # 3 hits
        self.cache.get("key")
        self.cache.get("key")
        self.cache.get("key")
        # 1 miss
        self.cache.get("nonexistent")

        info = self.cache.cache_info()
        # 3 hits / 4 total = 75%
        assert info["hit_rate"] == 75.0

    def test_cache_info_hit_rate_zero_total(self):
        """Test hit rate is 0 when no operations performed."""
        info = self.cache.cache_info()
        assert info["hit_rate"] == 0.0

    def test_cache_info_size(self):
        """Test size reflects current cache entries."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")

        info = self.cache.cache_info()
        assert info["size"] == 2


class TestCacheManagerCleanupExpired:
    """Tests for CacheManager cleanup_expired operation."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager._instance = None
        self.cache = CacheManager()

    def test_cleanup_expired_removes_expired_entries(self):
        """Test cleanup_expired removes only expired entries."""
        # Set one expiring and one non-expiring
        self.cache.set("expiring", "value1", ttl=0.01)
        self.cache.set("fresh", "value2", ttl=300)

        # Wait for expiration
        time.sleep(0.02)

        count = self.cache.cleanup_expired()

        assert count == 1
        assert self.cache.get("fresh") == "value2"

    def test_cleanup_expired_no_expired_entries(self):
        """Test cleanup_expired returns 0 when no entries expired."""
        self.cache.set("key1", "value1", ttl=300)
        self.cache.set("key2", "value2", ttl=300)

        count = self.cache.cleanup_expired()
        assert count == 0

    def test_cleanup_expired_empty_cache(self):
        """Test cleanup_expired on empty cache returns 0."""
        count = self.cache.cleanup_expired()
        assert count == 0


class TestCachedDecorator:
    """Tests for the @cached decorator."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager._instance = None

    def test_cached_caches_function_result(self):
        """Test @cached caches the result of a function."""
        call_count = 0

        @cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # No additional call

    def test_cached_with_different_arguments(self):
        """Test @cached handles different arguments separately."""
        call_count = 0

        @cached(ttl=60)
        def add(a, b):
            nonlocal call_count
            call_count += 1
            return a + b

        result1 = add(1, 2)
        result2 = add(3, 4)
        result3 = add(1, 2)  # Should use cache

        assert result1 == 3
        assert result2 == 7
        assert result3 == 3
        assert call_count == 2  # Only 2 actual calls

    def test_cached_with_keyword_arguments(self):
        """Test @cached handles keyword arguments."""
        call_count = 0

        @cached(ttl=60)
        def greet(name, greeting="Hello"):
            nonlocal call_count
            call_count += 1
            return f"{greeting}, {name}!"

        # Same call with positional args twice - should cache
        result1 = greet("World")
        result2 = greet("World")

        # Different call with keyword arg
        result3 = greet("World", greeting="Hi")

        assert result1 == "Hello, World!"
        assert result2 == "Hello, World!"
        assert result3 == "Hi, World!"
        assert call_count == 2  # First and third call (second uses cache)

    def test_cached_respects_ttl(self):
        """Test @cached respects TTL expiration."""
        call_count = 0

        @cached(ttl=0.01)
        def quick_expire(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = quick_expire(5)
        assert result1 == 10
        assert call_count == 1

        # Wait for expiration
        time.sleep(0.02)

        result2 = quick_expire(5)
        assert result2 == 10
        assert call_count == 2  # Had to recalculate


class TestMakeCacheKey:
    """Tests for _make_cache_key function."""

    def test_make_cache_key_with_no_args(self):
        """Test key generation with no arguments."""
        key = _make_cache_key("my_func", (), {})
        assert key == "my_func"

    def test_make_cache_key_with_positional_args(self):
        """Test key generation with positional arguments."""
        key = _make_cache_key("func", (1, "test", True), {})
        assert key == "func:1:test:True"

    def test_make_cache_key_with_kwargs(self):
        """Test key generation with keyword arguments."""
        key = _make_cache_key("func", (), {"a": 1, "b": 2})
        # kwargs are sorted
        assert key == "func:a=1:b=2"

    def test_make_cache_key_with_mixed_args(self):
        """Test key generation with both positional and keyword args."""
        key = _make_cache_key("func", (1, 2), {"c": 3, "d": 4})
        assert key == "func:1:2:c=3:d=4"

    def test_make_cache_key_kwargs_sorted(self):
        """Test that kwargs are sorted for consistent keys."""
        key1 = _make_cache_key("func", (), {"a": 1, "b": 2})
        key2 = _make_cache_key("func", (), {"b": 2, "a": 1})
        assert key1 == key2
