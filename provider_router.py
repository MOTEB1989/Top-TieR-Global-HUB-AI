import os
from typing import Callable, Dict

from anthropic_provider import AnthropicProvider
from base_provider import BaseProvider
from hf_provider import HuggingFaceProvider
from openai_provider import OpenAIProvider


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value


def _build_factories() -> Dict[str, Callable[[], BaseProvider]]:
    return {
        "openai": lambda: OpenAIProvider(_require_env("OPENAI_API_KEY")),
        "anthropic": lambda: AnthropicProvider(_require_env("ANTHROPIC_API_KEY")),
        "huggingface": lambda: HuggingFaceProvider(_require_env("HF_API_KEY")),
    }


_PROVIDER_FACTORIES = _build_factories()
_PROVIDER_CACHE: Dict[str, BaseProvider] = {}
_DEFAULT_PROVIDER = "openai"


def get_provider(name: str) -> BaseProvider:
    """Return a provider instance by name, defaulting to OpenAI."""
    if not name:
        name = _DEFAULT_PROVIDER

    normalized_name = name.lower()
    if normalized_name not in _PROVIDER_FACTORIES:
        normalized_name = _DEFAULT_PROVIDER

    if normalized_name not in _PROVIDER_CACHE:
        _PROVIDER_CACHE[normalized_name] = _PROVIDER_FACTORIES[normalized_name]()

    return _PROVIDER_CACHE[normalized_name]
