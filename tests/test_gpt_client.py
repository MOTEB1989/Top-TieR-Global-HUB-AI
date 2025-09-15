import os
import sys
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from api_server import app
from gpt_client import GPTClient, GPTRequest, GPTResponse


client = TestClient(app)


class TestGPTClient:
    """Test cases for GPTClient"""
    
    def test_gpt_client_no_api_key(self):
        """Test GPT client without API key"""
        with patch.dict(os.environ, {}, clear=True):
            gpt_client = GPTClient()
            assert not gpt_client.is_available()
    
    def test_gpt_client_with_api_key(self):
        """Test GPT client with API key"""
        gpt_client = GPTClient(api_key="test-key")
        assert gpt_client.is_available()
    
    @pytest.mark.asyncio
    async def test_generate_response_no_api_key(self):
        """Test generate_response without API key"""
        gpt_client = GPTClient()
        request = GPTRequest(prompt="Hello, world!")
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            await gpt_client.generate_response(request)
    
    @pytest.mark.asyncio
    @patch('openai.Completion.create')
    async def test_generate_response_success(self, mock_openai_create):
        """Test successful GPT response generation"""
        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "  Hello! How can I help you?  "
        mock_response.usage = {"total_tokens": 10}
        mock_response.model = "text-davinci-003"
        mock_openai_create.return_value = mock_response
        
        gpt_client = GPTClient(api_key="test-key")
        request = GPTRequest(prompt="Hello, world!")
        
        response = await gpt_client.generate_response(request)
        
        assert isinstance(response, GPTResponse)
        assert response.response == "Hello! How can I help you?"
        assert response.usage == {"total_tokens": 10}
        assert response.model == "text-davinci-003"
    
    @pytest.mark.asyncio
    @patch('openai.Completion.create')
    async def test_generate_response_api_error(self, mock_openai_create):
        """Test GPT API error handling"""
        mock_openai_create.side_effect = Exception("API Error")
        
        gpt_client = GPTClient(api_key="test-key")
        request = GPTRequest(prompt="Hello, world!")
        
        with pytest.raises(RuntimeError, match="GPT API error: API Error"):
            await gpt_client.generate_response(request)


class TestGPTEndpoint:
    """Test cases for /gpt endpoint"""
    
    def test_gpt_endpoint_no_api_key(self):
        """Test /gpt endpoint without API key configured"""
        with patch.dict(os.environ, {}, clear=True):
            # Reinitialize the gpt_client in the module
            with patch('api_server.gpt_client') as mock_client:
                mock_client.is_available.return_value = False
                
                response = client.post(
                    "/gpt",
                    json={"prompt": "Hello, world!"}
                )
                
                assert response.status_code == 503
                assert "GPT service unavailable" in response.json()["detail"]
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set - skipping live test"
    )
    def test_gpt_endpoint_live(self):
        """Live test with actual OpenAI API (skips without key)"""
        response = client.post(
            "/gpt",
            json={
                "prompt": "Say 'Hello, world!' in one word",
                "max_tokens": 5,
                "temperature": 0.1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "usage" in data
        assert "model" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    @patch('api_server.gpt_client')
    def test_gpt_endpoint_mock_success(self, mock_client):
        """Test /gpt endpoint with mocked successful response"""
        # Configure mock
        mock_client.is_available.return_value = True
        mock_response = GPTResponse(
            response="Hello! How can I help you?",
            usage={"total_tokens": 10},
            model="text-davinci-003"
        )
        
        # Make the async method return a coroutine
        import asyncio
        async def mock_generate_response(request):
            return mock_response
        mock_client.generate_response = mock_generate_response
        
        response = client.post(
            "/gpt",
            json={"prompt": "Hello, world!", "max_tokens": 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello! How can I help you?"
        assert data["usage"] == {"total_tokens": 10}
        assert data["model"] == "text-davinci-003"
    
    @patch('api_server.gpt_client')
    def test_gpt_endpoint_value_error(self, mock_client):
        """Test /gpt endpoint with ValueError"""
        mock_client.is_available.return_value = True
        
        # Make the async method raise ValueError
        async def mock_generate_response(request):
            raise ValueError("Invalid request")
        mock_client.generate_response = mock_generate_response
        
        response = client.post(
            "/gpt",
            json={"prompt": "Hello, world!"}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid request"
    
    @patch('api_server.gpt_client')
    def test_gpt_endpoint_runtime_error(self, mock_client):
        """Test /gpt endpoint with RuntimeError"""
        mock_client.is_available.return_value = True
        
        # Make the async method raise RuntimeError
        async def mock_generate_response(request):
            raise RuntimeError("API Error")
        mock_client.generate_response = mock_generate_response
        
        response = client.post(
            "/gpt",
            json={"prompt": "Hello, world!"}
        )
        
        assert response.status_code == 500
        assert response.json()["detail"] == "API Error"


def test_health_check():
    """Test that health check endpoint still works"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint():
    """Test that root endpoint still works"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"