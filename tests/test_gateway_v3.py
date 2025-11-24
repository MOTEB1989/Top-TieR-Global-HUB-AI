import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gateway


def test_guess_task_from_path():
    assert gateway.guess_task_from_path("src/module/example.py") == "review_code"
    assert gateway.guess_task_from_path("docs/README.md") == "document_analysis"
    assert gateway.guess_task_from_path("laws/regulation.pdf") == "legal_analysis"
    assert gateway.guess_task_from_path("banking/policy.yaml") == "banking_compliance"
    assert gateway.guess_task_from_path("notes/tech/trends.txt") == "tech_trends"


def test_detect_tasks_from_content():
    content = "This function fixes a bug in the code while meeting legal regulation in the bank sector."  # noqa: E501
    tasks = gateway.detect_tasks_from_content(content)
    assert "review_code" in tasks
    assert "legal_analysis" in tasks
    assert "banking_compliance" in tasks

    medical_tasks = gateway.detect_tasks_from_content("patient diagnosis requires medical care")
    assert "medical_info" in medical_tasks

    tech_tasks = gateway.detect_tasks_from_content("AI and tech trends are evolving")
    assert "tech_trends" in tech_tasks


def test_read_file_smart_txt(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello world", encoding="utf-8")
    assert gateway.read_file_smart(sample) == "hello world"


def test_empty_file_handling(tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    output = gateway.run_gateway_on_file(empty)
    assert "الملف فارغ" in output
    assert output.strip().endswith("---")


def test_large_file_truncation():
    large_content = "a" * 60000
    with mock.patch("gateway.read_file_smart", return_value=large_content):
        output = gateway.run_gateway_on_file("/tmp/fake.txt")
    assert "50000" in output
    assert output.count("a") == 50000
    assert output.strip().endswith("---")


def test_invalid_file_format():
    with mock.patch("gateway.read_file_smart", side_effect=ValueError("bad format")):
        output = gateway.run_gateway_on_file("/tmp/invalid.bin")
    assert "تعذر قراءة الملف" in output
    assert "bad format" in output
    assert output.strip().endswith("---")


def test_call_model_mocked():
    with mock.patch("gateway.call_openai", return_value="openai ok") as openai_mock:
        result = gateway.call_model("openai", "prompt")
    openai_mock.assert_called_once_with("prompt", timeout=120)
    assert result == "openai ok"

    with mock.patch("gateway.call_groq", return_value="groq ok") as groq_mock:
        result = gateway.call_model("groq", "prompt")
    groq_mock.assert_called_once_with("prompt", timeout=120)
    assert result == "groq ok"

    with mock.patch("gateway.call_azure_openai", return_value="azure ok") as azure_mock:
        result = gateway.call_model("azure", "prompt")
    azure_mock.assert_called_once_with("prompt", timeout=120)
    assert result == "azure ok"

    with mock.patch("gateway.call_local_model", return_value="local ok") as local_mock:
        result = gateway.call_model("local", "prompt")
    local_mock.assert_called_once_with("prompt", timeout=120)
    assert result == "local ok"

    try:
        gateway.call_model("unknown", "prompt")
    except ValueError as exc:  # pragma: no cover
        assert "Unsupported provider" in str(exc)
