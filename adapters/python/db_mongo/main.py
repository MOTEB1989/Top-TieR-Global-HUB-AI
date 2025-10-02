import os

from fastapi import FastAPI
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = MongoClient(MONGO_URL)
db = client["lexcode"]

app = FastAPI(title="LexCode MongoDB Service")


@app.get("/health")
def health():
    try:
        db.list_collection_names()
        return {"status": "ok", "db": "mongo"}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


@app.post("/documents/")
def add_document(doc: dict):
    result = db.documents.insert_one(doc)
    return {"inserted_id": str(result.inserted_id)}


@app.get("/documents/")
def list_documents():
    return list(db.documents.find({}, {"_id": 0}))
