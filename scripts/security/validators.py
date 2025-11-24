"""
Input/Output Validation Module
Provides comprehensive validation and sanitization for security.
"""

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse


class InputValidator:
    """
    Validates and sanitizes user inputs to prevent injection attacks.
    """

    # Regex patterns for common validations
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,32}$")
    PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{1,14}$")
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    
    # Dangerous patterns for SQL injection
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b|\bAND\b).*?=.*?",
        r";\s*DROP\s+TABLE",
        r";\s*DELETE\s+FROM",
        r";\s*UPDATE\s+",
        r";\s*INSERT\s+INTO",
        r"--",
        r"/\*.*?\*/",
        r"xp_cmdshell",
        r"exec\s*\(",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or len(email) > 254:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format (alphanumeric, underscore, hyphen).
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username:
            return False
        return bool(InputValidator.USERNAME_PATTERN.match(username))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format (E.164 format).
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        return bool(InputValidator.PHONE_PATTERN.match(phone))

    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Validate URL format and scheme.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]
        
        try:
            parsed = urlparse(url)
            return parsed.scheme in allowed_schemes and bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """
        Detect potential SQL injection attempts.
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not text:
            return False
        
        text_upper = text.upper()
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def detect_xss(text: str) -> bool:
        """
        Detect potential XSS (Cross-Site Scripting) attempts.
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious patterns found, False otherwise
        """
        if not text:
            return False
        
        for pattern in InputValidator.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string by removing dangerous characters.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Remove control characters except newlines and tabs
        text = "".join(char for char in text if ord(char) >= 32 or char in ["\n", "\t"])
        
        return text.strip()

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML by escaping special characters.
        
        Args:
            text: Text to sanitize
            
        Returns:
            HTML-safe string
        """
        if not text:
            return ""
        
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
        }
        
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        
        return text

    @staticmethod
    def validate_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """
        Validate integer value with optional range check.
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            int_value = int(value)
            
            if min_val is not None and int_value < min_val:
                return False
            if max_val is not None and int_value > max_val:
                return False
            
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_telegram_user_id(user_id: Union[int, str]) -> bool:
        """
        Validate Telegram user ID format.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if valid, False otherwise
        """
        try:
            uid = int(user_id)
            # Telegram user IDs are positive integers
            return uid > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_api_key(api_key: str, prefix: Optional[str] = None) -> bool:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            prefix: Expected prefix (e.g., "sk-" for OpenAI)
            
        Returns:
            True if valid, False otherwise
        """
        if not api_key or len(api_key) < 10:
            return False
        
        if prefix and not api_key.startswith(prefix):
            return False
        
        # Check for placeholder values
        placeholder_patterns = ["PASTE_", "YOUR_", "INSERT_", "EXAMPLE_", "${{"]
        for pattern in placeholder_patterns:
            if pattern in api_key:
                return False
        
        return True


class OutputValidator:
    """
    Validates and sanitizes output data before sending to clients.
    """

    @staticmethod
    def sanitize_error_message(error: Exception) -> str:
        """
        Sanitize error messages to prevent information leakage.
        
        Args:
            error: Exception object
            
        Returns:
            Safe error message
        """
        error_str = str(error)
        
        # Remove sensitive patterns
        sensitive_patterns = [
            r"password\s*=\s*['\"].*?['\"]",
            r"api[_-]?key\s*=\s*['\"].*?['\"]",
            r"token\s*=\s*['\"].*?['\"]",
            r"secret\s*=\s*['\"].*?['\"]",
            r"jdbc:.*?://.*?@",
        ]
        
        for pattern in sensitive_patterns:
            error_str = re.sub(pattern, "[REDACTED]", error_str, flags=re.IGNORECASE)
        
        return error_str

    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """
        Mask sensitive data showing only last N characters.
        
        Args:
            data: Data to mask
            mask_char: Character to use for masking
            visible_chars: Number of characters to keep visible
            
        Returns:
            Masked string
        """
        if not data or len(data) <= visible_chars:
            return mask_char * len(data) if data else ""
        
        masked_length = len(data) - visible_chars
        return mask_char * masked_length + data[-visible_chars:]

    @staticmethod
    def validate_json_response(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate JSON response structure.
        
        Args:
            data: Response data
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file operations.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove path traversal attempts
        filename = filename.replace("..", "").replace("/", "").replace("\\", "")
        
        # Keep only alphanumeric, dots, hyphens, underscores
        filename = re.sub(r"[^\w\.-]", "_", filename)
        
        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
            name = name[: max_length - len(ext) - 1]
            filename = f"{name}.{ext}" if ext else name
        
        return filename


# Example usage and testing
if __name__ == "__main__":
    print("=== Input Validation Examples ===\n")
    
    # Email validation
    emails = ["user@example.com", "invalid.email", "test@test"]
    for email in emails:
        valid = InputValidator.validate_email(email)
        print(f"Email '{email}': {'✓ Valid' if valid else '✗ Invalid'}")
    
    # SQL injection detection
    print("\n=== SQL Injection Detection ===")
    test_inputs = [
        "SELECT * FROM users",
        "normal input",
        "admin' OR '1'='1",
        "'; DROP TABLE users--",
    ]
    for inp in test_inputs:
        is_suspicious = InputValidator.detect_sql_injection(inp)
        print(f"Input '{inp}': {'⚠ Suspicious' if is_suspicious else '✓ Safe'}")
    
    # XSS detection
    print("\n=== XSS Detection ===")
    test_inputs = [
        "Hello, world!",
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
    ]
    for inp in test_inputs:
        is_xss = InputValidator.detect_xss(inp)
        print(f"Input '{inp[:30]}': {'⚠ XSS Detected' if is_xss else '✓ Safe'}")
    
    # Output sanitization
    print("\n=== Output Sanitization ===")
    api_key = "sk-proj-1234567890abcdefghijklmnop"
    masked = OutputValidator.mask_sensitive_data(api_key, visible_chars=4)
    print(f"Original: {api_key}")
    print(f"Masked: {masked}")
    
    # Filename sanitization
    print("\n=== Filename Sanitization ===")
    filenames = ["../../../etc/passwd", "my file.txt", "test<script>.js"]
    for fname in filenames:
        sanitized = OutputValidator.sanitize_filename(fname)
        print(f"Original: '{fname}' → Sanitized: '{sanitized}'")
