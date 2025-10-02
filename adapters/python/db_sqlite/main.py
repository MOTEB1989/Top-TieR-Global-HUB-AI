from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import database, models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="LexCode SQLite Service")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "db": "sqlite"}


@app.post("/documents/")
def create_document(doc: dict, db: Session = Depends(get_db)):
    db_doc = models.Document(doc_id=doc["doc_id"], text=doc["text"])
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"id": db_doc.id, "doc_id": db_doc.doc_id}


@app.get("/documents/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db)):
    db_doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"doc_id": db_doc.doc_id, "text": db_doc.text}
