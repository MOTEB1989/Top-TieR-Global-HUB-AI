import logging
import os
import time
from typing import Dict

from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SERVICE_NAME = "phi3"
RAG_ENGINE_URL = os.getenv("RAG_ENGINE_URL", "http://localhost:8081")

app = FastAPI(title="Phi-3 Local Stub")

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
    return {"service": SERVICE_NAME, "rag_engine": RAG_ENGINE_URL}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics_endpoint() -> Dict[str, int]:
    return metrics


@app.post("/generate")
async def generate(payload: Dict[str, str]) -> Dict[str, str]:
    prompt = payload.get("prompt", "").strip()
    generated = "" if not prompt else f"[phi-local] Response to: {prompt}"
    return {"completion": generated, "model": SERVICE_NAME}
