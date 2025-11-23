from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Phi-3 Local Runner", version="0.1.0")


class InferRequest(BaseModel):
    prompt: str


class InferResponse(BaseModel):
    output: str


@app.get("/health", response_model=dict)
def health() -> dict:
    return {"status": "ok"}


@app.post("/infer", response_model=InferResponse)
def infer(request: InferRequest) -> InferResponse:
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")
    return InferResponse(output=f"Mock response for prompt: {request.prompt}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("phi_server:app", host="0.0.0.0", port=8082, reload=False)
