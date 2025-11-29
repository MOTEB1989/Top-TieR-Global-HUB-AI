#!/usr/bin/env python3
"""إنشاء تقرير Markdown لشجرة الملفات من GitHub API."""

import argparse
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


def fetch_repo_tree(repo: str, ref: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    """جلب شجرة الملفات من GitHub API."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1"
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("tree", [])


def build_markdown(tree: List[Dict[str, Any]], repo: str, ref: str) -> str:
    """إعداد محتوى Markdown للتقرير مع إحصائيات وفحص أولي للملفات الحساسة."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    extensions = [Path(item["path"]).suffix for item in tree if item.get("type") == "blob"]
    ext_counts = Counter(extensions)

    md_content = [
        "# 📁 تقرير فحص المستودع",
        "",
        f"المستودع: **{repo}@{ref}**",
        f"تاريخ الفحص: {timestamp}",
        "",
        f"إجمالي الملفات: **{len(tree)}**",
        "",
        "## قائمة الملفات:",
    ]

    for item in tree:
        path = item.get("path", "")
        type_ = item.get("type", "unknown")
        size = item.get("size")
        size_display = size if size is not None else "N/A"
        md_content.append(f"- `{path}` | النوع: **{type_}** | الحجم: {size_display}")

    md_content.extend([
        "",
        "## إحصائيات حسب الامتداد:",
    ])
    if ext_counts:
        for ext, count in ext_counts.most_common():
            md_content.append(f"- {ext or 'بدون امتداد'}: {count} ملف")
    else:
        md_content.append("- لا توجد ملفات مسجلة لإحصاء الامتدادات")

    sensitive_candidates = [
        item
        for item in tree
        if any(keyword in item.get("path", "").lower() for keyword in ["env", "secret", "config"])
    ]
    md_content.extend([
        "",
        "## ملفات حرجة محتملة:",
    ])
    if sensitive_candidates:
        for item in sensitive_candidates:
            md_content.append(f"- ⚠️ {item.get('path', '')}")
    else:
        md_content.append("- لا توجد ملفات حرجة مكتشفة")

    return "\n".join(md_content) + "\n"


def write_markdown(output_path: Path, content: str) -> None:
    """حفظ محتوى Markdown في المسار المحدد."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def default_report_path() -> Path:
    """إرجاع مسار افتراضي لتقرير اليوم."""
    today = datetime.now().strftime("%Y-%m-%d")
    return Path("docs") / f"repo-scan-{today}.md"


def default_protocol_path() -> Path:
    """إرجاع مسار افتراضي لملف التعليمات للبروتوكول."""
    today = datetime.now().strftime("%Y-%m-%d")
    return Path("docs") / f"system-instructions-{today}.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="تقرير شجرة الملفات من GitHub API")
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI"),
        help="اسم المستودع بصيغة owner/repo",
    )
    parser.add_argument(
        "--ref",
        default=os.getenv("GITHUB_REF", "main"),
        help="الفرع أو الوسم المطلوب",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="مسار ملف Markdown الناتج",
    )
    parser.add_argument(
        "--protocol-output",
        default=None,
        help="مسار ملف البروتوكول (System Instructions – Salima)",
    )
    parser.add_argument(
        "--skip-protocol",
        action="store_true",
        help="تخطي إنشاء ملف البروتوكول",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = os.getenv("GITHUB_TOKEN")

    try:
        tree = fetch_repo_tree(args.repo, args.ref, token)
    except requests.HTTPError as exc:
        print(f"فشل الاتصال: {exc.response.status_code} - {exc.response.text}")
        raise SystemExit(1)
    except requests.RequestException as exc:
        print(f"⚠️ خطأ في الاتصال: {exc}")
        raise SystemExit(1)

    md_content = build_markdown(tree, args.repo, args.ref)
    output_path = Path(args.output) if args.output else default_report_path()
    write_markdown(output_path, md_content)
    print(f"✅ تم إنشاء الملف {output_path} بنجاح")

    if not args.skip_protocol:
        protocol_text = """
# 🧩 بروتوكول Salima (System Instructions)

1. الفحص التلقائي للمستودع قبل أي كود جديد
2. إنشاء تقرير Markdown في docs/
3. تمرير التقرير للنموذج للتحليل
4. الالتزام بمعايير الأمان والجودة
5. عدم كتابة أي كود جديد إلا بعد مراجعة الملفات القائمة
6. كشف أولي عن الملفات الحساسة (.env, secrets, config)
7. حفظ كل عملية فحص في ملف مستقل بتاريخ التنفيذ
""".strip()

        protocol_path = Path(args.protocol_output) if args.protocol_output else default_protocol_path()
        write_markdown(protocol_path, protocol_text)
        print(f"✅ تم إنشاء ملف التعليمات: {protocol_path}")
        print("\n--- نسخة جاهزة للـ Prompt ---\n")
        print(protocol_text)


if __name__ == "__main__":
    main()
