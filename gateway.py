#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI Gateway V3

• Multi-provider: OpenAI / Groq / Azure / Local
• Multi-task per file: code_review / legal / medical / tech / banking / document
• Multi-file-type: txt / md / py / rs / js / ts / yaml / yml / docx / pdf
• Output: Markdown مهيأ للدمج في تقارير أو تعليقات Pull Requests
"""

# This script is a standalone CLI tool.
# It is NOT imported by the main application code (gateway/ package is still the programmatic entrypoint).
# It is meant for CI/PR automation and local file review.

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Dict, List

import requests

try:
    from docx import Document  # type: ignore  # لقراءة DOCX
except ImportError:
    Document = None  # type: ignore

try:
    from PyPDF2 import PdfReader  # type: ignore  # لقراءة PDF
except ImportError:
    PdfReader = None  # type: ignore

# —– إعداد المسارات والـ Prompts —–

BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "ai_prompts"

TASK_PROMPTS: Dict[str, str] = {
    "code_review": "review_code.txt",
    "legal": "legal_analysis.txt",
    "medical": "medical_info.txt",
    "tech": "tech_trends.txt",
    "banking": "banking_compliance.txt",
    "document": "document_analysis.txt",
}


def load_prompt(task: str) -> str:
    """تحميل نص الـ prompt المناسب للمهمة."""

    if task not in TASK_PROMPTS:
        raise ValueError(f"مهمة غير مدعومة: {task}")

    path = PROMPTS_DIR / TASK_PROMPTS[task]
    if not path.is_file():
        raise FileNotFoundError(f"ملف الـprompt غير موجود: {path}")

    return path.read_text(encoding="utf-8")


# —– قراءة الملفات بأنواع مختلفة —–


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_docx_file(path: Path) -> str:
    if Document is None:
        raise RuntimeError("الحزمة python-docx غير مثبتة (مطلوبة لقراءة DOCX).")

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf_file(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("الحزمة PyPDF2 غير مثبتة (مطلوبة لقراءة PDF).")

    reader = PdfReader(str(path))
    texts: List[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        texts.append(txt)
    return "\n".join(texts)


def read_file_smart(path_str: str) -> str:
    """اختيار طريقة القراءة حسب الامتداد."""

    path = Path(path_str)
    if not path.is_file():
        raise FileNotFoundError(f"الملف غير موجود: {path_str}")

    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx_file(path)
    if suffix == ".pdf":
        return read_pdf_file(path)

    return read_text_file(path)


# —– كشف نوع المهمة من المسار والمحتوى —–


def guess_task_from_path(path_str: str) -> str:
    """تخمين المهمة الأساسية من المسار/الامتداد."""

    p = Path(path_str)
    suffix = p.suffix.lower()
    parts = p.as_posix().split("/")

    if "laws" in parts:
        return "legal"
    if "banking" in parts:
        return "banking"
    if "research" in parts:
        return "tech"

    if suffix in [".py", ".rs", ".js", ".ts"]:
        return "code_review"
    if suffix in [".md", ".txt", ".docx", ".pdf", ".yaml", ".yml"]:
        return "document"

    return "document"


def detect_tasks_from_content(content: str) -> List[str]:
    """كشف المهام المحتملة من النص نفسه (يمكن أن يكون أكثر من تخصص)."""

    lowered = content.lower()
    tasks: List[str] = []

    # مؤشرات برمجية
    if any(keyword in lowered for keyword in [
        "def ",
        "class ",
        "import ",
        "console.log",
        "fn ",
        "pub ",
        "async ",
        "await ",
    ]):
        tasks.append("code_review")

    # مؤشرات قانونية
    if any(word in lowered for word in [
        "نظام",
        "لائحة",
        "قانون",
        "تشريع",
        "مادة ",
        "محكمة",
        "دعوى",
        "عقد",
        "اتفاقية",
    ]):
        tasks.append("legal")

    # مؤشرات مصرفية / امتثال
    if any(word in lowered for word in [
        "kyc",
        "aml",
        "pii",
        "gdpr",
        "معاملة",
        "حساب",
        "رصيد",
        "مخاطر تشغيلية",
        "ائتمان",
        "عميل",
        "transfers",
        "swift",
    ]):
        tasks.append("banking")

    # مؤشرات تقنية حديثة
    if any(word in lowered for word in [
        "ai",
        "ml",
        "llm",
        "neural",
        "cloud",
        "kubernetes",
        "docker",
        "cyber",
        "zero trust",
        "space",
        "satellite",
    ]):
        tasks.append("tech")

    # مؤشرات طبية
    if any(word in lowered for word in [
        "mayo clinic",
        "nih",
        "who",
        "تشخيص",
        "أعراض",
        "دواء",
        "علاج",
        "سرطان",
        "ضغط",
        "سكر",
        "diabetes",
        "hypertension",
    ]):
        tasks.append("medical")

    # إذا لم يوجد أي مؤشر، نستخدم document كمهمة عامة
    if not tasks:
        tasks.append("document")

    # إزالة التكرارات مع الحفاظ على الترتيب
    unique_tasks: List[str] = []
    for t in tasks:
        if t not in unique_tasks:
            unique_tasks.append(t)
    return unique_tasks


def guess_language_from_extension(path_str: str) -> str:
    suffix = Path(path_str).suffix.lower()
    mapping = {
        ".py": "Python",
        ".rs": "Rust",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".md": "Markdown",
    }
    return mapping.get(suffix, "غير محددة")


# —– مزودو النماذج —–


def call_openai(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY غير مضبوط.")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_groq(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY غير مضبوط.")
    model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_azure(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("AZURE_OPENAI_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not api_key or not endpoint or not deployment:
        raise RuntimeError("متغيرات Azure OpenAI غير مكتملة (AZURE_OPENAI_KEY/ENDPOINT/DEPLOYMENT).")

    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_local(system_prompt: str, user_content: str) -> str:
    """نموذج محلي (مثل Phi-3) عبر خادم HTTP داخلي."""

    endpoint = os.getenv("LOCAL_MODEL_ENDPOINT")
    if not endpoint:
        raise RuntimeError("LOCAL_MODEL_ENDPOINT غير مضبوط لمزود local.")

    headers = {"Content-Type": "application/json"}
    payload = {
        "system": system_prompt,
        "input": user_content,
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data.get("output", "")


def call_model(system_prompt: str, user_content: str) -> str:
    provider = os.getenv("PROVIDER", "openai").lower()
    if provider == "openai":
        return call_openai(system_prompt, user_content)
    if provider == "groq":
        return call_groq(system_prompt, user_content)
    if provider == "azure":
        return call_azure(system_prompt, user_content)
    if provider == "local":
        return call_local(system_prompt, user_content)

    raise ValueError(f"مزود غير مدعوم: {provider}")


# —– بناء محتوى المستخدم —–


def build_user_content(task: str, content: str, filename: str | None) -> str:
    """تهيئة محتوى المستخدم المرسل للنموذج، مع بعض الميتاداتا."""

    if task == "code_review":
        lang = guess_language_from_extension(filename or "")
        return (
            f"الملف: {filename or 'غير معروف'}\n"
            f"اللغة المحتملة: {lang}\n\n"
            "الكود:\n"
            f"{content}\n"
        )

    header = f"الملف: {filename}\n\n" if filename else ""
    return header + content


# —– تشغيل الـGateway على ملف واحد —–


def run_gateway_on_file(file_path: str, task_mode: str = "auto") -> str:
    """يشغّل الـGateway على ملف واحد ويعيد نص Markdown جاهز."""

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"الملف غير موجود: {file_path}")

    raw_content = read_file_smart(file_path)

    if task_mode == "auto":
        base_task = guess_task_from_path(file_path)
        detected_tasks = detect_tasks_from_content(raw_content)

        if base_task not in detected_tasks:
            detected_tasks.insert(0, base_task)

        tasks: List[str] = []
        for detected in detected_tasks:
            if detected not in tasks:
                tasks.append(detected)
    else:
        tasks = [task_mode]

    sections: List[str] = []
    sections.append(f"## 📄 الملف: `{file_path}`\n")

    for task in tasks:
        try:
            system_prompt = load_prompt(task)
        except Exception as exc:  # noqa: BLE001
            sections.append(f"### ⚠️ المهمة: `{task}`\n\nتعذر تحميل الـprompt: {exc}\n")
            continue

        user_content = build_user_content(task, raw_content, file_path)

        try:
            model_output = call_model(system_prompt, user_content)
        except Exception as exc:  # noqa: BLE001
            sections.append(f"### ⚠️ المهمة: `{task}`\n\nفشل استدعاء النموذج: {exc}\n")
            continue

        sections.append(f"### 🧠 المهمة: `{task}`\n\n{model_output}\n")

    sections.append("\n---\n")
    return "\n".join(sections)


# —– CLI —–


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Gateway V3")
    parser.add_argument(
        "--task",
        type=str,
        default="auto",
        help="مهمة محددة (code_review, legal, medical, tech, banking, document) أو auto لاكتشاف المهام تلقائياً.",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="مسار الملف المراد تحليله.",
    )

    args = parser.parse_args()

    markdown_result = run_gateway_on_file(args.file, task_mode=args.task)
    print(markdown_result)


if __name__ == "__main__":
    main()
