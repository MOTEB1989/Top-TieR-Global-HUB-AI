#!/usr/bin/env python3
"""
Utility script to align environment configuration across the repository.

It will:
- Generate or refresh `.env.example` with the required environment variables.
- Inject shared secret references into each workflow under `.github/workflows/`.
- Ensure `docker-compose.yml` consumes those environment variables.
- Append an "Environment Setup" section to the README when missing.
"""

from pathlib import Path
import re

ENV_VARS = {
    "OPENAI_API_KEY": "sk-...",
    "DB_URL": "postgresql://postgres:motebai@postgres:5432/motebai",
    "OPENSEARCH_URL": "http://opensearch:9200",
    "MINIO_ENDPOINT": "http://minio:9000",
    "MINIO_ROOT_USER": "motebai",
    "MINIO_ROOT_PASSWORD": "motebai123",
    "REDIS_URL": "redis://redis:6379",
    "NEO4J_URI": "bolt://neo4j:7687",
    "NEO4J_AUTH": "neo4j/motebai",
    "CLICKHOUSE_URL": "http://clickhouse:8123",
}

SECRET_VALUES = {key: f"${{{{ secrets.{key} }}}}" for key in ENV_VARS}

README_SECTION = """
## 🔑 Environment Setup

1. Copy `.env.example` → `.env`
2. Fill in real values (keys, URLs, passwords).
3. Add them into GitHub Secrets with the same names.
4. Docker Compose and GitHub Actions will automatically pick them up.
"""


def write_env_example() -> None:
    env_file = Path(".env.example")
    lines = [f"{key}={value}\n" for key, value in ENV_VARS.items()]
    env_file.write_text("".join(lines))
    print("✅ Generated .env.example")


def _parse_env_block(lines, start_index):
    block_lines = []
    index = start_index + 1
    while index < len(lines) and (lines[index].startswith("  ") or lines[index].strip() == ""):
        block_lines.append(lines[index])
        index += 1
    return block_lines, index


def patch_workflow(path: Path) -> bool:
    content = path.read_text()
    lines = content.splitlines(keepends=True)

    root_env_idx = next((i for i, line in enumerate(lines) if line.startswith("env:")), None)
    changed = False

    if root_env_idx is not None:
        block_lines, block_end = _parse_env_block(lines, root_env_idx)
        env_entries = {}
        for raw in block_lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#") or ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            env_entries[key.strip()] = value.strip()
        for key, value in SECRET_VALUES.items():
            if env_entries.get(key) != value:
                env_entries[key] = value
                changed = True
        if changed:
            new_block = ["env:\n"]
            new_block.extend(f"  {k}: {env_entries[k]}\n" for k in env_entries)
            if block_end >= len(lines) or lines[block_end] != "\n":
                new_block.append("\n")
            lines = lines[:root_env_idx] + new_block + lines[block_end:]
    else:
        name_idx = next((i for i, line in enumerate(lines) if line.startswith("name:")), None)
        if name_idx is None:
            return False
        insert_idx = name_idx + 1
        # Remove blank lines directly after name to keep spacing consistent.
        while insert_idx < len(lines) and lines[insert_idx] == "\n":
            lines.pop(insert_idx)
        block = ["env:\n"]
        block.extend(f"  {key}: {value}\n" for key, value in SECRET_VALUES.items())
        block.append("\n")
        lines[insert_idx:insert_idx] = block
        changed = True

    if changed:
        path.write_text("".join(lines))
        print(f"🔧 Patched workflow: {path.name}")
    return changed


def patch_workflows() -> None:
    wf_dir = Path(".github/workflows")
    if not wf_dir.exists():
        return
    for wf in sorted(wf_dir.glob("*.yml")):
        patch_workflow(wf)


MOTEBAI_ENV_ENTRIES = [
    "OPENAI_API_KEY=${OPENAI_API_KEY}",
    "DB_URL=${DB_URL}",
    "OPENSEARCH_URL=${OPENSEARCH_URL}",
    "MINIO_ENDPOINT=${MINIO_ENDPOINT}",
    "MINIO_ROOT_USER=${MINIO_ROOT_USER}",
    "MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}",
    "REDIS_URL=${REDIS_URL}",
    "NEO4J_URI=${NEO4J_URI}",
    "NEO4J_AUTH=${NEO4J_AUTH}",
    "CLICKHOUSE_URL=${CLICKHOUSE_URL}",
]

MOTEBAI_ENV_PATTERN = re.compile(
    r"(  motebai-api:\n(?:    .*\n)*?    environment:\n)(?P<body>(?:      - .*\n)+)",
    re.MULTILINE,
)


def patch_docker_compose() -> None:
    dc_file = Path("docker-compose.yml")
    if not dc_file.exists():
        return

    text = dc_file.read_text()
    original = text

    env_file_snippet = (
        "  motebai-api:\n    build: .\n    ports:\n      - \"8000:8000\"\n    env_file:\n      - .env\n"
    )
    if env_file_snippet not in text:
        text = text.replace(
            "  motebai-api:\n    build: .\n    ports:\n      - \"8000:8000\"\n",
            env_file_snippet,
            1,
        )

    match = MOTEBAI_ENV_PATTERN.search(text)
    if match:
        body = match.group("body")
        lines = [line for line in body.splitlines() if line.strip()]
        existing = {line.strip() for line in lines}
        for entry in MOTEBAI_ENV_ENTRIES:
            candidate = f"- {entry}"
            if candidate not in existing:
                lines.append(f"      - {entry}")
                existing.add(candidate)
        new_body = "\n".join(lines) + "\n"
        text = text[: match.start("body")] + new_body + text[match.end("body") :]

    text = text.replace(
        "- MINIO_ROOT_USER=minioadmin", "- MINIO_ROOT_USER=${MINIO_ROOT_USER}"
    )
    text = text.replace(
        "- MINIO_ROOT_PASSWORD=minioadmin",
        "- MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}",
    )

    if "    env_file:\n      - .env\n      - /opt/veritas/.env.neo4j" not in text:
        text = text.replace(
            "    env_file:\n      - /opt/veritas/.env.neo4j",
            "    env_file:\n      - .env\n      - /opt/veritas/.env.neo4j",
        )

    text = text.replace(
        "- NEO4J_AUTH=${NEO4J_USER}:${NEO4J_PASSWORD}", "- NEO4J_AUTH=${NEO4J_AUTH}"
    )

    if text != original:
        dc_file.write_text(text)
        print("🔧 Patched docker-compose.yml")


def patch_readme() -> None:
    readme = Path("README.md")
    if not readme.exists():
        return
    contents = readme.read_text()
    if "Environment Setup" not in contents:
        readme.write_text(contents.rstrip() + "\n\n" + README_SECTION.strip() + "\n")
        print("📖 Updated README.md")


if __name__ == "__main__":
    write_env_example()
    patch_workflows()
    patch_docker_compose()
    patch_readme()
