"""Redis adapter example using ``redis-py``."""
from __future__ import annotations

import os
from typing import Optional

try:
    import redis
except ImportError as exc:  # pragma: no cover - optional dependency
    redis = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


DEFAULT_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_client(url: str | None = None) -> "redis.Redis":
    """Return a Redis client configured from the provided URL."""

    if redis is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "redis is required for the Redis adapter. Install it with 'pip install redis'."
        ) from _IMPORT_ERROR

    return redis.from_url(url or DEFAULT_URL)


def ping(url: str | None = None) -> Optional[bool]:
    """Ping the Redis server to confirm connectivity."""

    client = get_client(url)
    try:
        return client.ping()
    finally:
        client.close()


if __name__ == "__main__":  # pragma: no cover - demo helper
    try:
        print(ping())
    except RuntimeError as error:
        print(error)
