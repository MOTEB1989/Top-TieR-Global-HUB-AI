#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
anthropic_client.py

Anthropic (Claude) chat completion wrapper (placeholder/basic implementation).
محول Anthropic للدردشة.
"""

import os
import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class AnthropicError(Exception):
    """Anthropic API error."""
    pass


class AnthropicClient:
    """Anthropic Claude client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1"
        
        if not self.api_key:
            logger.warning("[anthropic_client] No API key configured")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return bool(self.api_key)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 60
    ) -> str:
        """
        Call Anthropic messages API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Generated text response
            
        Raises:
            AnthropicError: If API call fails
        """
        if not self.api_key:
            raise AnthropicError("مفتاح Anthropic غير مهيأ - Anthropic API key not configured")
        
        # Convert messages: extract system prompt if present
        system_prompt = ""
        api_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                api_messages.append(msg)
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "model": model,
            "messages": api_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                error_msg = f"Anthropic error {response.status_code}: {response.text[:200]}"
                logger.error(f"[anthropic_client] {error_msg}")
                raise AnthropicError(error_msg)
            
            data = response.json()
            content = data["content"][0]["text"]
            
            # Log usage
            usage = data.get("usage", {})
            logger.info(
                f"[anthropic_client] model={model} "
                f"input_tokens={usage.get('input_tokens', 'N/A')} "
                f"output_tokens={usage.get('output_tokens', 'N/A')}"
            )
            
            return content
            
        except requests.exceptions.Timeout:
            raise AnthropicError("انتهت مهلة الاتصال بـ Anthropic - Anthropic request timeout")
        except requests.exceptions.RequestException as e:
            raise AnthropicError(f"خطأ في الاتصال بـ Anthropic - Connection error: {e}")
        except (KeyError, IndexError) as e:
            raise AnthropicError(f"استجابة غير متوقعة من Anthropic - Unexpected response: {e}")
        except Exception as e:
            logger.error(f"[anthropic_client] Unexpected error: {e}")
            raise AnthropicError(f"خطأ غير متوقع - Unexpected error: {e}")
