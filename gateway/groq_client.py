import os
from typing import Any, Dict, List
from .base import LLMClient, ensure_messages_format, Message, Completion


class GroqClient(LLMClient):
    provider = "groq"

    def _get_client(self):
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("groq package is not installed; install 'groq' to use GroqClient.") from exc

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in the environment.")
        return Groq(api_key=api_key)

    def generate(self, messages: List[Message], **kwargs: Any) -> Completion:
        client = self._get_client()
        msgs = ensure_messages_format(messages)
        resp = client.chat.completions.create(model=self.model, messages=msgs, **kwargs)
        choice = resp.choices[0]
        text = choice.message.content or ""
        usage = getattr(resp, "usage", None)
        usage_dict = dict(usage) if isinstance(usage, dict) else {}
        return {
            "text": text,
            "model": resp.model or self.model,
            "provider": self.provider,
            "usage": usage_dict,
            "raw": resp,
        }
