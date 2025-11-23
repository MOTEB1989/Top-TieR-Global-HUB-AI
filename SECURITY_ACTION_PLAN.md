# Security Action Plan - خطة العمل الأمنية

## نظرة عامة - Overview

This document outlines the 7-day security priorities and hardening measures implemented in the Top-TieR-Global-HUB-AI project.

هذه الوثيقة تحدد أولويات الأمان لمدة 7 أيام وإجراءات التعزيز المنفذة في مشروع Top-TieR-Global-HUB-AI.

---

## 🎯 Goals - الأهداف

1. **Eliminate weak defaults** - إزالة الإعدادات الافتراضية الضعيفة
2. **Enforce strong authentication** - فرض مصادقة قوية
3. **Implement rate limiting** - تنفيذ تحديد المعدل
4. **Secure file handling** - تأمين معالجة الملفات
5. **Enhance secret management** - تحسين إدارة الأسرار
6. **Improve encryption** - تحسين التشفير
7. **Comprehensive documentation** - توثيق شامل

---

## Day 1-2: Critical Security Fixes

### ✅ Completed Items

#### 1. Secret Management - إدارة الأسرار

**Problem**: Secrets printed in logs, weak masking.

**Solution**:
- Extended masking to cover: `_TOKEN`, `_KEY`, `_PASSWORD`, `_PASS`, `_AUTH`
- Implemented `mask_secret()` in `scripts/lib/common.py`
- Updated `verify_env.py` to use enhanced masking

**Verification**:
```bash
python scripts/verify_env.py
# Secrets should appear as: sk-pro...f123
```

#### 2. Weak Default Credentials

**Problem**: `.env.example` contained weak defaults like `motebai`, `password`, `motebai123`.

**Solution**:
- Replaced with placeholders: `CHANGE_THIS_PASSWORD`
- Added security comments and generation guidance
- Documented password generation: `openssl rand -base64 32`

**Verification**:
```bash
grep -E "motebai|password123" .env.example
# Should return no results
```

#### 3. Environment Variable Enforcement

**Problem**: `OPENAI_MODEL` was optional, leading to inconsistencies.

**Solution**:
- Made `OPENAI_MODEL` mandatory in `verify_env.py`
- Added `--strict` flag to treat warnings as errors
- Updated `.env.example` with clear REQUIRED/OPTIONAL markers

**Verification**:
```bash
unset OPENAI_MODEL
python scripts/verify_env.py
# Should fail with clear error message
```

---

## Day 3-4: Bot Security Enhancements

### ✅ Completed Items

#### 4. Rate Limiting - تحديد المعدل

**Problem**: No protection against message spam/abuse.

**Solution**:
- Implemented `RateLimiter` class in `scripts/lib/common.py`
- Default: 20 messages/user/minute
- Configurable via `TELEGRAM_RATE_LIMIT_PER_MIN`
- Per-user tracking with sliding window

**Verification**:
```bash
# Send >20 messages in 1 minute
# Expected: Rate limit error message
```

**Implementation**:
```python
from scripts.lib.common import RateLimiter

rate_limiter = RateLimiter(messages_per_minute=20)
if not rate_limiter.is_allowed(user_id):
    # Reject message
```

#### 5. File Upload Security

**Problem**: No validation of filenames or file sizes.

**Solution**:
- Filename sanitization against path traversal
- Maximum file size: 2MB
- Functions: `sanitize_filename()`, `validate_file_size()`

**Attack Mitigation**:
- Path traversal: `../../../etc/passwd` → `passwd`
- Invalid characters: `<script>file.txt` → `_script_file.txt`
- Large files: >2MB rejected with clear error

**Verification**:
```bash
# Test in post_refactor_check.sh
bash scripts/post_refactor_check.sh
# Section 5 should PASS
```

#### 6. OpenAI Model Fallback

**Problem**: Single point of failure if primary model unavailable.

**Solution**:
- Added `OPENAI_FALLBACK_MODEL` (optional)
- Automatic retry once on model errors (404, 400)
- `--force-fallback` flag for testing

**Configuration**:
```bash
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
```

**Behavior**:
1. Try primary model
2. On error 404/400, try fallback once
3. If fallback also fails, return error to user
4. No infinite retry loops

---

## Day 5: Encryption and Data Protection

### ✅ Completed Items

#### 7. Deterministic Encryption Key Derivation

**Problem**: `veritas-web/app.py` generated fresh encryption key each run, making data unreadable after restart.

**Solution**:
- Derive Fernet key from `SECRET_KEY` using SHA-256
- Deterministic: same `SECRET_KEY` → same encryption key
- Implemented in `scripts/lib/common.py` and `veritas-web/app.py`

**Before**:
```python
cipher_suite = Fernet(Fernet.generate_key())  # Random each time
```

**After**:
```python
hash_digest = hashlib.sha256(SECRET_KEY.encode()).digest()
fernet_key = base64.urlsafe_b64encode(hash_digest)
cipher_suite = Fernet(fernet_key)  # Deterministic
```

**Verification**:
```python
from scripts.lib.common import derive_fernet_key
key1 = derive_fernet_key("test")
key2 = derive_fernet_key("test")
assert key1 == key2  # Must be identical
```

#### 8. OpenAI Client Upgrade

**Problem**: Using legacy `openai==0.27.10` with deprecated API.

**Solution**:
- Upgraded to `openai>=1.43.0`
- Updated code to use new API shape (kept requests-based for compatibility)
- Added `cryptography>=41.0.0` for Fernet

**Migration**:
```bash
pip install -r requirements.txt
# Will upgrade openai to 1.43.0+
```

---

## Day 6: Validation and Testing

### ✅ Completed Items

#### 9. Comprehensive Validation Script

**Created**: `scripts/post_refactor_check.sh`

**Checks**:
1. Environment verification
2. Import validation
3. Dry-run mode
4. Fallback simulation
5. Filename sanitization
6. Rate limiter logic
7. Secret masking
8. Encryption key derivation

**Usage**:
```bash
bash scripts/post_refactor_check.sh
```

**Expected Output**:
```
✅ Passed: 8
❌ Failed: 0
🎉 All checks PASSED!
```

#### 10. CLI Flags and Modes

**Added**:
- `--dry-run`: Validate configuration without starting bot
- `--mode=refactored`: Use refactored code path
- `--force-fallback`: Force fallback model for testing

**Examples**:
```bash
# Validate before deployment
python scripts/telegram_chatgpt_mode.py --dry-run

# Test fallback without breaking primary
python scripts/telegram_chatgpt_mode.py --force-fallback --dry-run

# Production mode
python scripts/telegram_chatgpt_mode.py --mode=refactored
```

---

## Day 7: Documentation and Deployment

### ✅ Completed Items

#### 11. Documentation

**Created**:
1. `SCRIPTS_OVERVIEW.md` - Complete script reference
2. `BOT_VALIDATION.md` - Step-by-step validation guide (Arabic)
3. `SECURITY_ACTION_PLAN.md` - This document

**Updated**:
1. `.env.example` - Removed weak defaults, added guidance
2. `railway.json` - Updated start command
3. `requirements.txt` - OpenAI upgrade

#### 12. Deployment Configuration

**railway.json**:
```json
{
  "deploy": {
    "startCommand": "python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py --mode=refactored"
  }
}
```

**Benefits**:
- Environment validated before bot starts
- Uses refactored secure code path
- Fails fast on misconfiguration

---

## Security Checklist - قائمة التحقق الأمنية

### Pre-Deployment Checks

- [ ] All secrets set in deployment environment (not in code)
- [ ] `OPENAI_MODEL` configured
- [ ] `TELEGRAM_ALLOWLIST` set for production
- [ ] Strong database passwords (not defaults)
- [ ] `SECRET_KEY` is unique and strong
- [ ] `verify_env.py` passes
- [ ] `post_refactor_check.sh` passes
- [ ] Rate limiting configured appropriately

### Post-Deployment Checks

- [ ] Bot responds to `/whoami`
- [ ] Bot responds to `/status`
- [ ] Rate limiting enforced
- [ ] Large files rejected
- [ ] Fallback model works (if configured)
- [ ] Logs don't expose full secrets
- [ ] File uploads sanitized

---

## Threat Model - نموذج التهديد

### Mitigated Threats

| Threat | Mitigation | Severity |
|--------|-----------|----------|
| Secret exposure in logs | Enhanced masking | High |
| Weak default credentials | Removed from examples | High |
| Telegram spam/abuse | Rate limiting | Medium |
| Path traversal in uploads | Filename sanitization | High |
| Large file DoS | File size limits | Medium |
| Single point of failure | Model fallback | Low |
| Data loss on restart | Deterministic encryption | Medium |

### Remaining Considerations

1. **Network Security**: 
   - Use HTTPS/TLS for all external connections
   - Railway provides this by default

2. **Database Security**:
   - Use strong passwords (not defaults)
   - Enable SSL/TLS for database connections
   - Regular backups

3. **Access Control**:
   - Always use `TELEGRAM_ALLOWLIST` in production
   - Regularly review authorized users
   - Monitor for unauthorized access attempts

4. **Monitoring**:
   - Set up alerts for rate limit violations
   - Monitor error rates and fallback usage
   - Track failed authentication attempts

---

## Future Security Enhancements

### Short-term (Next Sprint)

1. **Input Validation**:
   - Sanitize user prompts before sending to OpenAI
   - Maximum prompt length enforcement

2. **Audit Logging**:
   - Log all bot interactions with timestamps
   - Track model usage and costs
   - Record rate limit violations

3. **Session Management**:
   - Expire old chat sessions
   - Implement session timeout

### Medium-term (Next Month)

1. **Advanced Rate Limiting**:
   - Different limits for different command types
   - Temporary bans for repeated violations

2. **Content Filtering**:
   - Block malicious prompts
   - Implement content moderation

3. **Multi-factor Authentication**:
   - Optional 2FA for privileged commands

### Long-term (Next Quarter)

1. **Security Audit**:
   - Third-party security review
   - Penetration testing

2. **Compliance**:
   - GDPR compliance for user data
   - Data retention policies

3. **Advanced Monitoring**:
   - Anomaly detection
   - Real-time threat response

---

## Incident Response Plan

### Security Incident Procedure

1. **Detection**:
   - Monitor logs for unusual activity
   - Set up alerts for critical events

2. **Containment**:
   - Immediately revoke compromised credentials
   - Disable affected services if necessary

3. **Investigation**:
   - Review logs for attack vectors
   - Identify scope of compromise

4. **Recovery**:
   - Rotate all secrets
   - Update configurations
   - Redeploy services

5. **Post-Mortem**:
   - Document incident
   - Update security measures
   - Train team on lessons learned

### Emergency Contacts

- **Repository Owner**: @MOTEB1989
- **Security Issues**: Open private security advisory on GitHub

---

## Compliance and Best Practices

### General Security Guidelines

1. **Never commit secrets**:
   ```bash
   # Check before commit
   git diff | grep -E "sk-|password|secret"
   ```

2. **Regular updates**:
   ```bash
   # Update dependencies monthly
   pip install --upgrade -r requirements.txt
   ```

3. **Security scanning**:
   ```bash
   # Use tools like
   bandit -r scripts/
   safety check
   ```

4. **Code review**:
   - All security-related changes reviewed
   - Use GitHub branch protection

---

## Testing Security Measures

### Automated Tests

```bash
# Run all security checks
bash scripts/post_refactor_check.sh

# Specific tests
python -c "from scripts.lib.common import sanitize_filename; \
  assert sanitize_filename('../../../etc/passwd') == 'passwd'"
```

### Manual Tests

1. **Rate Limiting**: Send >20 messages/minute
2. **File Upload**: Try uploading >2MB file
3. **Path Traversal**: Upload file with `../` in name
4. **Secret Masking**: Check logs for exposed secrets

---

## Conclusion - الخلاصة

This 7-day security action plan addresses critical vulnerabilities and implements comprehensive security measures:

- ✅ Secrets properly masked
- ✅ Weak defaults eliminated
- ✅ Rate limiting implemented
- ✅ File uploads secured
- ✅ Fallback model added
- ✅ Encryption improved
- ✅ Comprehensive validation

**Status**: All items completed and tested.

**Next Steps**: 
1. Deploy to production
2. Monitor for issues
3. Continue with future enhancements

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: @MOTEB1989  
**Review Schedule**: Monthly
