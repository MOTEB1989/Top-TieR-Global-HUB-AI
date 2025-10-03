"""Gateway API bridging external callers with orchestrator and core services."""
from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://orchestrator:3100")
CORE_URL = os.environ.get("CORE_URL", "http://core:3000")


class InferenceRequest(BaseModel):
    prompt: str
    options: Dict[str, Any] | None = None


app = FastAPI(title="Gateway API", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/lex/run")
async def forward_lex(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{ORCHESTRATOR_URL}/v1/lex/run", json=payload)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    return response.json()


@app.post("/v1/ai/infer")
async def forward_core(request: InferenceRequest) -> Dict[str, Any]:
    payload = {"prompt": request.prompt, **(request.options or {})}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{CORE_URL}/v1/ai/infer", json=payload)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    return response.json()
