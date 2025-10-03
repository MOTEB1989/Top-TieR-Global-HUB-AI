"""Agent package exposing registry for orchestrator service."""

from .registry import AGENT_REGISTRY, get_agent_for_task

__all__ = ["AGENT_REGISTRY", "get_agent_for_task"]
