from __future__ import annotations

import os
from typing import Any

import requests

from services.local_llm.phi_runner import generate_local_phi


class PhiLocalClient:
    provider_name = "local_phi3"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("LOCAL_PHI_BASE_URL")

    def chat(self, prompt: str, model: str | None = None, **_: Any) -> str:
        if self.base_url:
            try:
                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={"messages": [{"role": "user", "content": prompt}], "model": model},
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except Exception:
                pass
        return generate_local_phi(prompt, model_path=model)


__all__ = ["PhiLocalClient"]
