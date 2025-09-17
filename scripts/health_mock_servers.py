#!/usr/bin/env python3
"""
Health Check Mock Servers
Simple HTTP servers that provide health endpoints for CI testing.
"""

import json
import time
import asyncio
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "mock-1.0.0",
                "service": getattr(self.server, 'service_name', 'unknown')
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_server(port, service_name="health-mock"):
    """Start a health mock server on specified port"""
    import socket
    
    # Check if port is already in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', port)) == 0:
            print(f"Port {port} already in use, checking if it's a health endpoint...")
            try:
                import urllib.request
                response = urllib.request.urlopen(f'http://localhost:{port}/health', timeout=2)
                print(f"✅ {service_name} already running on port {port}")
                return None  # Server already running
            except:
                print(f"❌ Port {port} in use but not responding to health checks")
                raise RuntimeError(f"Port {port} is occupied")
    
    server = HTTPServer(('localhost', port), HealthHandler)
    server.service_name = service_name
    
    def run_server():
        print(f"Starting {service_name} health server on port {port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
    
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
    
    # Give server a moment to start
    time.sleep(0.5)
    
    # Verify server is actually responding
    import urllib.request
    try:
        urllib.request.urlopen(f'http://localhost:{port}/health', timeout=2)
        print(f"✅ {service_name} server responding on port {port}")
    except Exception as e:
        print(f"❌ {service_name} server failed to start: {e}")
        raise
    
    return server

def main():
    """Start both health servers"""
    print("Starting health check mock servers...")
    
    servers = []
    
    # Start CORE_API mock on port 8000
    core_server = start_server(8000, "CORE_API")
    if core_server:
        servers.append(core_server)
    
    # Start VERITAS_WEB mock on port 8080
    web_server = start_server(8080, "VERITAS_WEB")
    if web_server:
        servers.append(web_server)
    
    if servers:
        print(f"Health servers started ({len(servers)} new servers). Press Ctrl+C to stop.")
    else:
        print("All required health servers are already running.")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\nShutting down {len(servers)} health servers...")
        for server in servers:
            server.shutdown()

if __name__ == "__main__":
    main()