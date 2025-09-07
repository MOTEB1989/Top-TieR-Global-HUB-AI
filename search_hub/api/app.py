from fastapi import FastAPI
from pydantic import BaseModel
from search_hub.gpt_client import query_gpt

app = FastAPI(title="Open Search Hub", version="0.1.0")

class GPTRequest(BaseModel):
    prompt: str

class GPTResponse(BaseModel):
    response: str

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/gpt", response_model=GPTResponse)
def interact_with_gpt(request: GPTRequest):
    reply = query_gpt(request.prompt)
    return GPTResponse(response=reply)