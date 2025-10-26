# Status & Health Scripts

This directory contains helper scripts that collect environment status and health reports for CodeX deployments.

## Available scripts

- `collect_status.sh`: Summarises local system, Kubernetes, Docker, and Neo4j information with optional CI status checks.
- `codex_system_security_check.sh`: Runs the "CodeX Full System & Security Check", verifying prerequisite tools, probing key services, summarising dependencies, and optionally posting an auto-generated report back to GitHub pull requests.

## Usage

Run the scripts from the repository root:

```bash
./scripts/status/codex_system_security_check.sh
```

or

```bash
./scripts/status/collect_status.sh
```

Both scripts emit their reports to STDOUT. The security check additionally saves the Markdown summary to `codex_auto_report.log` for later review.
