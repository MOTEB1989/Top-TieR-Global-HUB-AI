from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    """Abstract base class for AI inference providers."""

    @abstractmethod
    async def infer(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate a response for the supplied prompt using the given model."""
        raise NotImplementedError
