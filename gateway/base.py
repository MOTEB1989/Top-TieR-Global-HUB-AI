from abc import ABC, abstractmethod
from typing import Any, Dict, List

Message = Dict[str, str]
Completion = Dict[str, Any]


class LLMClient(ABC):
    provider: str
    model: str

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def generate(self, messages: List[Message], **kwargs: Any) -> Completion:
        """Return a normalized completion dict."""


def ensure_messages_format(prompt_or_messages: Any) -> List[Message]:
    if isinstance(prompt_or_messages, str):
        return [{"role": "user", "content": prompt_or_messages}]
    if isinstance(prompt_or_messages, list):
        return prompt_or_messages
    raise TypeError(
        "Messages must be a string prompt or a list of message dictionaries with role/content."
    )
