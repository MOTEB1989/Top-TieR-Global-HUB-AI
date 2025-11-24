"""
OpenAI API Integration Tests
Tests real connectivity and functionality with OpenAI API.
"""

import os
import pytest
import asyncio
from typing import Optional


class TestOpenAIIntegration:
    """Integration tests for OpenAI API."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.skip_if_no_key = pytest.mark.skipif(
            not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"),
            reason="OPENAI_API_KEY not configured"
        )

    @pytest.mark.integration
    def test_api_key_configured(self):
        """Test that OpenAI API key is configured."""
        assert self.api_key is not None, "OPENAI_API_KEY environment variable not set"
        assert not self.api_key.startswith("PASTE_"), "OPENAI_API_KEY is placeholder value"
        assert not self.api_key.startswith("${{"), "OPENAI_API_KEY is template value"
        assert len(self.api_key) > 20, "OPENAI_API_KEY seems too short"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test listing available OpenAI models."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                assert response.status == 200, f"Failed to list models: {response.status}"
                
                data = await response.json()
                assert "data" in data, "Response missing 'data' field"
                assert len(data["data"]) > 0, "No models returned"
                
                # Check for common models
                model_ids = [model["id"] for model in data["data"]]
                print(f"\nAvailable models count: {len(model_ids)}")
                print(f"Sample models: {model_ids[:5]}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_simple_completion(self):
        """Test simple text completion with OpenAI."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Say 'Hello' in one word."}
            ],
            "max_tokens": 10,
            "temperature": 0.1,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                assert response.status == 200, f"Completion failed: {response.status}"
                
                data = await response.json()
                assert "choices" in data, "Response missing 'choices' field"
                assert len(data["choices"]) > 0, "No choices returned"
                
                message = data["choices"][0]["message"]
                assert "content" in message, "Message missing 'content' field"
                assert len(message["content"]) > 0, "Empty response content"
                
                print(f"\nResponse: {message['content']}")
                print(f"Model used: {data['model']}")
                print(f"Tokens used: {data['usage']['total_tokens']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_streaming_completion(self):
        """Test streaming completion with OpenAI."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Count from 1 to 3."}
            ],
            "max_tokens": 20,
            "stream": True,
        }
        
        chunks_received = 0
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                assert response.status == 200, f"Streaming failed: {response.status}"
                
                async for line in response.content:
                    if line:
                        chunks_received += 1
                
                assert chunks_received > 0, "No streaming chunks received"
                print(f"\nReceived {chunks_received} streaming chunks")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_invalid_model(self):
        """Test error handling with invalid model."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "invalid-model-name",
            "messages": [
                {"role": "user", "content": "Test"}
            ],
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                assert response.status in [400, 404], f"Expected error status, got {response.status}"
                
                data = await response.json()
                assert "error" in data, "Error response should contain 'error' field"
                print(f"\nError message: {data['error'].get('message', 'N/A')}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test API rate limiting behavior."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        import time
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
        }
        
        # Make multiple requests quickly
        request_count = 3
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(request_count):
                task = session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            
            success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
            
            print(f"\nRequests: {request_count}, Success: {success_count}, Duration: {duration:.2f}s")
            
            # Clean up
            for response in responses:
                if not isinstance(response, Exception):
                    response.close()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test OpenAI API response time."""
        if not self.api_key or self.api_key.startswith("PASTE_") or self.api_key.startswith("${{"):
            pytest.skip("OPENAI_API_KEY not configured")
        
        import aiohttp
        import time
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10,
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                await response.json()
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                print(f"\nResponse time: {response_time:.2f}ms")
                
                # Assert reasonable response time (under 10 seconds)
                assert response_time < 10000, f"Response time too slow: {response_time}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
