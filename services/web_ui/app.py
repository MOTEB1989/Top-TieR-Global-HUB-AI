import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Web UI Stub")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head><title>Web UI Stub</title></head>
        <body>
            <h1>Web UI Placeholder</h1>
            <p>This stub ensures the local RAG stack can start without full frontend assets.</p>
        </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8003"))
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
