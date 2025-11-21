"""Configuration helpers for the RAG engine.

Values are read from environment variables so deployments can override them
without changing code. Defaults are intentionally lightweight to keep CI fast.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict


@dataclass
class DocChunk:
    """Normalized chunk representation used across loaders and retrievers."""

    path: str
    chunk_index: int
    content: str
    metadata: Dict[str, str]


def _get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value if value is not None and value != "" else default


@lru_cache(maxsize=1)
def get_settings() -> Dict[str, object]:
    return {
        "RAG_EMBEDDING_PROVIDER": _get_env("RAG_EMBEDDING_PROVIDER", "local"),
        "RAG_EMBEDDING_MODEL": _get_env("RAG_EMBEDDING_MODEL", "all-mpnet-base-v2"),
        "RAG_QDRANT_URL": _get_env("RAG_QDRANT_URL"),
        "RAG_QDRANT_API_KEY": _get_env("RAG_QDRANT_API_KEY"),
        "RAG_COLLECTION_NAME": _get_env("RAG_COLLECTION_NAME", "top_tier_rag"),
        "RAG_TOP_K": int(_get_env("RAG_TOP_K", "5")),
        "RAG_CACHE_ENABLED": _get_env("RAG_CACHE_ENABLED", "true").lower() == "true",
        "RAG_CHUNK_SIZE": int(_get_env("RAG_CHUNK_SIZE", "800")),
        "RAG_CHUNK_OVERLAP": int(_get_env("RAG_CHUNK_OVERLAP", "100")),
        "RAG_MAX_PDF_MB": int(_get_env("RAG_MAX_PDF_MB", "10")),
    }


def reset_settings_cache() -> None:
    get_settings.cache_clear()


__all__ = ["DocChunk", "get_settings", "reset_settings_cache"]
