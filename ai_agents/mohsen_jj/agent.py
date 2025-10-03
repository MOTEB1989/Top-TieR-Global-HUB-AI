"""Mohsen JJ – code explainer and reviewer."""
from __future__ import annotations

from typing import Any, Dict

from ai_agents.base import AgentResponse, BaseAgent


class MohsenJJAgent(BaseAgent):
    name = "mohsen_jj"
    description = "Explains source code, comments on changes, and annotates diffs."
    capabilities = ("explain", "comment", "document", "code", "annotate")

    def run(self, task: str, payload: Dict[str, Any] | None = None) -> AgentResponse:
        payload = payload or {}
        file_path = payload.get("file_path", "unknown file")
        commentary = (
            f"Reviewing {file_path}. Highlighting readability improvements, "
            "complexity hotspots, and documenting intent for future maintainers."
        )
        return AgentResponse(
            agent=self.name,
            task=task,
            output=commentary,
            metadata={"context": payload},
        )


AGENT = MohsenJJAgent()
