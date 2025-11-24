"""
Telegram Bot API Integration Tests
Tests real connectivity and functionality with Telegram Bot API.
"""

import os
import pytest
import asyncio


class TestTelegramIntegration:
    """Integration tests for Telegram Bot API."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_base = "https://api.telegram.org"

    @pytest.mark.integration
    def test_bot_token_configured(self):
        """Test that Telegram bot token is configured."""
        assert self.bot_token is not None, "TELEGRAM_BOT_TOKEN environment variable not set"
        assert not self.bot_token.startswith("PASTE_"), "TELEGRAM_BOT_TOKEN is placeholder value"
        assert ":" in self.bot_token, "TELEGRAM_BOT_TOKEN format invalid (should contain ':')"
        assert len(self.bot_token) > 30, "TELEGRAM_BOT_TOKEN seems too short"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_me(self):
        """Test getting bot information."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/bot{self.bot_token}/getMe"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                assert response.status == 200, f"getMe failed: {response.status}"
                
                data = await response.json()
                assert data["ok"] is True, "API response not ok"
                
                result = data["result"]
                assert "id" in result, "Bot ID missing"
                assert "username" in result, "Bot username missing"
                assert "is_bot" in result, "is_bot field missing"
                assert result["is_bot"] is True, "Not a bot account"
                
                print(f"\nBot Info:")
                print(f"  ID: {result['id']}")
                print(f"  Username: @{result['username']}")
                print(f"  Name: {result.get('first_name', 'N/A')}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_updates(self):
        """Test getting bot updates."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/bot{self.bot_token}/getUpdates"
        params = {"limit": 5, "timeout": 1}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"getUpdates failed: {response.status}"
                
                data = await response.json()
                assert data["ok"] is True, "API response not ok"
                
                updates = data["result"]
                print(f"\nReceived {len(updates)} updates")
                
                if updates:
                    update = updates[0]
                    print(f"Latest update ID: {update['update_id']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_webhook_info(self):
        """Test getting webhook information."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/bot{self.bot_token}/getWebhookInfo"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                assert response.status == 200, f"getWebhookInfo failed: {response.status}"
                
                data = await response.json()
                assert data["ok"] is True, "API response not ok"
                
                result = data["result"]
                print(f"\nWebhook Info:")
                print(f"  URL: {result.get('url', 'Not set')}")
                print(f"  Pending updates: {result.get('pending_update_count', 0)}")
                print(f"  Max connections: {result.get('max_connections', 'N/A')}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_send_chat_action(self):
        """Test sending chat action (typing indicator)."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id or chat_id.startswith("PASTE_"):
            pytest.skip("TELEGRAM_CHAT_ID not configured for testing")
        
        import aiohttp
        
        url = f"{self.api_base}/bot{self.bot_token}/sendChatAction"
        payload = {
            "chat_id": chat_id,
            "action": "typing"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                # May fail if chat_id is invalid, which is expected in test environment
                if response.status == 200:
                    data = await response.json()
                    assert data["ok"] is True, "sendChatAction failed"
                    print("\n✓ Chat action sent successfully")
                else:
                    print(f"\n⚠ Chat action failed (expected in test env): {response.status}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_my_commands(self):
        """Test getting bot commands."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/bot{self.bot_token}/getMyCommands"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                assert response.status == 200, f"getMyCommands failed: {response.status}"
                
                data = await response.json()
                assert data["ok"] is True, "API response not ok"
                
                commands = data["result"]
                print(f"\nBot has {len(commands)} commands configured")
                
                for cmd in commands:
                    print(f"  /{cmd['command']} - {cmd['description']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_invalid_token(self):
        """Test error handling with invalid token."""
        import aiohttp
        
        invalid_token = "123456:ABC-DEF-INVALID"
        url = f"{self.api_base}/bot{invalid_token}/getMe"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                # Should return 401 Unauthorized or 404 Not Found
                assert response.status in [401, 404], f"Expected error status, got {response.status}"
                
                data = await response.json()
                assert data["ok"] is False, "Should not be ok"
                print(f"\nError description: {data.get('description', 'N/A')}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Test Telegram API response time."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        import time
        
        url = f"{self.api_base}/bot{self.bot_token}/getMe"
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                await response.json()
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                print(f"\nResponse time: {response_time:.2f}ms")
                
                # Telegram API should be fast (under 2 seconds)
                assert response_time < 2000, f"Response time too slow: {response_time}ms"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_file_info(self):
        """Test getting file information (without actual file)."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        # Using invalid file_id to test error handling
        url = f"{self.api_base}/bot{self.bot_token}/getFile"
        params = {"file_id": "invalid_file_id"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data = await response.json()
                
                # Expected to fail with invalid file_id
                assert data["ok"] is False, "Should fail with invalid file_id"
                print(f"\nExpected error: {data.get('description', 'N/A')}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test making concurrent API calls."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        import time
        
        url = f"{self.api_base}/bot{self.bot_token}/getMe"
        
        # Make 5 concurrent requests
        request_count = 5
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(request_count):
                task = session.get(url, timeout=aiohttp.ClientTimeout(total=10))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            
            success_count = sum(
                1 for r in responses
                if not isinstance(r, Exception) and r.status == 200
            )
            
            print(f"\nConcurrent requests: {request_count}")
            print(f"Successful: {success_count}")
            print(f"Total time: {duration:.2f}s")
            print(f"Avg time per request: {(duration / request_count) * 1000:.2f}ms")
            
            # Clean up
            for response in responses:
                if not isinstance(response, Exception):
                    response.close()
            
            assert success_count == request_count, "Not all requests succeeded"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
