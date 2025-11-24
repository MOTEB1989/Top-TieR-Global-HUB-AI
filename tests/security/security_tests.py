"""
Security Vulnerability Tests
Tests for common security vulnerabilities and attack vectors.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.security.validators import InputValidator, OutputValidator
from scripts.security.rate_limiter import TokenBucketRateLimiter, SlidingWindowRateLimiter


class TestInputValidation:
    """Test input validation and sanitization."""

    @pytest.mark.security
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection."""
        # Malicious inputs
        malicious_inputs = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT NULL--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for inp in malicious_inputs:
            assert InputValidator.detect_sql_injection(inp), f"Failed to detect SQL injection: {inp}"
        
        # Safe inputs
        safe_inputs = [
            "normal text",
            "user@example.com",
            "123456"
        ]
        
        for inp in safe_inputs:
            assert not InputValidator.detect_sql_injection(inp), f"False positive for SQL injection: {inp}"

    @pytest.mark.security
    def test_xss_detection(self):
        """Test XSS attack detection."""
        # Malicious inputs
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='evil.com'>",
            "<body onload=alert('XSS')>"
        ]
        
        for inp in xss_inputs:
            assert InputValidator.detect_xss(inp), f"Failed to detect XSS: {inp}"
        
        # Safe inputs
        safe_inputs = [
            "This is normal text",
            "Email: user@example.com",
            "Price: $100"
        ]
        
        for inp in safe_inputs:
            assert not InputValidator.detect_xss(inp), f"False positive for XSS: {inp}"

    @pytest.mark.security
    def test_email_validation(self):
        """Test email format validation."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "admin+tag@company.org"
        ]
        
        for email in valid_emails:
            assert InputValidator.validate_email(email), f"Valid email rejected: {email}"
        
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user name@example.com",
            "user@.com"
        ]
        
        for email in invalid_emails:
            assert not InputValidator.validate_email(email), f"Invalid email accepted: {email}"

    @pytest.mark.security
    def test_api_key_validation(self):
        """Test API key validation."""
        # Valid keys
        valid_keys = [
            "sk-1234567890abcdefghijklmnop",
            "ghp_1234567890abcdefghijklmnop"
        ]
        
        for key in valid_keys:
            assert InputValidator.validate_api_key(key), f"Valid API key rejected: {key[:10]}..."
        
        # Invalid keys (placeholders)
        invalid_keys = [
            "PASTE_YOUR_KEY_HERE",
            "${{secrets.API_KEY}}",
            "INSERT_KEY",
            "short"
        ]
        
        for key in invalid_keys:
            assert not InputValidator.validate_api_key(key), f"Invalid API key accepted: {key}"

    @pytest.mark.security
    def test_string_sanitization(self):
        """Test string sanitization."""
        # Test null byte removal
        dirty = "text\x00with\x00nulls"
        clean = InputValidator.sanitize_string(dirty)
        assert "\x00" not in clean, "Null bytes not removed"
        
        # Test length limiting
        long_string = "a" * 2000
        clean = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(clean) <= 100, "String not truncated"

    @pytest.mark.security
    def test_html_sanitization(self):
        """Test HTML escape sanitization."""
        dangerous_html = "<script>alert('xss')</script>"
        safe_html = InputValidator.sanitize_html(dangerous_html)
        
        assert "<script>" not in safe_html, "Script tags not escaped"
        assert "&lt;" in safe_html, "HTML not properly escaped"

    @pytest.mark.security
    def test_filename_sanitization(self):
        """Test filename sanitization for path traversal prevention."""
        dangerous_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "file<script>.txt",
            "file|name.txt"
        ]
        
        for fname in dangerous_filenames:
            safe = OutputValidator.sanitize_filename(fname)
            assert ".." not in safe, f"Path traversal not prevented: {fname}"
            assert "/" not in safe, f"Directory separator not removed: {fname}"
            assert "\\" not in safe, f"Backslash not removed: {fname}"


class TestRateLimiting:
    """Test rate limiting mechanisms."""

    @pytest.mark.security
    def test_token_bucket_rate_limiting(self):
        """Test token bucket rate limiter."""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        
        user_id = "test_user"
        
        # Should allow first 5 requests
        for i in range(5):
            assert limiter.is_allowed(user_id), f"Request {i+1} should be allowed"
        
        # 6th request should be denied
        assert not limiter.is_allowed(user_id), "6th request should be denied"
        
        # Reset and try again
        limiter.reset(user_id)
        assert limiter.is_allowed(user_id), "First request after reset should be allowed"

    @pytest.mark.security
    def test_sliding_window_rate_limiting(self):
        """Test sliding window rate limiter."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
        
        user_id = "test_user"
        
        # Should allow first 3 requests
        for i in range(3):
            assert limiter.is_allowed(user_id), f"Request {i+1} should be allowed"
        
        # 4th request should be denied
        assert not limiter.is_allowed(user_id), "4th request should be denied"
        
        # Check request count
        count = limiter.get_request_count(user_id)
        assert count == 3, f"Expected 3 requests, got {count}"


class TestSecretManagement:
    """Test secret management security."""

    @pytest.mark.security
    def test_sensitive_data_masking(self):
        """Test masking of sensitive data."""
        api_key = "sk-1234567890abcdefghijklmnop"
        masked = OutputValidator.mask_sensitive_data(api_key, visible_chars=4)
        
        assert masked.endswith("mnop"), "Last 4 characters should be visible"
        assert masked.startswith("*"), "Beginning should be masked"
        assert len(masked) == len(api_key), "Length should be preserved"

    @pytest.mark.security
    def test_error_message_sanitization(self):
        """Test error message sanitization to prevent info leakage."""
        class TestError(Exception):
            pass
        
        error = TestError("Database error: password='secret123' at line 42")
        sanitized = OutputValidator.sanitize_error_message(error)
        
        assert "secret123" not in sanitized, "Password leaked in error message"
        assert "[REDACTED]" in sanitized or "password" not in sanitized.lower(), "Sensitive info not redacted"


class TestAuthenticationBypass:
    """Test authentication bypass attempts."""

    @pytest.mark.security
    def test_telegram_user_id_validation(self):
        """Test Telegram user ID validation."""
        # Valid user IDs
        valid_ids = [123456, "789012", 999999999]
        for uid in valid_ids:
            assert InputValidator.validate_telegram_user_id(uid), f"Valid ID rejected: {uid}"
        
        # Invalid user IDs
        invalid_ids = [0, -1, "invalid", None, ""]
        for uid in invalid_ids:
            assert not InputValidator.validate_telegram_user_id(uid), f"Invalid ID accepted: {uid}"


class TestCryptography:
    """Test cryptographic operations."""

    @pytest.mark.security
    def test_password_hashing(self):
        """Test password hashing is one-way."""
        from scripts.security.encryption import DataEncryptor
        
        password = "SecurePassword123!"
        hash1 = DataEncryptor.hash_data(password)
        hash2 = DataEncryptor.hash_data(password)
        
        # Same input should produce same hash
        assert hash1 == hash2, "Hashes should be consistent"
        
        # Hash should be different from original
        assert hash1 != password, "Hash should not equal password"
        
        # Hash should be hexadecimal
        assert all(c in "0123456789abcdef" for c in hash1), "Hash should be hexadecimal"

    @pytest.mark.security
    def test_encryption_decryption(self):
        """Test encryption and decryption."""
        from scripts.security.encryption import DataEncryptor
        
        encryptor = DataEncryptor()
        sensitive_data = "API_KEY=sk-1234567890"
        
        # Encrypt
        encrypted = encryptor.encrypt_to_string(sensitive_data)
        
        # Encrypted should be different
        assert encrypted != sensitive_data, "Encrypted data should differ from original"
        
        # Decrypt
        decrypted = encryptor.decrypt_from_string(encrypted)
        assert decrypted == sensitive_data, "Decrypted data should match original"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
