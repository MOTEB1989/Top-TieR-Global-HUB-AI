"""
Redis Cache Middleware for Top-TieR Global HUB AI
Implements cache-aside pattern with TTL based on query type
"""
import hashlib
import json
import logging
import os
from typing import Any, Dict, Optional

import redis
from fastapi import Request

logger = logging.getLogger(__name__)


class CacheMiddleware:
    """Redis-based cache middleware with intelligent TTL management"""
    
    def __init__(self):
        """Initialize Redis connection and configuration"""
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.cache_ttl_default = int(os.getenv("CACHE_TTL_DEFAULT", "600"))  # 10 minutes
        self.cache_ttl_osint = int(os.getenv("CACHE_TTL_OSINT", "1800"))  # 30 minutes
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.redis_client = None
    
    def _generate_cache_key(self, provider: str, model: str, text: str, scope: Optional[str] = None) -> str:
        """Generate cache key based on provider, model, normalized text, and scope"""
        # Normalize text by removing excessive whitespace and formatting
        normalized_text = " ".join(text.strip().split())
        
        # Create hash components
        components = [provider, model, normalized_text]
        if scope:
            components.append(scope)
        
        # Generate hash
        content = "|".join(components)
        cache_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return f"cache:{provider}:{model}:{scope or 'general'}:{cache_hash}"
    
    def _get_ttl(self, scope: Optional[str] = None) -> int:
        """Get TTL based on query scope"""
        if scope and "osint" in scope.lower():
            return self.cache_ttl_osint
        return self.cache_ttl_default
    
    def get(self, provider: str, model: str, text: str, scope: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached response if available"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(provider, model, text, scope)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            
            logger.debug(f"Cache miss for key: {cache_key}")
            return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, provider: str, model: str, text: str, response: Dict[str, Any], scope: Optional[str] = None) -> bool:
        """Cache response with appropriate TTL"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(provider, model, text, scope)
            ttl = self._get_ttl(scope)
            
            # Add metadata to cached response
            cache_data = {
                "response": response,
                "cached_at": json.dumps({"timestamp": "now"}),  # Simplified timestamp
                "ttl": ttl,
                "scope": scope
            }
            
            success = self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data, default=str)
            )
            
            if success:
                logger.info(f"Cached response for key: {cache_key} (TTL: {ttl}s)")
            
            return bool(success)
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, provider: str, model: str, text: str, scope: Optional[str] = None) -> bool:
        """Delete cached response"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(provider, model, text, scope)
            result = self.redis_client.delete(cache_key)
            logger.info(f"Deleted cache key: {cache_key}")
            return bool(result)
        
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries (use with caution)"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys("cache:*")
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries")
                return True
            return True
        
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            keys = self.redis_client.keys("cache:*")
            
            return {
                "enabled": True,
                "connected": True,
                "total_keys": len(keys),
                "memory_used": info.get("used_memory_human", "Unknown"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                ) * 100
            }
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": True, "connected": False, "error": str(e)}


# Global cache instance
cache = CacheMiddleware()