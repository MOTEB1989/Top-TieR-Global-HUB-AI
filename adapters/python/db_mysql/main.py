from fastapi import FastAPI, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from . import database

app = FastAPI(title="LexCode MySQL Service")


@app.get("/health")
def health(db: Session = Depends(database.SessionLocal)):
    try:
        _ = db.connection()
        return {"status": "ok", "db": "mysql"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/sql")
def run_sql(payload: dict = Body(...), db: Session = Depends(database.SessionLocal)):
    sql = payload.get("sql", "")
    params = payload.get("params", [])
    if not sql:
        raise HTTPException(status_code=400, detail="sql required")
    try:
        result = db.execute(sql, params)
        if sql.strip().lower().startswith("select"):
            rows = [dict(r._mapping) for r in result.fetchall()]
            columns = list(rows[0].keys()) if rows else []
            return {"rows": rows, "columns": columns}
        else:
            db.commit()
            return {"rows": [], "columns": [], "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
