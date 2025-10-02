from fastapi import FastAPI
import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
client = redis.Redis.from_url(REDIS_URL)

app = FastAPI(title="LexCode Redis Service")


@app.get("/health")
def health():
    try:
        pong = client.ping()
        return {"status": "ok", "db": "redis", "ping": pong}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/set/{key}")
def set_key(key: str, value: str):
    client.set(key, value)
    return {"key": key, "value": value}


@app.get("/get/{key}")
def get_key(key: str):
    val = client.get(key)
    return {"key": key, "value": val.decode() if isinstance(val, bytes) else None}
