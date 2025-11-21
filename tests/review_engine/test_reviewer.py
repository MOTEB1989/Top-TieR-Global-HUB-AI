import os
import sys
import types
from typing import Any, Dict

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from review_engine import llm_review
from review_engine.reviewer import ReviewEngine

@pytest.fixture(autouse=True)
def mock_gateway(monkeypatch):
    # Provide a fake gateway module so ReviewEngine initialization works
    gateway_module = types.ModuleType("gateway")
    gateway_module.get_gateway = lambda: types.SimpleNamespace(provider="mock-provider", model="mock-model")
    gateway_module.simple_chat = lambda **kwargs: {
        "provider": kwargs.get("provider"),
        "model": kwargs.get("model"),
    }
    monkeypatch.setitem(sys.modules, "gateway", gateway_module)

    def _mock_run_llm(prompt: str, provider: str | None = None, model: str | None = None) -> Dict[str, Any]:
        return {
            "summary": f"summary for {prompt[:10]}",
            "findings": ["llm finding"],
            "risk_level": "medium",
            "recommendations": ["llm recommendation"],
            "provider": provider or "mock-provider",
            "model": model or "mock-model",
            "raw": {"prompt": prompt},
        }

    monkeypatch.setattr(llm_review, "run_llm", _mock_run_llm)
    yield


@pytest.fixture
def engine():
    return ReviewEngine()


def _assert_normalized(result: Dict[str, Any]):
    expected_keys = {
        "summary",
        "findings",
        "risk_level",
        "recommendations",
        "provider",
        "model",
        "raw",
    }
    assert expected_keys.issubset(result.keys())
    assert isinstance(result["findings"], list)
    assert isinstance(result["recommendations"], list)


def test_code_review(engine):
    code_sample = "import os\n\nprint('hello')"
    result = engine.run("code", code_sample)
    _assert_normalized(result)
    assert any("Unused import" in f or "llm finding" in f for f in result["findings"])


def test_security_review(engine):
    security_sample = "api_key='secret'\nrequests.get(url, verify=False)"
    result = engine.run("security", security_sample)
    _assert_normalized(result)
    assert any("Hardcoded" in f or "llm finding" in f for f in result["findings"])


def test_document_review(engine):
    doc_sample = "This policy describes controls. It is short."  # brevity triggers static finding
    result = engine.run("document", doc_sample)
    _assert_normalized(result)
    assert result["risk_level"] in {"low", "medium", "high"}


def test_unknown_review_type(engine):
    with pytest.raises(ValueError):
        engine.run("unknown", "content")
