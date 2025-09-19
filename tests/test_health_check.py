import pytest
import subprocess
import time
import sys
import os
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add the veritas-web directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "veritas-web"))

from api_server import app


class TestHealthCheck:
    """Test cases for health check functionality"""
    
    def test_api_health_endpoint(self):
        """Test the main API health endpoint"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "2.0.0"
    
    def test_web_health_endpoint(self):
        """Test the veritas web health endpoint"""
        # Import here to avoid path issues
        try:
            from app import app as web_app
            client = TestClient(web_app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "1.0.0"
            assert "timestamp" in data
            assert "uptime" in data
            assert "dependencies" in data
        except ImportError:
            pytest.skip("Veritas web app not available for testing")
    
    def test_health_check_script_exists(self):
        """Test that the health check script exists and is executable"""
        import os
        script_path = "/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/scripts/veritas_health_check.sh"
        
        assert os.path.exists(script_path), "Health check script should exist"
        assert os.access(script_path, os.X_OK), "Health check script should be executable"
    
    def test_health_check_script_no_services(self):
        """Test health check script when services are not running"""
        import os
        script_path = "/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/scripts/veritas_health_check.sh"
        
        # Run the script when no services are running
        result = subprocess.run(
            [script_path], 
            capture_output=True, 
            text=True,
            cwd="/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI"
        )
        
        # Should fail when services are not running
        assert result.returncode != 0, "Health check should fail when services are not running"
        assert "❌" in result.stdout, "Should show error indicators"
        assert "health check failed" in result.stdout.lower(), "Should indicate failure"
    
    def test_api_health_response_format(self):
        """Test that API health response has correct format"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "version"]
        for field in required_fields:
            assert field in data, f"Health response should include {field}"
        
        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
    
    def test_web_health_response_format(self):
        """Test that web health response has correct format"""
        try:
            from app import app as web_app
            client = TestClient(web_app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            required_fields = ["status", "version", "timestamp", "uptime", "dependencies"]
            for field in required_fields:
                assert field in data, f"Health response should include {field}"
            
            # Check data types
            assert isinstance(data["status"], str)
            assert isinstance(data["version"], str)
            assert isinstance(data["uptime"], (int, float))
            assert isinstance(data["dependencies"], dict)
        except ImportError:
            pytest.skip("Veritas web app not available for testing")
    
    def test_web_health_dependencies_check(self):
        """Test that web health endpoint checks dependencies"""
        try:
            from app import app as web_app
            client = TestClient(web_app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            dependencies = data["dependencies"]
            
            # Should check main_api dependency
            assert "main_api" in dependencies
            # Since API isn't running in this test, should be "unhealthy"
            assert dependencies["main_api"] in ["healthy", "unhealthy", "unavailable"]
            
            # Should report redis status
            assert "redis" in dependencies
            assert dependencies["redis"] in ["healthy", "unhealthy", "disabled"]
            
            # Should have neo4j status
            assert "neo4j" in dependencies
        except ImportError:
            pytest.skip("Veritas web app not available for testing")
    
    @pytest.mark.skipif(
        True,  # Skip by default since it requires actual service startup
        reason="Integration test - requires service startup"
    )
    def test_health_check_integration(self):
        """Integration test for full health check workflow"""
        # This test would start actual services and run the health check
        # Skipped by default as it requires more setup
        pass


class TestHealthCheckConfiguration:
    """Test cases for health check configuration"""
    
    def test_api_port_configuration(self):
        """Test that API uses correct port configuration"""
        from api_server import app
        # The API should be configurable via environment
        assert hasattr(app, 'title')
        assert app.title == "Top-TieR Global HUB AI API"
    
    def test_web_port_configuration(self):
        """Test that web service uses correct port configuration"""
        try:
            from app import settings
            
            # Should default to port 8080 (our fixed port)
            assert settings.PORT == 8080, "Veritas web should use port 8080 by default"
        except ImportError:
            pytest.skip("Veritas web app not available for testing")
    
    def test_health_check_urls(self):
        """Test that health check uses correct URLs"""
        script_path = "/home/runner/work/Top-TieR-Global-HUB-AI/Top-TieR-Global-HUB-AI/scripts/veritas_health_check.sh"
        
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Should check localhost:8000 for core API
        assert "http://localhost:8000/health" in script_content
        
        # Should check localhost:8080 for veritas web
        assert "http://localhost:8080/health" in script_content