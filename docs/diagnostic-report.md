# Repository Diagnostic Report

## Overview
This report summarizes repository structure issues, potential dead code, CI/CD risks, container/orchestration gaps, and security concerns identified during the scan.

## Suspicious or Redundant Files
- Multiple large compressed bundles at repo root appear unused in build/test flows: `top-tier-base-files.zip`, `LexCode-Hybrid-Starter-AI-Infer.zip`, `topTireAI-quality-pack.zip`, `veritas-nexus-v2.zip`, `bluetooth-open-diagnostics.zip`, `bluetooth-open-diagnostics2.zip`. Consider removing or relocating to release assets to reduce repo weight and avoid stale content. 【4da44d†L2-L7】
- `test_gpt_connection.py.save` duplicates the live script and risks confusion; prefer removing the `.save` copy. 【F:test_gpt_connection.py.save†L1-L10】
- `Owner` contains non-code prose with no references elsewhere; evaluate need. 【F:Owner†L1-L4】

## Broken/Unused Modules
- `docker-compose.yml` references `./core` and `./services/api` build contexts that do not exist in the repository, so the compose stack cannot build. 【F:docker-compose.yml†L2-L13】【f0b856†L1-L2】
- CI workflow builds `./gateway/Dockerfile`, but no `gateway` directory exists, causing deterministic CI failures. 【F:.github/workflows/CI.yml†L75-L125】【1cd45c†L1-L2】

## GitHub Actions Findings
- All workflows inject many production secrets (`DB_URL`, `OPENSEARCH_URL`, `MINIO_*`, `REDIS_URL`, `NEO4J_*`, `CLICKHOUSE_URL`) at the top level even when jobs do not need them, broadening exposure. 【F:.github/workflows/CI.yml†L3-L13】【F:.github/workflows/context-collector.yml†L3-L13】【F:.github/workflows/external-api-diagnosis.yml†L3-L13】
- `CI` workflow depends on missing `gateway` build context and local compose services, so it will fail early; the slack notification step uses `${{ needs.push-image.result || 'skipped' }}` inside an expression string that may render literally rather than conditionally. 【F:.github/workflows/CI.yml†L75-L137】
- `cleanup.yml` and `comment-on-pr6.yml` embed no guards for absent `GITHUB_TOKEN` scopes beyond default; YAML files end without trailing newline but remain syntactically valid. 【F:.github/workflows/cleanup.yml†L1-L120】【F:.github/workflows/comment-on-pr6.yml†L1-L83】

## Secrets and Missing Configuration
- Critical secrets required for CI (`OPENAI_API_KEY`, DB/Redis/Neo4j/MinIO/ClickHouse URLs, Docker credentials, Slack webhook) are mandatory but not provided by defaults; runs will fail or expose secrets unnecessarily. 【F:.github/workflows/CI.yml†L3-L137】
- `external-api-diagnosis.yml` assumes `OPENAI_API_KEY` and full GitHub CLI authentication; missing values will fail scheduled jobs. 【F:.github/workflows/external-api-diagnosis.yml†L17-L76】

## Docker & Kubernetes Analysis
- Dockerfile installs dependencies with `npm install || true`, masking install failures; no explicit production build artifacts or healthcheck command. 【F:Dockerfile†L1-L8】
- Compose stack points to nonexistent build contexts, so services cannot start. 【F:docker-compose.yml†L2-L13】
- Kubernetes manifests hardcode `latest` images and omit resource/affinity/PodDisruptionBudget hardening; service selectors are minimal. Secrets names (`app-secrets`, `neo4j-auth`, `osint-secrets`) are referenced but example secret specs are only partially provided. 【F:k8s/core-deployment.yaml†L1-L93】【F:k8s/osint-deployment.yaml†L1-L93】

## Security Risks
- Broad secret exposure across workflows increases leak surface; actions with `run` steps can echo values inadvertently. 【F:.github/workflows/CI.yml†L3-L13】
- External API diagnostic script calls public APIs without rate-limit/backoff and prints responses directly to GitHub issues, potentially leaking data. 【F:.github/workflows/external-api-diagnosis.yml†L39-L76】【F:scripts/diagnose_external_apis.py†L1-L58】
- Dockerfile copies entire repo (including example env files and archives) into the image, inflating attack surface; no `.dockerignore` is referenced in build steps. 【F:Dockerfile†L3-L8】

## Prioritized Issues
1. **High** – Fix CI/GitHub Actions build paths (`gateway`, `core`, `services/api`) to restore pipeline reliability. 【F:.github/workflows/CI.yml†L75-L125】【F:docker-compose.yml†L2-L13】
2. **High** – Limit secret exposure in workflows to only required jobs/steps and scope permissions minimally. 【F:.github/workflows/CI.yml†L3-L13】【F:.github/workflows/context-collector.yml†L3-L13】
3. **Medium** – Remove or relocate large archive files and `.save` scripts to reduce repository footprint and confusion. 【4da44d†L2-L7】【F:test_gpt_connection.py.save†L1-L10】
4. **Medium** – Harden Docker/K8s configurations (pin image tags, fail-fast installs, add healthchecks/resource constraints/PDBs, ensure referenced secrets exist). 【F:Dockerfile†L1-L8】【F:k8s/core-deployment.yaml†L1-L93】
5. **Low** – Clarify or remove miscellaneous prose files (`Owner`) not tied to builds. 【F:Owner†L1-L4】

## Immediate Cleanup Candidates
- Remove unused archives from repository history or move to release assets. 【4da44d†L2-L7】
- Delete `test_gpt_connection.py.save` backup copy. 【F:test_gpt_connection.py.save†L1-L10】
- Evaluate necessity of `Owner` text file. 【F:Owner†L1-L4】

