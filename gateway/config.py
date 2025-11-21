import os
from typing import Optional

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
AZURE_MODEL = os.getenv("AZURE_MODEL", DEFAULT_MODEL)
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "local-llm")


def get_default_provider() -> str:
    return DEFAULT_PROVIDER


def get_default_model() -> str:
    return DEFAULT_MODEL
