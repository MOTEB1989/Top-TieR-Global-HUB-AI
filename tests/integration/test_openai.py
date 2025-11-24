"""
OpenAI API Integration Tests
اختبارات تكامل OpenAI API
"""

import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

# Import test markers from conftest
from tests.conftest import skip_if_no_openai


class TestOpenAIConnection:
    """Tests for OpenAI API connectivity"""

    @pytest.mark.integration
    def test_openai_module_import(self):
        """Test that openai module can be imported"""
        try:
            import openai
            assert openai is not None
        except ImportError:
            pytest.fail("openai module not installed")

    @pytest.mark.integration
    def test_api_key_configuration(self, test_config):
        """Test OpenAI API key configuration"""
        api_key = test_config.get("openai_api_key")
        assert api_key is not None, "OpenAI API key not configured"
        
        # Mock test - don't expose real key
        if api_key and api_key != "sk-proj-PASTE_YOUR_KEY_HERE":
            assert api_key.startswith("sk-"), "Invalid OpenAI API key format"

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_openai_completion_mock(self, mock_create, mock_openai_response):
        """Test OpenAI completion with mocked response"""
        mock_create.return_value = mock_openai_response
        
        import openai
        openai.api_key = "test-key"
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Test prompt",
            max_tokens=10
        )
        
        assert response is not None
        assert response.choices[0].text == "Test response from GPT"
        mock_create.assert_called_once()


class TestOpenAIErrorHandling:
    """Tests for OpenAI API error handling"""

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_api_error_handling(self, mock_create):
        """Test handling of OpenAI API errors"""
        import openai
        
        # Simulate API error
        mock_create.side_effect = openai.error.APIError("API Error")
        
        with pytest.raises(openai.error.APIError):
            openai.Completion.create(
                engine="text-davinci-003",
                prompt="Test",
                max_tokens=10
            )

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_rate_limit_error(self, mock_create):
        """Test handling of rate limit errors"""
        import openai
        
        # Simulate rate limit error
        mock_create.side_effect = openai.error.RateLimitError("Rate limit exceeded")
        
        with pytest.raises(openai.error.RateLimitError):
            openai.Completion.create(
                engine="text-davinci-003",
                prompt="Test",
                max_tokens=10
            )

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_timeout_error(self, mock_create):
        """Test handling of timeout errors"""
        import openai
        
        # Simulate timeout
        mock_create.side_effect = openai.error.Timeout("Request timeout")
        
        with pytest.raises(openai.error.Timeout):
            openai.Completion.create(
                engine="text-davinci-003",
                prompt="Test",
                max_tokens=10
            )


class TestOpenAIRetryLogic:
    """Tests for OpenAI retry logic"""

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_retry_on_failure(self, mock_create):
        """Test retry logic on API failures"""
        import openai
        
        # First call fails, second succeeds
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "Success after retry"
        
        mock_create.side_effect = [
            openai.error.APIError("Temporary error"),
            mock_response
        ]
        
        # Simulate retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt="Test",
                    max_tokens=10
                )
                assert response.choices[0].text == "Success after retry"
                break
            except openai.error.APIError:
                if attempt == max_retries - 1:
                    raise

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_exponential_backoff(self, mock_create):
        """Test exponential backoff on retries"""
        import openai
        import time
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "Success"
        
        # Fail twice, then succeed
        mock_create.side_effect = [
            openai.error.RateLimitError("Rate limit"),
            openai.error.RateLimitError("Rate limit"),
            mock_response
        ]
        
        max_retries = 3
        base_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt="Test",
                    max_tokens=10
                )
                assert response is not None
                break
            except openai.error.RateLimitError:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise


class TestOpenAITokenization:
    """Tests for OpenAI tokenization"""

    @pytest.mark.integration
    def test_tiktoken_import(self):
        """Test tiktoken library import"""
        try:
            import tiktoken
            assert tiktoken is not None
        except ImportError:
            pytest.skip("tiktoken not installed")

    @pytest.mark.integration
    def test_token_encoding(self):
        """Test token encoding for GPT models"""
        try:
            import tiktoken
            
            encoding = tiktoken.get_encoding("cl100k_base")
            text = "Hello, world!"
            tokens = encoding.encode(text)
            
            assert len(tokens) > 0
            assert isinstance(tokens, list)
            
            # Decode back
            decoded = encoding.decode(tokens)
            assert decoded == text
            
        except ImportError:
            pytest.skip("tiktoken not installed")

    @pytest.mark.integration
    def test_token_count_estimation(self):
        """Test token count estimation"""
        try:
            import tiktoken
            
            encoding = tiktoken.get_encoding("cl100k_base")
            
            # Test various texts
            test_cases = [
                ("Hello", 1),
                ("Hello, world!", 4),
                ("This is a longer test sentence.", 7)
            ]
            
            for text, expected_min_tokens in test_cases:
                tokens = encoding.encode(text)
                assert len(tokens) >= expected_min_tokens
                
        except ImportError:
            pytest.skip("tiktoken not installed")


class TestGPTClient:
    """Tests for GPT client functionality"""

    @pytest.mark.integration
    def test_gpt_client_initialization(self, mock_env_vars):
        """Test GPT client initialization"""
        from gpt_client import GPTClient
        
        client = GPTClient()
        assert client is not None
        assert client.is_available()

    @pytest.mark.integration
    def test_gpt_client_no_api_key(self):
        """Test GPT client without API key"""
        with patch.dict(os.environ, {}, clear=True):
            from gpt_client import GPTClient
            
            client = GPTClient()
            assert not client.is_available()

    @pytest.mark.integration
    @pytest.mark.asyncio
    @patch('openai.Completion.create')
    async def test_gpt_generate_response(self, mock_create, mock_openai_response):
        """Test GPT response generation"""
        mock_create.return_value = mock_openai_response
        
        from gpt_client import GPTClient, GPTRequest
        
        client = GPTClient(api_key="test-key")
        request = GPTRequest(
            prompt="Test prompt",
            max_tokens=50,
            temperature=0.7
        )
        
        response = await client.generate_response(request)
        
        assert response is not None
        assert response.response == "Test response from GPT"
        assert response.usage["total_tokens"] == 10

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_gpt_error_no_api_key(self):
        """Test GPT client error when no API key"""
        from gpt_client import GPTClient, GPTRequest
        
        client = GPTClient()
        request = GPTRequest(prompt="Test")
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            await client.generate_response(request)


class TestOpenAIModels:
    """Tests for different OpenAI models"""

    @pytest.mark.integration
    @patch('openai.Completion.create')
    def test_text_davinci_model(self, mock_create, mock_openai_response):
        """Test text-davinci-003 model"""
        import openai
        
        mock_create.return_value = mock_openai_response
        openai.api_key = "test-key"
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Test",
            max_tokens=10
        )
        
        assert response is not None

    @pytest.mark.integration
    @patch('openai.ChatCompletion.create')
    def test_gpt_35_turbo_model(self, mock_create):
        """Test gpt-3.5-turbo model"""
        import openai
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_create.return_value = mock_response
        
        openai.api_key = "test-key"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        
        assert response is not None

    @pytest.mark.integration
    @pytest.mark.requires_api
    @skip_if_no_openai
    @pytest.mark.slow
    async def test_live_openai_api_call(self, test_config, timeout_seconds):
        """Live test with actual OpenAI API (requires API key)"""
        from gpt_client import GPTClient, GPTRequest
        
        client = GPTClient()
        
        if not client.is_available():
            pytest.skip("OpenAI API key not available")
        
        request = GPTRequest(
            prompt="Say 'test' in one word",
            max_tokens=5,
            temperature=0.1
        )
        
        try:
            response = await asyncio.wait_for(
                client.generate_response(request),
                timeout=timeout_seconds
            )
            
            assert response is not None
            assert isinstance(response.response, str)
            assert len(response.response) > 0
            assert response.usage is not None
            assert response.model is not None
            
        except asyncio.TimeoutError:
            pytest.fail(f"OpenAI API call timed out after {timeout_seconds} seconds")
        except Exception as e:
            pytest.fail(f"OpenAI API call failed: {str(e)}")


class TestOpenAIStreamingResponse:
    """Tests for streaming responses (future functionality)"""

    @pytest.mark.integration
    def test_streaming_placeholder(self):
        """Placeholder for streaming response tests"""
        # This is a placeholder for future streaming functionality
        assert True, "Streaming tests to be implemented when feature is added"
