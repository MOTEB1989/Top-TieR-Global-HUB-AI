#!/usr/bin/env python3
"""
Test module for health check functionality.
Validates that the health endpoints return proper responses.
"""

import pytest
import requests
import subprocess
import time
import sys
import os
from multiprocessing import Process

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def start_api_server():
    """Start the Core API server in a subprocess"""
    import uvicorn
    from api_server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")

def start_veritas_web():
    """Start the Veritas Web server in a subprocess"""
    import uvicorn
    from veritas_web.app import app
    uvicorn.run(app, host="127.0.0.1", port=8088, log_level="critical")

class TestHealthCheck:
    """Test health check functionality"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment by starting services"""
        cls.api_process = Process(target=start_api_server)
        cls.veritas_process = Process(target=start_veritas_web)
        
        cls.api_process.start()
        cls.veritas_process.start()
        
        # Wait for services to start
        time.sleep(3)
        
    @classmethod
    def teardown_class(cls):
        """Cleanup test environment"""
        if hasattr(cls, 'api_process'):
            cls.api_process.terminate()
            cls.api_process.join(timeout=5)
            
        if hasattr(cls, 'veritas_process'):
            cls.veritas_process.terminate()
            cls.veritas_process.join(timeout=5)
    
    def test_core_api_health_endpoint(self):
        """Test Core API health endpoint"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] == "ok"
            assert "version" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Core API service not available for testing")
    
    def test_veritas_web_health_endpoint(self):
        """Test Veritas Web health endpoint"""
        try:
            response = requests.get("http://localhost:8088/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "version" in data
            assert "uptime" in data
            assert "dependencies" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Veritas Web service not available for testing")
    
    def test_health_check_script(self):
        """Test the health check script execution"""
        try:
            # Run the health check script
            result = subprocess.run(
                ["./scripts/veritas_health_check.sh"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Check that the script completed successfully
            assert result.returncode == 0, f"Health check script failed: {result.stderr}"
            
            # Check that both services were verified
            output = result.stdout
            assert "CORE_API is healthy" in output
            assert "VERITAS_WEB is healthy" in output
            assert "All services are healthy" in output
            
        except subprocess.TimeoutExpired:
            pytest.fail("Health check script timed out")
        except FileNotFoundError:
            pytest.skip("Health check script not found")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])