from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import database

app = FastAPI(title="LexCode PostgreSQL Service")


@app.get("/health")
def health():
    return {"status": "ok", "db": "postgres"}


@app.get("/test")
def test_conn(db: Session = Depends(database.SessionLocal)):
    try:
        db.connection()
        return {"connection": "ok"}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
