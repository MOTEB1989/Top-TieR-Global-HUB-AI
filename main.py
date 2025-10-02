from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

from provider_router import get_provider  # noqa: E402

app = FastAPI(title="Provider-Agnostic Inference Engine")


class InferRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model: Optional[str] = None


@app.post("/v1/ai/infer")
async def infer(request: InferRequest):
    try:
        engine = get_provider(request.provider)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        output = await engine.infer(request.prompt, request.model)
    except Exception as exc:  # pragma: no cover - provider-specific errors
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"output": output}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
