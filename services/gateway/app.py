import logging
import os
import time
from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SERVICE_NAME = "gateway"
PHI3_URL = os.getenv("PHI3_URL", "http://localhost:8082")
RAG_ENGINE_URL = os.getenv("RAG_ENGINE_URL", "http://localhost:8081")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "phi_local")

app = FastAPI(title="Gateway")

metrics: Dict[str, int] = {"requests_total": 0}


def _safe_post_json(url: str, payload: Dict, timeout: int = 10) -> Dict:
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        logging.error("Request to %s failed: %s", url, exc)
        return {}


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
        "llm_provider": LLM_PROVIDER,
        "phi3": PHI3_URL,
        "rag_engine": RAG_ENGINE_URL,
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics_endpoint() -> Dict[str, int]:
    return metrics


@app.post("/chat")
async def chat(payload: Dict[str, str]) -> Dict:
    message = payload.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    contexts_response = _safe_post_json(f"{RAG_ENGINE_URL}/retrieve", {"query": message})
    contexts: List[Dict[str, str]] = contexts_response.get("contexts", [])

    completion_response = _safe_post_json(
        f"{PHI3_URL}/generate", {"prompt": message, "contexts": contexts}
    )
    completion = completion_response.get("completion", "")

    return {
        "message": message,
        "completion": completion,
        "contexts": contexts,
        "llm_provider": LLM_PROVIDER,
    }
