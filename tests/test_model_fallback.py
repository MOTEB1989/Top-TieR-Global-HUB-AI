"""
Unit tests for model fallback functionality in scripts/lib/common.py
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Path configuration handled by conftest.py
from lib.common import (
    select_model,
    should_retry_with_fallback,
    try_model_with_fallback
)


class TestSelectModel:
    """Test cases for select_model() function"""
    
    def test_select_model_with_both_set(self):
        """Test select_model when both primary and fallback are set"""
        with patch.dict(os.environ, {
            'OPENAI_MODEL': 'gpt-4o-mini',
            'OPENAI_FALLBACK_MODEL': 'gpt-4o'
        }):
            primary, fallback = select_model()
            assert primary == 'gpt-4o-mini'
            assert fallback == 'gpt-4o'
    
    def test_select_model_with_default_primary(self):
        """Test select_model uses default when OPENAI_MODEL not set"""
        with patch.dict(os.environ, {}, clear=True):
            primary, fallback = select_model()
            assert primary == 'gpt-4o-mini'  # default
            assert fallback is None
    
    def test_select_model_without_fallback(self):
        """Test select_model when only primary is set"""
        with patch.dict(os.environ, {
            'OPENAI_MODEL': 'gpt-4o'
        }, clear=True):
            primary, fallback = select_model()
            assert primary == 'gpt-4o'
            assert fallback is None


class TestShouldRetryWithFallback:
    """Test cases for should_retry_with_fallback() function"""
    
    def test_rate_limit_error_429(self):
        """Test detection of rate limit errors (HTTP 429)"""
        error = Exception("OpenAI error 429: Rate limit exceeded")
        assert should_retry_with_fallback(error) is True
    
    def test_rate_limit_text(self):
        """Test detection of rate limit text in error"""
        error = Exception("rate limit reached for requests")
        assert should_retry_with_fallback(error) is True
    
    def test_model_not_found(self):
        """Test detection of model not found errors"""
        error = Exception("The model 'gpt-5' does not exist")
        assert should_retry_with_fallback(error) is True
    
    def test_invalid_request_model_error(self):
        """Test detection of invalid_request_error with model"""
        error = Exception("invalid_request_error: The model is unavailable")
        assert should_retry_with_fallback(error) is True
    
    def test_service_unavailable_503(self):
        """Test detection of service unavailable (503)"""
        error = Exception("503 Service temporarily unavailable")
        assert should_retry_with_fallback(error) is True
    
    def test_timeout_error(self):
        """Test detection of timeout errors"""
        error = Exception("Request timed out after 60 seconds")
        assert should_retry_with_fallback(error) is True
    
    def test_non_retriable_error(self):
        """Test that non-retriable errors return False"""
        error = Exception("Invalid API key provided")
        assert should_retry_with_fallback(error) is False
    
    def test_generic_error(self):
        """Test that generic errors return False"""
        error = Exception("Something went wrong")
        assert should_retry_with_fallback(error) is False


class TestTryModelWithFallback:
    """Test cases for try_model_with_fallback() function"""
    
    def test_successful_primary_call(self):
        """Test that successful primary call returns result immediately"""
        api_call = MagicMock(return_value="success")
        result = try_model_with_fallback(
            api_call=api_call,
            primary_model="gpt-4o-mini",
            fallback_model="gpt-4o",
            operation_name="test"
        )
        
        assert result == "success"
        api_call.assert_called_once_with("gpt-4o-mini")
    
    def test_fallback_on_rate_limit(self):
        """Test fallback when primary fails with rate limit"""
        api_call = MagicMock()
        api_call.side_effect = [
            Exception("OpenAI error 429: Rate limit exceeded"),
            "fallback success"
        ]
        
        result = try_model_with_fallback(
            api_call=api_call,
            primary_model="gpt-4o-mini",
            fallback_model="gpt-4o",
            operation_name="test"
        )
        
        assert result == "fallback success"
        assert api_call.call_count == 2
        api_call.assert_any_call("gpt-4o-mini")
        api_call.assert_any_call("gpt-4o")
    
    def test_no_fallback_on_non_retriable_error(self):
        """Test that non-retriable errors don't trigger fallback"""
        api_call = MagicMock()
        api_call.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception, match="Invalid API key"):
            try_model_with_fallback(
                api_call=api_call,
                primary_model="gpt-4o-mini",
                fallback_model="gpt-4o",
                operation_name="test"
            )
        
        # Should only call primary, not fallback
        api_call.assert_called_once_with("gpt-4o-mini")
    
    def test_no_fallback_when_not_configured(self):
        """Test that error is raised when no fallback is configured"""
        api_call = MagicMock()
        api_call.side_effect = Exception("OpenAI error 429: Rate limit exceeded")
        
        with pytest.raises(Exception, match="Rate limit exceeded"):
            try_model_with_fallback(
                api_call=api_call,
                primary_model="gpt-4o-mini",
                fallback_model=None,  # No fallback
                operation_name="test"
            )
        
        # Should only call primary
        api_call.assert_called_once_with("gpt-4o-mini")
    
    def test_both_models_fail(self):
        """Test that error is raised when both primary and fallback fail"""
        api_call = MagicMock()
        api_call.side_effect = [
            Exception("OpenAI error 429: Rate limit exceeded"),
            Exception("OpenAI error 429: Rate limit exceeded on fallback")
        ]
        
        with pytest.raises(Exception, match="Rate limit exceeded on fallback"):
            try_model_with_fallback(
                api_call=api_call,
                primary_model="gpt-4o-mini",
                fallback_model="gpt-4o",
                operation_name="test"
            )
        
        # Should call both models
        assert api_call.call_count == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
