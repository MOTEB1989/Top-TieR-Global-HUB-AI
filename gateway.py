# -*- coding: utf-8 -*-
"""Simple gateway utilities with safe file handling and task detection."""
from __future__ import annotations

from pathlib import Path
from typing import List, Union


def guess_task_from_path(path: Union[str, Path]) -> str:
    """Guess the appropriate task based on file path and extension."""
    resolved = Path(path)
    suffix = resolved.suffix.lower()
    parts = [part.lower() for part in resolved.parts]

    if any("bank" in part for part in parts):
        return "banking_compliance"
    if any("law" in part or "legal" in part for part in parts):
        return "legal_analysis"
    if suffix in {".py", ".js", ".ts", ".java", ".go"}:
        return "review_code"
    if suffix in {".yaml", ".yml"}:
        return "tech_trends"
    if suffix in {".pdf", ".doc", ".docx"}:
        return "document_analysis"
    if suffix in {".md", ".txt"}:
        return "document_analysis"
    return "document_analysis"


def detect_tasks_from_content(content: str) -> List[str]:
    """Detect possible analysis tasks from the provided text content."""
    lowered = content.lower()
    tasks: List[str] = []

    if any(keyword in lowered for keyword in ["function", "class", "bug", "code"]):
        tasks.append("review_code")
    if any(keyword in lowered for keyword in ["regulation", "contract", "legal", "law"]):
        tasks.append("legal_analysis")
    if any(keyword in lowered for keyword in ["bank", "audit", "finance", "aml"]):
        tasks.append("banking_compliance")
    if any(keyword in lowered for keyword in ["medical", "patient", "diagnosis", "therapy"]):
        tasks.append("medical_info")
    if any(keyword in lowered for keyword in ["tech", "trend", "ai", "machine learning"]):
        tasks.append("tech_trends")

    if not tasks:
        tasks.append("document_analysis")

    return tasks


def _read_pdf(path: Path) -> str:
    """Read text content from a PDF file safely."""
    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # pragma: no cover - exercised via run_gateway_on_file
        return f"<<READ_ERROR:{exc}>>"


def _read_docx(path: Path) -> str:
    """Read text content from a DOCX file safely."""
    try:
        from docx import Document  # type: ignore

        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:  # pragma: no cover - exercised via run_gateway_on_file
        return f"<<READ_ERROR:{exc}>>"


def read_file_smart(path: Union[str, Path]) -> str:
    """Read a file using the appropriate parser based on extension."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {resolved}")

    suffix = resolved.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(resolved)
    if suffix in {".doc", ".docx"}:
        return _read_docx(resolved)

    return resolved.read_text(encoding="utf-8", errors="ignore")


def _format_read_error(reason: str) -> str:
    """Format a read error into the expected Markdown block."""
    return f"### ⚠️ تعذر قراءة الملف\nالسبب: {reason}\n---\n"


def _format_empty_file() -> str:
    """Format an empty file notice as Markdown."""
    return "### ⚠️ الملف فارغ\nلم يتم العثور على محتوى في الملف.\n---\n"


def run_gateway_on_file(path: Union[str, Path]) -> str:
    """Run the gateway on a single file, returning Markdown output."""
    try:
        content = read_file_smart(path)
    except Exception as exc:
        return _format_read_error(str(exc))

    if content.startswith("<<READ_ERROR:") and content.endswith(">>"):
        reason = content[len("<<READ_ERROR:") : -2]
        return _format_read_error(reason)

    if content == "":
        return _format_empty_file()

    truncated = False
    if len(content) > 50000:
        content = content[:50000]
        truncated = True

    output_parts = ["### المحتوى\n", content]
    if truncated:
        output_parts.append("\n**تم تقليم المحتوى لتجاوز الحد المسموح به (50000 حرف).**")
    output_parts.append("\n---\n")
    return "".join(output_parts)


def call_openai(prompt: str, *, timeout: int = 120) -> str:
    """Placeholder OpenAI call; should be mocked in tests."""
    raise RuntimeError("call_openai should be mocked during tests")


def call_groq(prompt: str, *, timeout: int = 120) -> str:
    """Placeholder Groq call; should be mocked in tests."""
    raise RuntimeError("call_groq should be mocked during tests")


def call_azure_openai(prompt: str, *, timeout: int = 120) -> str:
    """Placeholder Azure OpenAI call; should be mocked in tests."""
    raise RuntimeError("call_azure_openai should be mocked during tests")


def call_local_model(prompt: str, *, timeout: int = 120) -> str:
    """Placeholder local model call; should be mocked in tests."""
    raise RuntimeError("call_local_model should be mocked during tests")


def call_model(provider: str, prompt: str) -> str:
    """Dispatch to the correct model provider with timeout enforcement."""
    normalized = provider.lower().strip()
    if normalized == "openai":
        return call_openai(prompt, timeout=120)
    if normalized == "groq":
        return call_groq(prompt, timeout=120)
    if normalized == "azure":
        return call_azure_openai(prompt, timeout=120)
    if normalized == "local":
        return call_local_model(prompt, timeout=120)

    raise ValueError(f"Unsupported provider: {provider}")
