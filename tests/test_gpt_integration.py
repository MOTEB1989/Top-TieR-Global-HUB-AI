"""
Tests for GPT client and API endpoint.
Tests skip gracefully when OpenAI API key is not configured to keep CI green.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api_server import app
from gpt_client import GPTClient, gpt_client


client = TestClient(app)


class TestGPTClient:
    """Tests for GPT client functionality."""
    
    def test_gpt_client_initialization_without_api_key(self):
        """Test GPT client initialization without API key."""
        # Clear any existing API key for this test
        with patch.dict(os.environ, {}, clear=True):
            test_client = GPTClient()
            assert not test_client.is_configured()
            assert test_client.api_key is None
    
    def test_gpt_client_initialization_with_api_key(self):
        """Test GPT client initialization with API key."""
        test_api_key = "test-api-key"
        test_client = GPTClient(api_key=test_api_key)
        assert test_client.is_configured()
        assert test_client.api_key == test_api_key
    
    def test_gpt_client_initialization_from_env(self):
        """Test GPT client initialization from environment variable."""
        test_api_key = "test-env-api-key"
        with patch.dict(os.environ, {"OPENAI_API_KEY": test_api_key}):
            test_client = GPTClient()
            assert test_client.is_configured()
            assert test_client.api_key == test_api_key
    
    @pytest.mark.asyncio
    async def test_generate_response_without_api_key(self):
        """Test response generation without API key."""
        test_client = GPTClient()  # No API key
        result = await test_client.generate_response("Test prompt")
        
        assert "error" in result
        assert result["error"] == "OpenAI API key not configured"
        assert "message" in result
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OpenAI API key not available - skipping to keep CI green"
    )
    @pytest.mark.asyncio
    async def test_generate_response_with_api_key_real(self):
        """Test response generation with real API key (only runs if key is available)."""
        result = await gpt_client.generate_response("Hello, world!")
        
        # Should either succeed or fail with a valid error structure
        assert isinstance(result, dict)
        if "error" not in result:
            assert "success" in result
            assert "response" in result
        else:
            # If there's an error, it should have proper error structure
            assert "message" in result
    
    @pytest.mark.asyncio
    async def test_generate_response_mocked_success(self):
        """Test response generation with mocked OpenAI success."""
        test_client = GPTClient(api_key="fake-key")
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].text = "Mocked response"
        mock_response.usage = {"total_tokens": 10}
        
        with patch("openai.Completion.create", return_value=mock_response):
            result = await test_client.generate_response("Test prompt")
            
            assert result["success"] is True
            assert result["response"] == "Mocked response"
            assert "usage" in result
    
    @pytest.mark.asyncio
    async def test_generate_response_mocked_auth_error(self):
        """Test response generation with mocked authentication error."""
        test_client = GPTClient(api_key="fake-key")
        
        with patch("openai.Completion.create") as mock_create:
            import openai
            mock_create.side_effect = openai.error.AuthenticationError("Invalid API key")
            
            result = await test_client.generate_response("Test prompt")
            
            assert result["error"] == "Authentication failed"
            assert result["message"] == "Invalid OpenAI API key"


class TestGPTEndpoint:
    """Tests for GPT API endpoint."""
    
    def test_gpt_endpoint_without_api_key(self):
        """Test GPT endpoint returns 503 when API key is not configured."""
        # Mock the global gpt_client to not be configured
        with patch.object(gpt_client, 'is_configured', return_value=False):
            response = client.post("/gpt", json={"prompt": "Hello"})
            assert response.status_code == 503
            assert "GPT service not available" in response.json()["detail"]
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OpenAI API key not available - skipping to keep CI green"
    )
    def test_gpt_endpoint_with_api_key_real(self):
        """Test GPT endpoint with real API key (only runs if key is available)."""
        response = client.post("/gpt", json={
            "prompt": "Say hello in a friendly way",
            "max_tokens": 50
        })
        
        # Should either succeed or return a proper error
        assert response.status_code in [200, 400, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "success" in data
    
    def test_gpt_endpoint_with_mocked_success(self):
        """Test GPT endpoint with mocked successful response."""
        mock_result = {
            "success": True,
            "response": "Hello! How can I help you today?"
        }
        
        with patch.object(gpt_client, 'is_configured', return_value=True), \
             patch.object(gpt_client, 'generate_response', return_value=mock_result):
            
            response = client.post("/gpt", json={"prompt": "Hello"})
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["response"] == "Hello! How can I help you today?"
    
    def test_gpt_endpoint_with_mocked_error(self):
        """Test GPT endpoint with mocked error response."""
        mock_result = {
            "error": "Rate limit exceeded",
            "message": "Please try again later"
        }
        
        with patch.object(gpt_client, 'is_configured', return_value=True), \
             patch.object(gpt_client, 'generate_response', return_value=mock_result):
            
            response = client.post("/gpt", json={"prompt": "Hello"})
            assert response.status_code == 400
            assert "Rate limit exceeded" in response.json()["detail"]
    
    def test_gpt_endpoint_invalid_request(self):
        """Test GPT endpoint with invalid request data."""
        # Mock the client as configured but test validation
        with patch.object(gpt_client, 'is_configured', return_value=True):
            # Missing prompt
            response = client.post("/gpt", json={})
            assert response.status_code == 422  # Validation error
            
            # Invalid max_tokens type
            response = client.post("/gpt", json={
                "prompt": "Hello",
                "max_tokens": "invalid"
            })
            assert response.status_code == 422  # Validation error


class TestHealthEndpoints:
    """Tests for existing health endpoints to ensure they still work."""
    
    def test_root_endpoint(self):
        """Test root endpoint still works."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to Top-TieR Global HUB AI API!"
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
    
    def test_api_endpoint(self):
        """Test legacy API endpoint still works."""
        response = client.get("/api")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to the API!"
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
    
    def test_health_endpoint(self):
        """Test health check endpoint still works."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"