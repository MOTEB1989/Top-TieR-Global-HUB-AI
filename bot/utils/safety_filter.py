#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
safety_filter.py

Basic content safety filtering (secrets detection).
فلتر الأمان للمحتوى.
"""

import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class SafetyFilter:
    """Filters sensitive content from user input."""
    
    def __init__(self):
        """Initialize safety filter with patterns."""
        # Patterns for common secret formats
        self.secret_patterns = [
            (r'sk-[A-Za-z0-9]{20,}', "OpenAI API key"),
            (r'ghp_[A-Za-z0-9]{36,}', "GitHub Personal Access Token"),
            (r'gho_[A-Za-z0-9]{36,}', "GitHub OAuth Token"),
            (r'ghs_[A-Za-z0-9]{36,}', "GitHub App Token"),
            (r'ghu_[A-Za-z0-9]{36,}', "GitHub User Token"),
            (r'glpat-[A-Za-z0-9_\-]{20,}', "GitLab Personal Access Token"),
            (r'xox[baprs]-[A-Za-z0-9\-]+', "Slack Token"),
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
            (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
            (r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com', "Google OAuth"),
            (r'sq0[a-z]{3}-[0-9A-Za-z\-_]{22,}', "Square OAuth Secret"),
            (r'-----BEGIN [A-Z]+ PRIVATE KEY-----', "Private Key"),
            (r'bearer\s+[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+', "JWT Token"),
            (r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+', "JWT Token (base64)"),
        ]
        
        logger.info(f"[safety_filter] Initialized with {len(self.secret_patterns)} patterns")
    
    def scan_for_secrets(self, text: str) -> Tuple[bool, List[str]]:
        """
        Scan text for potential secrets.
        
        Args:
            text: Text to scan
            
        Returns:
            Tuple of (has_secrets, list_of_detected_types)
        """
        detected = []
        
        for pattern, description in self.secret_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(description)
                logger.warning(f"[safety_filter] Detected potential secret: {description}")
        
        return len(detected) > 0, detected
    
    def filter_input(self, text: str) -> Tuple[bool, str, List[str]]:
        """
        Filter user input for sensitive content.
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (is_safe, message, detected_types)
            - is_safe: True if no secrets detected
            - message: Warning message if unsafe
            - detected_types: List of detected secret types
        """
        has_secrets, detected = self.scan_for_secrets(text)
        
        if has_secrets:
            warning = (
                "⚠️ **تحذير أمني - Security Warning**\n\n"
                "تم اكتشاف محتوى حساس محتمل في رسالتك:\n"
                "Potential sensitive content detected in your message:\n\n"
            )
            
            for secret_type in detected:
                warning += f"• {secret_type}\n"
            
            warning += (
                "\n**لن يتم معالجة هذه الرسالة لحماية بياناتك.**\n"
                "This message will not be processed to protect your data.\n\n"
                "الرجاء إزالة أي مفاتيح API، توكنات، أو معلومات حساسة وإعادة المحاولة.\n"
                "Please remove any API keys, tokens, or sensitive information and try again."
            )
            
            return False, warning, detected
        
        return True, "", []
    
    def mask_secrets(self, text: str) -> str:
        """
        Mask detected secrets in text (for logging).
        
        Args:
            text: Text to mask
            
        Returns:
            Text with secrets masked
        """
        masked_text = text
        
        for pattern, _ in self.secret_patterns:
            masked_text = re.sub(
                pattern,
                "[SECRET_REDACTED]",
                masked_text,
                flags=re.IGNORECASE
            )
        
        return masked_text
