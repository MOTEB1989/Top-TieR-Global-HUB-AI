"""FastAPI orchestrator routing tasks across specialized agents."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from ai_agents import AGENT_REGISTRY, get_agent_for_task
from ai_agents.base import AgentResponse, BaseAgent, summarize_agents
from ai_agents.lex_orchestrator.agent import AGENT as LEX_ORCHESTRATOR

CORE_INFER_URL = os.environ.get("CORE_URL", "http://core:3000/v1/ai/infer")


class TaskRequest(BaseModel):
    task: str = Field(..., description="High level instruction to execute.")
    payload: Dict[str, Any] | None = Field(
        default=None, description="Optional contextual data for the agent."
    )
    agent: Optional[str] = Field(
        default=None,
        description="Force a specific agent to handle the task. If omitted the orchestrator will choose.",
    )
    delegate_to_core: bool = Field(
        default=False,
        description="Whether to call the core inference service with the provided prompt.",
    )


class TaskResponse(BaseModel):
    agent: str
    task: str
    output: str
    metadata: Dict[str, Any]


app = FastAPI(title="Lex Orchestrator API", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/agents")
def list_agents() -> Dict[str, Any]:
    return {"agents": summarize_agents(AGENT_REGISTRY.values())}


async def _call_core_infer(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="delegate_to_core requires a 'prompt' entry in payload.",
        )

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(CORE_INFER_URL, json={"prompt": prompt, **payload})
        response.raise_for_status()
    return response.json()


@app.post("/v1/lex/run", response_model=TaskResponse)
async def run_task(request: TaskRequest) -> TaskResponse:
    agent: BaseAgent | None = None
    if request.agent:
        if request.agent == LEX_ORCHESTRATOR.name:
            agent = LEX_ORCHESTRATOR
        else:
            agent = AGENT_REGISTRY.get(request.agent)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Unknown agent '{request.agent}'.",
                )
    else:
        agent = get_agent_for_task(request.task) or LEX_ORCHESTRATOR

    try:
        agent_response: AgentResponse = agent.run(request.task, request.payload)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent '{agent.name}' failed to handle task: {exc}",
        ) from exc

    metadata = dict(agent_response.metadata)
    if request.delegate_to_core:
        core_metadata = await _call_core_infer(request.payload or {})
        metadata["core"] = core_metadata

    return TaskResponse(
        agent=agent_response.agent,
        task=agent_response.task,
        output=agent_response.output,
        metadata=metadata,
    )
