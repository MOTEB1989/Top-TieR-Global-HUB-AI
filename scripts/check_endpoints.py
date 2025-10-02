#!/usr/bin/env python3
"""Utility script to probe internal and external service endpoints."""
from __future__ import annotations

import json
import os
import socket
from typing import Dict, Optional

import requests

# Candidate endpoints that we probe for availability
CANDIDATES: Dict[str, Optional[str]] = {
    "local_gateway": "http://localhost:3000/v1/ai/infer",
    "lan_gateway": None,  # Will be populated by the LAN IP if available
    "rust_internal": "http://localhost:8080/health",
    "runner_local": "http://localhost:8000/runner/run",
    "lexcode_api": "https://api.lexcode.ai/chat",
    "lexcode_runner": "https://runner.lexcode.ai",
    "lexcode_hub": "https://hub.lexcode.ai",
    "lexcode_grafana": "https://grafana.lexcode.ai",
    "lexcode_kb": "https://kb.lexcode.ai",
}


def get_lan_ip() -> Optional[str]:
    """Determine the LAN IP address for the current machine, if possible."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


def check(url: str) -> Dict[str, Optional[object]]:
    """Perform a simple GET request to the URL and capture the result."""
    try:
        response = requests.get(url, timeout=3)
        return {"status": response.status_code, "ok": response.ok}
    except Exception as exc:  # noqa: BLE001 - capturing any requests exception
        return {"status": None, "ok": False, "error": str(exc)}


def main() -> None:
    lan_ip = get_lan_ip()
    if lan_ip:
        CANDIDATES["lan_gateway"] = f"http://{lan_ip}:3000/v1/ai/infer"

    results: Dict[str, Dict[str, Optional[object]]] = {}
    for name, url in CANDIDATES.items():
        if url:
            results[name] = {"url": url, **check(url)}

    os.makedirs("ops", exist_ok=True)
    report_path = os.path.join("ops", "endpoints_report.json")
    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
