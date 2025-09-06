from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from typing import Dict, Any

# Fallback if python-dotenv is not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

app = FastAPI(
    title="Top-TieR Global HUB AI API",
    description="Veritas Nexus v2 - Open-source OSINT platform API",
    version="2.0.0"
)

class HealthResponse(BaseModel):
    message: str
    status: str
    version: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        message="Welcome to Top-TieR Global HUB AI API!",
        status="healthy",
        version="2.0.0"
    )

@app.get("/api", response_model=HealthResponse)
async def get_api():
    """Legacy API endpoint for backward compatibility"""
    return HealthResponse(
        message="Welcome to the API!",
        status="healthy", 
        version="2.0.0"
    )

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check"""
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    # Try to import uvicorn, fall back to basic message if not available
    try:
        import uvicorn
        
        # Configuration from environment variables with defaults
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        debug = os.getenv("DEBUG", "false").lower() == "true"
        
        uvicorn.run(
            "api_server:app", 
            host=host, 
            port=port, 
            reload=debug,
            log_level="info" if not debug else "debug"
        )
    except ImportError:
        print("FastAPI/Uvicorn not available. Please install with: pip install fastapi uvicorn")
        print("API server ready for deployment with modern dependencies.")