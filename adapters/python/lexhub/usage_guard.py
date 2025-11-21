"""Lightweight usage guard with hourly quotas."""
from dataclasses import dataclass
import time
from typing import Dict


@dataclass
class Limits:
    max_requests: int = 100
    window_seconds: int = 3600


class UsageGuard:
    def __init__(self, limits: Limits | None = None):
        self.limits = limits or Limits()
        self.usage: Dict[str, int] = {}

    def check(self, user_id: str) -> bool:
        bucket = self._bucket_key(user_id)
        self.usage[bucket] = self.usage.get(bucket, 0) + 1
        return self.usage[bucket] <= self.limits.max_requests

    def _bucket_key(self, user_id: str) -> str:
        window = int(time.time() / self.limits.window_seconds)
        return f"{user_id}:{window}"
