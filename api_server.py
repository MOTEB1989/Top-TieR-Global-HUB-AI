from fastapi import FastAPI
from pydantic import BaseModel
import subprocess, json, shlex

app = FastAPI(title="Veritas Console API")

class RunRequest(BaseModel):
    command: str   # analyze|verify|evaluate|report|search|trace
    domain: str    # osint|medical|realestate|legal
    target: str
    scope: str = "basic"
    depth: str = "basic"
    sources: str = "auto"

@app.post("/run")
def run(req: RunRequest):
    flag = "--target"
    if req.command == "verify": flag = "--value"
    elif req.command == "evaluate": flag = "--property"
    elif req.command == "report": flag = "--identifier"
    elif req.command == "search": flag = "--query"
    cmd = [
        "python", "veritas_console.py",
        req.command,
        "--domain", req.domain,
        flag, req.target,
        "--scope", req.scope,
        "--depth", req.depth,
        "--sources", req.sources
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return json.loads(out.decode("utf-8"))
