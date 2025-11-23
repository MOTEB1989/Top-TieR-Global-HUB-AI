import os
from typing import Any, Dict

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Unified Gateway", version="0.1.0")

PHI3_URL = os.getenv("PHI3_URL", "http://phi3:8082")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "phi_local")


class CompletionRequest(BaseModel):
    prompt: str


class CompletionResponse(BaseModel):
    output: str
    provider: str


@app.get("/health", response_model=Dict[str, Any])
def health() -> Dict[str, Any]:
    return {"status": "ok", "provider": LLM_PROVIDER}


@app.post("/complete", response_model=CompletionResponse)
def complete(request: CompletionRequest) -> CompletionResponse:
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")

    try:
        response = requests.post(
            f"{PHI3_URL}/infer",
            json={"prompt": request.prompt},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network failure handling
        raise HTTPException(status_code=502, detail=f"Failed to reach Phi-3 service: {exc}")

    payload = response.json()
    output = payload.get("output") or "Phi-3 did not return any output."
    return CompletionResponse(output=output, provider=LLM_PROVIDER)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("gateway_server:app", host="0.0.0.0", port=3000, reload=False)
