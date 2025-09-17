#!/usr/bin/env python3
"""
Simple health check validation script.
Tests the health check script functionality without requiring full service startup.
"""

import os
import subprocess
import sys
import tempfile

def test_health_check_script_exists():
    """Test that the health check script exists and is executable"""
    script_path = "scripts/veritas_health_check.sh"
    assert os.path.exists(script_path), f"Health check script not found: {script_path}"
    assert os.access(script_path, os.X_OK), f"Health check script is not executable: {script_path}"
    print("✅ Health check script exists and is executable")
    return True

def test_health_check_script_syntax():
    """Test that the health check script has valid syntax"""
    script_path = "scripts/veritas_health_check.sh"
    
    try:
        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", script_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Bash syntax error: {result.stderr}"
        print("✅ Health check script has valid bash syntax")
        
    except Exception as e:
        print(f"❌ Syntax check failed: {e}")
        return False
    
    return True

def test_workflow_file_exists():
    """Test that the workflow file exists and is valid YAML"""
    workflow_path = ".github/workflows/veritas-health.yml"
    assert os.path.exists(workflow_path), f"Workflow file not found: {workflow_path}"
    
    try:
        import yaml
        with open(workflow_path, 'r') as f:
            yaml.safe_load(f)
        print("✅ Workflow file exists and is valid YAML")
    except ImportError:
        print("⚠️  PyYAML not available, skipping YAML validation")
    except Exception as e:
        print(f"❌ Workflow YAML validation failed: {e}")
        return False
    
    return True

def test_api_server_module():
    """Test that the API server module can be imported"""
    try:
        sys.path.insert(0, '.')
        import api_server
        print("✅ API server module can be imported")
        return True
    except ImportError as e:
        print(f"❌ API server import failed: {e}")
        return False

def test_veritas_web_module():
    """Test that the Veritas web module can be imported"""
    try:
        sys.path.insert(0, '.')
        # Import the app module directly from veritas-web directory
        import importlib.util
        spec = importlib.util.spec_from_file_location("veritas_web_app", "veritas-web/app.py")
        veritas_web_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(veritas_web_app)
        print("✅ Veritas web module can be imported")
        return True
    except ImportError as e:
        print(f"❌ Veritas web import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Veritas web validation failed: {e}")
        return False

def test_health_check_configuration():
    """Test that health check configuration is correct"""
    script_path = "scripts/veritas_health_check.sh"
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check for correct port configurations
    assert "8000" in content, "Core API port 8000 not found in health check script"
    assert "8088" in content, "Veritas Web port 8088 not found in health check script"
    
    # Check for proper environment variable handling
    assert "CORE_URL" in content, "CORE_URL environment variable not handled"
    assert "OSINT_URL" in content, "OSINT_URL environment variable not handled"
    
    print("✅ Health check configuration looks correct")
    return True

def main():
    """Run all validation tests"""
    print("Running health check validation tests...")
    print("=" * 50)
    
    tests = [
        test_health_check_script_exists,
        test_health_check_script_syntax,
        test_workflow_file_exists,
        test_api_server_module,
        test_veritas_web_module,
        test_health_check_configuration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is not False:  # Handle None as success
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("❌ Some validation tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())