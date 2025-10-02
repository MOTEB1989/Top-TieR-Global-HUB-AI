"""Lightweight LexCode runner implementation used by the runner service."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class LexCodeRunner:
    """Execute a LexCode recipe stored on disk."""

    def __init__(self, recipe_path: str) -> None:
        self.recipe_path = Path(recipe_path)

    def _load_recipe(self) -> Dict[str, Any]:
        if not self.recipe_path.exists():
            msg = f"Recipe file not found: {self.recipe_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        with self.recipe_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        logger.debug("Loaded recipe with keys: %s", list(data.keys()))
        return data

    def run(self) -> None:
        recipe = self._load_recipe()

        steps = recipe.get("steps") or []
        if not isinstance(steps, list):
            logger.warning("Recipe 'steps' is not a list; skipping execution pipeline.")
            return

        for index, step in enumerate(steps, start=1):
            step_name = step.get("name") if isinstance(step, dict) else None
            logger.info("Executing step %s/%s: %s", index, len(steps), step_name or "unnamed-step")

        logger.info("LexCode recipe execution completed for %s", self.recipe_path)
