"""FastAPI wrapper service for the :class:`LexCodeRunner`.

The service accepts a recipe payload, stores it in a temporary YAML
file and delegates execution to the Python runner.  It mirrors the API
shape described in the product specification so that downstream
services can integrate with a stable contract.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from lexcode_runner import LexCodeRunner

app = FastAPI(title="LexCode Runner Service")


class RunRequest(BaseModel):
    recipe: dict
    save: Optional[bool] = True


@app.post("/run")
async def run_recipe(req: RunRequest):
    """Persist the recipe to disk, run it and return the execution status."""
    tmp_file: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yml", delete=False, encoding="utf-8"
        ) as handle:
            yaml.dump(req.recipe, handle, allow_unicode=True)
            tmp_file = Path(handle.name)

        runner = LexCodeRunner(tmp_file)
        runner.run()
    except Exception as exc:  # pragma: no cover - defensive, ensures API response
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if tmp_file and tmp_file.exists():
            os.unlink(tmp_file)

    if req.save:
        return {"status": "ok", "recipe": req.recipe}
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "lexcode-runner"}
