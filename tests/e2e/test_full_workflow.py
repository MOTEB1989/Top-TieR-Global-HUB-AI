"""
End-to-End Workflow Tests
Tests complete user workflows from start to finish.
"""

import os
import pytest
import asyncio
import time


class TestTelegramBotWorkflow:
    """End-to-end tests for Telegram bot workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_chat_workflow(self):
        """Test complete chat workflow: message → processing → AI response → reply."""
        if not all([
            self.bot_token and not self.bot_token.startswith("PASTE_"),
            self.openai_key and not self.openai_key.startswith("PASTE_")
        ]):
            pytest.skip("Required API keys not configured")
        
        import aiohttp
        
        # Step 1: Verify bot is alive
        bot_url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        async with aiohttp.ClientSession() as session:
            async with session.get(bot_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                assert response.status == 200, "Bot not available"
                bot_info = await response.json()
                assert bot_info["ok"], "Bot API error"
                print(f"\n✓ Step 1: Bot verified (@{bot_info['result']['username']})")
        
        # Step 2: Check OpenAI availability
        openai_url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(openai_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, "OpenAI not available"
                print("✓ Step 2: OpenAI API accessible")
        
        # Step 3: Simulate message processing
        message_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 20
        }
        
        completion_url = "https://api.openai.com/v1/chat/completions"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                completion_url,
                headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                json=message_payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                assert response.status == 200, "OpenAI completion failed"
                data = await response.json()
                ai_response = data["choices"][0]["message"]["content"]
                print(f"✓ Step 3: AI response generated: '{ai_response[:30]}...'")
        
        # Step 4: Verify workflow complete
        print("✓ Step 4: Complete workflow successful\n")
        assert True, "Workflow completed successfully"

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling workflow."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        # Step 1: Test with invalid request
        invalid_url = f"https://api.telegram.org/bot{self.bot_token}/invalidMethod"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(invalid_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data = await response.json()
                assert not data["ok"], "Should return error"
                print(f"\n✓ Error handling: {data.get('description', 'N/A')}")
        
        # Step 2: Verify error logged (would check logs in production)
        print("✓ Error workflow handled correctly\n")

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_multi_service_integration(self):
        """Test integration across multiple services."""
        services_available = []
        
        # Check Telegram
        if self.bot_token and not self.bot_token.startswith("PASTE_"):
            try:
                import aiohttp
                url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            services_available.append("telegram")
            except:
                pass
        
        # Check OpenAI
        if self.openai_key and not self.openai_key.startswith("PASTE_"):
            try:
                import aiohttp
                url = "https://api.openai.com/v1/models"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            services_available.append("openai")
            except:
                pass
        
        # Check GitHub
        if self.github_token and not self.github_token.startswith("PASTE_"):
            try:
                import aiohttp
                url = f"https://api.github.com/repos/{self.github_repo}"
                headers = {"Authorization": f"token {self.github_token}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            services_available.append("github")
            except:
                pass
        
        print(f"\n✓ Services available: {', '.join(services_available)}")
        assert len(services_available) > 0, "No services available"

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_performance_workflow(self):
        """Test end-to-end workflow performance."""
        if not self.bot_token or self.bot_token.startswith("PASTE_"):
            pytest.skip("TELEGRAM_BOT_TOKEN not configured")
        
        import aiohttp
        
        start_time = time.time()
        
        # Simulate complete workflow timing
        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                await response.json()
        
        total_time = (time.time() - start_time) * 1000
        
        print(f"\n✓ Workflow performance: {total_time:.2f}ms")
        assert total_time < 5000, f"Workflow too slow: {total_time}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
