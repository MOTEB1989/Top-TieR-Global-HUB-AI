"""Common building blocks for domain-specific agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass
class AgentResponse:
    """Normalized response returned by every agent."""

    agent: str
    task: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    """Minimal interface that every agent implementation must satisfy."""

    name: str = "base-agent"
    description: str = ""
    capabilities: Iterable[str] = ()

    def can_handle(self, task: str) -> bool:
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in self.capabilities)

    def run(self, task: str, payload: Dict[str, Any] | None = None) -> AgentResponse:
        raise NotImplementedError("Agents must implement the `run` method.")

    def summarize_capabilities(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": list(self.capabilities),
        }


def summarize_agents(agents: Iterable[BaseAgent]) -> List[Dict[str, Any]]:
    return [agent.summarize_capabilities() for agent in agents]
