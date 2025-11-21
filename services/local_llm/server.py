from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel
from services.local_llm.phi_runner import generate_local_phi

app = FastAPI()


class ChatRequest(BaseModel):
    messages: list[Dict[str, Any]]
    model: str | None = None
    max_tokens: int = 512


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat_completions(body: ChatRequest) -> Dict[str, Any]:
    prompt_parts = [m.get("content", "") for m in body.messages]
    prompt = "\n".join(prompt_parts)
    output = generate_local_phi(prompt, model_path=body.model, max_tokens=body.max_tokens)
    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": output},
            }
        ]
    }


if __name__ == "__main__":  # pragma: no cover - manual
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
