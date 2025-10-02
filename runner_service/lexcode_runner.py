"""Lightweight recipe runner used by the FastAPI wrapper service.

This implementation focuses on being easy to extend while still
providing useful behaviour out of the box.  The runner loads a YAML
recipe file that follows the LexCode conventions and executes each
listed task sequentially.  For now, a task simply logs the configured
steps which is enough for integration testing and future expansion.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

logger = logging.getLogger(__name__)


class LexCodeRunner:
    """Execute a LexCode recipe stored in a YAML file."""

    def __init__(self, recipe_path: str | Path) -> None:
        self.recipe_path = Path(recipe_path)
        if not self.recipe_path.exists():
            raise FileNotFoundError(f"Recipe file not found: {self.recipe_path}")

    def load_recipe(self) -> Dict[str, Any]:
        """Load and return the recipe from disk."""
        with self.recipe_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        if not isinstance(data, dict):
            raise ValueError("Recipe file must contain a YAML mapping at the top level")
        return data

    def run(self) -> None:
        """Execute the recipe.

        The default implementation iterates over tasks and steps,
        logging information about the execution.  This is sufficient for
        the API wrapper to confirm that recipes are dispatched correctly
        without requiring any backend services.
        """

        recipe = self.load_recipe()
        project = recipe.get("project", "<unknown>")
        logger.info("Running LexCode recipe for project %s", project)

        tasks: Iterable[Dict[str, Any]] = recipe.get("tasks", []) or []
        if not isinstance(tasks, Iterable):
            raise ValueError("Recipe 'tasks' must be an iterable of task definitions")

        for task in tasks:
            self._run_task(task)

        logger.info("Completed LexCode recipe for project %s", project)

    def _run_task(self, task: Dict[str, Any]) -> None:
        task_id = task.get("id", "<unknown>")
        task_name = task.get("name", task_id)
        logger.info("Starting task %s (%s)", task_id, task_name)

        steps: List[Dict[str, Any]] = task.get("steps", []) or []
        if not isinstance(steps, list):
            raise ValueError(f"Task {task_id} steps must be a list")

        for index, step in enumerate(steps, start=1):
            self._run_step(task_id, index, step)

        logger.info("Finished task %s (%s)", task_id, task_name)

    def _run_step(self, task_id: str, step_number: int, step: Dict[str, Any]) -> None:
        if not isinstance(step, dict):
            raise ValueError(f"Task {task_id} step {step_number} must be a mapping")

        process = step.get("process", {})
        if not isinstance(process, dict):
            raise ValueError(f"Task {task_id} step {step_number} process must be a mapping")

        model = process.get("model", "<unspecified-model>")
        prompt = process.get("prompt", "")
        logger.info(
            "Task %s step %d -> model=%s prompt=%s",
            task_id,
            step_number,
            model,
            prompt,
        )

        # Future implementations could integrate with LLMs or other backends here.
        # For now we only log the step execution to keep the runner lightweight.


__all__ = ["LexCodeRunner"]
