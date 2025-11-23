import os
from fastapi import FastAPI

app = FastAPI(title="Phi-3 Stub Service")


@app.get("/")
async def read_root():
    return {
        "service": "phi3",
        "message": "Placeholder Phi-3 inference endpoint for local testing",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8001"))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
