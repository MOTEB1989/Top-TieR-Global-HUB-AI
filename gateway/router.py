"""Simplified chat gateway used by local RAG flows."""
from __future__ import annotations

import os
from typing import Optional

import openai

from gpt_client import GPTClient

DEFAULT_MODEL = os.getenv("DEFAULT_CHAT_MODEL", "gpt-3.5-turbo")


def simple_chat(prompt: str, provider: Optional[str] = None, model: Optional[str] = None) -> str:
    """Return a single-turn chat completion using the existing GPT client."""
    client = GPTClient()
    if not client.is_available():
        raise RuntimeError("OpenAI API key not configured for chat gateway.")

    openai.api_key = client.api_key
    engine = (model or DEFAULT_MODEL)
    if engine == "gpt-3.5-turbo":
        engine = "text-davinci-003"

    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=512,
        temperature=0.2,
    )
    return response.choices[0].text.strip()
