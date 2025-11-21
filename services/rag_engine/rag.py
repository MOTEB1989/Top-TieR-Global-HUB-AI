from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Iterable, List

from services.embeddings.embedding_model import get_embedding
from services.rag_engine import cache
from services.rag_engine.config import get_settings
from services.rag_engine.loaders import load_pdf_files, load_text_files
from services.rag_engine.retrievers import QdrantRetriever
from gateway.router import simple_chat

logger = logging.getLogger(__name__)


def _select_loader(doc_type: str):
    if doc_type == "text":
        return [load_text_files]
    if doc_type == "pdf":
        return [load_pdf_files]
    return [load_text_files, load_pdf_files]


def ingest(path: Path, doc_type: str = "auto") -> None:
    settings = get_settings()
    retriever = QdrantRetriever()
    loaders = _select_loader(doc_type)
    for loader in loaders:
        chunks = list(loader(path))
        if not chunks:
            logger.info("No chunks found for loader %s", loader.__name__)
            continue
        retriever.upsert_documents(chunks)
        logger.info("Upserted %s chunks via %s", len(chunks), loader.__name__)


def _build_context(matches: Iterable[object]) -> List[dict]:
    contexts = []
    for match in matches:
        payload = getattr(match, "payload", {}) or match.get("payload")
        score = getattr(match, "score", None) or getattr(match, "score", None) or match.get("score")
        contexts.append({
            "score": score,
            "content": payload.get("text") if isinstance(payload, dict) else None,
            "metadata": payload,
        })
    return contexts


def query(question: str, top_k: int | None = None) -> dict:
    settings = get_settings()
    top_k = top_k or int(settings["RAG_TOP_K"])
    provider = str(settings.get("RAG_EMBEDDING_PROVIDER", "local"))
    model = str(settings.get("RAG_EMBEDDING_MODEL", "all-mpnet-base-v2"))

    cached = cache.get_cached_answer(question, provider, model, top_k)
    if cached:
        return {"question": question, "answer": cached["answer"], "contexts": cached.get("contexts", [])}

    retriever = QdrantRetriever()
    query_embedding = get_embedding(question)
    matches = retriever.query_similar(query_embedding, top_k)

    context_lines = []
    contexts: List[dict] = []
    for match in matches:
        payload = match.payload
        text = match.payload.get("text") if isinstance(match.payload, dict) else ""
        context_lines.append(f"[score={match.score}] {text}")
        contexts.append({
            "score": match.score,
            "metadata": payload,
        })
    context_block = "\n".join(context_lines)
    prompt = (
        "You are a RAG assistant. Rely only on the provided context to answer in the user's language.\n"
        f"Context:\n{context_block}\n"
        f"Question: {question}\nAnswer:"
    )
    answer = simple_chat(prompt)
    result = {"question": question, "answer": answer, "contexts": contexts}
    cache.set_cached_answer(question, provider, model, top_k, result)
    return result


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="RAG engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("--path", type=Path, required=True)
    ingest_parser.add_argument("--type", choices=["text", "pdf", "auto"], default="auto")

    query_parser = subparsers.add_parser("query", help="Query RAG")
    query_parser.add_argument("question", type=str)
    query_parser.add_argument("--top-k", type=int, default=None)

    args = parser.parse_args(argv)

    if args.command == "ingest":
        ingest(args.path, args.type)
    elif args.command == "query":
        result = query(args.question, args.top_k)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
