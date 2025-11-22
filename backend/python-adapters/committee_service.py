#!/usr/bin/env python3
"""
committee_service.py

Unified demo service for handling Expert Committee (Council of Ministers) documents:
- Ingestion (PDF/HTML → JSON)
- Storage in Postgres
- RAG search
- Reference guard
- Decision engine
- FastAPI endpoints
"""

import os
import json
import hashlib
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import Json
from fastapi import FastAPI, Query

# ==========
# إعداد الاتصال بقاعدة البيانات
# ==========
DB_URL = os.getenv("DB_URL", "postgresql://postgres:motebai@postgres:5432/motebai")


def db_conn():
    return psycopg2.connect(DB_URL)


# ==========
# 1) Ingestion
# ==========
def sha1_of_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def ingest_committee_document(title: str, content: str, source_url: Optional[str] = None) -> int:
    """Save committee document into Postgres rag.documents + rag.chunks"""
    with db_conn() as conn, conn.cursor() as cur:
        sha1 = sha1_of_text(content)
        cur.execute(
            """
            INSERT INTO rag.documents(title, source_url, text_sha1, lang, ingested_at, meta)
            VALUES (%s, %s, %s, 'ar', now(), %s)
            RETURNING id
            """,
            (title, source_url, sha1, json.dumps({"source": "committee"})),
        )
        doc_id = cur.fetchone()[0]

        # split content into chunks (simplified: every 500 chars)
        for i in range(0, len(content), 500):
            chunk = content[i : i + 500]
            cur.execute(
                """
                INSERT INTO rag.chunks(document_id, chunk_no, content, meta)
                VALUES (%s, %s, %s, %s)
                """,
                (doc_id, i // 500, chunk, json.dumps({"len": len(chunk)})),
            )
        conn.commit()
    return doc_id


# ==========
# 2) RAG basic retrieval
# ==========
def rag_query(keyword: str) -> List[Dict[str, Any]]:
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT d.id, d.title, c.content
            FROM rag.documents d
            JOIN rag.chunks c ON d.id = c.document_id
            WHERE c.content ILIKE %s
            LIMIT 5
            """,
            (f"%{keyword}%",),
        )
        rows = cur.fetchall()
    return [{"doc_id": r[0], "title": r[1], "snippet": r[2]} for r in rows]


# ==========
# 3) Reference Guard
# ==========
def reference_guard(answer: str, refs: List[Dict[str, Any]]) -> str:
    if not refs:
        return "⚠️ لا يوجد مرجع من لجنة الخبراء لهذا الجواب."
    return answer + "\n\nالمراجع:\n" + "\n".join([
        f"- {r['title']} (#{r['doc_id']})" for r in refs
    ])


# ==========
# 4) Decision Engine (تجريبي)
# ==========
def apply_rule(transaction: Dict[str, Any]) -> Dict[str, Any]:
    # مثال تجريبي: إذا المبلغ > 500000 أضف إنذار
    alerts = []
    if transaction.get("amount", 0) > 500_000:
        alerts.append({"rule": "AML-HIGH-AMOUNT", "severity": "high"})
    return {"transaction": transaction, "alerts": alerts}


# ==========
# 5) FastAPI endpoints
# ==========
app = FastAPI(title="Expert Committee Service")


@app.post("/bootstrap")
def bootstrap_example():
    """Endpoint to insert a sample document with two chunks for bootstrap testing."""
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO rag.documents (title, source_url, lang, meta)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            ("وثيقة تجريبية", "http://example.com/test", "ar", Json({"bootstrap": True})),
        )
        doc_id = cur.fetchone()[0]

        chunks = [
            (doc_id, 1, "هذا محتوى الفقرة الأولى.", {"note": "اختبار"}),
            (doc_id, 2, "هذا محتوى الفقرة الثانية.", {"note": "اختبار"}),
        ]
        for chunk_doc_id, chunk_no, content, meta in chunks:
            cur.execute(
                """
                INSERT INTO rag.chunks (document_id, chunk_no, content, meta)
                VALUES (%s, %s, %s, %s)
                """,
                (chunk_doc_id, chunk_no, content, Json(meta)),
            )

        conn.commit()

    return {"message": "✅ تم إدخال وثيقة تجريبية مع قطعها", "document_id": doc_id}


@app.post("/v1/ingest")
def api_ingest(title: str, content: str, source_url: Optional[str] = None):
    doc_id = ingest_committee_document(title, content, source_url)
    return {"status": "ok", "doc_id": doc_id}


@app.get("/v1/rag/query")
def api_rag_query(q: str = Query(..., description="Keyword to search in committee docs")):
    refs = rag_query(q)
    answer = f"وجدت {len(refs)} مقطع يحتوي على '{q}'."
    return {"answer": reference_guard(answer, refs), "refs": refs}


@app.post("/v1/decision/apply")
def api_apply_decision(transaction: Dict[str, Any]):
    return apply_rule(transaction)
