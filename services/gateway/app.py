import os
from fastapi import FastAPI

app = FastAPI(title="Gateway Stub")


@app.get("/")
async def read_root():
    return {
        "service": "gateway",
        "message": "Stub gateway for routing requests in local development",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8002"))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
