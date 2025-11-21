from __future__ import annotations

from typing import Any


class MockClient:
    provider_name = "mock"

    def chat(self, prompt: str, **_: Any) -> str:
        return f"[mock-response] {prompt[:100]}"


__all__ = ["MockClient"]
