from __future__ import annotations

import os
from typing import Any

try:  # pragma: no cover - optional
    from openai import OpenAI
except Exception:  # pragma: no cover - optional
    OpenAI = None

import requests

from gateway.mock_client import MockClient
from gateway.phi_local_client import PhiLocalClient


class _OpenAIClient:
    provider_name = "openai"

    def __init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        self.client = OpenAI()

    def chat(self, prompt: str, model: str | None = None, **kwargs: Any) -> str:  # pragma: no cover - network
        response = self.client.chat.completions.create(
            model=model or os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.2),
        )
        return response.choices[0].message.content


class _GroqClient:
    provider_name = "groq"

    def chat(self, prompt: str, model: str | None = None, **kwargs: Any) -> str:  # pragma: no cover - network
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "model": model or os.getenv("LLM_MODEL", "mixtral-8x7b-32768"),
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        resp.raise_for_status()
        payload = resp.json()
        return payload.get("choices", [{}])[0].get("message", {}).get("content", "")


_PROVIDERS = {
    "mock": MockClient,
    "phi3": PhiLocalClient,
    "local_phi3": PhiLocalClient,
    "openai": _OpenAIClient,
    "groq": _GroqClient,
}


def _get_client(provider: str):
    provider_key = provider.lower()
    if provider_key not in _PROVIDERS:
        raise RuntimeError(f"Unsupported provider {provider}")
    return _PROVIDERS[provider_key]()


def simple_chat(prompt: str, provider: str | None = None, model: str | None = None, **kwargs: Any) -> str:
    provider = provider or os.getenv("LLM_PROVIDER", "mock")
    client = _get_client(provider)
    return client.chat(prompt, model=model or os.getenv("LLM_MODEL"), **kwargs)


__all__ = ["simple_chat"]
