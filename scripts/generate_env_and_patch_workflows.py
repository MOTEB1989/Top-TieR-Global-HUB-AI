#!/usr/bin/env python3
"""
Script for Codex:
- Generates a .env.example file with all required environment variables.
- Patches all GitHub workflows in .github/workflows/ to inject secrets automatically.
- Updates docker-compose.yml to use env variables.
- Appends an "Environment Setup" section in README.md if not present.
"""

import os
import re
import yaml
from pathlib import Path

# --- Step 1: Generate .env.example ---
env_vars = {
    "OPENAI_API_KEY": "sk-...",
    "DB_URL": "postgresql://postgres:motebai@postgres:5432/motebai",
    "OPENSEARCH_URL": "http://opensearch:9200",
    "MINIO_ENDPOINT": "http://minio:9000",
    "MINIO_ROOT_USER": "motebai",
    "MINIO_ROOT_PASSWORD": "motebai123",
    "REDIS_URL": "redis://redis:6379",
    "NEO4J_URI": "bolt://neo4j:7687",
    "NEO4J_AUTH": "neo4j/motebai",
    "CLICKHOUSE_URL": "http://clickhouse:8123",
}

env_file = Path(".env.example")
with env_file.open("w") as f:
    for k, v in env_vars.items():
        f.write(f"{k}={v}\n")
print("✅ Generated .env.example")

# --- Step 2: Patch workflows ---
wf_dir = Path(".github/workflows")
if wf_dir.exists():
    for wf in wf_dir.glob("*.yml"):
        data = yaml.safe_load(wf.read_text())
        # inject env if not present
        if "env" not in data:
            data["env"] = {}
        for k in env_vars:
            data["env"][k] = f"${{{{ secrets.{k} }}}}"
        wf.write_text(yaml.dump(data, sort_keys=False))
        print(f"🔧 Patched workflow: {wf.name}")

# --- Step 3: Patch docker-compose.yml ---
dc_file = Path("docker-compose.yml")
if dc_file.exists():
    content = dc_file.read_text()
    for k in env_vars:
        if k in content:
            continue
        # replace hardcoded values
        content = re.sub(r"(motebai123|motebai|postgres|neo4j/motebai)", f"${{{k}}}", content)
    dc_file.write_text(content)
    print("🔧 Patched docker-compose.yml")

# --- Step 4: Update README.md ---
readme = Path("README.md")
section = """
## 🔑 Environment Setup

1. Copy `.env.example` → `.env`
2. Fill in real values (keys, URLs, passwords).
3. Add them into GitHub Secrets with the same names.
4. Docker Compose and GitHub Actions will automatically pick them up.
"""
if readme.exists():
    text = readme.read_text()
    if "Environment Setup" not in text:
        with readme.open("a") as f:
            f.write(section)
        print("📖 Updated README.md")
