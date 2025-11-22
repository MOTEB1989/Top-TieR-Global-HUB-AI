#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Health Check for RAG + Gateway + UI
- يتحقق من:
  * وجود وسلامة docker-compose.rag.yml
  * وجود ملف .env وعرض أسماء المفاتيح بدون القيم
  * نقاط الصحة للخدمات الأساسية (Rust/Gateway/RAG/Phi3/Streamlit)
  * تكوين تكاملات OpenAI / Groq / Anthropic / Neo4j / Qdrant
- يعيد كود خروج 0 عند نجاح كل الفحوصات، وغير ذلك 1
- يكتب تقرير JSON في system_health_report.json
"""

import os
import subprocess
import sys
import json
from typing import Tuple
import requests

DOCKER_COMPOSE_FILE = "docker-compose.rag.yml"
REPORT_FILE = "system_health_report.json"

def run_cmd(cmd: list[str]) -> Tuple[str, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError as e:
        return "", f"EXECUTABLE_NOT_FOUND: {e}"
    except Exception as e:
        return "", f"UNEXPECTED_ERROR: {e}"

def check_docker_compose(report: dict) -> bool:
    if not os.path.exists(DOCKER_COMPOSE_FILE):
        report["docker_compose"] = "not_found"
        return False
    out, err = run_cmd(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "config"])
    if err.startswith("EXECUTABLE_NOT_FOUND"):
        report["docker_compose"] = "docker_not_installed"
        return False
    if err:
        report["docker_compose"] = f"config_error: {err}"
        return False
    report["docker_compose"] = "ok"
    return True

def check_env(report: dict) -> bool:
    if not os.path.exists(".env"):
        report["env"] = "not_found"
        return False
    keys = []
    with open(".env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
            else:
                key = line
            keys.append(key)
    if not keys:
        report["env"] = "empty"
        return False
    report["env"] = {"keys": keys}
    return True

def check_service(url: str, name: str, report: dict) -> bool:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            report[name] = "ok"
            return True
        else:
            report[name] = f"status_{r.status_code}"
            return False
    except requests.exceptions.ConnectionError as e:
        report[name] = f"connection_error: {e}"
        return False
    except requests.exceptions.Timeout:
        report[name] = "timeout"
        return False
    except Exception as e:
        report[name] = f"error: {e}"
        return False

def check_integrations(report: dict) -> bool:
    integrations = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Groq": os.getenv("GROQ_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Neo4j": os.getenv("NEO4J_URI"),
        "Qdrant": os.getenv("QDRANT_URL"),
    }
    all_ok = True
    report["integrations"] = {}
    for name, value in integrations.items():
        if value:
            report["integrations"][name] = "configured"
        else:
            report["integrations"][name] = "not_configured"
            all_ok = False
    return all_ok

def main() -> None:
    report = {}
    overall_ok = True

    overall_ok &= check_docker_compose(report)
    overall_ok &= check_env(report)
    overall_ok &= check_service("http://localhost:8080/health", "Rust Core", report)
    overall_ok &= check_service("http://localhost:3000/health", "Gateway", report)
    overall_ok &= check_service("http://localhost:8081/health", "RAG Engine", report)
    overall_ok &= check_service("http://localhost:8082/health", "Phi-3 Local Runner", report)
    overall_ok &= check_service("http://localhost:8501", "Streamlit Web UI", report)
    overall_ok &= check_integrations(report)

    report["summary"] = "ok" if overall_ok else "failed"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Report written to {REPORT_FILE}")
    if overall_ok:
        print("✅ All checks passed (or only minor warnings).")
        sys.exit(0)
    else:
        print("❌ One or more checks failed. See report for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
