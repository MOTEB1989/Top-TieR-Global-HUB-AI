#!/usr/bin/env python3
"""
common.py - Shared utilities for bot scripts

Provides model selection logic with fallback support for resilience
when primary OpenAI model requests fail.
"""

import os
import logging
from typing import Optional, Tuple, Callable, Any

logger = logging.getLogger(__name__)


def select_model() -> Tuple[str, Optional[str]]:
    """
    Read and return primary and fallback model names from environment.
    
    Returns:
        Tuple of (primary_model, fallback_model)
        - primary_model: From OPENAI_MODEL env var (defaults to 'gpt-4o-mini')
        - fallback_model: From OPENAI_FALLBACK_MODEL env var (optional, can be None)
    """
    primary = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    fallback = os.getenv("OPENAI_FALLBACK_MODEL")
    
    return primary, fallback


def should_retry_with_fallback(exception: Exception) -> bool:
    """
    Determine if an exception warrants retrying with fallback model.
    
    Args:
        exception: The exception raised during API call
        
    Returns:
        True if fallback should be attempted, False otherwise
    """
    error_str = str(exception).lower()
    
    # Check for rate limit errors (HTTP 429)
    if "429" in error_str or "rate limit" in error_str or "rate_limit" in error_str:
        return True
    
    # Check for model not found / unsupported model
    if "model" in error_str and ("not found" in error_str or "does not exist" in error_str):
        return True
    
    # Check for invalid request due to model issues
    if "invalid_request_error" in error_str and "model" in error_str:
        return True
    
    # Check for temporary service issues
    if "503" in error_str or "service unavailable" in error_str:
        return True
    
    # Check for timeout issues
    if "timeout" in error_str or "timed out" in error_str:
        return True
    
    return False


def try_model_with_fallback(
    api_call: Callable[[str], Any],
    primary_model: str,
    fallback_model: Optional[str],
    operation_name: str = "API call"
) -> Any:
    """
    Execute an API call with automatic fallback to secondary model on failure.
    
    Args:
        api_call: Callable that takes model name and performs the API operation
        primary_model: Primary model to try first
        fallback_model: Fallback model to try if primary fails (optional)
        operation_name: Description of operation for logging
        
    Returns:
        Result from the API call
        
    Raises:
        Exception: If both primary and fallback (if available) fail
        
    Note:
        - Only retries ONCE with fallback model
        - Logs warnings when switching to fallback
    """
    try:
        logger.debug(f"Attempting {operation_name} with primary model: {primary_model}")
        return api_call(primary_model)
    except Exception as e:
        # Check if we should retry with fallback
        if fallback_model and should_retry_with_fallback(e):
            logger.warning(
                f"Primary model '{primary_model}' failed for {operation_name}: {e}. "
                f"Attempting fallback to '{fallback_model}'..."
            )
            try:
                result = api_call(fallback_model)
                logger.info(f"Successfully completed {operation_name} using fallback model '{fallback_model}'")
                return result
            except Exception as fallback_error:
                logger.error(
                    f"Fallback model '{fallback_model}' also failed for {operation_name}: {fallback_error}"
                )
                raise fallback_error
        else:
            # No fallback available or error doesn't warrant retry
            if fallback_model:
                logger.debug(f"Error does not warrant fallback retry: {e}")
            raise e
