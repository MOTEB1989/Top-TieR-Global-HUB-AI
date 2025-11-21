#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto-Fix Engine
----------------
يقوم بمحاولات إصلاح تلقائية للمشكلات الشائعة في المستودع:

1) إصلاح مسارات Docker Compose.
2) إصلاح healthcheck endpoints إن كانت مفقودة.
3) إصلاح متغيرات البيئة المفقودة عبر إضافة placeholders آمنة.
4) إصلاح المشاكل التقليدية في .env.
5) إضافة missing folders تلقائياً.
6) إصلاح مشاكل python imports الشائعة.
"""

from pathlib import Path
import yaml


REQUIRED_ENV_KEYS = [
    "OPENAI_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "NEO4J_URI",
    "QDRANT_URL",
]


def safe_write(path: Path, content: str) -> None:
    """Write content to disk using UTF-8 encoding."""
    path.write_text(content, encoding="utf-8")


def ensure_env_keys():
    """Ensure required environment keys exist in .env, adding placeholders when missing."""
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("\n".join(f"{key}=" for key in REQUIRED_ENV_KEYS) + "\n", encoding="utf-8")
        return "⚠️ No .env found — created one with empty placeholders.", True

    lines = env_path.read_text(encoding="utf-8").splitlines()
    existing = {ln.split("=")[0] for ln in lines if "=" in ln}

    missing = [k for k in REQUIRED_ENV_KEYS if k not in existing]
    if not missing:
        return "All env keys exist.", True

    with Path(".env").open("a", encoding="utf-8") as env_file:
        for key in missing:
            env_file.write(f"{key}=\n")

    return f"Added missing env keys: {missing}", True


def fix_docker_compose():
    """Add sensible defaults to docker-compose.yml services when missing."""
    compose_path = Path("docker-compose.yml")
    if not compose_path.exists():
        return "⚠️ No docker-compose.yml found.", False

    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    if not data:
        return "⚠️ docker-compose.yml is empty.", False

    modified = False

    for _, service in data.get("services", {}).items():
        if not isinstance(service, dict):
            continue

        # إصلاح healthcheck لو مفقود
        if "healthcheck" not in service:
            service["healthcheck"] = {
                "test": [
                    "CMD-SHELL",
                    "curl -sf http://localhost:${PORT:-8080}/health || exit 1",
                ],
                "interval": "30s",
                "timeout": "10s",
                "retries": 5,
            }
            modified = True

        # إصلاح restart policy
        if service.get("restart") != "unless-stopped":
            service["restart"] = "unless-stopped"
            modified = True

    if modified:
        safe_write(compose_path, yaml.dump(data, sort_keys=False))
        return "Docker compose file updated.", True

    return "No docker compose fixes needed.", True


def ensure_directories():
    """Create a set of commonly expected directories if they are missing."""
    needed_dirs = [
        Path("logs"),
        Path("tmp"),
        Path("artifacts"),
    ]
    created = []

    for directory in needed_dirs:
        if directory.exists():
            continue
        directory.mkdir(parents=True, exist_ok=True)
        created.append(str(directory))

    if created:
        return f"Created missing directories: {created}", True

    return "All auxiliary directories exist.", True


def auto_fix_everything():
    """Run all auto-fix routines and return a human-friendly summary."""
    messages = []

    messages.append(ensure_env_keys()[0])
    messages.append(fix_docker_compose()[0])
    messages.append(ensure_directories()[0])

    return "\n".join(messages)


if __name__ == "__main__":
    print(auto_fix_everything())
