import os
from fastapi import FastAPI

app = FastAPI(title="RAG Engine Stub")


@app.get("/")
async def read_root():
    return {
        "service": "rag_engine",
        "message": "Placeholder implementation for local RAG stack",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
