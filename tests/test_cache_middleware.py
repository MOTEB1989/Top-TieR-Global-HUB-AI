"""
Tests for core cache middleware functionality
"""
import pytest
from unittest.mock import Mock, patch
from core.cache_middleware import CacheMiddleware


def test_cache_middleware_init():
    """Test cache middleware initialization"""
    with patch('core.cache_middleware.redis.Redis') as mock_redis:
        mock_redis.return_value.ping.return_value = True
        cache = CacheMiddleware()
        assert cache.redis_host == "redis"
        assert cache.cache_ttl_default == 600
        assert cache.cache_ttl_osint == 1800


def test_generate_cache_key():
    """Test cache key generation"""
    with patch('core.cache_middleware.redis.Redis'):
        cache = CacheMiddleware()
        cache.redis_client = None  # Disable Redis for unit test
        
        key = cache._generate_cache_key("openai", "gpt-3.5-turbo", "test query", "osint")
        assert key.startswith("cache:openai:gpt-3.5-turbo:osint:")
        assert len(key.split(":")[-1]) == 16  # Hash length


def test_get_ttl():
    """Test TTL calculation based on scope"""
    with patch('core.cache_middleware.redis.Redis'):
        cache = CacheMiddleware()
        cache.redis_client = None
        
        # OSINT scope should return longer TTL
        assert cache._get_ttl("osint") == 1800
        assert cache._get_ttl("general") == 600
        assert cache._get_ttl(None) == 600


def test_cache_operations_without_redis():
    """Test cache operations when Redis is not available"""
    with patch('core.cache_middleware.redis.Redis') as mock_redis:
        mock_redis.side_effect = Exception("Connection failed")
        cache = CacheMiddleware()
        
        # Should return None/False gracefully when Redis is not available
        assert cache.get("openai", "gpt-3.5-turbo", "test") is None
        assert cache.set("openai", "gpt-3.5-turbo", "test", {"response": "test"}) is False
        assert cache.delete("openai", "gpt-3.5-turbo", "test") is False


def test_cache_stats():
    """Test cache statistics"""
    with patch('core.cache_middleware.redis.Redis'):
        cache = CacheMiddleware()
        cache.redis_client = None  # Simulate no Redis
        
        stats = cache.get_stats()
        assert stats["enabled"] is False