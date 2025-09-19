#!/usr/bin/env python3
"""
Test the health mock servers functionality
"""

import time
import json
import urllib.request
import subprocess
import threading
import signal
import os
import sys
from pathlib import Path

def test_health_mock_servers():
    """Test that health mock servers work correctly"""
    
    # Path to the script
    script_path = Path(__file__).parent.parent / "scripts" / "health_mock_servers.py"
    
    print("Testing health mock servers...")
    
    # Start the servers in a subprocess
    proc = subprocess.Popen([
        sys.executable, str(script_path)
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    try:
        # Give servers time to start
        time.sleep(3)
        
        # Test CORE_API endpoint
        print("Testing CORE_API endpoint...")
        response = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
        assert response.status == 200, f"Expected 200, got {response.status}"
        
        data = json.loads(response.read().decode())
        assert data['status'] == 'ok', f"Expected status 'ok', got {data['status']}"
        assert data['service'] == 'CORE_API', f"Expected service 'CORE_API', got {data['service']}"
        assert 'timestamp' in data, "Missing timestamp field"
        assert 'version' in data, "Missing version field"
        print("✅ CORE_API endpoint test passed")
        
        # Test VERITAS_WEB endpoint
        print("Testing VERITAS_WEB endpoint...")
        response = urllib.request.urlopen('http://localhost:8080/health', timeout=5)
        assert response.status == 200, f"Expected 200, got {response.status}"
        
        data = json.loads(response.read().decode())
        assert data['status'] == 'ok', f"Expected status 'ok', got {data['status']}"
        assert data['service'] == 'VERITAS_WEB', f"Expected service 'VERITAS_WEB', got {data['service']}"
        assert 'timestamp' in data, "Missing timestamp field"
        assert 'version' in data, "Missing version field"
        print("✅ VERITAS_WEB endpoint test passed")
        
        # Test 404 for invalid endpoints
        print("Testing 404 for invalid endpoint...")
        try:
            urllib.request.urlopen('http://localhost:8000/invalid', timeout=5)
            assert False, "Expected 404 for invalid endpoint"
        except urllib.error.HTTPError as e:
            assert e.code == 404, f"Expected 404, got {e.code}"
        print("✅ 404 test passed")
        
        print("✅ All health mock server tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up the subprocess
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

if __name__ == "__main__":
    success = test_health_mock_servers()
    sys.exit(0 if success else 1)