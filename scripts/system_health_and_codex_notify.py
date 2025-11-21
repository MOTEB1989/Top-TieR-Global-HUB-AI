#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Shared helpers for building system health reports and notifying Codex in CI."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple


REQUIRED_ENV_KEYS: List[str] = [
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "NEO4J_URI",
    "QDRANT_URL",
]


class CheckResult:
    """Simple container for health check results."""

    def __init__(self, name: str, passed: bool, details: str):
        self.name = name
        self.passed = passed
        self.details = details

    def to_markdown(self) -> str:
        status = "✅" if self.passed else "⚠️"
        return f"- {status} **{self.name}** — {self.details}"


def run_command(cmd: Iterable[str]) -> Tuple[str, bool]:
    """Execute a command and return its output and success flag."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    output = (result.stdout or result.stderr).strip()
    return output, result.returncode == 0


def check_env_vars() -> CheckResult:
    missing = [key for key in REQUIRED_ENV_KEYS if not os.getenv(key)]
    if missing:
        return CheckResult("Environment variables", False, f"Missing: {', '.join(missing)}")
    return CheckResult("Environment variables", True, "All required keys are present.")


def check_docker_compose() -> CheckResult:
    compose_path = Path("docker-compose.yml")
    if not compose_path.exists():
        return CheckResult("Docker Compose", False, "docker-compose.yml is missing.")
    return CheckResult("Docker Compose", True, "docker-compose.yml found.")


def check_git_status() -> CheckResult:
    output, ok = run_command(["git", "status", "--short"])
    if not ok:
        return CheckResult("Git", False, "Unable to read repository status.")
    if output:
        return CheckResult("Git", False, f"Working tree has changes:\n{output}")
    return CheckResult("Git", True, "Working tree is clean.")


def check_python() -> CheckResult:
    version = platform.python_version()
    return CheckResult("Python", True, f"Python {version} detected.")


def build_markdown_report() -> str:
    """Build a markdown-formatted health report."""
    checks = [
        check_python(),
        check_env_vars(),
        check_docker_compose(),
        check_git_status(),
    ]

    lines = ["# System Health Report", ""]
    lines.extend(check.to_markdown() for check in checks)

    return "\n".join(lines)


def notify_codex_if_ci(report: str) -> None:
    """Persist a report for Codex consumption when running in CI."""
    if not os.getenv("CI"):
        return

    artifact_path = Path("auto_diagnose_report.md")
    artifact_path.write_text(report, encoding="utf-8")
    print(f"Codex notification stub: wrote report to {artifact_path} for CI collection.")


__all__ = [
    "build_markdown_report",
    "notify_codex_if_ci",
]
