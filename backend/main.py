"""FastAPI backend application for Top-TieR Global HUB AI."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import messages

# Initialize FastAPI app
app = FastAPI(
    title="Top-TieR Global HUB AI Backend",
    description="Backend API for OSINT platform with bilingual support",
    version="1.0.0",
)

# Configure CORS
# NOTE: In production, restrict origins to your frontend domain
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    messages.router,
    prefix="/api/v1",
    tags=["messages"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Top-TieR Global HUB AI Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", "8000"))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
