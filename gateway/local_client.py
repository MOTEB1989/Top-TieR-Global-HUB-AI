import os
from typing import Any, Dict, List
from .base import LLMClient, Message, Completion, ensure_messages_format


class LocalLLMClient(LLMClient):
    provider = "local"

    def generate(self, messages: List[Message], **kwargs: Any) -> Completion:
        """
        Basic placeholder for a local LLM endpoint.

        Expected env vars:
        - LOCAL_LLM_BASE_URL (e.g., http://localhost:11434/v1/chat/completions)
        
        For now this only raises until wired to a real endpoint.
        """
        base_url = os.getenv("LOCAL_LLM_BASE_URL")
        raise RuntimeError(
            "LocalLLMClient is not wired yet. Set LOCAL_LLM_BASE_URL and implement HTTP call here."
        )
