#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
rate_limiter.py

Per-user rate limiting with sliding window.
تحديد معدل الرسائل لكل مستخدم.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter with sliding window."""
    
    def __init__(self, window_seconds: int = 3600, max_messages: int = 30):
        """
        Initialize rate limiter.
        
        Args:
            window_seconds: Time window in seconds (default 1 hour)
            max_messages: Maximum messages per window (default 30)
        """
        self.window_seconds = window_seconds
        self.max_messages = max_messages
        self.user_logs: Dict[int, List[datetime]] = {}
        logger.info(f"[rate_limiter] Initialized: {max_messages} msgs per {window_seconds}s")
    
    def _clean_old_entries(self, user_id: int) -> None:
        """Remove timestamps outside the current window."""
        if user_id not in self.user_logs:
            return
        
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        self.user_logs[user_id] = [
            ts for ts in self.user_logs[user_id] if ts > cutoff
        ]
    
    def check_limit(self, user_id: int) -> bool:
        """
        Check if user is within rate limit.
        
        Returns:
            True if user can proceed, False if rate limited
        """
        self._clean_old_entries(user_id)
        
        if user_id not in self.user_logs:
            self.user_logs[user_id] = []
        
        current_count = len(self.user_logs[user_id])
        
        if current_count >= self.max_messages:
            logger.warning(f"[rate_limiter] User {user_id} rate limited: {current_count}/{self.max_messages}")
            return False
        
        return True
    
    def record_message(self, user_id: int) -> None:
        """Record a message from user."""
        if user_id not in self.user_logs:
            self.user_logs[user_id] = []
        
        self.user_logs[user_id].append(datetime.utcnow())
        logger.debug(f"[rate_limiter] Recorded message for user {user_id}")
    
    def get_remaining(self, user_id: int) -> int:
        """Get remaining message quota for user."""
        self._clean_old_entries(user_id)
        
        if user_id not in self.user_logs:
            return self.max_messages
        
        return max(0, self.max_messages - len(self.user_logs[user_id]))
    
    def get_reset_time(self, user_id: int) -> int:
        """Get seconds until rate limit resets for user."""
        self._clean_old_entries(user_id)
        
        if user_id not in self.user_logs or not self.user_logs[user_id]:
            return 0
        
        oldest = min(self.user_logs[user_id])
        reset_time = oldest + timedelta(seconds=self.window_seconds)
        now = datetime.utcnow()
        
        if reset_time <= now:
            return 0
        
        return int((reset_time - now).total_seconds())
