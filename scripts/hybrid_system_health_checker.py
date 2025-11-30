#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hybrid System Health Checker + Codex Notifier
---------------------------------------------
يقوم بما يلي:

1) فحص Docker Compose والخدمات الأساسية.
2) فحص مفاتيح البيئة والتكاملات.
3) فحص نقاط الصحة Rust/API/Streamlit.
4) بناء تقرير Markdown.
5) إذا تم تشغيله داخل GitHub Actions → يخاطب Codex تلقائياً:
   - يفتح تعليق على PR أو Issue
   - يرفق تقرير
   - يرفق Prompt جاهز لطلب إصلاح من Codex.

يعمل محليًا + داخل CI بنفس الوقت.
"""

import json
import os
import subprocess
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com"


def run(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:  # pragma: no cover - defensive guard for subprocess
        return f"ERROR: {e}"


def check_docker_services():
    return run(["docker", "compose", "ps"])


def check_env_file():
    env_path = Path(".env")
    if not env_path.exists():
        return "❌ ملف .env غير موجود"
    content = env_path.read_text().strip().splitlines()
    keys = [line for line in content if line.strip() and not line.startswith("#")]
    return "Found keys:\n" + "\n".join(f"- {k}" for k in keys)


def check_url(name, url):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return f"✅ {name} يعمل — {url}"
        return f"⚠️ {name} استجاب بكود: {response.status_code}"
    except Exception as e:  # pragma: no cover - external call
        return f"❌ {name} غير متاح: {e}"


def check_integrations():
    integrations = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Groq": os.getenv("GROQ_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Neo4j": os.getenv("NEO4J_URI"),
        "Qdrant": os.getenv("QDRANT_URL"),
    }
    lines = []
    for name, key in integrations.items():
        if key:
            lines.append(f"✅ {name} جاهز")
        else:
            lines.append(f"⚠️ {name} غير مهيأ")
    return "\n".join(lines)


def build_markdown_report():
    report_lines = ["# 🧪 System Health Diagnostic Report\n"]

    report_lines.append("## 🔧 Docker Services\n")
    report_lines.append("```\n" + check_docker_services() + "\n```")

    report_lines.append("\n## 🔐 Environment (.env)\n")
    report_lines.append(check_env_file())

    report_lines.append("\n## 🧩 Services\n")
    report_lines.append(check_url("Rust Core", "http://localhost:8080/health"))
    report_lines.append(check_url("API Gateway", "http://localhost:3000/health"))
    report_lines.append(check_url("Streamlit", "http://localhost:8501"))

    report_lines.append("\n## 🌐 Integrations\n")
    report_lines.append(check_integrations())

    return "\n".join(report_lines)


def notify_codex_if_ci(report_md: str):
    """إنشاء تعليق أو Issue حسب بيئة GitHub Actions تلقائياً."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Not running in CI — skipping Codex notification.")
        return

    repo_full = os.getenv("GITHUB_REPOSITORY", "")
    if not repo_full or "/" not in repo_full:
        print("GITHUB_REPOSITORY is not set; cannot post report.")
        return

    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        print("GITHUB_EVENT_PATH is not available; cannot determine PR number.")
        return

    owner, repo = repo_full.split("/", 1)
    event = json.loads(Path(event_path).read_text())

    pr_number = event.get("pull_request", {}).get("number")

    prompt = f"""
Codex, open the repository:

{owner}/{repo}

and diagnose the system health issues found in the automated diagnostic report.

Report:
{report_md}

Goal:
- Identify root cause
- Provide fixes
- Generate a patch (unified diff)
"""

    body = (
        "## 🤖 System Health Check\n"
        "### 📄 التقرير الآلي:\n\n"
        + report_md
        + "\n\n---\n"
        "### 🧠 تعليمات لـ Codex:\n"
        f"```\n{prompt}\n```"
    )

    headers = {"Authorization": f"Bearer {github_token}"}

    if pr_number:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        data = {"body": body}
        requests.post(url, headers=headers, json=data, timeout=10)
        print("Posted report as PR comment.")
    else:
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
        data = {"title": "System Health Diagnostic Report", "body": body}
        requests.post(url, headers=headers, json=data, timeout=10)
        print("Posted report as new Issue.")


if __name__ == "__main__":
    report = build_markdown_report()
    print(report)
    notify_codex_if_ci(report)
