import tempfile
import time
from typing import Optional

import yaml
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

from lexcode_runner import LexCodeRunner
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="LexCode Runner Service")

RUN_REQUESTS = Counter("runner_requests_total", "عدد طلبات التشغيل")
RUN_ERRORS = Counter("runner_errors_total", "عدد الأخطاء أثناء التشغيل")
RUN_DURATION = Histogram("runner_duration_seconds", "مدة تشغيل الوصفة بالثواني")


class RunRequest(BaseModel):
    recipe: dict
    save: Optional[bool] = True


@app.post("/run")
async def run_recipe(req: RunRequest):
    RUN_REQUESTS.inc()
    start = time.time()
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(req.recipe, f, allow_unicode=True)
            recipe_path = f.name

        runner = LexCodeRunner(recipe_path)
        runner.run()

        RUN_DURATION.observe(time.time() - start)
        return {"status": "ok", "recipe": req.recipe if req.save else None}

    except Exception as e:  # pylint: disable=broad-except
        RUN_ERRORS.inc()
        return {"status": "error", "error": str(e)}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "lexcode-runner"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
