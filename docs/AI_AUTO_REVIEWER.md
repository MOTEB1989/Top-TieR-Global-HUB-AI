# AI Auto Reviewer

## How it works
The AI Auto Reviewer runs `gateway.py` against files changed in a pull request, prompting an LLM to highlight potential bugs, security weaknesses, and documentation gaps. Each provider writes a dedicated Markdown report so reviewers can trace findings back to the model that produced them.

## Multi-provider architecture
- Providers are discovered from secrets: `OPENAI_API_KEY`, `GROQ_API_KEY`, and `LOCAL_MODEL_ENDPOINT`.
- Detected providers are written to `providers.txt` and iterated in order; the current provider is exported via `PROVIDER` before invoking the gateway.
- Outputs are isolated per provider under `ai_review_output/review_<provider>.md`, allowing side-by-side comparison of findings.

## Risk scoring algorithm
- `scripts/ai_risk_assessor.py` scans all provider review files for warning signals: `⚠️`, `خطر`, `مخاطر`, `critical`, `security`, `vulnerability`, `ثغرة`.
- The total number of warning signals across all files determines the risk level:
  - 0 → `low`
  - 1–3 → `medium`
  - >3 → `high`
- A JSON summary is written to `ai_review_output/risk_summary.json` and an Arabic sentence is printed with the risk level and warning count.

## Example risk classifications
- **Low:** No warning signals found. `risk_level` is `low` and `total_warnings` is 0.
- **Medium:** One to three warning signals. Example summary: `"risk_level": "medium", "total_warnings": 2`.
- **High:** More than three warning signals aggregated across provider outputs. Example summary: `"risk_level": "high", "total_warnings": 5`.

## Artifacts and visibility
- Provider-specific reviews: `ai_review_output/review_<provider>.md`.
- Risk summary JSON: `ai_review_output/risk_summary.json` (uploaded as `ai-risk-summary`).
- A short Arabic summary is appended to the GitHub Actions job summary for quick scanning.

## Advisory-only
The AI reviewer is **advisory**. Its findings do not block merges; human reviewers maintain final authority and should verify any flagged issues.

## Future improvements
- Multi-provider consensus with agreement scoring.
- Automatic ranking of findings by severity and affected component.
- Parallelized provider calls to speed up review latency.
