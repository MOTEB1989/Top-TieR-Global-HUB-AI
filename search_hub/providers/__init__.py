from .searxng import SearxProvider
from .yacy import YaCyProvider
from .huggingface import HuggingFaceProvider
from .arxiv import ArxivProvider
from .paperswithcode import PapersWithCodeProvider
from .github import GitHubProvider

class ProviderRegistry:
    def __init__(self):
        self._providers = {
            "searxng": SearxProvider(),
            "yacy": YaCyProvider(),
            "huggingface": HuggingFaceProvider(),
            "arxiv": ArxivProvider(),
            "paperswithcode": PapersWithCodeProvider(),
            "github": GitHubProvider(),
        }
    def get_provider(self, name: str):
        if name not in self._providers:
            raise ValueError(f"Unknown provider {name}")
        return self._providers[name]

registry = ProviderRegistry()
