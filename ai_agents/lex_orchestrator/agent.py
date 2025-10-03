"""Lex Orchestrator – meta coordinator across domain agents."""
from __future__ import annotations

from typing import Any, Dict, List

from ai_agents.base import AgentResponse, BaseAgent, summarize_agents
from ai_agents.registry import AGENT_REGISTRY


class LexOrchestratorAgent(BaseAgent):
    name = "lex_orchestrator"
    description = "Routes tasks to domain experts and aggregates their responses."
    capabilities = ("coordinate", "orchestrate", "route", "overview")

    def run(self, task: str, payload: Dict[str, Any] | None = None) -> AgentResponse:
        payload = payload or {}
        summary: List[Dict[str, Any]] = summarize_agents(AGENT_REGISTRY.values())
        message = (
            "Lex orchestrator online. Available specialists summarised for "
            "routing. Submit task details via orchestrator API to delegate."
        )
        return AgentResponse(
            agent=self.name,
            task=task,
            output=message,
            metadata={"agents": summary, "context": payload},
        )


AGENT = LexOrchestratorAgent()
