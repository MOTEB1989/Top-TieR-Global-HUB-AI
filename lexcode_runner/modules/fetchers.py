import os

import psycopg2
import requests


def handle_fetch(config):
    source = config.get("source")

    if source == "postgres":
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            dbname=os.getenv("PG_DB", "postgres"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "postgres"),
            port=int(os.getenv("PG_PORT", "5432")),
        )
        cur = conn.cursor()
        cur.execute(config["query"])
        rows = cur.fetchall()
        cur.close()
        conn.close()
        print(f"📥 Fetched {len(rows)} rows from Postgres")
        return rows

    if source == "opensearch":
        base = os.getenv("OPENSEARCH_URL", "http://localhost:9200").rstrip("/")
        index = config["index"]
        url = f"{base}/{index}/_search"
        query = config.get("query", "")
        query_body = {"query": {"match": {"_all": query}}} if query else {"query": {"match_all": {}}}
        resp = requests.get(url, json=query_body)
        resp.raise_for_status()
        docs = resp.json()
        hits = docs.get("hits", {}).get("hits", [])
        print(f"📥 Fetched {len(hits)} docs from OpenSearch index={index}")
        return hits

    if source == "github.repo":
        path = config.get("path", "")
        repo = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")
        token = os.getenv("LEXCODE_GITHUB_TOKEN")
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}"} if token else {}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        files = resp.json()
        print(f"📥 Fetched {len(files)} files from GitHub repo {repo}/{path}")
        return files

    print(f"⚠️ Unknown fetch source: {source}")
    return None
