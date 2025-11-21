from __future__ import annotations

from typing import Any, Iterable, List, Tuple

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    faiss = None

from ..config import DocChunk
from ...embeddings.embedding_model import get_embedding, get_vector_size


class FaissRetriever:
    def __init__(self) -> None:
        if faiss is None:
            raise RuntimeError("FAISS is not installed. Install faiss-cpu to enable local indexing.")
        self.index = faiss.IndexFlatL2(get_vector_size())
        self.metadata: List[Tuple[str, int, dict]] = []

    def build_index(self, chunks: Iterable[DocChunk]) -> None:
        vectors: List[List[float]] = []
        self.metadata.clear()
        for chunk in chunks:
            vectors.append(get_embedding(chunk.content))
            self.metadata.append((chunk.path, chunk.chunk_index, chunk.metadata))
        if vectors:
            import numpy as np

            self.index.add(np.array(vectors, dtype="float32"))

    def query_index(self, query_embedding: List[float], top_k: int) -> List[dict[str, Any]]:
        if not hasattr(self, "index"):
            raise RuntimeError("Index not built. Call build_index first.")
        import numpy as np

        distances, indices = self.index.search(np.array([query_embedding], dtype="float32"), top_k)
        results: List[dict[str, Any]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            path, chunk_idx, metadata = self.metadata[idx]
            results.append({
                "score": float(dist),
                "payload": {
                    "path": path,
                    "chunk_index": chunk_idx,
                    **metadata,
                },
            })
        return results


__all__ = ["FaissRetriever"]
