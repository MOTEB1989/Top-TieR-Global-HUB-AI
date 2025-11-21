import time
from dataclasses import dataclass

@dataclass
class Limits:
    max_requests: int = 100

class UsageGuard:
    def __init__(self):
        self.limits = Limits()
        self.usage = {}
    
    def check(self, user_id: str) -> bool:
        hour = int(time.time() / 3600)
        key = f"{user_id}:{hour}"
        self.usage[key] = self.usage.get(key, 0) + 1
        return self.usage[key] <= self.limits.max_requests
