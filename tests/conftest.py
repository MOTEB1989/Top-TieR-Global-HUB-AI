"""
Shared test fixtures and configuration for integration tests
تهيئة الاختبارات المشتركة
"""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import MagicMock, AsyncMock

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Environment & Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration from environment variables"""
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "github_token": os.getenv("GITHUB_TOKEN"),
        "github_repo": os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI"),
        "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "neo4j_auth": os.getenv("NEO4J_AUTH", "neo4j/password"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "db_url": os.getenv("DB_URL", "postgresql://postgres:password@localhost:5432/testdb"),
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key-123",
        "TELEGRAM_BOT_TOKEN": "123456:ABC-DEF-test-token",
        "GITHUB_TOKEN": "ghp_test_token_123",
        "NEO4J_URI": "bolt://localhost:7687",
        "REDIS_URL": "redis://localhost:6379",
        "DB_URL": "postgresql://postgres:test@localhost:5432/testdb",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


# ============================================================================
# OpenAI API Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].text = "Test response from GPT"
    response.choices[0].message = MagicMock()
    response.choices[0].message.content = "Test response from GPT"
    response.usage = {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}
    response.model = "gpt-3.5-turbo"
    return response


@pytest.fixture
def openai_api_available(test_config) -> bool:
    """Check if OpenAI API is available for testing"""
    return bool(test_config["openai_api_key"] and 
                test_config["openai_api_key"] != "sk-proj-PASTE_YOUR_KEY_HERE")


# ============================================================================
# Telegram Bot Fixtures
# ============================================================================

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram Bot instance"""
    bot = MagicMock()
    bot.get_me = AsyncMock(return_value=MagicMock(
        id=123456789,
        is_bot=True,
        first_name="Test Bot",
        username="test_bot"
    ))
    bot.send_message = AsyncMock(return_value=MagicMock(
        message_id=1,
        text="Test message",
        chat=MagicMock(id=123456)
    ))
    return bot


@pytest.fixture
def telegram_api_available(test_config) -> bool:
    """Check if Telegram API is available for testing"""
    return bool(test_config["telegram_bot_token"] and 
                test_config["telegram_bot_token"] != "PASTE_YOUR_BOT_TOKEN_HERE")


# ============================================================================
# GitHub API Fixtures
# ============================================================================

@pytest.fixture
def mock_github_client():
    """Mock GitHub client"""
    client = MagicMock()
    
    # Mock repository
    repo = MagicMock()
    repo.name = "Top-TieR-Global-HUB-AI"
    repo.full_name = "MOTEB1989/Top-TieR-Global-HUB-AI"
    repo.description = "Test repo"
    repo.stargazers_count = 10
    
    # Mock issues
    issue = MagicMock()
    issue.number = 1
    issue.title = "Test Issue"
    issue.state = "open"
    repo.get_issues = MagicMock(return_value=[issue])
    
    client.get_repo = MagicMock(return_value=repo)
    return client


@pytest.fixture
def github_api_available(test_config) -> bool:
    """Check if GitHub API is available for testing"""
    return bool(test_config["github_token"] and 
                test_config["github_token"] != "PASTE_YOUR_GITHUB_TOKEN_HERE")


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver"""
    driver = MagicMock()
    session = MagicMock()
    
    # Mock query result
    result = MagicMock()
    result.single = MagicMock(return_value={"count": 1})
    session.run = MagicMock(return_value=result)
    
    driver.session = MagicMock(return_value=session)
    driver.verify_connectivity = MagicMock()
    return driver


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    client = MagicMock()
    client.ping = MagicMock(return_value=True)
    client.set = MagicMock(return_value=True)
    client.get = MagicMock(return_value=b"test_value")
    client.delete = MagicMock(return_value=1)
    return client


@pytest.fixture
def mock_postgres_connection():
    """Mock PostgreSQL connection"""
    conn = MagicMock()
    cursor = MagicMock()
    
    # Mock cursor methods
    cursor.execute = MagicMock()
    cursor.fetchone = MagicMock(return_value=(1,))
    cursor.fetchall = MagicMock(return_value=[(1, "test")])
    cursor.close = MagicMock()
    
    conn.cursor = MagicMock(return_value=cursor)
    conn.commit = MagicMock()
    conn.rollback = MagicMock()
    conn.close = MagicMock()
    
    return conn


# ============================================================================
# FastAPI Test Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """FastAPI test client"""
    try:
        from fastapi.testclient import TestClient
        from api_server import app
        return TestClient(app)
    except ImportError:
        pytest.skip("FastAPI not available")


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def sample_test_data() -> Dict[str, Any]:
    """Sample test data for various tests"""
    return {
        "gpt_prompt": "Hello, this is a test prompt",
        "telegram_message": "Test message from integration tests",
        "github_issue_title": "Test Issue from Integration Tests",
        "test_key": "integration_test_key",
        "test_value": "integration_test_value"
    }


@pytest.fixture
def timeout_seconds() -> int:
    """Default timeout for API calls in tests"""
    return 30


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
async def async_mock_session():
    """Mock async HTTP session"""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"status": "ok"})
    response.text = AsyncMock(return_value="OK")
    session.get = AsyncMock(return_value=response)
    session.post = AsyncMock(return_value=response)
    session.close = AsyncMock()
    return session


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API credentials"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "load: mark test as load/stress test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )


# ============================================================================
# Skip Conditions
# ============================================================================

skip_if_no_openai = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or 
    os.getenv("OPENAI_API_KEY") == "sk-proj-PASTE_YOUR_KEY_HERE",
    reason="OpenAI API key not configured"
)

skip_if_no_telegram = pytest.mark.skipif(
    not os.getenv("TELEGRAM_BOT_TOKEN") or 
    os.getenv("TELEGRAM_BOT_TOKEN") == "PASTE_YOUR_BOT_TOKEN_HERE",
    reason="Telegram Bot token not configured"
)

skip_if_no_github = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN") or 
    os.getenv("GITHUB_TOKEN") == "PASTE_YOUR_GITHUB_TOKEN_HERE",
    reason="GitHub token not configured"
)
