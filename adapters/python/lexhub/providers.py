from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class AIClient:
    provider: str
    model: str
    def infer(self, prompt: str) -> Dict[str, Any]:
        return {"provider": self.provider, "model": self.model, "echo": prompt}

@dataclass
class Dataset:
    uri: str
    def head(self, n: int = 5):
        return [{"row": i, "value": f"sample-{i}"} for i in range(n)]

def connect_ai(provider: str, model: str) -> AIClient:
    return AIClient(provider=provider, model=model)

def connect_dataset(uri: str) -> Dataset:
    return Dataset(uri=uri)
