import base64
import os
import sys
from typing import Optional

import requests


def get_env_variable(name: str) -> Optional[str]:
    """Fetch an environment variable and log if it is missing."""
    value = os.getenv(name)
    if not value:
        print(f"⚠️ Environment variable '{name}' is not set.")
    return value


def build_headers(token: Optional[str]) -> dict:
    if not token:
        return {"Accept": "application/vnd.github.v3+json"}
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def fetch_file(repo: str, path: str, headers: dict) -> Optional[str]:
    """Fetch and decode a file's contents from GitHub."""
    if not repo:
        print("⚠️ Cannot fetch files without a repository name.")
        return None

    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
        except (KeyError, ValueError, UnicodeDecodeError) as exc:
            print(f"❌ Failed to decode content for {path}: {exc}")
            return None
        return content

    if response.status_code == 404:
        print(f"ℹ️ File '{path}' was not found in the repository.")
        return None

    print(f"❌ Failed to fetch '{path}': {response.status_code} {response.text}")
    return None


def post_comment(repo: str, pr_number: str, body: str, headers: dict) -> bool:
    if not repo or not pr_number:
        print("⚠️ Repository or PR number missing; cannot post a comment.")
        return False

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    response = requests.post(url, headers=headers, json={"body": body}, timeout=30)

    if response.status_code == 201:
        print("✅ Comment posted to the PR successfully.")
        return True

    print(
        "❌ Failed to post comment: "
        f"{response.status_code} {response.text}"
    )
    return False


def main() -> int:
    token = get_env_variable("GITHUB_TOKEN")
    repo = get_env_variable("GITHUB_REPOSITORY")
    pr_number = get_env_variable("PR_NUMBER")

    headers = build_headers(token)

    analysis_report = ["## LexCode Autopilot Report", ""]

    requirements = fetch_file(repo, "requirements.txt", headers)
    if requirements is not None:
        analysis_report.append("📂 **requirements.txt موجود:**")
        analysis_report.append("```")
        analysis_report.append(requirements)
        analysis_report.append("```")
        analysis_report.append(
            "_إضافة تحليلات إضافية حول الإعتمادات يمكن إدراجها هنا لاحقًا._"
        )
    else:
        analysis_report.append("⚠️ لم يتم العثور على ملف `requirements.txt`.")

    comment_body = "\n".join(analysis_report)

    if not pr_number:
        print("⚠️ No PR number provided; skipping comment posting.")
        return 1

    if not post_comment(repo or "", pr_number, comment_body, headers):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
