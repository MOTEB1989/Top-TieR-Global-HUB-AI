from fastapi import FastAPI
from clickhouse_driver import Client
import os

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))

client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT)

app = FastAPI(title="LexCode ClickHouse Service")


@app.get("/health")
def health():
    try:
        version = client.execute("SELECT version()")
        version_value = version[0][0] if version else None
        return {"status": "ok", "db": "clickhouse", "version": version_value}
    except Exception as exc:
        return {"error": str(exc)}
