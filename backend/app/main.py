"""
FastAPI Backend Application for Top-TieR Global HUB AI
تطبيق FastAPI الخلفي لمركز Top-TieR العالمي للذكاء الاصطناعي
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.routers import example

app = FastAPI(
    title="Top-TieR Global HUB AI Backend",
    description="Backend API for OSINT intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration - adjust for production
# In production, set CORS_ORIGINS environment variable with specific domains
cors_origins = settings.ENV == "production" and os.getenv("CORS_ORIGINS", "").split(",") or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and Railway deployment
    نقطة فحص الصحة للمراقبة ونشر Railway
    """
    return {
        "status": "healthy",
        "service": "backend",
        "environment": settings.ENV,
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """
    Root endpoint
    النقطة الجذرية
    """
    return {
        "message": "Top-TieR Global HUB AI Backend API",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(example.router, prefix="/api/v1", tags=["example"])
