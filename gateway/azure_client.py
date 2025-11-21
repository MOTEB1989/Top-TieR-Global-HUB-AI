from typing import Any, Dict, List
from .base import LLMClient, Message, Completion, ensure_messages_format


class AzureOpenAIClient(LLMClient):
    provider = "azure"

    def generate(self, messages: List[Message], **kwargs: Any) -> Completion:
        """
        TODO: Implement Azure OpenAI client integration.

        Expected env vars:
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_DEPLOYMENT

        For now this client raises a RuntimeError to avoid silent misconfiguration.
        """
        raise RuntimeError("AzureOpenAIClient is not yet implemented. Configure Azure and update this client.")
