from fastapi import FastAPI, Body, HTTPException
import sqlite3

app = FastAPI(title="LexCode SQLite Service")


@app.get("/health")
def health():
    return {"status": "ok", "db": "sqlite"}


@app.post("/sql")
def run_sql(payload: dict = Body(...)):
    sql = payload.get("sql", "")
    params = payload.get("params", [])
    if not sql:
        raise HTTPException(status_code=400, detail="sql required")

    conn = sqlite3.connect("./lexcode.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        if sql.strip().lower().startswith("select"):
            rows = [dict(r) for r in cur.fetchall()]
            columns = list(rows[0].keys()) if rows else []
            return {"rows": rows, "columns": columns}
        else:
            conn.commit()
            return {"rows": [], "columns": [], "status": "ok"}
    finally:
        cur.close()
        conn.close()
