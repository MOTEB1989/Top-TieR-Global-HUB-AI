#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hybrid System Health Checker + Codex Notifier

Functions:
1) Check Docker Compose services.
2) Check .env presence and list non-comment keys.
3) Check health endpoints for core services (Rust / API Gateway / Streamlit).
4) Check basic integrations (OpenAI, Groq, Anthropic, Neo4j, Qdrant).
5) Build a Markdown report.
6) If running inside GitHub Actions, post the report as a PR comment or Issue,
   including a ready-to-use prompt for Codex to generate fixes.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import List

import requests

GITHUB_API = "https://api.github.com"


def run(cmd: List[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.stdout
    except Exception as e:  # noqa: BLE001
        return f"ERROR: {e}"


def check_docker_services() -> str:
    return run(["docker", "compose", "ps"])


def check_env_file() -> str:
    env_path = Path(".env")
    if not env_path.exists():
        return "❌ ملف .env غير موجود"
    content = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    keys = [line for line in content if line.strip() and not line.strip().startswith("#")]
    if not keys:
        return "⚠️ .env موجود لكن بدون مفاتيح واضحة"
    joined = "\n".join(f"- {k}" for k in keys)
    return "✅ تم العثور على .env بالمفاتيح التالية:\n" + joined


def check_url(name: str, url: str) -> str:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return f"✅ {name} يعمل — {url}"
        return f"⚠️ {name} استجاب بكود HTTP={r.status_code} — {url}"
    except Exception as e:  # noqa: BLE001
        return f"❌ {name} غير متاح: {e} — {url}"


def check_integrations() -> str:
    integrations = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Groq": os.getenv("GROQ_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Neo4j": os.getenv("NEO4J_URI"),
        "Qdrant": os.getenv("QDRANT_URL"),
    }
    lines: List[str] = []
    for name, key in integrations.items():
        if key:
            lines.append(f"✅ {name} integration configured")
        else:
            lines.append(f"⚠️ {name} integration NOT configured")
    return "\n".join(lines)


def build_markdown_report() -> str:
    md: List[str] = []
    md.append("# 🧪 System Health Diagnostic Report\n")

    md.append("## 🔧 Docker Services\n")
    md.append("```")
    md.append(check_docker_services().strip() or "(no output)")
    md.append("```")

    md.append("\n## 🔐 Environment (.env)\n")
    md.append(check_env_file())

    md.append("\n## 🧩 Services\n")
    md.append(check_url("Rust Core", "http://localhost:8080/health"))
    md.append(check_url("API Gateway", "http://localhost:3000/health"))
    md.append(check_url("Streamlit Web UI", "http://localhost:8501"))

    md.append("\n## 🌐 Integrations\n")
    md.append(check_integrations())

    return "\n".join(md)


def notify_codex_if_ci(report_md: str) -> None:
    """Post the report as a PR comment or Issue in GitHub if GITHUB_TOKEN is set."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Not running in GitHub Actions (GITHUB_TOKEN missing) — skipping Codex notification.")
        return

    repo_full = os.getenv("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        print("GITHUB_REPOSITORY is malformed, cannot notify Codex.")
        return
    owner, repo = repo_full.split("/", 1)

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        print("GITHUB_EVENT_PATH missing, cannot inspect event.")
        return
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))

    pr_number = event.get("pull_request", {}).get("number")

    prompt = f"""
Codex, open the repository:

{owner}/{repo}

and diagnose the system health issues found in the automated diagnostic report below.

Report (Markdown):
{report_md}

Goals:
- Identify likely root causes.
- Suggest concrete remediation steps (commands, config edits).
- Optionally propose a patch as a unified diff.
"""

    body = (
        "## 🤖 System Health Check\n"
        "### 📄 التقرير الآلي:\n\n"
        + report_md
        + "\n\n---\n"
        "### 🧠 تعليمات مقترحة لـ Codex:\n"
        f"```text\n{prompt}\n```"
    )

    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github+json"}

    if pr_number:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        data = {"body": body}
        requests.post(url, headers=headers, json=data, timeout=10)
        print("Posted health report as PR comment.")
    else:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
        data = {"title": "System Health Diagnostic Report", "body": body}
        requests.post(url, headers=headers, json=data, timeout=10)
        print("Posted health report as new Issue.")


def main() -> None:
    report = build_markdown_report()
    print(report)
    notify_codex_if_ci(report)


if __name__ == "__main__":
    main()

