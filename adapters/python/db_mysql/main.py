from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import database

app = FastAPI(title="LexCode MySQL Service")


@app.get("/health")
def health(db: Session = Depends(database.SessionLocal)):
    try:
        conn = db.connection()
        conn.close()
        return {"status": "ok", "db": "mysql"}
    except Exception as exc:
        return {"error": str(exc)}
