#!/usr/bin/env python3
# scripts/lexcode.py
import os, re, json, sys, subprocess, socket, pathlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / "ops"
OPS.mkdir(exist_ok=True)

# ---------- Utilities ----------
def sh(cmd, check=True, env=None):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, env=env or os.environ, text=True, capture_output=True)

def which(binname):
    from shutil import which as _w
    return _w(binname)

def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# ---------- Route Scanner ----------
JS_PATTERNS = [
    r'\bapp\.(get|post|put|patch|delete|options|head)\(["\']([^"\']+)["\']',
    r'\brouter\.(get|post|put|patch|delete|options|head)\(["\']([^"\']+)["\']',
    r'\bfastify\.(get|post|put|patch|delete|options|head)\(["\']([^"\']+)["\']',
    r'\bserver\.route\(\s*{\s*method:\s*["\']?([A-Z]+)["\']?,\s*path:\s*["\']([^"\']+)["\']',
]
RS_PATTERNS = [
    # axum: .route("/v1/ai/infer", get(handler))
    r'\.route\(\s*["\']([^"\']+)["\']\s*,\s*(get|post|put|delete|patch)',
    # actix: #[get("/health")]  #[post("/v1/ai/infer")]
    r'#\s*\[(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)\]',
    # rocket: #[get("/health")]
    r'#\s*\[(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']\s*\)\]',
]

PORT_HINTS = {
    "external": [3000],
    "internal": [8080],
}

def scan_routes():
    routes = []
    for ext in ("*.js","*.ts","*.mjs","*.cjs","*.rs"):
        for p in ROOT.rglob(ext):
            if "node_modules" in p.parts or "target" in p.parts:
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if p.suffix in (".js",".ts",".mjs",".cjs"):
                for pat in JS_PATTERNS:
                    for m in re.finditer(pat, txt, re.I):
                        method, path = (m.group(1).upper(), m.group(2))
                        routes.append({"file": str(p.relative_to(ROOT)), "method": method, "path": path, "lang":"js"})
            elif p.suffix == ".rs":
                for pat in RS_PATTERNS:
                    for m in re.finditer(pat, txt, re.I):
                        if pat.startswith(r'\.route'):
                            path, method = (m.group(1), m.group(2).upper())
                        else:
                            method, path = (m.group(1).upper(), m.group(2))
                        routes.append({"file": str(p.relative_to(ROOT)), "method": method, "path": path, "lang":"rs"})

    # Guess layer by port references in files
    def guess_layer(route):
        file = route["file"]
        try:
            txt = (ROOT / file).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return "unknown"
        internal_hits = sum(str(p) in txt for p in PORT_HINTS["internal"])
        external_hits = sum(str(p) in txt for p in PORT_HINTS["external"])
        if external_hits and not internal_hits:
            return "external"
        if internal_hits and not external_hits:
            return "internal"
        return "unknown"

    for r in routes:
        r["layer"] = guess_layer(r)

    return routes

# ---------- Tunnels ----------
def start_cloudflare_tunnel():
    # Requires: cloudflared + CF_TUNNEL_TOKEN env
    token = os.environ.get("CF_TUNNEL_TOKEN")
    if not which("cloudflared") or not token:
        return None
    # Start named tunnel in quick mode
    proc = subprocess.Popen(["cloudflared","tunnel","--no-autoupdate","run"],
                            env=dict(os.environ, CF_TUNNEL_TOKEN=token),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(2)
    # Try to extract hostname from logs
    url = None
    t0 = time.time()
    while time.time() - t0 < 20:
        line = proc.stdout.readline().strip()
        if not line:
            continue
        if "trycloudflare.com" in line or "https://" in line:
            m = re.search(r'https://[^\s]+' , line)
            if m:
                url = m.group(0)
                break
    return {"provider":"cloudflare","url":url, "proc":proc}

def start_ngrok_tunnel(port):
    if not which("ngrok"):
        return None
    token = os.environ.get("NGROK_AUTHTOKEN")
    if token:
        sh(["ngrok","config","add-authtoken", token], check=False)
    proc = subprocess.Popen(["ngrok","http",str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # ngrok prints url to a TUI; fallback to API-less parse via logs
    url = None
    t0 = time.time()
    while time.time() - t0 < 20:
        line = proc.stdout.readline()
        if "url=" in line and "https://" in line:
            m = re.search(r'https://[^\s]+' , line)
            if m:
                url = m.group(0)
                break
    return {"provider":"ngrok","url":url, "proc":proc}

def best_public_url(preferred_port=3000):
    # 1) Cloudflare
    cf = start_cloudflare_tunnel()
    if cf and cf["url"]:
        return cf
    # 2) ngrok
    ng = start_ngrok_tunnel(preferred_port)
    if ng and ng["url"]:
        return ng
    # 3) LAN fallback
    ip = lan_ip()
    return {"provider":"lan","url":f"http://{ip}:{preferred_port}","proc":None}

# ---------- Postman export ----------
def export_postman(routes, base_url, outfile):
    coll = {
      "info": {"name": "LexCode API Collection", "_postman_id": "lexcode-auto", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
      "item": []
    }
    seen = set()
    for r in routes:
      path = r["path"]
      if not path.startswith("/"):
          path = "/" + path
      key = (r["method"], path)
      if key in seen: 
          continue
      seen.add(key)
      coll["item"].append({
        "name": f"{r['method']} {path}",
        "request": {
          "method": r["method"],
          "header": [{"key":"Content-Type","value":"application/json"}],
          "url": {"raw": base_url + path, "protocol":"https" if base_url.startswith("https") else "http",
                  "host":[base_url.replace("https://","").replace("http://","").split('/')[0]],
                  "path": [p for p in path.split('/') if p]},
          "body": {"mode":"raw","raw":"{\n  \"input\": \"hello\"\n}"}
        }
      })
    Path(outfile).write_text(json.dumps(coll, indent=2), encoding="utf-8")

# ---------- CLI ----------
def main():
    if len(sys.argv) < 2:
        print("Usage:\n  lexcode.py routes        # scan & save report\n  lexcode.py tunnel [port] # start best tunnel (prefers 3000)\n  lexcode.py all           # routes + tunnel + postman export")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "routes":
        routes = scan_routes()
        report = {"count": len(routes), "routes": routes}
        (OPS / "routes.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[OK] routes saved -> {OPS/'routes.json'}")
    elif cmd == "tunnel":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        t = best_public_url(port)
        print(json.dumps({"provider":t["provider"], "url":t["url"]}, indent=2))
    elif cmd == "all":
        routes = scan_routes()
        (OPS / "routes.json").write_text(json.dumps({"count":len(routes),"routes":routes}, indent=2), encoding="utf-8")
        print(f"[OK] routes saved -> {OPS/'routes.json'}")
        t = best_public_url(3000)
        base = t["url"]
        export_postman(routes, base, OPS / "api_collection.postman.json")
        print(json.dumps({
            "tunnel": {"provider": t["provider"], "base_url": base},
            "files": {
                "routes": str(OPS / "routes.json"),
                "postman": str(OPS / "api_collection.postman.json")
            }
        }, indent=2))
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
