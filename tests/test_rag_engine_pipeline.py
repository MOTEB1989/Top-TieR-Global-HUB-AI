import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from services.rag_engine import config
from services.rag_engine.loaders import load_pdf_files, load_text_files
from services.rag_engine import rag


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    monkeypatch.setenv("RAG_CHUNK_SIZE", "10")
    monkeypatch.setenv("RAG_CHUNK_OVERLAP", "0")
    monkeypatch.setenv("RAG_MAX_PDF_MB", "5")
    monkeypatch.setenv("RAG_QDRANT_URL", "http://localhost:6333")
    config.reset_settings_cache()
    yield
    config.reset_settings_cache()


def test_text_loader_chunking(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_text("abcdefghij12345", encoding="utf-8")
    chunks = list(load_text_files(tmp_path))
    assert len(chunks) == 2
    assert chunks[0].content.startswith("abcdefghij")


def test_pdf_loader_synthetic(tmp_path: Path):
    fitz = pytest.importorskip("fitz")
    pdf_path = tmp_path / "doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF world")
    doc.save(pdf_path)
    doc.close()

    chunks = list(load_pdf_files(tmp_path))
    assert chunks
    assert chunks[0].metadata["page_number"] == "1"


def test_rag_query_with_mocks(monkeypatch):
    class FakeRetriever:
        def __init__(self):
            self.query_calls = []

        def query_similar(self, embedding, top_k):
            self.query_calls.append((embedding, top_k))
            return [SimpleNamespace(score=0.9, payload={"text": "context text", "source": "doc"})]

        def upsert_documents(self, chunks):  # pragma: no cover - not used
            pass

    monkeypatch.setenv("RAG_QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("RAG_EMBEDDING_PROVIDER", "local")
    monkeypatch.setenv("RAG_EMBEDDING_MODEL", "stub")
    config.reset_settings_cache()

    monkeypatch.setattr(rag, "QdrantRetriever", FakeRetriever)
    monkeypatch.setattr(rag, "get_embedding", lambda text: [0.1, 0.2, 0.3])
    monkeypatch.setattr(rag, "simple_chat", lambda prompt, **_: "answer from mock")

    result = rag.query("question?", top_k=1)
    assert result["answer"] == "answer from mock"
    assert result["contexts"]
