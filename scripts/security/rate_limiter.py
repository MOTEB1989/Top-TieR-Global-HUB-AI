"""
Rate Limiting Module
Implements advanced rate limiting algorithms including Token Bucket and Sliding Window.
"""

import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, Optional


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""

    @abstractmethod
    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed.
        
        Args:
            key: Identifier for the requester (user_id, ip_address, etc.)
            
        Returns:
            True if request is allowed, False otherwise
        """
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """
        Reset rate limit for a key.
        
        Args:
            key: Identifier to reset
        """
        pass


class TokenBucketRateLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter.
    
    Tokens are added to the bucket at a constant rate.
    Each request consumes one token.
    If no tokens available, request is denied.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket rate limiter.
        
        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict[str, float]] = {}

    def _refill(self, key: str) -> None:
        """
        Refill tokens based on elapsed time.
        
        Args:
            key: Identifier for the bucket
        """
        now = time.time()
        bucket = self.buckets.get(key)
        
        if bucket:
            elapsed = now - bucket["last_refill"]
            tokens_to_add = elapsed * self.refill_rate
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
            bucket["last_refill"] = now

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed under token bucket algorithm.
        
        Args:
            key: Identifier for the requester
            
        Returns:
            True if allowed (token available), False otherwise
        """
        if key not in self.buckets:
            self.buckets[key] = {
                "tokens": self.capacity,
                "last_refill": time.time()
            }

        self._refill(key)
        
        if self.buckets[key]["tokens"] >= 1:
            self.buckets[key]["tokens"] -= 1
            return True
        return False

    def reset(self, key: str) -> None:
        """
        Reset the token bucket for a key.
        
        Args:
            key: Identifier to reset
        """
        if key in self.buckets:
            self.buckets[key] = {
                "tokens": self.capacity,
                "last_refill": time.time()
            }

    def get_remaining_tokens(self, key: str) -> float:
        """
        Get remaining tokens for a key.
        
        Args:
            key: Identifier to check
            
        Returns:
            Number of remaining tokens
        """
        if key not in self.buckets:
            return self.capacity
        
        self._refill(key)
        return self.buckets[key]["tokens"]


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding Window Rate Limiter.
    
    Tracks requests within a sliding time window.
    More accurate than fixed window, prevents bursts at window boundaries.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize sliding window rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Size of the sliding window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: Dict[str, deque] = {}

    def _clean_old_requests(self, key: str) -> None:
        """
        Remove requests outside the current window.
        
        Args:
            key: Identifier for the window
        """
        if key not in self.windows:
            return
        
        now = time.time()
        cutoff = now - self.window_seconds
        
        window = self.windows[key]
        while window and window[0] < cutoff:
            window.popleft()

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed under sliding window algorithm.
        
        Args:
            key: Identifier for the requester
            
        Returns:
            True if allowed, False otherwise
        """
        if key not in self.windows:
            self.windows[key] = deque()

        self._clean_old_requests(key)
        
        if len(self.windows[key]) < self.max_requests:
            self.windows[key].append(time.time())
            return True
        return False

    def reset(self, key: str) -> None:
        """
        Reset the sliding window for a key.
        
        Args:
            key: Identifier to reset
        """
        if key in self.windows:
            self.windows[key].clear()

    def get_request_count(self, key: str) -> int:
        """
        Get current request count in the window.
        
        Args:
            key: Identifier to check
            
        Returns:
            Number of requests in current window
        """
        if key not in self.windows:
            return 0
        
        self._clean_old_requests(key)
        return len(self.windows[key])

    def get_time_until_reset(self, key: str) -> float:
        """
        Get time until the oldest request expires.
        
        Args:
            key: Identifier to check
            
        Returns:
            Seconds until reset (0 if window is empty)
        """
        if key not in self.windows or not self.windows[key]:
            return 0.0
        
        oldest_request = self.windows[key][0]
        now = time.time()
        return max(0, self.window_seconds - (now - oldest_request))


class FixedWindowRateLimiter(RateLimiter):
    """
    Fixed Window Rate Limiter.
    
    Simple implementation that resets at fixed intervals.
    Fast but allows bursts at window boundaries.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize fixed window rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Window duration in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: Dict[str, Dict[str, any]] = {}

    def _get_current_window(self) -> int:
        """
        Get current window identifier.
        
        Returns:
            Window identifier (epoch timestamp divided by window size)
        """
        return int(time.time() / self.window_seconds)

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed under fixed window algorithm.
        
        Args:
            key: Identifier for the requester
            
        Returns:
            True if allowed, False otherwise
        """
        current_window = self._get_current_window()
        
        if key not in self.windows:
            self.windows[key] = {
                "window": current_window,
                "count": 0
            }
        
        window_data = self.windows[key]
        
        # Reset if new window
        if window_data["window"] != current_window:
            window_data["window"] = current_window
            window_data["count"] = 0
        
        if window_data["count"] < self.max_requests:
            window_data["count"] += 1
            return True
        return False

    def reset(self, key: str) -> None:
        """
        Reset the fixed window for a key.
        
        Args:
            key: Identifier to reset
        """
        if key in self.windows:
            current_window = self._get_current_window()
            self.windows[key] = {
                "window": current_window,
                "count": 0
            }


# Example usage and testing
if __name__ == "__main__":
    import time
    
    print("=== Token Bucket Rate Limiter ===")
    # 5 requests per second, burst of 10
    token_limiter = TokenBucketRateLimiter(capacity=10, refill_rate=5.0)
    
    user_id = "user_123"
    for i in range(15):
        allowed = token_limiter.is_allowed(user_id)
        remaining = token_limiter.get_remaining_tokens(user_id)
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'} (Tokens: {remaining:.2f})")
        time.sleep(0.1)
    
    print("\n=== Sliding Window Rate Limiter ===")
    # 5 requests per 2 seconds
    sliding_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=2)
    
    for i in range(8):
        allowed = sliding_limiter.is_allowed(user_id)
        count = sliding_limiter.get_request_count(user_id)
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'} (Count: {count}/5)")
        time.sleep(0.3)
    
    print("\n=== Fixed Window Rate Limiter ===")
    # 3 requests per 1 second window
    fixed_limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=1)
    
    for i in range(8):
        allowed = fixed_limiter.is_allowed(user_id)
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}")
        time.sleep(0.25)
