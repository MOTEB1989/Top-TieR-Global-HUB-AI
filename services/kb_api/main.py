from fastapi import FastAPI, Query, HTTPException
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

app = FastAPI(title="LexCode KB API")

DB_PATH = os.getenv("KB_PATH", ".kb_store")
COLLECTION_NAME = os.getenv("KB_COLLECTION", "lexcode_kb")
MODEL_NAME = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# init chroma + model
client = chromadb.PersistentClient(path=DB_PATH, settings=Settings(allow_reset=False))
coll = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
model = SentenceTransformer(MODEL_NAME)

@app.get("/health")
def health():
    return {"status": "ok", "collection": COLLECTION_NAME, "db_path": DB_PATH}

@app.get("/search")
def search(q: str = Query(..., description="Query text"), top_k: int = 5):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    emb = model.encode([q], normalize_embeddings=True).tolist()
    results = coll.query(query_embeddings=emb, n_results=top_k)
    docs = [
        {
            "id": i,
            "text": d,
            "score": s,
            "path": m.get("path"),
            "chunk": m.get("chunk")
        }
        for i, d, s, m in zip(results["ids"][0], results["documents"][0], results["distances"][0], results["metadatas"][0])
    ]
    return {"query": q, "results": docs}

@app.get("/ask")
def ask(q: str = Query(...), top_k: int = 5):
    """
    استرجاع + دمج (RAG) — يرجع أفضل مقاطع مرتبطة بالسؤال.
    يمكن لاحقًا تمريرها لنموذج لغة عبر Gateway.
    """
    search_results = search(q, top_k)
    context = "\n\n".join([r["text"] for r in search_results["results"]])
    return {
        "query": q,
        "context": context,
        "results": search_results["results"]
    }
