# AGENT_PLAYBOOK

## Purpose
Playbook for safe agent operations in Top-TieR-Global-HUB-AI.

## Safety Limits
- Destructive commands require confirm step.
- Max automatic merges per run: 5 (configurable).

## Commands (bot)
- /scan -> run full repository scan
- /preflight -> run preflight checks
- /auto_merge <PR> -> attempt merge (allowlist + manual confirm)
- /logs -> show logs (read-only)
- /whoami -> return your Telegram numeric ID (useful to add to TELEGRAM_ALLOWLIST)

## Last Updated: ${TIMESTAMP}
