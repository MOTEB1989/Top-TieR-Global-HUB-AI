"""Core inference stub exposing a consistent API surface."""
from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")


class InferencePayload(BaseModel):
    prompt: str = Field(..., description="Prompt submitted to the language model.")
    model: str = Field(default=DEFAULT_MODEL, description="Model identifier to use.")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)


app = FastAPI(title="Core Inference Service", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ai/infer")
def infer(payload: InferencePayload) -> Dict[str, Any]:
    snippet = payload.prompt.strip().splitlines()[0][:120]
    message = (
        "This is a stubbed response from the core inference service. "
        "Integrate with your preferred LLM provider for production use."
    )
    return {
        "model": payload.model,
        "temperature": payload.temperature,
        "preview": snippet,
        "message": message,
    }
