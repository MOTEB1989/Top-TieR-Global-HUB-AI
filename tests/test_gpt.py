import os
import pytest
from fastapi.testclient import TestClient

from api_server import app
from gpt_client import GPTClient, GPTRequest


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set"
)
def test_gpt_endpoint_with_api_key():
    """Test the /gpt endpoint with a real API key (live test)"""
    client = TestClient(app)
    response = client.post(
        "/gpt",
        json={
            "prompt": "Hello, how are you?",
            "model": "text-davinci-003",
            "max_tokens": 10,
            "temperature": 0.5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "text" in data
    assert "model" in data
    assert data["model"] == "text-davinci-003"
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0


def test_gpt_endpoint_without_api_key():
    """Test the /gpt endpoint without API key returns proper error"""
    # Save original API key if exists
    original_key = os.environ.get("OPENAI_API_KEY")
    
    # Temporarily remove API key
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        # Reimport to reinitialize without API key
        import importlib
        import api_server
        importlib.reload(api_server)
        
        client = TestClient(api_server.app)
        response = client.post(
            "/gpt",
            json={
                "prompt": "Hello, how are you?",
                "model": "text-davinci-003",
                "max_tokens": 10,
                "temperature": 0.5
            }
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "GPT service unavailable" in data["detail"]
    
    finally:
        # Restore original API key if it existed
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set"
)
def test_gpt_client_initialization():
    """Test GPT client can be initialized with API key"""
    client = GPTClient()
    assert client.is_available()
    assert client.api_key is not None


def test_gpt_client_initialization_without_key():
    """Test GPT client raises error without API key"""
    # Save original API key if exists
    original_key = os.environ.get("OPENAI_API_KEY")
    
    # Temporarily remove API key
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            GPTClient()
    finally:
        # Restore original API key if it existed
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_gpt_request_validation():
    """Test GPT request model validation"""
    # Test valid request
    valid_request = GPTRequest(prompt="Test prompt")
    assert valid_request.prompt == "Test prompt"
    assert valid_request.model == "text-davinci-003"  # default
    assert valid_request.max_tokens == 100  # default
    assert valid_request.temperature == 0.7  # default
    
    # Test custom parameters
    custom_request = GPTRequest(
        prompt="Custom prompt",
        model="gpt-3.5-turbo-instruct",
        max_tokens=50,
        temperature=0.8
    )
    assert custom_request.prompt == "Custom prompt"
    assert custom_request.model == "gpt-3.5-turbo-instruct"
    assert custom_request.max_tokens == 50
    assert custom_request.temperature == 0.8