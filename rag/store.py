import json
import sqlite3
from pathlib import Path
from typing import Dict, List

from .config import DB_PATH


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                path TEXT,
                chunk_index INTEGER,
                content TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                doc_id INTEGER,
                chunk_index INTEGER,
                vector TEXT
            )
            """
        )
        conn.commit()


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for av, bv in zip(a, b):
        dot += av * bv
        norm_a += av * av
        norm_b += bv * bv

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / ((norm_a ** 0.5) * (norm_b ** 0.5))


def add_chunk(path: str, chunk_index: int, content: str, embedding: List[float]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (path, chunk_index, content) VALUES (?, ?, ?)",
            (path, chunk_index, content),
        )
        doc_id = cur.lastrowid
        cur.execute(
            "INSERT INTO embeddings (doc_id, chunk_index, vector) VALUES (?, ?, ?)",
            (doc_id, chunk_index, json.dumps(embedding)),
        )
        conn.commit()


def get_top_k_similar(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    results: List[Dict] = []
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT documents.path, documents.chunk_index, documents.content, embeddings.vector "
            "FROM documents JOIN embeddings ON documents.id = embeddings.doc_id"
        )
        rows = cur.fetchall()

    for path, chunk_index, content, vector_text in rows:
        try:
            vector = [float(x) for x in json.loads(vector_text)]
        except Exception:
            continue
        score = _cosine_similarity(query_embedding, vector)
        results.append(
            {
                "path": path,
                "chunk_index": chunk_index,
                "content": content,
                "score": score,
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
