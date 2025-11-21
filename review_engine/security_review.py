"""Security-focused review helpers."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from review_engine import llm_review


SECRET_PATTERNS: Dict[str, str] = {
    r"AKIA[0-9A-Z]{16}": "Possible AWS access key detected.",
    r"(?i)secret[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9/+]{16,}['\"]?": "Hardcoded secret key detected.",
    r"(?i)password\s*[:=]\s*['\"].+['\"]": "Hardcoded password detected.",
    r"(?i)api[_-]?key\s*[:=]\s*['\"].+['\"]": "Hardcoded API key detected.",
}

INSECURE_USAGE: Dict[str, str] = {
    r"verify=False": "TLS verification disabled in request.",
    r"md5\(": "MD5 is a weak hash; prefer SHA-256 or better.",
    r"sha1\(": "SHA-1 is deprecated; use stronger hashing.",
    r"random\.random\(": "Use secrets module for security-sensitive randomness.",
}


def _detect_patterns(code: str, patterns: Dict[str, str]) -> List[str]:
    matches: List[str] = []
    for pattern, description in patterns.items():
        if re.search(pattern, code):
            matches.append(description)
    return matches


def _derive_risk_level(findings: Iterable[str]) -> str:
    if any("hardcoded" in finding.lower() or "key" in finding.lower() for finding in findings):
        return "high"
    return "medium" if findings else "low"


def review_security(
    content: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform security review combining pattern detection with LLM reasoning."""
    static_findings: List[str] = []
    static_findings.extend(_detect_patterns(content, SECRET_PATTERNS))
    static_findings.extend(_detect_patterns(content, INSECURE_USAGE))

    prompt = llm_review.build_prompt("security", content, metadata=metadata, static_findings=static_findings)
    ai_response = llm_review.run_llm(prompt, provider=provider, model=model)

    findings: List[str] = list(static_findings)
    recommendations: List[str] = []

    if isinstance(ai_response, dict):
        findings.extend(ai_response.get("findings") or [])
        recommendations.extend(ai_response.get("recommendations") or [])
        summary = ai_response.get("summary") or "Security review completed."
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
            "Rotate any detected secrets and remove them from source control.",
            "Enable TLS verification and use modern cryptography primitives.",
        ],
        "provider": provider_name,
        "model": model_name,
        "raw": ai_response,
    }
