#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
groq_client.py

Groq chat completion wrapper (OpenAI-compatible API).
محول Groq للدردشة.
"""

import os
import logging
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class GroqError(Exception):
    """Groq API error."""
    pass


class GroqClient:
    """Groq client (OpenAI-compatible API)."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            logger.warning("[groq_client] No API key configured")
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return bool(self.api_key)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 60
    ) -> str:
        """
        Call Groq chat completion API (OpenAI-compatible).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Generated text response
            
        Raises:
            GroqError: If API call fails
        """
        if not self.api_key:
            raise GroqError("مفتاح Groq غير مهيأ - Groq API key not configured")
        
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
                error_msg = f"Groq error {response.status_code}: {response.text[:200]}"
                logger.error(f"[groq_client] {error_msg}")
                raise GroqError(error_msg)
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Log usage
            usage = data.get("usage", {})
            logger.info(
                f"[groq_client] model={model} "
                f"tokens={usage.get('total_tokens', 'N/A')} "
                f"prompt={usage.get('prompt_tokens', 'N/A')} "
                f"completion={usage.get('completion_tokens', 'N/A')}"
            )
            
            return content
            
        except requests.exceptions.Timeout:
            raise GroqError("انتهت مهلة الاتصال بـ Groq - Groq request timeout")
        except requests.exceptions.RequestException as e:
            raise GroqError(f"خطأ في الاتصال بـ Groq - Connection error: {e}")
        except KeyError as e:
            raise GroqError(f"استجابة غير متوقعة من Groq - Unexpected response: {e}")
        except Exception as e:
            logger.error(f"[groq_client] Unexpected error: {e}")
            raise GroqError(f"خطأ غير متوقع - Unexpected error: {e}")
