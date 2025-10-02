from typing import Optional

import openai

from base_provider import BaseProvider


_DEFAULT_MODEL = "gpt-3.5-turbo"


class OpenAIProvider(BaseProvider):
    """Inference provider backed by OpenAI's chat completion API."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key must be provided")
        openai.api_key = api_key

    async def infer(self, prompt: str, model: Optional[str] = None) -> str:
        model_name = model or _DEFAULT_MODEL
        response = await openai.ChatCompletion.acreate(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["choices"][0]["message"]["content"].strip()
