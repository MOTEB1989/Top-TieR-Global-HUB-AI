from fastapi import FastAPI

app = FastAPI(title="Core Service", version="1.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "core"}

@app.get("/")
def root():
    return {"message": "Core service running successfully"}
