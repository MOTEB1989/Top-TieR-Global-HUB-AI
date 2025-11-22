#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Gateway V3
- Multi-provider: OpenAI / Groq / Azure / Local HTTP endpoint
- Multi-task per file: code_review / legal / medical / tech / banking / document
- Multi-file-type: txt / md / py / rs / js / ts / yaml / yml / docx / pdf
- Output: Markdown formatted for PR reviews or standalone reports.
"""

from __future__ import annotations

import os
import argparse
from pathlib import Path
from typing import Dict, List, Union

import requests

try:
    from docx import Document  # type: ignore[import]
except ImportError:
    Document = None

try:
    from PyPDF2 import PdfReader  # type: ignore[import]
except ImportError:
    PdfReader = None


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
    """Load the text prompt template for a given task."""
    if task not in TASK_PROMPTS:
        raise ValueError(f"Unsupported task: {task}")
    path = PROMPTS_DIR / TASK_PROMPTS[task]
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


# ---------- File readers ----------

def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_docx_file(path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required to read DOCX files.")
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf_file(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("PyPDF2 is required to read PDF files.")
    reader = PdfReader(str(path))
    texts: List[str] = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        texts.append(txt)
    return "\n".join(texts)


def read_file_smart(path: Union[str, Path]) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    suffix = p.suffix.lower()
    if suffix == ".docx":
        return read_docx_file(p)
    if suffix == ".pdf":
        return read_pdf_file(p)
    return read_text_file(p)


# ---------- Task & language detection ----------

def guess_task_from_path(path_str: str) -> str:
    p = Path(path_str)
    suffix = p.suffix.lower()
    parts = p.as_posix().split("/")

    if "laws" in parts or "legal" in parts:
        return "legal"
    if "banking" in parts or "finance" in parts:
        return "banking"
    if "research" in parts or "tech" in parts:
        return "tech"

    if suffix in {".py", ".rs", ".js", ".ts"}:
        return "code_review"
    if suffix in {".md", ".txt", ".docx", ".pdf", ".yaml", ".yml"}:
        return "document"

    return "document"


def detect_tasks_from_content(content: str) -> List[str]:
    lowered = content.lower()
    tasks: List[str] = []

    # Code indicators
    if any(k in lowered for k in ["def ", "class ", "import ", "console.log", "fn ", "pub ", "async ", "await "]):
        tasks.append("code_review")

    # Legal indicators
    if any(k in lowered for k in ["نظام", "لائحة", "قانون", "تشريع", "مادة ", "محكمة", "دعوى", "عقد", "اتفاقية"]):
        tasks.append("legal")

    # Banking/Compliance indicators
    if any(k in lowered for k in ["kyc", "aml", "pii", "gdpr", "معاملة", "حساب", "رصيد", "ائتمان", "عميل", "swift"]):
        tasks.append("banking")

    # Tech indicators
    if any(k in lowered for k in ["ai", "ml", "llm", "neural", "cloud", "kubernetes", "docker", "cyber", "zero trust"]):
        tasks.append("tech")

    # Medical indicators
    if any(k in lowered for k in ["تشخيص", "أعراض", "دواء", "علاج", "سرطان", "ضغط", "diabetes", "hypertension", "سكر"]):
        tasks.append("medical")

    if not tasks:
        tasks.append("document")

    unique: List[str] = []
    for t in tasks:
        if t not in unique:
            unique.append(t)
    return unique


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


# ---------- Model providers ----------

def call_openai(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
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
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def call_groq(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
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
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def call_azure(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("AZURE_OPENAI_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not api_key or not endpoint or not deployment:
        raise RuntimeError("Azure OpenAI env vars missing (AZURE_OPENAI_KEY / ENDPOINT / DEPLOYMENT).")

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
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def call_local(system_prompt: str, user_content: str) -> str:
    """
    Local LLM endpoint (e.g., Phi-3 via HTTP).

    Expected env:
      LOCAL_MODEL_ENDPOINT -> URL that accepts JSON:
        { "system": "...", "input": "..." }
      and returns JSON:
        { "output": "..." }
    """
    endpoint = os.getenv("LOCAL_MODEL_ENDPOINT")
    if not endpoint:
        raise RuntimeError("LOCAL_MODEL_ENDPOINT is not set for local provider.")

    headers = {"Content-Type": "application/json"}
    payload = {"system": system_prompt, "input": user_content}
    r = requests.post(endpoint, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
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
    raise ValueError(f"Unsupported provider: {provider}")


# ---------- User content builder ----------

def build_user_content(task: str, content: str, filename: str | None) -> str:
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


# ---------- Main gateway logic ----------

def run_gateway_on_file(file_path: str, task_mode: str = "auto") -> str:
    """
    Run the AI gateway on a single file and return Markdown text.

    task_mode:
      - "auto": detect tasks from path + content (may be multiple).
      - explicit: one of code_review / legal / medical / tech / banking / document
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw_content = read_file_smart(path)

    if task_mode == "auto":
        base_task = guess_task_from_path(file_path)
        detected_tasks = detect_tasks_from_content(raw_content)
        if base_task not in detected_tasks:
            detected_tasks.insert(0, base_task)
        tasks: List[str] = []
        for t in detected_tasks:
            if t not in tasks:
                tasks.append(t)
    else:
        tasks = [task_mode]

    sections: List[str] = []
    sections.append(f"## 📄 الملف: `{file_path}`\n")

    for task in tasks:
        try:
            system_prompt = load_prompt(task)
        except Exception as e:  # noqa: BLE001
            sections.append(f"### ⚠️ المهمة: `{task}`\n\nتعذر تحميل الـprompt: {e}\n")
            continue

        user_content = build_user_content(task, raw_content, file_path)

        try:
            model_output = call_model(system_prompt, user_content)
        except Exception as e:  # noqa: BLE001
            sections.append(f"### ⚠️ المهمة: `{task}`\n\nفشل استدعاء النموذج: {e}\n")
            continue

        sections.append(f"### 🧠 المهمة: `{task}`\n\n{model_output}\n")

    sections.append("\n---\n")
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Gateway V3")
    parser.add_argument(
        "--task",
        type=str,
        default="auto",
        help="Task: code_review, legal, medical, tech, banking, document, or 'auto' to auto-detect.",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the file to analyze.",
    )
    args = parser.parse_args()
    md = run_gateway_on_file(args.file, task_mode=args.task)
    print(md)


if __name__ == "__main__":
    main()

