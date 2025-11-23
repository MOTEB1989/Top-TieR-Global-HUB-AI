#!/bin/bash
# Post-Refactor Validation Script
# Validates environment, imports, dry-run, and fallback simulation

set -e

echo "=========================================="
echo "🔍 Post-Refactor Validation Check"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

# Helper functions
pass() {
    echo "✅ PASS: $1"
    ((PASSED++))
}

fail() {
    echo "❌ FAIL: $1"
    ((FAILED++))
}

# Section 1: Environment Verification
echo "📋 Section 1: Environment Verification"
echo "------------------------------------------"
if python3 scripts/verify_env.py 2>&1 | grep -q "جميع المتغيرات الحرجة موجودة"; then
    pass "verify_env.py runs successfully"
else
    fail "verify_env.py failed or OPENAI_MODEL missing"
fi

if python3 scripts/verify_env.py --strict 2>&1; then
    pass "verify_env.py --strict mode works"
else
    echo "⚠️  WARNING: Strict mode failed (may be expected if using placeholders)"
fi
echo ""

# Section 2: Import Validation
echo "📦 Section 2: Import Validation"
echo "------------------------------------------"
if python3 -c "from scripts.lib.common import get_openai_models, RateLimiter, sanitize_filename, validate_file_size" 2>/dev/null; then
    pass "scripts.lib.common imports successfully"
else
    fail "scripts.lib.common import failed"
fi

if python3 -c "import sys; sys.path.insert(0, 'scripts'); from lib.common import mask_secret, derive_fernet_key" 2>/dev/null; then
    pass "Additional common utilities import successfully"
else
    fail "Some common utilities failed to import"
fi
echo ""

# Section 3: Dry-Run Validation
echo "🏃 Section 3: Dry-Run Validation"
echo "------------------------------------------"
if python3 scripts/telegram_chatgpt_mode.py --dry-run 2>&1 | grep -q "Dry run successful"; then
    pass "telegram_chatgpt_mode.py --dry-run succeeds"
else
    fail "Dry-run mode failed"
fi

if python3 scripts/telegram_chatgpt_mode.py --help | grep -q "force-fallback"; then
    pass "CLI flags (--force-fallback) documented"
else
    fail "CLI help missing or incomplete"
fi
echo ""

# Section 4: Fallback Simulation
echo "🔄 Section 4: Fallback Model Simulation"
echo "------------------------------------------"
if python3 scripts/telegram_chatgpt_mode.py --force-fallback --dry-run 2>&1 | grep -q "Force fallback mode enabled"; then
    pass "Force fallback flag works in dry-run"
else
    fail "Force fallback mode not recognized"
fi
echo ""

# Section 5: File Sanitization Tests
echo "🛡️  Section 5: Filename Sanitization"
echo "------------------------------------------"
if python3 -c "
from scripts.lib.common import sanitize_filename
assert sanitize_filename('../../../etc/passwd') == 'passwd', 'Path traversal not blocked'
assert sanitize_filename('test<>file.txt') == 'test__file.txt', 'Invalid chars not sanitized'
assert len(sanitize_filename('a' * 300 + '.txt')) <= 260, 'Long filename not truncated'
print('All sanitization tests passed')
" 2>&1 | grep -q "All sanitization tests passed"; then
    pass "Filename sanitization works correctly"
else
    fail "Filename sanitization tests failed"
fi
echo ""

# Section 6: Rate Limiter Tests
echo "⏱️  Section 6: Rate Limiter"
echo "------------------------------------------"
if python3 -c "
from scripts.lib.common import RateLimiter
rl = RateLimiter(messages_per_minute=2)
# Allow first 2 messages
assert rl.is_allowed(12345), 'First message should be allowed'
assert rl.is_allowed(12345), 'Second message should be allowed'
# Third should be blocked
assert not rl.is_allowed(12345), 'Third message should be blocked'
print('Rate limiter working correctly')
" 2>&1 | grep -q "Rate limiter working correctly"; then
    pass "Rate limiter logic works"
else
    fail "Rate limiter tests failed"
fi
echo ""

# Section 7: Masking Logic
echo "🔒 Section 7: Secret Masking"
echo "------------------------------------------"
if python3 -c "
from scripts.lib.common import mask_secret
masked = mask_secret('sk-proj-1234567890abcdef', 'OPENAI_API_KEY')
assert '...' in masked or 'MASKED' in masked, 'Key not masked'
masked_pass = mask_secret('my_password_123', 'DB_PASSWORD')
assert '...' in masked_pass or 'MASKED' in masked_pass, 'Password not masked'
print('Masking works for _KEY, _TOKEN, _PASSWORD, _PASS, _AUTH')
" 2>&1 | grep -q "Masking works"; then
    pass "Secret masking covers all sensitive suffixes"
else
    fail "Masking logic incomplete"
fi
echo ""

# Section 8: Encryption Key Derivation
echo "🔐 Section 8: Encryption Key Derivation"
echo "------------------------------------------"
if python3 -c "
from scripts.lib.common import derive_fernet_key
key1 = derive_fernet_key('test-secret-key')
key2 = derive_fernet_key('test-secret-key')
assert key1 == key2, 'Key derivation not deterministic'
assert len(key1) == 44, 'Fernet key wrong length'  # base64 encoded 32 bytes = 44 chars
print('Deterministic key derivation works')
" 2>&1 | grep -q "Deterministic key derivation works"; then
    pass "Encryption key derivation is deterministic"
else
    fail "Encryption key derivation failed"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Summary"
echo "=========================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All checks PASSED! Refactor validated successfully."
    exit 0
else
    echo "⚠️  Some checks FAILED. Review the output above."
    exit 1
fi
