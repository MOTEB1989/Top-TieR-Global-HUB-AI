from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from .config import get_settings


CacheKey = Tuple[str, str, str, int]


def _normalize_question(question: str) -> str:
    return question.strip().lower()


def _should_cache() -> bool:
    return bool(get_settings().get("RAG_CACHE_ENABLED", True))


@lru_cache(maxsize=256)
def _cache_store(key: CacheKey) -> Optional[Dict[str, Any]]:
    return None


def get_cached_answer(question: str, provider: str, model: str, top_k: int) -> Optional[Dict[str, Any]]:
    if not _should_cache():
        return None
    key = (_normalize_question(question), provider, model, top_k)
    return _cache_store(key)


def set_cached_answer(question: str, provider: str, model: str, top_k: int, value: Dict[str, Any]) -> None:
    if not _should_cache():
        return
    key = (_normalize_question(question), provider, model, top_k)

    def _populate(_: CacheKey) -> Optional[Dict[str, Any]]:
        return value

    global _cache_store
    _cache_store.cache_clear()
    _cache_store = lru_cache(maxsize=256)(_populate)  # type: ignore
    _cache_store(key)


__all__ = ["get_cached_answer", "set_cached_answer"]
