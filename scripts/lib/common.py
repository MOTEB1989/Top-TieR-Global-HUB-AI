#!/usr/bin/env python3
"""
Common utility functions for Top-TieR-Global-HUB-AI scripts
Provides: masking, model selection, filename sanitization, rate limiting
"""

import os
import re
import time
import hashlib
import base64
from typing import Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta


# ================== Secret Masking ==================

SENSITIVE_SUFFIXES = ("_TOKEN", "_KEY", "_PASSWORD", "_PASS", "_AUTH")


def mask_secret(value: str, key: str) -> str:
    """
    Mask sensitive values for logging.
    
    Args:
        value: The value to potentially mask
        key: The environment variable key name
        
    Returns:
        Masked string if key ends with sensitive suffix, otherwise original value
    """
    if not value:
        return "***EMPTY***"
    
    key_upper = key.upper()
    if any(key_upper.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        if len(value) > 10:
            return value[:6] + "..." + value[-4:]
        return "***MASKED***"
    return value


def mask_env_dict(env_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Mask all sensitive values in an environment dictionary.
    
    Args:
        env_dict: Dictionary of environment variables
        
    Returns:
        New dictionary with sensitive values masked
    """
    return {k: mask_secret(v, k) for k, v in env_dict.items()}


# ================== OpenAI Model Selection ==================


def get_openai_models() -> Tuple[str, Optional[str]]:
    """
    Get primary and fallback OpenAI models from environment.
    
    Returns:
        Tuple of (primary_model, fallback_model or None)
        
    Raises:
        RuntimeError: If OPENAI_MODEL is not set
    """
    primary = os.getenv("OPENAI_MODEL", "").strip()
    if not primary:
        raise RuntimeError(
            "OPENAI_MODEL is required. Set it in your environment or .env file."
        )
    
    fallback = os.getenv("OPENAI_FALLBACK_MODEL", "").strip() or None
    return primary, fallback


def log_model_banner(primary: str, fallback: Optional[str]) -> None:
    """
    Log a structured banner showing configured models.
    
    Args:
        primary: Primary model name
        fallback: Optional fallback model name
    """
    print("=" * 60)
    print("🤖 OpenAI Model Configuration")
    print("=" * 60)
    print(f"  Primary Model:  {primary}")
    if fallback:
        print(f"  Fallback Model: {fallback}")
    else:
        print("  Fallback Model: Not configured")
    print("=" * 60)


# ================== Filename Sanitization ==================


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed filename length
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Remove any path components (prevent path traversal)
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    # Keep alphanumeric, dots, dashes, underscores
    filename = re.sub(r'[^\w\s.-]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Collapse multiple underscores/dashes
    filename = re.sub(r'[_-]+', '_', filename)
    
    # Truncate to max length while preserving extension
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        ext_len = len(ext)
        if ext_len < max_length - 10:  # Leave room for name
            name = name[:max_length - ext_len - 3] + "..."
            filename = name + ext
        else:
            filename = filename[:max_length]
    
    # Ensure we have something
    if not filename:
        filename = "unnamed_file"
    
    return filename


# ================== Rate Limiting ==================


class RateLimiter:
    """
    Simple token bucket rate limiter for per-user message limits.
    """
    
    def __init__(self, messages_per_minute: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            messages_per_minute: Maximum messages allowed per user per minute
        """
        self.messages_per_minute = messages_per_minute
        self.user_buckets: Dict[int, list] = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed to send a message.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is within rate limit, False otherwise
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Get user's message timestamps
        user_messages = self.user_buckets[user_id]
        
        # Remove old timestamps
        user_messages[:] = [ts for ts in user_messages if ts > cutoff]
        
        # Check if under limit
        if len(user_messages) >= self.messages_per_minute:
            return False
        
        # Add new timestamp
        user_messages.append(now)
        return True
    
    def get_wait_time(self, user_id: int) -> int:
        """
        Get seconds until user can send next message.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Seconds to wait, or 0 if can send immediately
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        user_messages = self.user_buckets[user_id]
        user_messages[:] = [ts for ts in user_messages if ts > cutoff]
        
        if len(user_messages) < self.messages_per_minute:
            return 0
        
        # Time until oldest message expires
        oldest = min(user_messages)
        wait_until = oldest + timedelta(minutes=1)
        wait_seconds = (wait_until - now).total_seconds()
        return max(0, int(wait_seconds))


# ================== File Size Validation ==================


def validate_file_size(file_size: int, max_size_mb: int = 2) -> Tuple[bool, str]:
    """
    Validate file size against maximum allowed.
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    max_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_bytes:
        size_mb = file_size / (1024 * 1024)
        return False, f"File too large: {size_mb:.2f}MB (max: {max_size_mb}MB)"
    
    return True, ""


# ================== Encryption Key Derivation ==================


def derive_fernet_key(secret_key: str) -> bytes:
    """
    Derive a deterministic Fernet key from SECRET_KEY using SHA-256.
    
    Args:
        secret_key: Source secret key string
        
    Returns:
        32-byte base64-encoded Fernet key
    """
    # Hash the secret key to get deterministic 32 bytes
    hash_digest = hashlib.sha256(secret_key.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(hash_digest)


# ================== Safe Main Wrapper ==================


def safe_main(func):
    """
    Decorator for main functions to handle errors gracefully.
    
    Args:
        func: Main function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    return wrapper
