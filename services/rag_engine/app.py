import logging
import os
import time
from typing import Dict, List

from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SERVICE_NAME = "rag_engine"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
PHI3_URL = os.getenv("PHI3_URL", "http://localhost:8082")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:3000")

app = FastAPI(title="RAG Engine")

metrics: Dict[str, int] = {"requests_total": 0}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    metrics["requests_total"] = metrics.get("requests_total", 0) + 1
    logging.info("Incoming %s %s", request.method, request.url.path)
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    logging.info(
        "Completed %s %s with status %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "qdrant": QDRANT_URL,
        "phi3": PHI3_URL,
        "gateway": GATEWAY_URL,
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics_endpoint() -> Dict[str, int]:
    return metrics


@app.post("/retrieve")
async def retrieve(payload: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    query = payload.get("query", "").strip()
    if not query:
        return {"contexts": []}

    placeholder_contexts = [
        {"source": "qdrant", "snippet": f"Relevant context for '{query}' from {QDRANT_URL}."},
        {"source": "notes", "snippet": "This is a demo RAG pipeline stub for local development."},
    ]
    return {"contexts": placeholder_contexts}


@app.post("/rerank")
async def rerank(payload: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
    contexts = payload.get("contexts", [])
    return {"contexts": contexts}


@app.post("/route")
async def route(payload: Dict[str, str]) -> Dict[str, str]:
    prompt = payload.get("prompt", "").strip()
    return {"target": "phi3" if prompt else ""}
