import os

import psycopg2
import requests


def handle_fetch(config):
    source = config.get("source")

    if source == "postgres":
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            dbname=os.getenv("PG_DB", "test"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "postgres"),
        )
        cur = conn.cursor()
        cur.execute(config["query"])
        rows = cur.fetchall()
        conn.close()
        print(f"📥 Fetched {len(rows)} rows from Postgres")
        return rows

    if source == "opensearch":
        url = f"http://localhost:9200/{config['index']}/_search"
        resp = requests.get(url, json={"query": {"match": {"_all": config["query"]}}})
        resp.raise_for_status()
        docs = resp.json()
        print(f"📥 Fetched {len(docs.get('hits', {}).get('hits', []))} docs from OpenSearch")
        return docs

    if source == "github.repo":
        path = config.get("path", "")
        repo = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")
        token = os.getenv("LEXCODE_GITHUB_TOKEN")
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}"} if token else {}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        files = resp.json()
        if isinstance(files, dict) and files.get("message"):
            raise RuntimeError(f"GitHub API error: {files['message']}")
        print(f"📥 Fetched {len(files)} files from GitHub repo")
        return files

    print(f"⚠️ Unknown fetch source: {source}")
    return None
