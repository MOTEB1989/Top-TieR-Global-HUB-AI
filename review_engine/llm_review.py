"""Shared helpers for LLM-powered review flows."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

BASE_PROMPTS: Dict[str, str] = {
    "code": (
        "You are a senior code reviewer. Analyze the provided code for correctness, maintainability, "
        "and security. Summarize issues, identify risks, and propose actionable recommendations."
    ),
    "security": (
        "You are an application security expert. Inspect the content for security weaknesses, "
        "secrets, and unsafe patterns. Provide concise findings, risk level, and remediation steps."
    ),
    "document": (
        "You are a technical documentation reviewer. Assess clarity, completeness, and compliance. "
        "Provide a crisp summary, key findings, risk level, and improvements."
    ),
}


def build_prompt(
    review_type: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    static_findings: Optional[Iterable[str]] = None,
) -> str:
    """Construct a structured prompt for downstream LLM calls."""
    header = BASE_PROMPTS.get(review_type, "General expert analysis. Provide risks and recommendations.")
    meta_lines: list[str] = []
    if metadata:
        for key, value in metadata.items():
            meta_lines.append(f"- {key}: {value}")
    static_lines: list[str] = []
    if static_findings:
        for finding in static_findings:
            static_lines.append(f"* {finding}")

    sections = [
        header,
        "\nContext:",
        content,
        "",
        "Metadata:" if meta_lines else "",
        "\n".join(meta_lines) if meta_lines else "",
        "",
        "Known observations:" if static_lines else "",
        "\n".join(static_lines) if static_lines else "",
        "",
        "Respond using JSON with keys: summary, findings (list), risk_level (low|medium|high), recommendations (list).",
    ]
    return "\n".join([part for part in sections if part])


def run_llm(prompt: str, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """Invoke the unified gateway to execute a chat completion."""
    import gateway  # type: ignore

    kwargs: Dict[str, Any] = {"prompt": prompt}
    if provider:
        kwargs["provider"] = provider
    if model:
        kwargs["model"] = model

    if hasattr(gateway, "simple_chat"):
        return gateway.simple_chat(**kwargs)

    gateway_client = gateway.get_gateway()  # type: ignore[attr-defined]
    return gateway_client.simple_chat(**kwargs)
