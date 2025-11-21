from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import List

from services.rag_engine.config import get_settings

logger = logging.getLogger(__name__)


class _BaseProvider:
    def embed(self, text: str) -> List[float]:  # pragma: no cover - interface
        raise NotImplementedError

    def vector_size(self) -> int:  # pragma: no cover - interface
        raise NotImplementedError


class _LocalProvider(_BaseProvider):
    def __init__(self) -> None:
        self.model_name = str(get_settings().get("RAG_EMBEDDING_MODEL", "all-mpnet-base-v2"))
        self._model = None

    @property
    def model(self):  # pragma: no cover - heavy
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, text: str) -> List[float]:  # pragma: no cover - heavy
        return list(self.model.encode(text))

    def vector_size(self) -> int:
        try:
            return int(self.model.get_sentence_embedding_dimension())
        except Exception:  # pragma: no cover - heavy
            return 768


class _OpenAIProvider(_BaseProvider):
    def __init__(self) -> None:
        from openai import OpenAI  # type: ignore

        self.client = OpenAI()
        self.model = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")

    def embed(self, text: str) -> List[float]:  # pragma: no cover - network
        response = self.client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)

    def vector_size(self) -> int:
        return 1536


@lru_cache(maxsize=1)
def _get_provider() -> _BaseProvider:
    provider = str(get_settings().get("RAG_EMBEDDING_PROVIDER", "local"))
    if provider == "openai":
        return _OpenAIProvider()
    return _LocalProvider()


def get_embedding(text: str) -> List[float]:
    """Return an embedding for the given text.

    NOTE: This must be mocked in CI to avoid heavy downloads or API calls.
    """

    return _get_provider().embed(text)


def get_vector_size() -> int:
    return _get_provider().vector_size()


__all__ = ["get_embedding", "get_vector_size"]
