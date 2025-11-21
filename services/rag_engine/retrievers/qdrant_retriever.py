from __future__ import annotations

import logging
from typing import Iterable, List

from ...embeddings.embedding_model import get_embedding, get_vector_size
from ..config import DocChunk, get_settings

logger = logging.getLogger(__name__)


class QdrantRetriever:
    def __init__(self) -> None:
        try:
            from qdrant_client import QdrantClient
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("qdrant-client is required for QdrantRetriever") from exc
        from qdrant_client.http import models as rest

        settings = get_settings()
        url = settings.get("RAG_QDRANT_URL")
        api_key = settings.get("RAG_QDRANT_API_KEY")
        if not url:
            raise RuntimeError("RAG_QDRANT_URL must be configured for Qdrant retriever")
        self.collection = str(settings.get("RAG_COLLECTION_NAME"))
        self.client = QdrantClient(url=url, api_key=api_key)
        self.rest = rest

    def ensure_collection(self) -> None:
        vector_size = get_vector_size()
        try:
            collections = self.client.get_collections()
            existing = {c.name for c in collections.collections}
            if self.collection in existing:
                return
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=self.rest.VectorParams(
                    size=vector_size,
                    distance=self.rest.Distance.COSINE,
                ),
            )
        except Exception as exc:
            raise RuntimeError("Failed to ensure Qdrant collection. Check connectivity and credentials.") from exc

    def upsert_documents(self, chunks: Iterable[DocChunk]) -> None:
        self.ensure_collection()
        points: List[self.rest.PointStruct] = []
        for chunk in chunks:
            embedding = get_embedding(chunk.content)
            points.append(
                self.rest.PointStruct(
                    id=f"{chunk.path}:{chunk.chunk_index}",
                    vector=embedding,
                    payload={
                        "path": chunk.path,
                        "chunk_index": chunk.chunk_index,
                        "text": chunk.content,
                        **chunk.metadata,
                    },
                )
            )
        if not points:
            logger.info("No points to upsert")
            return
        try:
            self.client.upsert(collection_name=self.collection, points=points)
        except Exception as exc:
            raise RuntimeError("Failed to upsert documents to Qdrant. Verify schema and network.") from exc

    def query_similar(self, query_embedding: List[float], top_k: int) -> List[object]:
        self.ensure_collection()
        try:
            result = self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
            )
            return result
        except Exception as exc:
            raise RuntimeError("Failed to query Qdrant for similar chunks.") from exc


__all__ = ["QdrantRetriever"]
