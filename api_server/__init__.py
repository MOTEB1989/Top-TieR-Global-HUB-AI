import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gpt_client import GPTClient, GPTRequest, GPTResponse

# Fallback if python-dotenv is not available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

app = FastAPI(
    title="Top-TieR Global HUB AI API",
    description="Veritas Nexus v2 - Open-source OSINT platform API",
    version="2.0.0",
)

# Initialize GPT client
gpt_client = GPTClient()


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
        version="2.0.0",
    )


@app.get("/api", response_model=HealthResponse)
async def get_api():
    """Legacy API endpoint for backward compatibility"""
    return HealthResponse(
        message="Welcome to the API!", status="healthy", version="2.0.0"
    )


@app.get("/health")
async def health() -> JSONResponse:
    """Health check endpoint used by container orchestration."""
    return JSONResponse(content={"status": "ok", "service": "veritas-api"})


@app.post("/gpt", response_model=GPTResponse)
async def gpt_endpoint(request: GPTRequest):
    """GPT endpoint for text generation"""
    if not gpt_client.is_available():
        raise HTTPException(
            status_code=503,
            detail="GPT service unavailable. OpenAI API key not configured."
        )
    
    try:
        response = await gpt_client.generate_response(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            log_level="info" if not debug else "debug",
        )
    except ImportError:
        print(
            "FastAPI/Uvicorn not available. Please install with: pip install fastapi uvicorn"
        )
        print("API server ready for deployment with modern dependencies.")
