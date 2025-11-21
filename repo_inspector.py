#!/usr/bin/env python3
"""
Top-TieR-Global-HUB-AI – Repository Inspector
يفحص المستودع فحصاً كاملاً ويخرج تقرير JSON للهندسة والبنية والأمان.
"""

import os
import json
import hashlib
from pathlib import Path

ROOT = Path(".").resolve()

# -------------------------
# مساعدات عامة
# -------------------------
def file_hash(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def read_text(path, max_len=3000):
    try:
        text = path.read_text(errors="ignore")
        return text[:max_len]
    except:
        return None

# -------------------------
# فحص الملفات
# -------------------------
def scan_files():
    files = []
    for p in ROOT.rglob("*"):
        if p.is_file():
            entry = {
                "path": str(p.relative_to(ROOT)),
                "size_bytes": p.stat().st_size,
                "extension": p.suffix.lower(),
                "hash": file_hash(p),
            }
            files.append(entry)
    return files

# -------------------------
# كشف الملفات الحساسة
# -------------------------
SENSITIVE_EXT = [".env", ".env.prod", ".key", ".pem", ".crt", ".secret"]
SENSITIVE_NAMES = ["secrets", "config", "password", "token", "apikey"]

def find_sensitive_files():
    danger = []
    for p in ROOT.rglob("*"):
        if p.is_file():
            name = p.name.lower()
            if any(name.endswith(ext) for ext in SENSITIVE_EXT) or \
               any(key in name for key in SENSITIVE_NAMES):
                danger.append(str(p))
    return danger

# -------------------------
# فحص Docker
# -------------------------
def inspect_docker():
    dockerfiles = [str(p) for p in ROOT.rglob("Dockerfile")]
    compose_files = [str(p) for p in ROOT.rglob("docker-compose.yml")]
    return {
        "dockerfiles": dockerfiles,
        "compose": compose_files,
        "dockerfile_samples": {f: read_text(Path(f)) for f in dockerfiles},
        "compose_samples": {f: read_text(Path(f)) for f in compose_files},
    }

# -------------------------
# فحص GitHub Actions
# -------------------------
def inspect_actions():
    actions_root = ROOT / ".github" / "workflows"
    if not actions_root.exists():
        return {}
    workflows = {}
    for p in actions_root.glob("*.yml"):
        workflows[p.name] = read_text(p)
    return workflows

# -------------------------
# فحص Dependecies
# -------------------------
def inspect_dependencies():
    deps = {}

    # Python
    req = ROOT / "requirements.txt"
    if req.exists():
        deps["python"] = req.read_text(errors="ignore")

    # Rust
    cargo = ROOT / "Cargo.toml"
    if cargo.exists():
        deps["rust"] = cargo.read_text(errors="ignore")

    # Node.js
    pkg = ROOT / "package.json"
    if pkg.exists():
        deps["node"] = pkg.read_text(errors="ignore")

    return deps

# -------------------------
# فحص SQL / RLS
# -------------------------
def inspect_sql():
    sql_files = [p for p in ROOT.rglob("*.sql")]
    sql_data = {}
    for p in sql_files:
        sql_data[str(p)] = read_text(p)
    return sql_data

# -------------------------
# أعلى 20 ملف حجماً
# -------------------------
def largest_files(files, limit=20):
    sorted_files = sorted(files, key=lambda f: f["size_bytes"], reverse=True)
    return sorted_files[:limit]

# -------------------------
# التقرير النهائي
# -------------------------
if __name__ == "__main__":
    files = scan_files()

    report = {
        "root": str(ROOT),
        "total_files": len(files),
        "languages_detected": list({f["extension"] for f in files}),
        "files": files,
        "largest_files": largest_files(files),
        "sensitive_files": find_sensitive_files(),
        "docker": inspect_docker(),
        "github_actions": inspect_actions(),
        "dependencies": inspect_dependencies(),
        "sql": inspect_sql(),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
