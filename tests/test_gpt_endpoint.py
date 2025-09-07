import os
import pytest

app = None
skip_reason = None

# Try canonical layout, then fallback
e1 = e2 = None
try:
    from search_hub.api.app import app as _app
    app = _app
except Exception as err1:
    e1 = err1
    try:
        from api_server import app as _app
        app = _app
    except Exception as err2:
        e2 = err2
        app = None
        skip_reason = f"Could not import FastAPI app: {e2 or e1}"

# Only try to import TestClient if we haven't decided to skip yet
if skip_reason is None:
    try:
        from fastapi.testclient import TestClient
    except Exception as err3:
        skip_reason = f"fastapi not installed: {err3}"

# Skip live test unless an API key is present
if skip_reason is None and not os.getenv("OPENAI_API_KEY"):
    skip_reason = "No OPENAI_API_KEY; skipping live GPT test"

@pytest.mark.skipif(skip_reason is not None, reason=skip_reason)
def test_gpt_endpoint_live():
    c = TestClient(app)
    r = c.post("/gpt", json={"prompt": "Hi"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "response" in data and isinstance(data["response"], str)
    assert 0 < len(data["response"]) <= 200
