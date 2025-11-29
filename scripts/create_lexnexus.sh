#!/usr/bin/env bash
set -euo pipefail

# Creates or updates the LexNexus custom GPT using the OpenAI GPTs API.
# Usage: ./scripts/create_lexnexus.sh [instructions_file]
#
# Environment variables:
#   OPENAI_API_KEY    (required) API key with access to the GPTs API.
#   VECTOR_STORE_ID   (optional) Existing vector store ID for file search.
#   MODEL             (optional) Defaults to gpt-4.1.
#   GPT_NAME          (optional) Defaults to "LexNexus AI".
#   GPT_DESCRIPTION   (optional) Defaults to "Smart AI Agent for Top-Tier Global Hub".

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[ERROR] OPENAI_API_KEY is not set." >&2
  exit 1
fi

for dep in curl jq; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "[ERROR] Missing dependency: $dep" >&2
    exit 1
  fi
done

GPT_NAME=${GPT_NAME:-"LexNexus AI"}
GPT_DESCRIPTION=${GPT_DESCRIPTION:-"Smart AI Agent for Top-Tier Global Hub"}
MODEL=${MODEL:-"gpt-4.1"}
VECTOR_STORE_ID=${VECTOR_STORE_ID:-""}

read -r -d '' DEFAULT_INSTRUCTIONS <<'TEXT'
You are LexNexus AI, the trusted intelligence and governance assistant for the Top-Tier Global Hub. Always provide concise, action-oriented responses with clear next steps, risks, and mitigations. Ask clarifying questions when information is missing and avoid guessing.

Response guidelines:
- Use headings and bullet points for readability.
- Highlight security, privacy, and compliance considerations for any recommendation.
- When citing data or artifacts, clearly state if a source is unavailable.
- Keep responses respectful, neutral, and free from speculation.
TEXT

if [[ $# -gt 0 ]]; then
  if [[ ! -f "$1" ]]; then
    echo "[ERROR] Instructions file not found: $1" >&2
    exit 1
  fi
  INSTRUCTIONS=$(<"$1")
else
  INSTRUCTIONS="$DEFAULT_INSTRUCTIONS"
fi

payload=$(jq -n \
  --arg name "$GPT_NAME" \
  --arg desc "$GPT_DESCRIPTION" \
  --arg instructions "$INSTRUCTIONS" \
  --arg model "$MODEL" \
  --arg vs "$VECTOR_STORE_ID" \
  --argjson starters '[
    "Give me a concise compliance and security checklist for a new SaaS vendor.",
    "Summarize the top delivery risks in our deployment plan and propose mitigations.",
    "Draft a short leadership update on the AI integration with key wins and blockers.",
    "What questions should we ask before onboarding a new data source into the platform?"
  ]' \
  '{
    name: $name,
    description: $desc,
    model: $model,
    instructions: $instructions,
    tools: (
      if $vs != "" then
        [
          {type: "file_search", file_search: {vector_store_ids: [$vs]}},
          {type: "code_interpreter"}
        ]
      else
        [{type: "code_interpreter"}]
      end
    ),
    conversation_starters: $starters
  }')

response=$(curl -sS -X POST "https://api.openai.com/v1/gpts" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$payload")

echo "$response" | jq '.'

gpt_id=$(echo "$response" | jq -r '.id // empty')
if [[ -n "$gpt_id" ]]; then
  echo "[INFO] Created/updated GPT: $gpt_id"
else
  echo "[WARN] GPT creation response did not include an id." >&2
fi
