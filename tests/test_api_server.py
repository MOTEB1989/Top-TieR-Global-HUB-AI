"""
Tests for API server endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from api_server import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    assert "features" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"


def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "real_time" in data
    assert "cache" in data
    assert "model_routing" in data


def test_metrics_prometheus_format(client):
    """Test Prometheus format metrics"""
    response = client.get("/metrics?format=prometheus")
    assert response.status_code == 200
    # Should return prometheus format as plain text
    assert "# Error" in response.text or "# HELP" in response.text


def test_dashboard_endpoint(client):
    """Test dashboard endpoint"""
    response = client.get("/metrics/dashboard")
    assert response.status_code == 200
    data = response.json()
    # Should return dashboard data structure


def test_stats_endpoint(client):
    """Test client stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    # Should return rate limiting stats


def test_job_submission(client):
    """Test job submission endpoint"""
    job_data = {
        "job": "heavy-task",
        "parameters": {"test": "value"}
    }
    response = client.post("/job", json=job_data)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"


def test_job_status(client):
    """Test job status retrieval"""
    response = client.get("/job/test-123")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "status" in data


@patch('api_server.gpt_client.is_available', return_value=False)
def test_query_without_api_key(mock_available, client):
    """Test query endpoint without API key"""
    query_data = {
        "query": "test query",
        "scope": ["general"]
    }
    response = client.post("/query", json=query_data)
    assert response.status_code == 503
    assert "GPT service unavailable" in response.json()["detail"]


@patch('api_server.gpt_client.is_available', return_value=True)
@patch('api_server.gpt_client.generate_response')
def test_query_with_caching(mock_generate, mock_available, client):
    """Test query endpoint with caching"""
    # Mock GPT response
    mock_response = Mock()
    mock_response.response = "Test response"
    mock_response.usage = {"total_tokens": 50}
    mock_response.model = "gpt-3.5-turbo"
    mock_generate.return_value = mock_response
    
    query_data = {
        "query": "test query",
        "scope": ["general"],
        "trace": True
    }
    
    response = client.post("/query", json=query_data)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "model_info" in data
    assert "cache_info" in data
    assert "metrics" in data
    assert "trace" in data  # Since trace=True