"""Static and LLM-assisted code review utilities."""
from __future__ import annotations

import ast
import re
from typing import Any, Dict, Iterable, List, Optional

from review_engine import llm_review


DANGEROUS_PATTERNS: Dict[str, str] = {
    r"\beval\(": "Use of eval can lead to arbitrary code execution.",
    r"\bexec\(": "Use of exec can lead to arbitrary code execution.",
    r"subprocess\.Popen": "subprocess.Popen without sanitization is risky.",
    r"os\.system": "os.system can be dangerous with untrusted input.",
    r"pickle\.load": "Unpickling untrusted data is unsafe.",
    r"yaml\.load\(": "yaml.load without SafeLoader is unsafe.",
}


def _detect_unused_imports(code: str) -> List[str]:
    """Detect unused imports using AST traversal."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    imported: set[str] = set()
    used: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imported.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.Name):
            used.add(node.id)

    return sorted(name for name in imported if name not in used)


def _detect_dangerous_patterns(code: str) -> List[str]:
    matches: List[str] = []
    for pattern, description in DANGEROUS_PATTERNS.items():
        if re.search(pattern, code):
            matches.append(description)
    return matches


def _detect_missing_error_handling(code: str) -> List[str]:
    if "try" in code:
        return []
    if "except" in code:
        return []
    return ["No explicit error handling (try/except) detected."]


def _collect_static_findings(code: str) -> List[str]:
    findings: List[str] = []
    findings.extend([f"Unused import: {name}" for name in _detect_unused_imports(code)])
    findings.extend(_detect_dangerous_patterns(code))
    findings.extend(_detect_missing_error_handling(code))
    return findings


def _derive_risk_level(findings: Iterable[str]) -> str:
    high_markers = ("arbitrary code execution", "unsafe", "dangerous")
    for finding in findings:
        lowered = finding.lower()
        if any(marker in lowered for marker in high_markers):
            return "high"
    return "medium" if findings else "low"


def review_code(
    content: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform static and LLM-assisted code review."""
    static_findings = _collect_static_findings(content)
    prompt = llm_review.build_prompt("code", content, metadata=metadata, static_findings=static_findings)
    ai_response = llm_review.run_llm(prompt, provider=provider, model=model)

    findings: List[str] = list(static_findings)
    recommendations: List[str] = []

    if isinstance(ai_response, dict):
        findings.extend(ai_response.get("findings") or [])
        recommendations.extend(ai_response.get("recommendations") or [])
        summary = ai_response.get("summary") or "Code review completed."
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
            "Add explicit error handling where appropriate.",
            "Review unused imports and remove dead code.",
        ],
        "provider": provider_name,
        "model": model_name,
        "raw": ai_response,
    }
