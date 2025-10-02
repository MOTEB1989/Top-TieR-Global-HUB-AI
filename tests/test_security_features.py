import importlib
import json
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def configured_app(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    mapping = {"admin-key": "admin", "dev-key": "dev", "viewer-key": "viewer"}
    monkeypatch.setenv("RBAC_API_KEYS", json.dumps(mapping))
    monkeypatch.setenv("RATE_LIMIT_REDIS_URL", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.delenv("SECRETS_BACKEND", raising=False)
    monkeypatch.delenv("RBAC_SECRET_PATH", raising=False)

    module = importlib.import_module("api_server")
    importlib.reload(module)

    client = TestClient(module.app)
    try:
        yield client
    finally:
        client.close()


def test_gpt_requires_role(configured_app: TestClient) -> None:
    response = configured_app.post("/gpt", json={"prompt": "hello"})
    assert response.status_code == 401

    response = configured_app.post(
        "/gpt",
        headers={"X-API-KEY": "viewer-key"},
        json={"prompt": "hello"},
    )
    assert response.status_code == 403


def test_gpt_allows_dev_role(configured_app: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    response = configured_app.post(
        "/gpt",
        headers={"X-API-KEY": "dev-key"},
        json={"prompt": "hello"},
    )
    # Service should authorise but fail because OpenAI key missing
    assert response.status_code in {400, 503}


def test_sync_requires_admin(configured_app: TestClient) -> None:
    response = configured_app.post(
        "/v1/sources/test/sync",
        headers={"X-API-KEY": "dev-key"},
    )
    assert response.status_code == 403

    response = configured_app.post(
        "/v1/sources/test/sync",
        headers={"X-API-KEY": "admin-key"},
    )
    # Ingestion may fail because of missing dependencies but RBAC passes first
    assert response.status_code in {200, 400, 404, 500}
