import os
from pathlib import Path

BASE_DIR = Path(os.getenv("RAG_BASE_DIR", ".")).resolve()
DB_PATH = BASE_DIR / os.getenv("RAG_DB_PATH", "rag_db.sqlite3")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
