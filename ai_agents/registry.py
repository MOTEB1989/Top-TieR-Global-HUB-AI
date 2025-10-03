"""Registry mapping logical names to instantiated agents."""
from __future__ import annotations

from typing import Dict

from ai_agents.base import BaseAgent
from ai_agents.mohsen_jj.agent import AGENT as MOHSEN_JJ_AGENT
from ai_agents.saudi_banks.agent import AGENT as SAUDI_BANKS_AGENT
from ai_agents.saudi_nexus.agent import AGENT as SAUDI_NEXUS_AGENT

AGENT_REGISTRY: Dict[str, BaseAgent] = {
    SAUDI_NEXUS_AGENT.name: SAUDI_NEXUS_AGENT,
    MOHSEN_JJ_AGENT.name: MOHSEN_JJ_AGENT,
    SAUDI_BANKS_AGENT.name: SAUDI_BANKS_AGENT,
}


def get_agent_for_task(task: str) -> BaseAgent | None:
    task_lower = task.lower()
    for agent in AGENT_REGISTRY.values():
        if agent.can_handle(task_lower):
            return agent
    return None
