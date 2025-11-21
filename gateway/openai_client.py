import os
from typing import Any, Dict, List
from .base import LLMClient, ensure_messages_format, Message, Completion


class OpenAIClient(LLMClient):
    provider = "openai"

    def _get_client(self):
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("openai package is not installed; install 'openai' to use OpenAIClient.") from exc

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        openai.api_key = api_key
        return openai

    def generate(self, messages: List[Message], **kwargs: Any) -> Completion:
        openai = self._get_client()
        msgs = ensure_messages_format(messages)
        resp = openai.ChatCompletion.create(model=self.model, messages=msgs, **kwargs)
        choice = resp["choices"][0]
        text = choice["message"]["content"]
        usage = resp.get("usage", {})
        return {
            "text": text,
            "model": resp.get("model", self.model),
            "provider": self.provider,
            "usage": usage,
            "raw": resp,
        }
