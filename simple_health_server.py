#!/usr/bin/env python3
"""
Simple health check server for testing health endpoints
"""
import asyncio
from datetime import datetime
from fastapi import FastAPI
import uvicorn

# Create two apps - one for each port
api_app = FastAPI(title="Core API Health", version="2.0.0")
web_app = FastAPI(title="Veritas Web Health", version="1.0.0")

@api_app.get("/health")
async def api_health():
    """Core API health endpoint"""
    return {
        "status": "ok",
        "service": "core_api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@api_app.get("/")
async def api_root():
    """Core API root endpoint"""
    return {
        "message": "Welcome to Top-TieR Global HUB AI API!",
        "status": "healthy",
        "version": "2.0.0"
    }

@web_app.get("/health")
async def web_health():
    """Veritas web health endpoint"""
    return {
        "status": "healthy",
        "service": "veritas_web",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": 1.0,
        "dependencies": {
            "main_api": "healthy",
            "redis": "disabled",
            "neo4j": "not_implemented"
        }
    }

@web_app.get("/")
async def web_root():
    """Veritas web root endpoint"""
    return {
        "message": "Veritas Mini-Web Service",
        "version": "1.0.0"
    }

async def run_api_server():
    """Run the API server on port 8000"""
    config = uvicorn.Config(api_app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def run_web_server():
    """Run the web server on port 8080"""
    config = uvicorn.Config(web_app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    """Run both servers concurrently"""
    print("Starting health check servers...")
    print("- Core API: http://localhost:8000/health")
    print("- Veritas Web: http://localhost:8080/health")
    
    await asyncio.gather(
        run_api_server(),
        run_web_server()
    )

if __name__ == "__main__":
    asyncio.run(main())