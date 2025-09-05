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
    cmd = f"python veritas_console.py {shlex.quote(req.command)} --domain {shlex.quote(req.domain)} {flag} {shlex.quote(req.target)} --scope {shlex.quote(req.scope)} --depth {shlex.quote(req.depth)} --sources {shlex.quote(req.sources)}"
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    return json.loads(out.decode("utf-8"))
