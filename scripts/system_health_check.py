#!/usr/bin/env python3
"""
Simple health checker for the RAG stack services.

Checks the availability of the following endpoints by default:
- Gateway: http://localhost:3000/health
- RAG Engine: http://localhost:8081/health
- Phi-3 Local Runner: http://localhost:8082/health
- Streamlit Web UI: http://localhost:8501
- Qdrant: http://localhost:6333/health (falls back to / if /health is unavailable)

The script prints a concise report and exits with status 0 even if some
services are unreachable, making it safe to run as an informational check.
"""
from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import List


@dataclass
class ServiceStatus:
    name: str
    url: str
    ok: bool
    message: str


def check_service(url: str, name: str) -> ServiceStatus:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status_code = response.getcode()
            return ServiceStatus(name=name, url=url, ok=200 <= status_code < 400, message=f"HTTP {status_code}")
    except urllib.error.HTTPError as exc:
        return ServiceStatus(name=name, url=url, ok=False, message=f"HTTP {exc.code}")
    except urllib.error.URLError as exc:
        return ServiceStatus(name=name, url=url, ok=False, message=str(exc.reason))
    except Exception as exc:  # pragma: no cover - defensive catch
        return ServiceStatus(name=name, url=url, ok=False, message=str(exc))


def print_report(report: List[ServiceStatus]) -> None:
    print("\n===== System Health Report =====")
    for entry in report:
        status_icon = "✅" if entry.ok else "❌"
        print(f"{status_icon} {entry.name:<20} {entry.url} — {entry.message}")
    print("================================\n")


def main() -> None:
    report: List[ServiceStatus] = []

    report.append(check_service("http://localhost:3000/health", "Gateway"))
    report.append(check_service("http://localhost:8081/health", "RAG Engine"))
    report.append(check_service("http://localhost:8082/health", "Phi-3 Local Runner"))
    report.append(check_service("http://localhost:8501", "Streamlit Web UI"))

    # Qdrant health: try /health first, fall back to root if needed.
    qdrant_status = check_service("http://localhost:6333/health", "Qdrant")
    if not qdrant_status.ok:
        qdrant_status = check_service("http://localhost:6333", "Qdrant")
    report.append(qdrant_status)

    print_report(report)


if __name__ == "__main__":
    main()
