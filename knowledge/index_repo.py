import glob
import hashlib
import os
import time

from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

REPO_ROOT = os.environ.get("REPO_ROOT", ".")
COLLECTION_NAME = os.environ.get("KB_COLLECTION", "lexcode_kb")
DB_PATH = os.environ.get("KB_PATH", ".chroma")
MODEL_NAME = os.environ.get("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

INCLUDE = [
    "**/*.md",
    "**/*.txt",
    "**/*.py",
    "**/*.js",
    "**/*.ts",
    "**/*.tsx",
    "**/*.json",
    "**/*.yml",
    "**/*.yaml",
    "**/*.sql",
]

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except Exception:
        return ""

def chunk(text: str, max_chars: int = 1200, overlap: int = 120):
    start = 0
    total = len(text)
    while start < total:
        yield text[start : start + max_chars]
        start += max(1, max_chars - overlap)

def doc_id(path: str, idx: int) -> str:
    raw = f"{path}::{idx}"
    return hashlib.sha1(raw.encode()).hexdigest()

def main() -> None:
    print("🚀 Loading embedding model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    print("🗃️ Init Chroma at:", DB_PATH)
    client = chromadb.PersistentClient(
        path=DB_PATH, settings=Settings(allow_reset=False)
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    files = []
    for pattern in INCLUDE:
        files.extend(glob.glob(os.path.join(REPO_ROOT, pattern), recursive=True))
    files = sorted(set(files))

    print(f"📚 Indexing {len(files)} files…")
    for path in tqdm(files):
        text = read_file(path)
        if not text.strip():
            continue
        for idx, chunk_text in enumerate(chunk(text)):
            entry_id = doc_id(path, idx)
            embedding = model.encode([chunk_text], normalize_embeddings=True).tolist()
            collection.add(
                documents=[chunk_text],
                metadatas=[{"path": path, "chunk": idx}],
                ids=[entry_id],
                embeddings=embedding,
            )
    print("✅ Indexing complete.")

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"⏱️ Done in {time.time() - start:.1f}s")
