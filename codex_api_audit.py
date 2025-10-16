#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
codex_api_audit.py (improved)
فحص المستودع لاكتشاف اتصالات خارجية (domains/endpoints)، SDKs، متغيرات بيئية وأنماط
تشير إلى أسرار. يُنتج تقرير JSON. لا يكشف أي قيمة حساسة — فقط أسماء المتغيرات ومواقعها.

تحسينات: متانة أفضل لمعالجة نتائج re.findall، فصل أنماط GitHub Actions عن بقية أنماط المتغيرات،
واستخدام Set[str] في التعليقات النوعية.
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set

try:
    from json import JSONDecodeError  # stdlib
except Exception:  # احتياط للبيئات القديمة
    JSONDecodeError = ValueError

try:
    import requests
except ImportError:
    print("مطلوب تثبيت requests: pip install requests", file=sys.stderr)
    sys.exit(1)

# ===== إعدادات افتراضية للمستودع (غيّرها عند الحاجة) =====
DEFAULT_OWNER = "MOTEB1989"
DEFAULT_REPO = "Top-TieR-Global-HUB-AI"
DEFAULT_BRANCH = "main"

GITHUB_API_BASE = "https://api.github.com"
CODEX_ENDPOINT = "https://api.lexcode.ai/v1/lex/run"
TIMEOUT = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

# ===== أنماط وكواشف =====
URL_RE = re.compile(r"https?://[^\s\"'`<>]+")
HTTP_METHOD_HINTS: Dict[str, re.Pattern[str]] = {
    "GET": re.compile(r"\b(get|method\s*[:=]\s*['\"]get['\"])\b", re.IGNORECASE),
    "POST": re.compile(r"\b(post|method\s*[:=]\s*['\"]post['\"])\b", re.IGNORECASE),
    "PUT": re.compile(r"\b(put|method\s*[:=]\s*['\"]put['\"])\b", re.IGNORECASE),
    "DELETE": re.compile(r"\b(delete|method\s*[:=]\s*['\"]delete['\"])\b", re.IGNORECASE),
    "PATCH": re.compile(r"\b(patch|method\s*[:=]\s*['\"]patch['\"])\b", re.IGNORECASE),
}

SDK_PATTERNS: Dict[str, re.Pattern[str]] = {
    "openai": re.compile(r"\bopenai\b|client\s*=\s*OpenAI\(", re.IGNORECASE),
    "anthropic": re.compile(r"\banthropic\b", re.IGNORECASE),
    "azure": re.compile(r"\bazure\b", re.IGNORECASE),
    "google-cloud": re.compile(r"\bgoogle[-_.]?(?:cloud|api|apis)\b|\bfrom\s+google\b", re.IGNORECASE),
    "boto3": re.compile(r"\bboto3\b", re.IGNORECASE),
    "aws-sdk": re.compile(r"\baws[-_.]?sdk\b|require\(['\"]aws-sdk['\"]\)", re.IGNORECASE),
    "stripe": re.compile(r"\bstripe\b", re.IGNORECASE),
    "twilio": re.compile(r"\btwilio\b", re.IGNORECASE),
    "slack": re.compile(r"\bslack[_-]?sdk\b|require\(['\"]@?slack", re.IGNORECASE),
    "sendgrid": re.compile(r"\bsendgrid\b|\b@sendgrid\b", re.IGNORECASE),
    "axios": re.compile(r"\baxios\b", re.IGNORECASE),
    "requests": re.compile(r"\brequests\.(?:get|post|put|delete|patch|head)\b", re.IGNORECASE),
    "node-fetch": re.compile(r"\bnode[-_.]?fetch\b|\bfetch\(", re.IGNORECASE),
}

# متغيرات بيئية / أسرار
# قائمة من الأزواج: (pattern, is_gha_secret) — الأخير خاص بصيغة GitHub Actions:  ${{ secrets.X }}
ENV_PATTERN_ENTRIES = [
    (re.compile(r"os\.getenv\(['\"]([A-Z0-9_]+)['\"]\)"), False),
    (re.compile(r"process\.env\.([A-Z0-9_]+)"), False),
    (re.compile(r"\bENV\[['\"]([A-Z0-9_]+)['\"]\]"), False),
    (re.compile(r"\$\{([A-Z0-9_]+)\}"), False),  # Bash/Docker-like
    (re.compile(r"\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}"), True),  # GitHub Actions
]

SUSPECT_KEYWORDS = re.compile(
    r"(API[_-]?KEY|SECRET|TOKEN|BEARER|ACCESS[_-]?KEY|PRIVATE[_-]?KEY|CLIENT[_-]?SECRET|AUTH|PASSWORD)",
    re.IGNORECASE,
)

CODE_EXTS: Set[str] = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".yml",
    ".yaml",
    ".env",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".gradle",
    ".properties",
}

SPECIAL_FILENAMES: Set[str] = {"Dockerfile"}

IGNORE_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".next",
    ".cache",
    "__pycache__",
}


def read_text_safe(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return ""


def walk_files(root: str) -> List[str]:
    result: List[str] = []
    for base, dirs, files in os.walk(root):
        # استبعد مجلدات ضخمة/مُولَّدة، لكن لا تستبعد .github
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS and d != ".git"
        ]
        for filename in files:
            if filename in SPECIAL_FILENAMES:
                result.append(os.path.join(base, filename))
                continue
            ext = os.path.splitext(filename)[1]
            if ext.lower() in CODE_EXTS:
                result.append(os.path.join(base, filename))
    return result


def classify_methods(snippet: str) -> List[str]:
    found: List[str] = []
    for method, pattern in HTTP_METHOD_HINTS.items():
        if pattern.search(snippet):
            found.append(method)
    return sorted(set(found))


def domain_of(url: str) -> str:
    try:
        after_scheme = url.split("://", 1)[1]
        host = after_scheme.split("/", 1)[0]
        host = host.split("@")[-1].split(":")[0]
        return host.lower()
    except (IndexError, ValueError):
        return ""


def safe_extract_var_from_findall_result(match: Any) -> str:
    """
    re.findall قد تعيد سلاسل أو tuples/lists (عند وجود مجموعات التقاط).
    هذه الدالة تُرجع اسم المتغيّر بأمان.
    """
    if isinstance(match, str):
        return match
    if isinstance(match, (list, tuple)):
        for element in match:
            if isinstance(element, str) and element:
                return element
        return ""
    try:
        return str(match)
    except (TypeError, ValueError) as exc:
        logging.warning("safe_extract_var_from_findall_result failed: %s", exc)
        return ""


def analyze_repo(repo_path: str) -> Dict[str, Any]:
    files = walk_files(repo_path)
    logging.info("فحص %d ملفًا...", len(files))

    api_hits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "endpoints": Counter(),
        "files": set(),
        "methods": Counter(),
    })
    sdks: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "files": set(),
        "hits": 0,
    })
    env_vars: Counter = Counter()
    suspects: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "files": set(),
        "hits": 0,
    })
    gha_secrets: Counter = Counter()

    for filepath in files:
        text = read_text_safe(filepath)
        if not text:
            continue

        for url in URL_RE.findall(text):
            domain = domain_of(url)
            if not domain or "localhost" in domain:
                continue
            api_hits[domain]["endpoints"][url] += 1
            api_hits[domain]["files"].add(filepath)

        methods_found = classify_methods(text)
        if methods_found:
            for domain, data in api_hits.items():
                if filepath in data["files"]:
                    for method in methods_found:
                        data["methods"][method] += 1

        for name, pattern in SDK_PATTERNS.items():
            hits = len(pattern.findall(text))
            if hits:
                sdks[name]["files"].add(filepath)
                sdks[name]["hits"] += hits

        for pattern, is_gha_secret in ENV_PATTERN_ENTRIES:
            for match in pattern.findall(text):
                var_name = safe_extract_var_from_findall_result(match)
                if not var_name:
                    continue
                env_vars[var_name] += 1
                if is_gha_secret:
                    gha_secrets[var_name] += 1

        for match in SUSPECT_KEYWORDS.finditer(text):
            token_name = match.group(0).upper()
            suspects[token_name]["files"].add(filepath)
            suspects[token_name]["hits"] += 1

    api_summary = []
    for domain, data in api_hits.items():
        api_summary.append({
            "domain": domain,
            "unique_endpoints": len(data["endpoints"]),
            "sample_endpoints": sorted(data["endpoints"].keys())[:20],
            "files_count": len(data["files"]),
            "methods": dict(data["methods"]),
        })
    api_summary.sort(key=lambda item: (-item["unique_endpoints"], item["domain"]))

    sdks_summary = []
    for name, data in sdks.items():
        sdks_summary.append({
            "sdk": name,
            "hits": data["hits"],
            "files_count": len(data["files"]),
            "sample_files": sorted(data["files"])[:20],
        })
    sdks_summary.sort(key=lambda item: -item["hits"])

    suspects_summary = []
    for token_name, data in suspects.items():
        suspects_summary.append({
            "token_like": token_name,
            "hits": data["hits"],
            "files_count": len(data["files"]),
            "sample_files": sorted(data["files"])[:20],
        })
    suspects_summary.sort(key=lambda item: -item["hits"])

    gha_secrets_top = [
        {"secret": name, "hits": count} for name, count in gha_secrets.most_common()
    ]

    report = {
        "generated_at": int(time.time()),
        "repo_path": repo_path,
        "apis_by_domain": api_summary,
        "sdks_detected": sdks_summary,
        "env_vars_detected": [
            {"name": name, "hits": count} for name, count in env_vars.most_common()
        ],
        "gh_actions_secrets": gha_secrets_top,
        "token_like_markers": suspects_summary,
        "notes": [
            "تقرير استدلالي/إحصائي: قد توجد إيجابيات كاذبة أو عناصر لم تُكتشف.",
            "لا يكشف التقرير أي قيمة حساسة؛ فقط أسماء المتغيرات وموقعها.",
        ],
        "confidence_hint": "heuristic",
    }
    return report


def download_repo_zip(owner: str, repo: str, ref: str, token: Optional[str]) -> str:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/zipball/{ref}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "codex-api-audit",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    logging.info("تنزيل أرشيف المستودع: %s", url)
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    tmpdir = tempfile.mkdtemp(prefix="repo_")
    zip_path = os.path.join(tmpdir, "repo.zip")
    with open(zip_path, "wb") as handle:
        handle.write(response.content)
    with zipfile.ZipFile(zip_path, "r") as zfile:
        zfile.extractall(tmpdir)
    subdirs = [
        os.path.join(tmpdir, entry)
        for entry in os.listdir(tmpdir)
        if os.path.isdir(os.path.join(tmpdir, entry))
    ]
    repo_root = [path for path in subdirs if os.path.basename(path) != "__MACOSX"]
    if not repo_root:
        raise RuntimeError("تعذر تحديد مجلد المستودع بعد فك الضغط.")
    return repo_root[0]


def send_report_to_codex(report: Dict[str, Any], repo_root: str, codex_api_key: Optional[str]) -> Dict[str, Any]:
    headers = {"User-Agent": "codex-api-audit"}
    if codex_api_key:
        headers["Authorization"] = f"Bearer {codex_api_key}"

    files = {
        "report": (
            "api_audit_report.json",
            json.dumps(report, ensure_ascii=False).encode("utf-8"),
            "application/json",
        )
    }
    data = {
        "task": "audit_repo_apis",
        "timestamp": str(int(time.time())),
        "repo_hint": report.get("repo_path", ""),
    }
    logging.info("إرسال التقرير إلى Codex: %s", CODEX_ENDPOINT)
    response = requests.post(
        CODEX_ENDPOINT,
        headers=headers,
        files=files,
        data=data,
        timeout=TIMEOUT,
    )
    try:
        payload = response.json()
    except JSONDecodeError:
        logging.warning("Codex returned non-JSON response; falling back to raw text.")
        payload = {"raw_text": response.text, "status_code": response.status_code}
    if not response.ok:
        logging.error("Codex أعاد خطأ HTTP %s", response.status_code)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="تدقيق اتصالات API داخل المستودع وإنتاج تقرير JSON (مع خيار إرساله إلى Codex)."
    )
    src = parser.add_mutually_exclusive_group(required=False)
    src.add_argument("--repo-path", help="مسار مجلد المستودع المحلي (افتراضي .)")
    src.add_argument("--owner", help="مالك GitHub (مع --repo)", default=DEFAULT_OWNER)
    parser.add_argument("--repo", help="اسم المستودع على GitHub (يتطلب --owner)", default=DEFAULT_REPO)
    parser.add_argument("--branch", help="الفرع/المرجع المراد تنزيله", default=DEFAULT_BRANCH)
    parser.add_argument("--send-to-codex", action="store_true", help="إرسال التقرير إلى Codex بعد توليده")
    parser.add_argument("--output", default="api_audit_report.json", help="اسم ملف مخرجات التقرير")
    args = parser.parse_args()

    repo_path = args.repo_path
    cleanup: Optional[str] = None

    if repo_path:
        repo_root = os.path.abspath(repo_path)
        if not os.path.isdir(repo_root):
            logging.error("المسار غير موجود: %s", repo_root)
            sys.exit(1)
    else:
        token = os.getenv("GIT_TOKEN")
        repo_root = download_repo_zip(args.owner, args.repo, args.branch, token)
        cleanup = os.path.dirname(repo_root)

    try:
        report = analyze_repo(repo_root)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
        logging.info("تم إنشاء التقرير: %s", args.output)

        if args.send_to_codex:
            codex_key = os.getenv("CODEX_API_KEY")
            payload = send_report_to_codex(report, repo_root, codex_key)
            print(json.dumps({"codex_response": payload}, ensure_ascii=False, indent=2))

    finally:
        if cleanup and os.path.isdir(cleanup):
            shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    main()
