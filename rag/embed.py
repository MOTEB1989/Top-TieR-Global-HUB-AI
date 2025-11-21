import os
from typing import List

from .config import EMBEDDING_MODEL


def get_embedding(text: str) -> List[float]:
    """
    Return an embedding vector for the given text using OpenAI embeddings.

    This is a manual, opt-in operation; it should be called only in CLI/ops flows,
    never in automated tests.
    """
    try:
        import openai
    except ImportError as exc:  # pragma: no cover - dependency optional in CI
        raise RuntimeError("openai package is required for RAG embeddings.") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set; cannot compute embeddings.")
    openai.api_key = api_key

    resp = openai.Embedding.create(model=EMBEDDING_MODEL, input=text)
    return resp["data"][0]["embedding"]
