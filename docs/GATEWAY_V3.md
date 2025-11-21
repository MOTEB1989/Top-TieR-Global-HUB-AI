# AI Gateway V3

## Overview
AI Gateway V3 provides a unified interface for running automated reviews across multiple AI providers. It focuses on portability, predictable outputs, and CI-friendly execution so teams can evaluate changes with consistent guardrails.

## Features
- **Multi-provider execution** with environment-driven provider selection (OpenAI, Groq, or local endpoints).
- **Task auto-detection** to choose the correct review prompt based on the file type or requested mode.
- **Deterministic logging** so each provider produces a dedicated Markdown report under `ai_review_output/`.
- **Risk scoring hook** that aggregates warning signals from all provider outputs into a JSON summary.
- **CI/CD integration** ready for GitHub Actions, including artifact uploads and summaries in the run UI.

## Task detection logic
- When invoked with `--task auto`, the gateway inspects each file extension to select the best-suited review preset.
- Language-aware prompts are picked for common stacks (Python, TypeScript/JavaScript, Rust, Docker, Kubernetes manifests, and Markdown docs).
- Unsupported or unknown extensions fall back to a generic static-analysis prompt that emphasizes clarity and safety findings.

## Provider selection logic
- Providers are inferred from environment variables:
  - `OPENAI_API_KEY` → `openai`
  - `GROQ_API_KEY` → `groq`
  - `LOCAL_MODEL_ENDPOINT` → `local`
- The workflow writes detected providers to `providers.txt` and iterates through each entry, exporting `PROVIDER` before calling `gateway.py`.
- Each provider appends to its own Markdown file named `ai_review_output/review_<provider>.md` to preserve separation of concerns.

## File type support
- Source code: `.py`, `.ts`, `.js`, `.rs`, `.go`, `.java` and similar extensions.
- Infrastructure: `.yaml` / `.yml` (Kubernetes and workflow files), Dockerfiles, and Compose manifests.
- Documentation: `.md` and `.rst`.
- Configurations: `.json`, `.toml`, `.ini`, and `.env` (excluding secrets; redaction is recommended upstream).

## Usage examples
- **Single file auto task:** `python gateway.py --task auto --file path/to/file.py`
- **Pinned provider:** set `PROVIDER=openai` (or `groq`, `local`) before running the gateway entry point.
- **Batch review (CI style):** iterate over a newline-delimited list of changed files and stream results into a provider-specific Markdown artifact.

## Integration with CI/CD
- The `ai-gateway-reviewer.yml` workflow checks out the repository, installs Python dependencies, and calculates the changed files for the pull request.
- A detection step records available providers into `providers.txt`, skips the run if none are configured, and preserves logs for auditing.
- For each provider, the workflow writes detailed review output to `ai_review_output/review_<provider>.md`.
- After reviews complete, `scripts/ai_risk_assessor.py` aggregates warning signals into `ai_review_output/risk_summary.json` and prints an Arabic summary to include in `$GITHUB_STEP_SUMMARY`.
- Artifacts `ai-review-output` (Markdown) and `ai-risk-summary` (JSON) are uploaded for downstream consumption or compliance archiving.

## Warnings & limitations
- Provider credentials must be set in repository secrets; missing credentials will skip the run.
- The gateway does not execute user code—analysis is static and relies on model reasoning.
- Risk scoring is heuristic-based and should be combined with manual code review for critical paths.
- Local provider endpoints must be reachable from the CI runner; timeouts are inherited from the configured model client.

## Troubleshooting
- **No providers detected:** ensure at least one of `OPENAI_API_KEY`, `GROQ_API_KEY`, or `LOCAL_MODEL_ENDPOINT` is configured in secrets.
- **Empty review outputs:** confirm `changed_files.txt` contains the expected paths; the workflow builds this from the PR diff.
- **Unicode issues in reports:** gateway and risk assessor default to UTF-8; validate that inputs are UTF-8 encoded.
- **Artifacts missing:** verify the GitHub Actions run completed the upload steps and was not skipped due to missing providers.

## Roadmap
- Multi-provider consensus that compares findings and highlights disagreements.
- File-level ranking to order findings by estimated severity and affected surface area.
- Parallel inference to reduce latency when evaluating many files across providers.
