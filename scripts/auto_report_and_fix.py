#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_report_and_fix.py (Hybrid Mode)

المهمة:
- قراءة سياق فشل Workflow من بيئة GitHub Actions.
- معرفة هل الفشل بسبب Lint/Test أو Build/Infra.
- إنشاء تقرير Markdown مختصر.
- إرساله إما كتعليق على PR (إن وجد) أو إنشاء Issue.
- تضمين "Prompt جاهز" لـ Codex/Copilot لمحاولة الإصلاح.

المتطلبات:
- متغير بيئة GITHUB_TOKEN (يوفره GitHub Actions تلقائياً).
- يجب تشغيل السكربت من داخل Workflow بعد اكتمال Run (يفضل من workflow_run أو من Job مخصص للفشل).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple

import requests

GITHUB_API = "https://api.github.com"


def github_request(method: str, url: str, token: str, **kwargs: Any) -> Any:
    headers = kwargs.pop("headers", {})
    headers.setdefault("Authorization", f"Bearer {token}")
    headers.setdefault("Accept", "application/vnd.github+json")
    resp = requests.request(method, url, headers=headers, timeout=20, **kwargs)
    resp.raise_for_status()
    if resp.content:
        try:
            return resp.json()
        except Exception:
            return resp.text
    return None


def classify_failure(workflow_name: str, job_names: List[str]) -> Literal["AUTO_FIX_SUGGESTED", "REPORT_ONLY"]:
    name_lower = workflow_name.lower()
    jobs_lower = " ".join(job_names).lower()
    hints = name_lower + " " + jobs_lower

    lint_keywords = ["lint", "flake8", "eslint", "ruff", "mypy", "clippy", "fmt", "format"]
    test_keywords = ["pytest", "unittest", "test", "coverage"]

    if any(k in hints for k in lint_keywords + test_keywords):
        return "AUTO_FIX_SUGGESTED"
    return "REPORT_ONLY"


def build_prompt_for_codex(
    owner: str,
    repo: str,
    run_id: int,
    workflow_name: str,
    job_names: List[str],
    failure_mode: Literal["AUTO_FIX_SUGGESTED", "REPORT_ONLY"],
    logs_url: str | None,
) -> str:
    """
    يبني Prompt جاهز لـ Codex يمكن نسخه واستخدامه لاحقاً.
    """
    lines: List[str] = []
    lines.append("Codex, open the repository:")
    lines.append("")
    lines.append(f"{owner}/{repo}")
    lines.append("")
    lines.append("and help diagnose and fix the failing GitHub Actions workflow.")
    lines.append("")
    lines.append(f"- Workflow name: {workflow_name}")
    lines.append(f"- Run ID: {run_id}")
    lines.append(f"- Failure mode: {failure_mode}")
    lines.append(f"- Jobs involved: {', '.join(job_names) or 'unknown'}")
    if logs_url:
        lines.append(f"- Logs URL (GitHub): {logs_url}")
    lines.append("")
    if failure_mode == "AUTO_FIX_SUGGESTED":
        lines.append("Goal:")
        lines.append("- Identify the root cause of the Lint/Test failure.")
        lines.append("- Propose and apply code changes to fix the issues.")
        lines.append("- Keep changes minimal and localized.")
    else:
        lines.append("Goal:")
        lines.append("- Analyze the build/infra failure.")
        lines.append("- Propose safe, step-by-step remediation.")
        lines.append("- Do NOT make destructive infra changes.")
    lines.append("")
    lines.append("Deliverables:")
    lines.append("- A single diff (patch) that fixes the failure.")
    lines.append("- A short explanation of what changed and why.")
    return "\n".join(lines)


def create_issue(owner: str, repo: str, token: str, title: str, body: str) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    data = {"title": title, "body": body}
    res = github_request("POST", url, token, json=data)
    return res.get("html_url", "") if isinstance(res, dict) else ""


def create_pr_comment(owner: str, repo: str, token: str, pr_number: int, body: str) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    data = {"body": body}
    res = github_request("POST", url, token, json=data)
    return res.get("html_url", "") if isinstance(res, dict) else ""


def load_event_payload() -> Dict[str, Any]:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).is_file():
        raise RuntimeError("GITHUB_EVENT_PATH is not set or file does not exist.")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def extract_run_context(event_name: str, payload: Dict[str, Any]) -> Tuple[int, str | None, List[str], str | None, int | None]:
    pr_number: int | None = None
    logs_url: str | None = None
    job_names: List[str] = []
    html_url: str | None = None
    run_id: int = 0

    if event_name == "workflow_run":
        wr = payload.get("workflow_run", {})
        run_id = wr.get("id", 0)
        logs_url = wr.get("logs_url")
        html_url = wr.get("html_url")
        pull_requests = wr.get("pull_requests", [])
        if pull_requests:
            pr_number = pull_requests[0].get("number")
    elif event_name == "pull_request":
        pr_number = payload.get("number")
    return run_id, logs_url, job_names, html_url, pr_number


def fetch_jobs(owner: str, repo: str, run_id: int, token: str) -> List[Dict[str, Any]]:
    if not run_id:
        return []
    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    data = github_request("GET", url, token)
    if isinstance(data, dict):
        return data.get("jobs", []) or []
    return []


def summarize_failing_jobs(jobs: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    failing_job_names: List[str] = []
    failing_summaries: List[str] = []
    for job in jobs:
        conclusion = job.get("conclusion")
        if conclusion == "success":
            continue
        job_name = job.get("name", "unknown")
        failing_job_names.append(job_name)
        failure_message = job.get("failure_message") or ""  # type: ignore[arg-type]

        failing_steps = [step for step in job.get("steps", []) if step.get("conclusion") not in {"success", None}]
        if failing_steps:
            step_names = ", ".join(step.get("name", "(unnamed)") for step in failing_steps)
            failure_message = failure_message or f"خطوات فاشلة: {step_names}"

        summary_line = f"- `{job_name}` → النتيجة: **{conclusion or 'unknown'}**"
        if failure_message:
            summary_line += f" — {failure_message}"
        failing_summaries.append(summary_line)
    return failing_job_names, failing_summaries


def main() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN is missing.")
        sys.exit(1)

    repo_full = os.getenv("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        print("❌ GITHUB_REPOSITORY is invalid.")
        sys.exit(1)
    owner, repo = repo_full.split("/", 1)

    workflow_name = os.getenv("GITHUB_WORKFLOW", "unknown-workflow")
    run_id_str = os.getenv("GITHUB_RUN_ID", "0")
    try:
        run_id = int(run_id_str)
    except ValueError:
        run_id = 0

    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    try:
        payload = load_event_payload()
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Failed to load event payload: {exc!r}")
        sys.exit(1)

    run_id_from_event, logs_url, job_names, html_url, pr_number = extract_run_context(event_name, payload)
    if run_id_from_event:
        run_id = run_id_from_event

    try:
        jobs = fetch_jobs(owner, repo, run_id, token)
        failing_job_names, failing_summaries = summarize_failing_jobs(jobs)
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️ Failed to fetch job names: {exc!r}")
        failing_job_names, failing_summaries = [], []

    # fallback to any job names we already have
    if not failing_job_names and job_names:
        failing_job_names = job_names

    failure_mode = classify_failure(workflow_name, failing_job_names)
    codex_prompt = build_prompt_for_codex(
        owner=owner,
        repo=repo,
        run_id=run_id,
        workflow_name=workflow_name,
        job_names=failing_job_names,
        failure_mode=failure_mode,
        logs_url=logs_url,
    )

    lines: List[str] = []
    lines.append(f"## ⚠️ Auto-Report: فشل في Workflow `{workflow_name}`")
    lines.append("")
    lines.append(f"- المستودع: `{owner}/{repo}`")
    lines.append(f"- رقم التشغيل (Run ID): `{run_id}`")
    lines.append(f"- نمط الفشل (Hybrid Mode): `{failure_mode}`")
    if failing_job_names:
        lines.append(f"- الوظائف المتأثرة (Jobs): {', '.join(failing_job_names)}")
    if logs_url:
        lines.append(f"- رابط السجلات (Logs): {logs_url}")
    if html_url:
        lines.append(f"- رابط التشغيل (Run): {html_url}")
    lines.append("")

    if failing_summaries:
        lines.append("### TL;DR / Summary")
        lines.extend(failing_summaries)
        lines.append("")

    lines.append("### 🎯 التعليمات المقترحة لـ Codex / Copilot")
    lines.append("")
    lines.append("```text")
    lines.append(codex_prompt)
    lines.append("```")
    lines.append("")
    if failure_mode == "AUTO_FIX_SUGGESTED":
        lines.append(
            "> ملاحظة: تم تصنيف هذا الفشل كـ **AUTO_FIX_SUGGESTED** (Lint/Test) ويمكن محاولة الإصلاح الآلي بأمان نسبي."
        )
    else:
        lines.append(
            "> ملاحظة: تم تصنيف هذا الفشل كـ **REPORT_ONLY** (Build/Infra/Security) ويفضل مراجعة بشرية مع مساعدة Codex."
        )

    body = "\n".join(lines)

    try:
        if pr_number:
            url = create_pr_comment(owner, repo, token, pr_number, body)
            print(f"✅ تم إنشاء تعليق على PR #{pr_number}: {url}")
        else:
            issue_title = f"Auto-Report: فشل في Workflow {workflow_name}"
            url = create_issue(owner, repo, token, issue_title, body)
            print(f"✅ تم إنشاء Issue للتتبع: {url}")
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Failed to publish report: {exc!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
