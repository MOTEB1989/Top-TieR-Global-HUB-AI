"""Script to trigger Codex Gateway API audit for the repository."""
import os
import sys
from typing import Any, Dict

import requests


CODex_URL = "https://api.lexcode.ai/v1/lex/run"
PROJECT = "Top-TieR-Global-HUB-AI"
TASK = "api_audit"
BRANCH = "main"
FILES = ["gpt_client.py", ".github/workflows/api-audit.yml"]
PROMPT = "تحقق من وجود تسريبات API ومخاطر أمنية"
LANGUAGE = "ar"


def build_payload() -> Dict[str, Any]:
    """Construct the payload sent to the Codex Gateway API."""
    return {
        "project": PROJECT,
        "task": TASK,
        "branch": BRANCH,
        "files": FILES,
        "mode": "analyze",
        "prompt": PROMPT,
        "language": LANGUAGE,
    }


def main() -> None:
    token = os.environ.get("GIT_TOKEN")
    if not token:
        raise SystemExit(
            "Environment variable GIT_TOKEN is required to call the Codex API."
        )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = build_payload()

    response = requests.post(CODex_URL, headers=headers, json=payload, timeout=60)

    print("Status Code:", response.status_code)
    try:
        print("Response:", response.json())
    except requests.exceptions.JSONDecodeError:
        print("Response Text:", response.text)

    response.raise_for_status()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - script entry point error surface
        print(f"Error executing Codex audit: {exc}", file=sys.stderr)
        raise
