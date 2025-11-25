"""
Redis client for caching and session storage.
Provides connection management and basic operations.
"""
import time
from typing import Optional, Tuple, Any

from backend.app.config import get_config
from backend.app.logging import db_logger

# Optional redis import - fail gracefully if not installed
try:
    import redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    RedisError = Exception  # type: ignore


class RedisClient:
    """Redis client with lazy initialization and health checking"""
    
    def __init__(self):
        self._client: Optional[Any] = None
        self._config = get_config()
    
    def _initialize(self) -> None:
        """Initialize Redis client if not already initialized"""
        if self._client is not None:
            return
        
        if not REDIS_AVAILABLE:
            db_logger.warning("redis package not available - Redis features disabled")
            return
        
        redis_url = self._config.REDIS_URL
        if not redis_url:
            db_logger.warning("REDIS_URL not configured - Redis features disabled")
            return
        
        try:
            self._client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            db_logger.info("Redis client initialized")
        except Exception as e:
            db_logger.error(f"Failed to initialize Redis client: {e}")
            self._client = None
    
    def is_available(self) -> bool:
        """Check if Redis client is configured and available"""
        return (
            REDIS_AVAILABLE
            and self._config.REDIS_URL is not None
        )
    
    async def health_check(self) -> Tuple[bool, str, Optional[float]]:
        """
        Perform health check on Redis connection.
        
        Returns:
            Tuple of (is_healthy, message, response_time_ms)
        """
        if not self.is_available():
            return False, "Redis not configured or redis package not available", None
        
        self._initialize()
        
        if self._client is None:
            return False, "Redis client initialization failed", None
        
        start_time = time.time()
        try:
            # Ping Redis server
            pong = self._client.ping()
            response_time_ms = (time.time() - start_time) * 1000
            
            if pong:
                return True, "Redis connection healthy", response_time_ms
            else:
                return False, "Redis ping returned False", response_time_ms
        
        except RedisError as e:
            response_time_ms = (time.time() - start_time) * 1000
            db_logger.error(f"Redis health check failed: {e}")
            return False, f"Redis error: {str(e)}", response_time_ms
        
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            db_logger.error(f"Unexpected error during Redis health check: {e}")
            return False, f"Unexpected error: {str(e)}", response_time_ms
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis by key.
        
        Args:
            key: Redis key
        
        Returns:
            Value as string or None if not found or error
        """
        if not self.is_available():
            return None
        
        self._initialize()
        if self._client is None:
            return None
        
        try:
            return self._client.get(key)
        except Exception as e:
            db_logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None
    ) -> bool:
        """
        Set value in Redis with optional expiration.
        
        Args:
            key: Redis key
            value: Value to store
            ex: Optional expiration time in seconds
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        self._initialize()
        if self._client is None:
            return False
        
        try:
            self._client.set(key, value, ex=ex)
            return True
        except Exception as e:
            db_logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    def get_client(self) -> Optional[Any]:
        """Get the underlying Redis client (for advanced usage)"""
        if not self.is_available():
            return None
        self._initialize()
        return self._client


# Global client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get the global Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
