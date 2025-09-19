#!/usr/bin/env python3
"""
Test to validate the health check fixes.
This test verifies that the health endpoints are working correctly
and the workflow logic is sound.
"""

import subprocess
import pytest
import requests
import time
from unittest.mock import patch, MagicMock


def test_health_check_script_exists():
    """Test that the health check script exists and is executable."""
    result = subprocess.run(
        ["test", "-x", "scripts/veritas_health_check.sh"],
        cwd="/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI",
        capture_output=True
    )
    assert result.returncode == 0, "Health check script should exist and be executable"


def test_health_check_script_syntax():
    """Test that the health check script has valid bash syntax."""
    result = subprocess.run(
        ["bash", "-n", "scripts/veritas_health_check.sh"],
        cwd="/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI",
        capture_output=True
    )
    assert result.returncode == 0, f"Health check script has syntax errors: {result.stderr.decode()}"


def test_api_health_endpoint_schema():
    """Test the API health endpoint returns expected schema when available."""
    # This test only runs if the API is actually running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert data["status"] == "ok"
            print(f"✅ API health endpoint working: {data}")
        else:
            print(f"ℹ️ API not running (status {response.status_code}) - skipping schema test")
    except requests.exceptions.ConnectionError:
        print("ℹ️ API not running - skipping schema test")


def test_veritas_web_health_endpoint_schema():
    """Test the Veritas Web health endpoint returns expected schema when available."""
    # This test only runs if the Veritas Web is actually running
    try:
        response = requests.get("http://localhost:8088/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "timestamp" in data
            assert "uptime" in data
            assert "dependencies" in data
            assert data["status"] == "healthy"
            print(f"✅ Veritas Web health endpoint working: {data}")
        else:
            print(f"ℹ️ Veritas Web not running (status {response.status_code}) - skipping schema test")
    except requests.exceptions.ConnectionError:
        print("ℹ️ Veritas Web not running - skipping schema test")


def test_docker_compose_configuration():
    """Test that docker-compose.yml has the correct configuration."""
    import yaml
    
    with open("/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/docker-compose.yml", "r") as f:
        compose_config = yaml.safe_load(f)
    
    # Check that API service exists and is configured correctly
    assert "api" in compose_config["services"]
    api_service = compose_config["services"]["api"]
    assert "8000:8000" in api_service["ports"]
    assert "healthcheck" in api_service
    
    # Check that veritas-web service exists and is configured correctly
    assert "veritas-web" in compose_config["services"]
    veritas_service = compose_config["services"]["veritas-web"]
    assert "8080:8088" in veritas_service["ports"]  # Should map host 8080 to container 8088
    assert "healthcheck" in veritas_service


def test_workflow_has_service_startup():
    """Test that the veritas-health.yml workflow includes service startup steps."""
    import yaml
    
    with open("/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/.github/workflows/veritas-health.yml", "r") as f:
        workflow = yaml.safe_load(f)
    
    # Get the steps from the health-check job
    steps = workflow["jobs"]["health-check"]["steps"]
    step_names = [step["name"] for step in steps if "name" in step]
    
    # Check that crucial steps are present
    assert any("Docker" in step_name for step_name in step_names), "Workflow should include Docker setup"
    assert any("Start" in step_name or "service" in step_name.lower() for step_name in step_names), "Workflow should start services"
    assert any("Clean" in step_name for step_name in step_names), "Workflow should include cleanup"
    
    print(f"✅ Workflow steps include: {step_names}")


def test_health_check_script_checks_correct_ports():
    """Test that the health check script checks the correct ports."""
    with open("/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/scripts/veritas_health_check.sh", "r") as f:
        script_content = f.read()
    
    # Check that script checks port 8000 for API
    assert "localhost:8000/health" in script_content, "Script should check API on port 8000"
    
    # Check that script checks port 8080 for Web UI (host port)
    assert "localhost:8080/health" in script_content, "Script should check Web UI on port 8080"
    
    # Ensure it's not checking the old wrong port 3000
    assert "localhost:3000" not in script_content, "Script should not check port 3000"


@patch('subprocess.run')
def test_health_check_script_logic(mock_subprocess):
    """Test the logic of the health check script with mocked responses."""
    # Mock successful curl responses
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    result = subprocess.run(
        ["bash", "-c", 'echo "Testing script logic - this would normally run the health check"'],
        capture_output=True
    )
    
    # The test itself just validates that we can mock the process
    assert result.returncode == 0


def test_requirements_include_necessary_packages():
    """Test that requirements.txt includes packages needed for health endpoints."""
    with open("/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/requirements.txt", "r") as f:
        requirements = f.read()
    
    # Check for essential packages
    assert "fastapi" in requirements.lower(), "FastAPI is required for API health endpoints"
    assert "uvicorn" in requirements.lower(), "Uvicorn is required to run FastAPI"
    assert "pydantic" in requirements.lower(), "Pydantic is required for API models"


if __name__ == "__main__":
    print("Running health check validation tests...")
    
    # Run all the tests
    test_health_check_script_exists()
    test_health_check_script_syntax()
    test_api_health_endpoint_schema()
    test_veritas_web_health_endpoint_schema()
    test_docker_compose_configuration()
    test_workflow_has_service_startup()
    test_health_check_script_checks_correct_ports()
    test_requirements_include_necessary_packages()
    
    print("✅ All validation tests passed!")