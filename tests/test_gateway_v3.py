import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATEWAY_PATH = ROOT / "gateway.py"

spec = importlib.util.spec_from_file_location("gateway_module", GATEWAY_PATH)
gateway = importlib.util.module_from_spec(spec)
assert spec and spec.loader  # for mypy/static checks
spec.loader.exec_module(gateway)


def test_guess_task_from_path():
    assert gateway.guess_task_from_path("src/example.py") == "code_review"
    assert gateway.guess_task_from_path("notes/readme.md") == "document"
    assert gateway.guess_task_from_path("docs/laws/policy.txt") == "legal"
    assert gateway.guess_task_from_path("banking/report.yaml") == "banking"
    assert gateway.guess_task_from_path("research/summary.pdf") == "tech"
    assert gateway.guess_task_from_path("unknown/file.unknown") == "document"


def test_detect_tasks_from_content_multiple_domains():
    text = (
        "def handler(): pass\n"
        "هذه اتفاقية قانونية\n"
        "معاملة بنكية مع ضوابط aml\n"
        "تشخيص سريري وضغط الدم\n"
        "تقنيات ai وcloud متقدمة\n"
    )
    tasks = gateway.detect_tasks_from_content(text)
    assert "code_review" in tasks
    assert "legal" in tasks
    assert "banking" in tasks
    assert "medical" in tasks
    assert "tech" in tasks


def test_detect_tasks_from_content_default_document():
    assert gateway.detect_tasks_from_content("نص عادي بدون إشارات") == ["document"]


def test_read_file_smart_text_and_markdown(tmp_path: Path):
    txt = tmp_path / "sample.txt"
    txt.write_text("hello")
    md = tmp_path / "sample.md"
    md.write_text("# title")

    assert gateway.read_file_smart(str(txt)) == "hello"
    assert gateway.read_file_smart(str(md)) == "# title"


def test_read_file_smart_docx(monkeypatch, tmp_path: Path):
    sample = tmp_path / "sample.docx"
    sample.write_text("stub")

    class Paragraph:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeDoc:
        paragraphs = [Paragraph("hello"), Paragraph("world")]

    monkeypatch.setattr(gateway, "Document", lambda path: FakeDoc())

    content = gateway.read_file_smart(str(sample))
    assert content == "hello\nworld"


def test_read_file_smart_pdf(monkeypatch, tmp_path: Path):
    sample = tmp_path / "sample.pdf"
    sample.write_text("stub")

    class Page:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class FakeReader:
        def __init__(self, path: str) -> None:  # noqa: ARG002
            self.pages = [Page("one"), Page("two")]

    monkeypatch.setattr(gateway, "PdfReader", FakeReader)

    content = gateway.read_file_smart(str(sample))
    assert content == "one\ntwo"


def test_run_gateway_on_file_with_mocked_model(monkeypatch, tmp_path: Path):
    target = tmp_path / "code.py"
    target.write_text("def foo():\n    return 1\n")

    monkeypatch.setattr(gateway, "call_model", lambda system_prompt, user_content: "تمت المراجعة")

    output = gateway.run_gateway_on_file(str(target), task_mode="code_review")
    assert "🧠 المهمة: `code_review`" in output
    assert "تمت المراجعة" in output
