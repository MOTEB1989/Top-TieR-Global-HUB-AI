"""FastAPI service for executing LexCode recipes with observability endpoints."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import Response

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from lexcode_runner import LexCodeRunner


app = FastAPI(title="LexCode Runner Service")


RUN_REQUESTS = Counter("runner_requests_total", "Total number of run requests")
RUN_ERRORS = Counter("runner_errors_total", "Total number of run errors")
RUN_DURATION = Histogram("runner_duration_seconds", "Duration of recipe runs in seconds")


class RunRequest(BaseModel):
    """Schema for runner invocations."""

    recipe: dict
    save: Optional[bool] = True


@app.post("/run")
async def run_recipe(req: RunRequest):
    """Execute a recipe using the LexCode runner."""

    RUN_REQUESTS.inc()
    start = time.perf_counter()
    recipe_path: Optional[Path] = None

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as handle:
            yaml.safe_dump(req.recipe, handle, allow_unicode=True, sort_keys=False)
            recipe_path = Path(handle.name)

        runner = LexCodeRunner(str(recipe_path))
        runner.run()

        RUN_DURATION.observe(time.perf_counter() - start)
        return {"status": "ok", "recipe": req.recipe if req.save else None}
    except Exception as exc:  # noqa: BLE001 - surface the raw error payload to clients
        RUN_ERRORS.inc()
        return {"status": "error", "error": str(exc)}
    finally:
        if recipe_path and not req.save and recipe_path.exists():
            try:
                recipe_path.unlink()
            except OSError:
                # If cleanup fails we do not want to impact the response path.
                pass


@app.get("/health")
async def health():
    """Liveness endpoint for orchestrators."""

    return {"status": "healthy", "service": "lexcode-runner"}


@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
