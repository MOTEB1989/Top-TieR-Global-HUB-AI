#!/usr/bin/env bash
set -euo pipefail

printf '== Veritas Stack Health Check ==\n'
date
printf '\n'

CORE_HEALTH_URL=${VERITAS_CORE_HEALTH_URL:-http://localhost:8000/health}

if [[ -n ${VERITAS_WEB_HEALTH_URL:-} ]]; then
  WEB_HEALTH_URL=$VERITAS_WEB_HEALTH_URL
else
  if [[ -n ${CODESPACES:-} || -n ${CODESPACE_NAME:-} ]]; then
    echo "Detected GitHub Codespaces environment — defaulting VERITAS_WEB health probe to port 8080." >&2
    WEB_HEALTH_URL=http://localhost:8080/health
  else
    WEB_HEALTH_URL=http://localhost:3000/health
  fi
fi
CONNECT_TIMEOUT=${VERITAS_HEALTH_CONNECT_TIMEOUT:-3}
MAX_TIME=${VERITAS_HEALTH_MAX_TIME:-8}
EXPECTED_PATTERN=${VERITAS_HEALTH_EXPECTED_PATTERN:-^2}

declare -a PASSED_SERVICES=()
declare -a FAILED_SERVICES=()
declare -a SKIPPED_SERVICES=()
declare -A SUMMARY_LINES=()

is_local_url() {
  local url=$1
  [[ $url == http://localhost* || $url == https://localhost* || $url == http://127.* || $url == https://127.* ]]
}

normalise_bool() {
  local value=${1:-}
  value=${value,,}
  case "$value" in
    true|1|yes|y) echo "true" ;;
    false|0|no|n) echo "false" ;;
    *) echo "" ;;
  esac
}

resolve_strict_mode() {
  local requested
  requested=$(normalise_bool "${VERITAS_HEALTH_STRICT:-}")

  if [[ -n $requested ]]; then
    echo "$requested"
    return
  fi

  if [[ ${GITHUB_ACTIONS:-} == "true" ]]; then
    local endpoints=()
    [[ -n $CORE_HEALTH_URL ]] && endpoints+=("$CORE_HEALTH_URL")
    [[ -n $WEB_HEALTH_URL ]] && endpoints+=("$WEB_HEALTH_URL")

    local all_local=true
    for candidate in "${endpoints[@]}"; do
      if [[ $candidate == skip ]]; then
        continue
      fi
      if ! is_local_url "$candidate"; then
        all_local=false
        break
      fi
    done

    if [[ $all_local == true ]]; then
      echo "GITHUB_ACTIONS detected with only localhost targets — downgrading to warning mode." >&2
      echo "false"
      return
    fi

    echo "true"
    return
  fi

  echo "true"
}

append_summary() {
  local key=$1
  local line=$2
  local existing=${SUMMARY_LINES[$key]-}
  SUMMARY_LINES["$key"]="${existing}${line}"$'\n'
}

STRICT_MODE=$(resolve_strict_mode)

check_service() {
  local name=$1
  local url=$2

  if [[ -z $url || $url == skip ]]; then
    echo "⏭️  Skipping $name (no URL configured)"
    SKIPPED_SERVICES+=("$name")
    append_summary "skipped" "- $name (no URL configured)"
    return
  fi

  printf 'Checking %s at %s ...\n' "$name" "$url"
  local status
  status=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" "$url" || true)
  status=${status:-000}
  status=${status//$'\n'/}

  if [[ $status =~ $EXPECTED_PATTERN ]]; then
    printf '✅ %s is healthy (%s)\n' "$name" "$status"
    PASSED_SERVICES+=("$name:$status")
    append_summary "passed" "- $name ($status)"
  else
    printf '❌ %s health check failed (status: %s)\n' "$name" "$status"
    FAILED_SERVICES+=("$name:$status")
    append_summary "failed" "- $name ($status)"
  fi
}

check_service "CORE_API" "$CORE_HEALTH_URL"
check_service "VERITAS_WEB" "$WEB_HEALTH_URL"

printf '\n'
if ((${#FAILED_SERVICES[@]} > 0)); then
  printf 'Summary (failed): %s\n' "${FAILED_SERVICES[*]}"
  if [[ $STRICT_MODE == "true" ]]; then
    printf '== Health check complete (failures detected) ==\n'
  else
    printf '== Health check complete (warnings only) ==\n'
  fi
else
  printf '== Health check complete ==\n'
fi

if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
  {
    echo '## Veritas Health Check'
    echo
    if [[ -n ${SUMMARY_LINES[passed]-} ]]; then
      echo '### ✅ Passed'
      printf '%s' "${SUMMARY_LINES[passed]-}"
      echo
    fi
    if [[ -n ${SUMMARY_LINES[failed]-} ]]; then
      echo '### ❌ Failed'
      printf '%s' "${SUMMARY_LINES[failed]-}"
      echo
    fi
    if [[ -n ${SUMMARY_LINES[skipped]-} ]]; then
      echo '### ⏭️ Skipped'
      printf '%s' "${SUMMARY_LINES[skipped]-}"
      echo
    fi
    echo "- Strict mode: $STRICT_MODE"
  } >>"$GITHUB_STEP_SUMMARY"
fi

if ((${#FAILED_SERVICES[@]} > 0)) && [[ $STRICT_MODE == "true" ]]; then
  exit 1
fi

exit 0
