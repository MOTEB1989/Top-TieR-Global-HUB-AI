#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

#############################################################################
# post_refactor_check.sh - Post-Refactor Diagnostic Script
#
# Purpose:
#   Validate that all refactored scripts are present, executable, and working
#   correctly after the comprehensive scripts refactor.
#
# Usage:
#   chmod +x scripts/post_refactor_check.sh
#   ./scripts/post_refactor_check.sh
#
# Exit Codes:
#   0 - All checks passed
#   1 - One or more checks failed
#############################################################################

# Colors for output
C_RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_BLUE=$'\033[34m'
C_CYAN=$'\033[36m'
C_BOLD=$'\033[1m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Helper functions
log_info()  { echo "${C_BLUE}ℹ${C_RESET} $*"; }
log_pass()  { echo "${C_GREEN}✅${C_RESET} $*"; ((PASSED_CHECKS++)); ((TOTAL_CHECKS++)); }
log_fail()  { echo "${C_RED}❌${C_RESET} $*"; ((FAILED_CHECKS++)); ((TOTAL_CHECKS++)); }
log_warn()  { echo "${C_YELLOW}⚠️${C_RESET} $*"; }
header()    { echo ""; echo "${C_BOLD}${C_CYAN}========== $* ==========${C_RESET}"; }

# Get repository root
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo ""
echo "${C_BOLD}${C_CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║   Post-Refactor Diagnostic Check         ║
║   Top-TieR Global HUB AI                  ║
╚═══════════════════════════════════════════╝
EOF
echo "${C_RESET}"

# ========== Check 1: Required Python Scripts Presence ==========
header "Required Python Scripts"

PYTHON_SCRIPTS=(
    "scripts/telegram_chatgpt_mode.py"
    "scripts/run_telegram_bot.py"
    "scripts/test_telegram_bot.py"
    "scripts/check_all_keys.py"
    "scripts/check_github_secrets.py"
    "scripts/close_github_items.py"
    "scripts/convert_thread_messages.py"
    "scripts/verify_env.py"
    "scripts/lib/common.py"
    "scripts/lib/__init__.py"
)

for script in "${PYTHON_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        log_pass "Present: $script"
    else
        log_fail "Missing: $script"
    fi
done

# ========== Check 2: Required Shell Scripts Presence ==========
header "Required Shell Scripts"

SHELL_SCRIPTS=(
    "scripts/GIT_READY_COMMANDS.sh"
    "scripts/check_connections.sh"
    "scripts/check_environment.sh"
    "scripts/collect_context_for_claude.sh"
    "scripts/comprehensive_setup_and_test.sh"
    "scripts/fix_and_create_all.sh"
    "scripts/force_fix_railway.sh"
    "scripts/run_everything.sh"
    "scripts/run_everything_railway.sh"
    "scripts/setup_check_connections.sh"
    "scripts/validate_check_connections.sh"
    "scripts/ultra_preflight.sh"
)

for script in "${SHELL_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        log_pass "Present: $script"
    else
        log_fail "Missing: $script"
    fi
done

# ========== Check 3: Script Executability ==========
header "Script Executability (Shell Scripts)"

for script in "${SHELL_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            log_pass "Executable: $script"
        else
            log_fail "Not executable: $script"
        fi
    fi
done

# ========== Check 4: Python Dependencies ==========
header "Python Dependencies"

if command -v python3 >/dev/null 2>&1; then
    log_pass "Python 3 available"
    
    # Test import of telegram
    if python3 -c "import telegram" 2>/dev/null; then
        log_pass "python-telegram-bot package available"
    else
        log_fail "python-telegram-bot package missing"
    fi
    
    # Test import of openai
    if python3 -c "import openai" 2>/dev/null; then
        log_pass "openai package available"
    else
        log_warn "openai package missing (optional for some scripts)"
        ((PASSED_CHECKS++)); ((TOTAL_CHECKS++))
    fi
    
    # Test import of requests
    if python3 -c "import requests" 2>/dev/null; then
        log_pass "requests package available"
    else
        log_fail "requests package missing"
    fi
    
    # Test import of dotenv
    if python3 -c "from dotenv import load_dotenv" 2>/dev/null; then
        log_pass "python-dotenv package available"
    else
        log_fail "python-dotenv package missing"
    fi
else
    log_fail "Python 3 not available"
fi

# ========== Check 5: Verify verify_env.py Functionality ==========
header "verify_env.py Functionality"

if python3 scripts/verify_env.py --help >/dev/null 2>&1; then
    log_pass "verify_env.py --help works"
else
    log_fail "verify_env.py --help failed"
fi

# Check strict mode flag
if python3 scripts/verify_env.py --help 2>&1 | grep -q "strict"; then
    log_pass "verify_env.py --strict flag available"
else
    log_fail "verify_env.py --strict flag missing"
fi

# ========== Check 6: telegram_chatgpt_mode.py Functionality ==========
header "telegram_chatgpt_mode.py Functionality"

# Check --help
if python3 scripts/telegram_chatgpt_mode.py --help >/dev/null 2>&1; then
    log_pass "telegram_chatgpt_mode.py --help works"
else
    log_fail "telegram_chatgpt_mode.py --help failed"
fi

# Check --dry-run flag
if python3 scripts/telegram_chatgpt_mode.py --help 2>&1 | grep -q "dry-run"; then
    log_pass "telegram_chatgpt_mode.py --dry-run flag available"
else
    log_fail "telegram_chatgpt_mode.py --dry-run flag missing"
fi

# Check --mode flag
if python3 scripts/telegram_chatgpt_mode.py --help 2>&1 | grep -q "mode"; then
    log_pass "telegram_chatgpt_mode.py --mode flag available"
else
    log_fail "telegram_chatgpt_mode.py --mode flag missing"
fi

# ========== Check 7: Documentation Files ==========
header "Documentation Files"

DOC_FILES=(
    "SCRIPTS_OVERVIEW.md"
    "BOT_VALIDATION.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [[ -f "$doc" ]]; then
        log_pass "Present: $doc"
    else
        log_fail "Missing: $doc"
    fi
done

# ========== Check 8: railway.json Configuration ==========
header "railway.json Configuration"

if [[ -f "railway.json" ]]; then
    log_pass "railway.json present"
    
    # Check if it contains the refactored mode flag
    if grep -q "mode=refactored" railway.json; then
        log_pass "railway.json contains --mode=refactored flag"
    else
        log_fail "railway.json missing --mode=refactored flag"
    fi
    
    # Check if it calls verify_env.py
    if grep -q "verify_env.py" railway.json; then
        log_pass "railway.json calls verify_env.py"
    else
        log_fail "railway.json doesn't call verify_env.py"
    fi
else
    log_fail "railway.json missing"
fi

# ========== Check 9: Shell Script Safety Flags ==========
header "Shell Script Safety Flags"

for script in "${SHELL_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        # Check for proper shebang
        if head -n 1 "$script" | grep -qE "^#!/(usr/bin/env bash|bin/bash)"; then
            # Check for set -euo pipefail
            if head -n 10 "$script" | grep -q "set -euo pipefail"; then
                log_pass "Safety flags present: $script"
            else
                log_warn "Missing 'set -euo pipefail': $script"
                ((PASSED_CHECKS++)); ((TOTAL_CHECKS++))
            fi
        else
            log_warn "Questionable shebang: $script"
            ((PASSED_CHECKS++)); ((TOTAL_CHECKS++))
        fi
    fi
done

# ========== Final Summary ==========
echo ""
echo "${C_BOLD}${C_CYAN}═══════════════════════════════════════════${C_RESET}"
echo "${C_BOLD}             Summary${C_RESET}"
echo "${C_BOLD}${C_CYAN}═══════════════════════════════════════════${C_RESET}"
echo ""
echo "  Total Checks: $TOTAL_CHECKS"
echo "  ${C_GREEN}Passed: $PASSED_CHECKS${C_RESET}"
echo "  ${C_RED}Failed: $FAILED_CHECKS${C_RESET}"
echo ""

if [[ $FAILED_CHECKS -eq 0 ]]; then
    echo "${C_GREEN}${C_BOLD}✅ All checks PASSED!${C_RESET}"
    echo "${C_GREEN}The refactoring is complete and successful.${C_RESET}"
    EXIT_CODE=0
else
    echo "${C_RED}${C_BOLD}❌ $FAILED_CHECKS check(s) FAILED${C_RESET}"
    echo "${C_YELLOW}Please review and fix the failing checks above.${C_RESET}"
    EXIT_CODE=1
fi

echo ""
echo "${C_CYAN}═══════════════════════════════════════════${C_RESET}"
echo ""

exit $EXIT_CODE
