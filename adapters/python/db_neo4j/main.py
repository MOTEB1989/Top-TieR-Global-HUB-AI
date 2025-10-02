from fastapi import FastAPI
from neo4j import GraphDatabase
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

app = FastAPI(title="LexCode Neo4j Service")


@app.get("/health")
def health():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as ok")
            record = result.single()
            return {"status": "ok", "db": "neo4j", "result": record["ok"] if record else None}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/add")
def add_node(label: str, name: str):
    with driver.session() as session:
        session.run(f"CREATE (n:{label} {{name:$name}})", name=name)
    return {"added": {"label": label, "name": name}}
