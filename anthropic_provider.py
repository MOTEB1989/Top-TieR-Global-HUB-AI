from typing import Optional

from anthropic import AsyncAnthropic

from base_provider import BaseProvider


_DEFAULT_MODEL = "claude-2.1"


class AnthropicProvider(BaseProvider):
    """Inference provider backed by Anthropic's Claude models."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Anthropic API key must be provided")
        self.client = AsyncAnthropic(api_key=api_key)

    async def infer(self, prompt: str, model: Optional[str] = None) -> str:
        model_name = model or _DEFAULT_MODEL
        response = await self.client.messages.create(
            model=model_name,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()
