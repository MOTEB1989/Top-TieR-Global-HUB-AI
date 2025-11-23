#!/bin/bash
# self_heal.sh (Smart Version)
set -e

REPORT_FILE="reports/ultra_report.json"
PLAN_FILE="reports/self_heal_plan.json"
# This should be the address of your API gateway when running
API_URL="http://localhost:3000/v1/ai/infer" 

# Check if the report file exists
if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ Error: Report file not found at $REPORT_FILE"
    echo "Please run the analysis step first (e.g., python ultra_agent_os.py)."
    exit 1
fi

# Read the report content
REPORT_CONTENT=$(cat "$REPORT_FILE")

# Craft the smart prompt for the LLM
# We ask it to act as a senior engineer and convert the report into a JSON repair plan
PROMPT="You are a senior software engineer analyzing a security and error report for a codebase. Your task is to create a JSON array of actionable 'recommended_fixes'. For each issue in the report, create a JSON object with 'file' and 'suggested_action'. If an automatic fix is possible, set suggested_action to 'autofix'. If it requires manual review, set it to 'manual_review'. Respond ONLY with the raw JSON array. Here is the report:

$REPORT_CONTENT"

# Configure the request payload for the API
# Using a HEREDOC for clarity
read -r -d '' REQUEST_BODY <<EOF
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant that generates JSON." },
    { "role": "user", "content": "$PROMPT" }
  ]
}
EOF

echo "🧠 Generating self-healing plan using Generative AI..."
echo "This may take a moment..."

# Call the LLM via the API gateway to generate the repair plan
# Note: This assumes the local services are running (docker compose up)
AI_RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  --data-binary @- <<< "$REQUEST_BODY")


# Check if the AI response is empty or failed
if [ -z "$AI_RESPONSE" ]; then
    echo "❌ Error: Failed to get a response from the AI model. Is the API Gateway running at $API_URL?"
    exit 1
fi

# Extract the JSON content from the LLM's response
# The full response might have extra data; we just want the assistant's message
# We use jq to parse the JSON response and extract the content, then parse that content again
PLAN_JSON=$(echo "$AI_RESPONSE" | jq -r '.choices[0].message.content')

# Check if the extracted plan is valid JSON
if ! echo "$PLAN_JSON" | jq -e . > /dev/null 2>&1; then
    echo "❌ Error: The AI model did not return valid JSON for the plan."
    echo "Received: $PLAN_JSON"
    exit 1
fi

# Create the final plan JSON object
echo "{\"source_report\":\"$REPORT_FILE\",\"generated_at\":\"$(date -u -Iseconds)\",\"recommended_fixes\":$PLAN_JSON}" > "$PLAN_FILE"

echo "✅ AI-generated self-heal plan created successfully at $PLAN_FILE"