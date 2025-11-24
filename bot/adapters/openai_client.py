#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
openai_client.py

OpenAI chat completion wrapper (non-streaming).
محول OpenAI للدردشة.
"""

import os
import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class OpenAIError(Exception):
    """OpenAI API error."""
    pass


class OpenAIClient:
    """OpenAI chat completions client."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            base_url: Base URL for API (defaults to env var or official)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        
        if not self.api_key:
            logger.warning("[openai_client] No API key configured")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return bool(self.api_key)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 60
    ) -> str:
        """
        Call OpenAI chat completion API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Generated text response
            
        Raises:
            OpenAIError: If API call fails
        """
        if not self.api_key:
            raise OpenAIError("مفتاح OpenAI غير مهيأ - OpenAI API key not configured")
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                error_msg = f"OpenAI error {response.status_code}: {response.text[:200]}"
                logger.error(f"[openai_client] {error_msg}")
                raise OpenAIError(error_msg)
            
            data = response.json()
            
            # Validate response structure
            if "choices" not in data or not data["choices"]:
                raise OpenAIError("استجابة غير متوقعة: لا توجد choices - No choices in response")
            
            content = data["choices"][0]["message"]["content"]
            
            # Log usage
            usage = data.get("usage", {})
            logger.info(
                f"[openai_client] model={model} "
                f"tokens={usage.get('total_tokens', 'N/A')} "
                f"prompt={usage.get('prompt_tokens', 'N/A')} "
                f"completion={usage.get('completion_tokens', 'N/A')}"
            )
            
            return content
            
        except requests.exceptions.Timeout:
            raise OpenAIError("انتهت مهلة الاتصال بـ OpenAI - OpenAI request timeout")
        except requests.exceptions.RequestException as e:
            raise OpenAIError(f"خطأ في الاتصال بـ OpenAI - Connection error: {e}")
        except KeyError as e:
            raise OpenAIError(f"استجابة غير متوقعة من OpenAI - Unexpected response: {e}")
        except Exception as e:
            logger.error(f"[openai_client] Unexpected error: {e}")
            raise OpenAIError(f"خطأ غير متوقع - Unexpected error: {e}")
