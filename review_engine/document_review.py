"""Document review utilities."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from review_engine import llm_review


def _clarity_score(content: str) -> float:
    sentences = [s for s in content.replace("\n", " ").split(".") if s.strip()]
    words = content.split()
    if not words:
        return 0.0
    avg_sentence_length = len(words) / max(len(sentences), 1)
    # Heuristic: shorter sentences -> clearer text
    return max(0.0, 10 - avg_sentence_length) / 10


def _collect_static_findings(content: str) -> List[str]:
    findings: List[str] = []
    clarity = _clarity_score(content)
    if clarity < 0.4:
        findings.append("Document may be hard to read; consider shorter sentences.")
    if len(content.split()) < 50:
        findings.append("Document is brief; verify completeness of requirements.")
    return findings


def _derive_risk_level(findings: List[str]) -> str:
    if not findings:
        return "low"
    return "medium" if len(findings) < 3 else "high"


def review_document(
    content: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform clarity/compliance checks plus AI summarization."""
    static_findings = _collect_static_findings(content)
    prompt = llm_review.build_prompt("document", content, metadata=metadata, static_findings=static_findings)
    ai_response = llm_review.run_llm(prompt, provider=provider, model=model)

    findings: List[str] = list(static_findings)
    recommendations: List[str] = []

    if isinstance(ai_response, dict):
        findings.extend(ai_response.get("findings") or [])
        recommendations.extend(ai_response.get("recommendations") or [])
        summary = ai_response.get("summary") or "Document review completed."
        risk_level = ai_response.get("risk_level") or _derive_risk_level(findings)
        provider_name = ai_response.get("provider") or provider
        model_name = ai_response.get("model") or model
    else:
        summary = str(ai_response)
        risk_level = _derive_risk_level(findings)
        provider_name = provider
        model_name = model

    return {
        "summary": summary,
        "findings": findings,
        "risk_level": risk_level,
        "recommendations": recommendations or [
            "Clarify ambiguous statements and ensure terminology is consistent.",
            "Expand sections with actionable requirements or acceptance criteria.",
        ],
        "provider": provider_name,
        "model": model_name,
        "raw": ai_response,
    }
