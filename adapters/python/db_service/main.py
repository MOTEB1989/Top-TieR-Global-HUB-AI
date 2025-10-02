from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from . import models
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LexCode Python DB Service")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "python-db"}


@app.post("/documents/")
def create_document(doc: dict, db: Session = Depends(get_db)):
    """
    doc = { "doc_id": "doc-1", "text": "...", "embedding": [0.1, 0.2, ...] }
    """
    db_doc = models.Document(
        doc_id=doc["doc_id"],
        text=doc["text"],
        embedding=json.dumps(doc.get("embedding", []))
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return {"id": db_doc.id, "doc_id": db_doc.doc_id}


@app.get("/documents/{doc_id}")
def get_document(doc_id: str, db: Session = Depends(get_db)):
    db_doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": db_doc.id,
        "doc_id": db_doc.doc_id,
        "text": db_doc.text,
        "embedding": json.loads(db_doc.embedding)
    }


@app.get("/documents/")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).all()
    return [
        {
            "id": d.id,
            "doc_id": d.doc_id,
            "text": d.text,
            "embedding": json.loads(d.embedding)
        }
        for d in docs
    ]
