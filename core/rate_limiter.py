"""
Rate Limiting Module for Top-TieR Global HUB AI
Implements Redis-based sliding window rate limiting with cost guards
"""
import logging
import os
import time
from typing import Dict, Optional, Tuple

import redis
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter with sliding window and cost controls"""
    
    def __init__(self):
        """Initialize rate limiter with Redis connection"""
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        # Rate limiting configuration
        self.default_rpm = int(os.getenv("RATE_LIMIT_RPM", "30"))  # requests per minute
        self.cost_ceiling = float(os.getenv("COST_CEILING", "10.0"))  # dollars per hour
        self.window_size = 60  # 1 minute window
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            logger.info(f"Rate limiter connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.warning(f"Redis connection failed for rate limiter: {e}. Rate limiting disabled.")
            self.redis_client = None
    
    def _get_client_key(self, request: Request) -> str:
        """Generate client identification key from request"""
        # Try to get user ID from headers or use IP address
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def check_rate_limit(self, request: Request, cost: Optional[float] = None) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limits
        
        Returns:
            Tuple of (allowed, info_dict)
        """
        if not self.redis_client:
            return True, {"rate_limiting": "disabled"}
        
        client_key = self._get_client_key(request)
        current_time = int(time.time())
        
        try:
            # Check request rate limit
            rate_allowed, rate_info = self._check_request_rate(client_key, current_time)
            
            # Check cost ceiling if cost is provided
            cost_allowed, cost_info = True, {}
            if cost is not None:
                cost_allowed, cost_info = self._check_cost_ceiling(client_key, current_time, cost)
            
            allowed = rate_allowed and cost_allowed
            
            # Combine info
            info = {
                "client": client_key,
                "rate_limit": rate_info,
                "cost_limit": cost_info,
                "allowed": allowed
            }
            
            return allowed, info
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request if rate limiting fails
            return True, {"error": str(e)}
    
    def _check_request_rate(self, client_key: str, current_time: int) -> Tuple[bool, Dict[str, any]]:
        """Check request rate using sliding window"""
        rate_key = f"rate:{client_key}"
        window_start = current_time - self.window_size
        
        try:
            # Remove old entries
            self.redis_client.zremrangebyscore(rate_key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis_client.zcard(rate_key)
            
            if current_count >= self.default_rpm:
                # Rate limit exceeded
                ttl = self.redis_client.ttl(rate_key)
                reset_time = current_time + (ttl if ttl > 0 else self.window_size)
                
                return False, {
                    "limit": self.default_rpm,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": ttl if ttl > 0 else self.window_size
                }
            
            # Add current request
            self.redis_client.zadd(rate_key, {str(current_time): current_time})
            self.redis_client.expire(rate_key, self.window_size)
            
            remaining = self.default_rpm - current_count - 1
            
            return True, {
                "limit": self.default_rpm,
                "remaining": remaining,
                "reset_time": current_time + self.window_size
            }
            
        except Exception as e:
            logger.error(f"Request rate check error: {e}")
            return True, {"error": str(e)}
    
    def _check_cost_ceiling(self, client_key: str, current_time: int, cost: float) -> Tuple[bool, Dict[str, any]]:
        """Check cost ceiling using hourly tracking"""
        cost_key = f"cost:{client_key}"
        hour_start = current_time - 3600  # 1 hour window
        
        try:
            # Remove old cost entries
            self.redis_client.zremrangebyscore(cost_key, 0, hour_start)
            
            # Calculate current hour cost
            cost_entries = self.redis_client.zrange(cost_key, 0, -1, withscores=True)
            current_cost = sum(float(entry[0]) for entry in cost_entries)
            
            if current_cost + cost > self.cost_ceiling:
                # Cost ceiling exceeded
                return False, {
                    "ceiling": self.cost_ceiling,
                    "current": current_cost,
                    "requested": cost,
                    "would_exceed": current_cost + cost,
                    "reset_time": current_time + 3600
                }
            
            # Add current cost
            self.redis_client.zadd(cost_key, {str(cost): current_time})
            self.redis_client.expire(cost_key, 3600)
            
            return True, {
                "ceiling": self.cost_ceiling,
                "current": current_cost + cost,
                "remaining": self.cost_ceiling - current_cost - cost
            }
            
        except Exception as e:
            logger.error(f"Cost ceiling check error: {e}")
            return True, {"error": str(e)}
    
    def get_client_stats(self, request: Request) -> Dict[str, any]:
        """Get current client rate limit and cost statistics"""
        if not self.redis_client:
            return {"rate_limiting": "disabled"}
        
        client_key = self._get_client_key(request)
        current_time = int(time.time())
        
        try:
            # Get rate limit stats
            rate_key = f"rate:{client_key}"
            window_start = current_time - self.window_size
            self.redis_client.zremrangebyscore(rate_key, 0, window_start)
            current_requests = self.redis_client.zcard(rate_key)
            
            # Get cost stats
            cost_key = f"cost:{client_key}"
            hour_start = current_time - 3600
            self.redis_client.zremrangebyscore(cost_key, 0, hour_start)
            cost_entries = self.redis_client.zrange(cost_key, 0, -1, withscores=True)
            current_cost = sum(float(entry[0]) for entry in cost_entries)
            
            return {
                "client": client_key,
                "rate_limit": {
                    "requests_this_minute": current_requests,
                    "limit": self.default_rpm,
                    "remaining": max(0, self.default_rpm - current_requests)
                },
                "cost_limit": {
                    "cost_this_hour": round(current_cost, 4),
                    "ceiling": self.cost_ceiling,
                    "remaining": round(max(0, self.cost_ceiling - current_cost), 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Client stats error: {e}")
            return {"error": str(e)}


def rate_limit_middleware(request: Request, cost: Optional[float] = None):
    """Middleware function to check rate limits"""
    rate_limiter = RateLimiter()
    allowed, info = rate_limiter.check_rate_limit(request, cost)
    
    if not allowed:
        # Determine which limit was exceeded
        if not info.get("rate_limit", {}).get("remaining", 1):
            # Rate limit exceeded
            rate_info = info["rate_limit"]
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": rate_info["limit"],
                    "retry_after": rate_info.get("retry_after", 60)
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(rate_info.get("retry_after", 60))
                }
            )
        
        elif "cost_limit" in info and info["cost_limit"].get("would_exceed"):
            # Cost ceiling exceeded
            cost_info = info["cost_limit"]
            raise HTTPException(
                status_code=402,  # Payment Required
                detail={
                    "error": "Cost ceiling exceeded",
                    "ceiling": cost_info["ceiling"],
                    "current": cost_info["current"],
                    "requested": cost_info["requested"]
                }
            )
    
    return info


# Global rate limiter instance
rate_limiter = RateLimiter()