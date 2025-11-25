import os
from typing import Any, Dict, List, Optional
from .base import Message, Completion
from .config import get_default_provider, get_default_model
from .openai_client import OpenAIClient
from .groq_client import GroqClient
from .azure_client import AzureOpenAIClient
from .local_client import LocalLLMClient


def get_gateway(provider: Optional[str] = None, model: Optional[str] = None):
    provider = (provider or get_default_provider()).lower()
    model = model or get_default_model()

    if provider == "openai":
        return OpenAIClient(model=model)
    if provider == "groq":
        return GroqClient(model=model)
    if provider == "azure":
        return AzureOpenAIClient(model=model)
    if provider == "local":
        return LocalLLMClient(model=model)
    raise ValueError(f"Unsupported LLM provider: {provider}")


def simple_chat(prompt: str, provider: Optional[str] = None, model: Optional[str] = None, **kwargs: Any) -> str:
    client = get_gateway(provider=provider, model=model)
    result: Completion = client.generate(prompt, **kwargs)
    return result.get("text", "")
