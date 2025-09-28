#!/usr/bin/env python3
"""
Test to ensure port configuration consistency across Docker files and configuration.
This test validates that the health check failures are resolved by ensuring all port
configurations are consistent.
"""

import re
import os
from pathlib import Path
import pytest


def read_file_content(file_path: str) -> str:
    """Read file content safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extract_ports_from_dockerfile(dockerfile_path: str) -> dict:
    """Extract port configurations from a Dockerfile."""
    content = read_file_content(dockerfile_path)
    ports = {}
    
    # Extract EXPOSE port
    expose_match = re.search(r'EXPOSE\s+(\d+)', content)
    if expose_match:
        ports['expose'] = int(expose_match.group(1))
    
    # Extract port from CMD (handle JSON array format)
    cmd_match = re.search(r'--port",\s*"(\d+)"', content)
    if cmd_match:
        ports['cmd'] = int(cmd_match.group(1))
    
    # Extract port from health check
    health_match = re.search(r'localhost:(\d+)/health', content)
    if health_match:
        ports['health'] = int(health_match.group(1))
    
    return ports


def extract_ports_from_docker_compose() -> dict:
    """Extract port configurations from docker-compose.yml."""
    content = read_file_content('docker-compose.yml')
    ports = {}
    
    # Find veritas-web service port mapping
    veritas_web_match = re.search(r'veritas-web:.*?ports:.*?"(\d+):(\d+)"', content, re.DOTALL)
    if veritas_web_match:
        ports['veritas_web_host'] = int(veritas_web_match.group(1))
        ports['veritas_web_container'] = int(veritas_web_match.group(2))
    
    # Find health check port in veritas-web section specifically
    veritas_health_match = re.search(r'veritas-web:.*?healthcheck:.*?test:.*?localhost:(\d+)/health', content, re.DOTALL)
    if veritas_health_match:
        ports['veritas_health_check'] = int(veritas_health_match.group(1))
    
    return ports


def extract_ports_from_health_script() -> dict:
    """Extract port configurations from health check script."""
    content = read_file_content('scripts/veritas_health_check.sh')
    ports = {}
    
    # Extract CORE_API port
    core_match = re.search(r'check_service\s+"CORE_API"\s+"http://localhost:(\d+)', content)
    if core_match:
        ports['core_api'] = int(core_match.group(1))
    
    # Extract VERITAS_WEB port
    veritas_match = re.search(r'check_service\s+"VERITAS_WEB"\s+"http://localhost:(\d+)', content)
    if veritas_match:
        ports['veritas_web'] = int(veritas_match.group(1))
    
    return ports


class TestPortConsistency:
    """Test class for port configuration consistency."""
    
    def test_veritas_web_dockerfile_ports_consistent(self):
        """Test that veritas-web Dockerfile has consistent port configuration."""
        ports = extract_ports_from_dockerfile('veritas-web/Dockerfile')
        
        # All ports should be the same
        expected_port = 8080
        assert ports.get('expose') == expected_port, f"EXPOSE should be {expected_port}, got {ports.get('expose')}"
        assert ports.get('cmd') == expected_port, f"CMD port should be {expected_port}, got {ports.get('cmd')}"
        assert ports.get('health') == expected_port, f"Health check port should be {expected_port}, got {ports.get('health')}"
    
    def test_veritas_mini_web_dockerfile_ports_consistent(self):
        """Test that veritas-mini-web Dockerfile has consistent port configuration."""
        ports = extract_ports_from_dockerfile('veritas-mini-web/Dockerfile')
        
        # All ports should be the same
        expected_port = 8080
        assert ports.get('expose') == expected_port, f"EXPOSE should be {expected_port}, got {ports.get('expose')}"
        assert ports.get('cmd') == expected_port, f"CMD port should be {expected_port}, got {ports.get('cmd')}"
        assert ports.get('health') == expected_port, f"Health check port should be {expected_port}, got {ports.get('health')}"
    
    def test_docker_compose_veritas_web_ports_consistent(self):
        """Test that docker-compose.yml has consistent port mapping for veritas-web."""
        ports = extract_ports_from_docker_compose()
        
        expected_port = 8080
        assert ports.get('veritas_web_host') == expected_port, f"Host port should be {expected_port}"
        assert ports.get('veritas_web_container') == expected_port, f"Container port should be {expected_port}"
        assert ports.get('veritas_health_check') == expected_port, f"Health check port should be {expected_port}"
    
    def test_health_check_script_ports_match_services(self):
        """Test that health check script uses correct ports for services."""
        ports = extract_ports_from_health_script()
        
        # Core API should be on 8000
        assert ports.get('core_api') == 8000, f"Core API port should be 8000, got {ports.get('core_api')}"
        
        # Veritas Web should be on 8080
        assert ports.get('veritas_web') == 8080, f"Veritas Web port should be 8080, got {ports.get('veritas_web')}"
    
    def test_all_veritas_web_configurations_match(self):
        """Integration test: all veritas-web port configurations should match."""
        dockerfile_ports = extract_ports_from_dockerfile('veritas-web/Dockerfile')
        compose_ports = extract_ports_from_docker_compose()
        script_ports = extract_ports_from_health_script()
        
        expected_port = 8080
        
        # All veritas-web related ports should be 8080
        assert dockerfile_ports.get('expose') == expected_port
        assert dockerfile_ports.get('cmd') == expected_port
        assert dockerfile_ports.get('health') == expected_port
        assert compose_ports.get('veritas_web_host') == expected_port
        assert compose_ports.get('veritas_web_container') == expected_port
        assert compose_ports.get('veritas_health_check') == expected_port
        assert script_ports.get('veritas_web') == expected_port


if __name__ == "__main__":
    # Change to repository root if needed
    os.chdir(Path(__file__).parent.parent)
    pytest.main([__file__, "-v"])