"""
Backward compatibility shim for api_server module.
This file provides the same interface as before, but imports from the new search_hub structure.
"""

# Import the app from the new location
from search_hub.api.app import app

# Also import gpt_client for backward compatibility with tests
from search_hub.api.app import gpt_client

# Keep the same behavior when run directly
if __name__ == "__main__":
    import os
    try:
        import uvicorn

        # Configuration from environment variables with defaults
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        debug = os.getenv("DEBUG", "false").lower() == "true"

        uvicorn.run(
            "api_server:app",  # Keep backward-compatible entrypoint
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
