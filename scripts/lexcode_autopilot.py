"""LexCode Autopilot pull request reporter.

This script is intended to run inside a GitHub Actions workflow. It inspects a
handful of common project files and posts a short review-style comment on the
current pull request summarising potential issues.
"""

from __future__ import annotations

import base64
import os
from typing import Callable, Dict, Iterable, List

import requests


GITHUB_API = "https://api.github.com"


def get_env_variable(name: str) -> str | None:
    """Return the value of the GitHub Actions environment variable ``name``."""

    value = os.getenv(name)
    if value:
        return value
    return None


def build_headers(token: str) -> Dict[str, str]:
    """Return the default headers used when calling the GitHub API."""

    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def fetch_file(repo: str, path: str, headers: Dict[str, str]) -> str | None:
    """Fetch ``path`` from ``repo`` using the GitHub API.

    Parameters
    ----------
    repo:
        The ``owner/repository`` identifier.
    path:
        The path to the file within the repository.
    headers:
        HTTP headers that include authentication information.

    Returns
    -------
    Optional[str]
        ``None`` if the file does not exist. Otherwise, the decoded file
        content.
    """

    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None

    data = response.json()
    return base64.b64decode(data["content"]).decode("utf-8")


def analyze_python(content: str) -> List[str]:
    """Return a list of warnings for the supplied Python ``content``."""

    issues: List[str] = []
    if "import os" in content and "os.system" in content:
        issues.append("⚠️ استخدام os.system قد يفتح ثغرات أمنية.")
    if "def " not in content:
        issues.append("⚠️ لم يتم العثور على أي دوال معرفة.")
    if '"""' not in content:
        issues.append("⚠️ لا يوجد توثيق (Docstrings).")
    return issues


def analyze_js(content: str) -> List[str]:
    """Return a list of warnings for the supplied JavaScript ``content``."""

    issues: List[str] = []
    if "eval(" in content:
        issues.append("⚠️ استخدام eval قد يكون خطر أمني.")
    if "var " in content:
        issues.append("ℹ️ يُفضَّل استخدام let/const بدل var.")
    return issues


def analyze_yaml(content: str) -> List[str]:
    """Return a list of warnings for the supplied YAML ``content``."""

    issues: List[str] = []
    if "latest" in content:
        issues.append("⚠️ استخدام نسخة 'latest' غير موصى به (حدد نسخة ثابتة).")
    return issues


def analyze_docker(content: str) -> List[str]:
    """Return a list of warnings for the supplied Dockerfile ``content``."""

    issues: List[str] = []
    if "FROM" in content and "latest" in content:
        issues.append("⚠️ يفضل تحديد نسخة واضحة بدل latest.")
    if "USER root" in content:
        issues.append("⚠️ لا يوصى باستخدام root داخل الحاويات.")
    return issues


def analyze_file(path: str, content: str) -> Iterable[str]:
    """Dispatch the ``content`` of ``path`` to the relevant analyser."""

    analyzers: Dict[str, Callable[[str], List[str]]] = {
        "py": analyze_python,
        "js": analyze_js,
        "json": analyze_js,
        "yml": analyze_yaml,
        "yaml": analyze_yaml,
        "dockerfile": analyze_docker,
    }

    suffix = path.split(".")[-1].lower()
    if path.lower() in {"dockerfile", "dockerfile"}:
        suffix = "dockerfile"

    analyzer = analyzers.get(suffix)
    if not analyzer:
        return []
    return analyzer(content)


def post_comment(repo: str, pr_number: str, body: str, headers: Dict[str, str]) -> None:
    """Publish ``body`` as a comment on ``pr_number`` within ``repo``."""

    url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
    response = requests.post(url, headers=headers, json={"body": body}, timeout=10)
    if response.status_code == 201:
        print("✅ تم نشر التعليق على الـ PR بنجاح")
    else:
        print("❌ فشل نشر التعليق:", response.json())


def build_report(repo: str, headers: Dict[str, str]) -> str:
    """Build the markdown report by scanning a predefined file list."""

    files_to_check = [
        "requirements.txt",
        "app.py",
        "main.py",
        "index.js",
        "package.json",
        "dockerfile",
        "Dockerfile",
        ".github/workflows/ci.yml",
    ]

    report_lines = ["## LexCode Autopilot Report", ""]

    for file_path in files_to_check:
        content = fetch_file(repo, file_path, headers)
        if not content:
            continue

        report_lines.append(f"### 🔍 {file_path}")
        issues = list(analyze_file(file_path, content))
        if issues:
            report_lines.extend(f"- {issue}" for issue in issues)
        else:
            report_lines.append("✅ لا توجد مشاكل واضحة.")
        report_lines.append("")

    return "\n".join(report_lines)


def main() -> None:
    """Entry point for the GitHub Actions helper script."""

    token = get_env_variable("GITHUB_TOKEN")
    repo = get_env_variable("GITHUB_REPOSITORY")
    pr_number = get_env_variable("PR_NUMBER")

    if not token or not repo:
        print("⚠️ لا يمكن المتابعة بدون متغيرات البيئة المطلوبة.")
        return

    headers = build_headers(token)
    report = build_report(repo, headers)

    if not pr_number:
        print(report)
        print("⚠️ لا يوجد رقم PR لكتابة التعليق")
        return

    post_comment(repo, pr_number, report, headers)


if __name__ == "__main__":
    main()

