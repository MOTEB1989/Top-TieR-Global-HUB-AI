import json
import os
from typing import List

import requests
import yaml


def check_workflows() -> List[str]:
    workflows_path = ".github/workflows"
    results: List[str] = []
    if not os.path.exists(workflows_path):
        return ["⚠️ No workflows directory found."]

    for file in sorted(os.listdir(workflows_path)):
        if file.endswith((".yml", ".yaml")):
            file_path = os.path.join(workflows_path, file)
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    content = yaml.safe_load(handle) or {}
                triggers = content.get("on", {})
                if isinstance(triggers, dict):
                    trigger_list = list(triggers.keys())
                else:
                    trigger_list = ["custom configuration"]
                results.append(f"✅ Workflow: **{file}** → triggers: {trigger_list}")
            except Exception as exc:  # pylint: disable=broad-except
                results.append(f"⚠️ Could not parse {file}: {exc}")

    if not results:
        results.append("ℹ️ No workflow files found.")
    return results


def check_scripts() -> List[str]:
    scripts_path = "scripts"
    if not os.path.exists(scripts_path):
        return ["⚠️ No scripts directory found."]

    expected = ["veritas_health_check.sh"]
    missing = [script for script in expected if not os.path.exists(os.path.join(scripts_path, script))]

    if missing:
        return [f"❌ Missing script: `{script}`" for script in missing]
    return ["✅ All expected scripts found."]


def check_ai_connections() -> List[str]:
    env_files = [".env", ".github/workflows/lexcode-bot.yml"]
    findings: List[str] = []

    for file in env_files:
        if not os.path.exists(file):
            continue
        try:
            with open(file, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            findings.append(f"⚠️ Could not read `{file}`: {exc}")
            continue

        if any(keyword in text for keyword in ("API_KEY", "OPENAI", "HUGGINGFACE")):
            findings.append(f"🔑 Possible AI API keys in `{file}`")

    if not findings:
        findings.append("ℹ️ No AI API keys detected (check manually).")
    return findings


def generate_report() -> str:
    report: List[str] = ["### 🩺 Repository Diagnostics Report", ""]

    report.append("**Workflows:**")
    report.extend(check_workflows())

    report.append("\n**Scripts:**")
    report.extend(check_scripts())

    report.append("\n**AI Connections:**")
    report.extend(check_ai_connections())

    return "\n".join(report)


def post_pr_comment(report_body: str) -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return

    try:
        with open(event_path, "r", encoding="utf-8") as event_file:
            event = json.load(event_file)
    except (OSError, json.JSONDecodeError):
        return

    pull_request = event.get("pull_request")
    if not pull_request:
        return

    pr_number = pull_request.get("number")
    repository = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")

    if not (pr_number and repository and token):
        return

    url = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-diagnose-script",
    }
    requests.post(url, headers=headers, json={"body": report_body}, timeout=10)


if __name__ == "__main__":
    print("=== Repository Diagnostics ===\n")
    report_output = generate_report()
    print(report_output)
    post_pr_comment(report_output)
