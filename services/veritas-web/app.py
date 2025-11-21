#!/usr/bin/env python3
"""
Veritas Mini-Web Service
A lightweight FastAPI service for private OSINT queries and internal operations.

This service provides:
- Private query endpoints
- Internal system monitoring
- Lightweight data processing
- Secure internal communication
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Settings:
    """Application settings"""
    
    # Server configuration
    HOST: str = os.getenv("MINI_WEB_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MINI_WEB_PORT", "8088"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    API_TOKEN: str = os.getenv("API_TOKEN", "veritas-mini-token-change-me")
    
    # External services
    MAIN_API_URL: str = os.getenv("MAIN_API_URL", "http://localhost:8000")
    NEO4J_URL: str = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    
    # Feature flags
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
    ENABLE_ENCRYPTION: bool = os.getenv("ENABLE_ENCRYPTION", "false").lower() == "true"

settings = Settings()

# Pydantic models
class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Response timestamp")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Uptime in seconds")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")

class QueryRequest(BaseModel):
    """Private query request model"""
    query: str = Field(..., description="Search query")
    query_type: str = Field(default="general", description="Type of query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Query filters")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum results")
    include_metadata: bool = Field(default=True, description="Include metadata in response")

class QueryResponse(BaseModel):
    """Private query response model"""
    query_id: str = Field(..., description="Unique query identifier")
    status: str = Field(..., description="Query status")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Query metadata")
    timestamp: datetime = Field(..., description="Response timestamp")

class SystemStats(BaseModel):
    """System statistics model"""
    active_connections: int = Field(..., description="Active connections")
    total_queries: int = Field(..., description="Total queries processed")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    average_response_time: float = Field(..., description="Average response time in ms")
    memory_usage: Dict[str, Any] = Field(..., description="Memory usage statistics")

# Global variables
start_time = datetime.now(timezone.utc)
redis_client: Optional[redis.Redis] = None
http_client: Optional[httpx.AsyncClient] = None
cipher_suite: Optional[Fernet] = None

# Security
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API token"""
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return credentials.credentials

# Dependency functions
async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client"""
    return redis_client if settings.ENABLE_CACHE else None

async def get_http_client() -> httpx.AsyncClient:
    """Get HTTP client"""
    if http_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HTTP client not available"
        )
    return http_client

# Utility functions
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not settings.ENABLE_ENCRYPTION or cipher_suite is None:
        return data
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not settings.ENABLE_ENCRYPTION or cipher_suite is None:
        return encrypted_data
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return encrypted_data

async def cache_get(key: str) -> Optional[str]:
    """Get value from cache"""
    if not settings.ENABLE_CACHE or redis_client is None:
        return None
    try:
        value = await redis_client.get(key)
        return value.decode() if value else None
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None

async def cache_set(key: str, value: str, expire: int = 300) -> bool:
    """Set value in cache"""
    if not settings.ENABLE_CACHE or redis_client is None:
        return False
    try:
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
        return False

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_client, http_client, cipher_suite
    
    logger.info("Starting Veritas Mini-Web Service...")
    
    # Initialize Redis client
    if settings.ENABLE_CACHE:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            redis_client = None
    
    # Initialize HTTP client
    try:
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        logger.info("HTTP client initialized")
    except Exception as e:
        logger.error(f"HTTP client initialization failed: {e}")
    
    # Initialize encryption
    if settings.ENABLE_ENCRYPTION:
        try:
            key = Fernet.generate_key() if settings.SECRET_KEY == "dev-key-change-in-production" else settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
            cipher_suite = Fernet(Fernet.generate_key())  # Use generated key for demo
            logger.info("Encryption initialized")
        except Exception as e:
            logger.warning(f"Encryption initialization failed: {e}")
    
    logger.info("Veritas Mini-Web Service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Veritas Mini-Web Service...")
    
    if http_client:
        await http_client.aclose()
    
    if redis_client:
        await redis_client.close()
    
    logger.info("Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Veritas Mini-Web Service",
    description="Private OSINT query service for internal operations",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware (restrictive for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routes

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {"message": "Veritas Mini-Web Service", "version": "1.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Check dependencies
    dependencies = {}
    
    # Check main API
    try:
        if http_client:
            response = await http_client.get(f"{settings.MAIN_API_URL}/health", timeout=5.0)
            dependencies["main_api"] = "healthy" if response.status_code == 200 else "unhealthy"
        else:
            dependencies["main_api"] = "unavailable"
    except Exception:
        dependencies["main_api"] = "unhealthy"
    
    # Check Redis
    if settings.ENABLE_CACHE and redis_client:
        try:
            await redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception:
            dependencies["redis"] = "unhealthy"
    else:
        dependencies["redis"] = "disabled"
    
    # Check Neo4j (placeholder - would need neo4j driver)
    dependencies["neo4j"] = "not_implemented"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        uptime=uptime,
        dependencies=dependencies
    )

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_token)])
async def private_query(
    request: QueryRequest,
    redis_client: Optional[redis.Redis] = Depends(get_redis),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """Execute private OSINT query"""
    query_id = f"mini_{int(datetime.now().timestamp())}_{hash(request.query) % 10000}"
    
    # Check cache first
    cache_key = f"query:{hash(request.query)}"
    cached_result = await cache_get(cache_key)
    
    if cached_result:
        logger.info(f"Cache hit for query: {query_id}")
        return QueryResponse(
            query_id=query_id,
            status="cached",
            results=[{"cached": True, "data": cached_result}],
            metadata={"source": "cache", "cached": True},
            timestamp=datetime.now(timezone.utc)
        )
    
    # Execute query against main API
    try:
        query_data = {
            "query": request.query,
            "type": request.query_type,
            "scope": ["osint"],
            "max_results": request.max_results
        }
        
        response = await http_client.post(
            f"{settings.MAIN_API_URL}/query",
            json=query_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result_data = response.json()
            
            # Cache the result
            await cache_set(cache_key, str(result_data), expire=600)  # 10 minutes
            
            return QueryResponse(
                query_id=query_id,
                status="completed",
                results=[result_data] if result_data else [],
                metadata={
                    "source": "main_api",
                    "cached": False,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                } if request.include_metadata else None,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Main API error: {response.text}"
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Query timeout - main API not responding"
        )
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal query processing error"
        )

@app.get("/stats", response_model=SystemStats, dependencies=[Depends(verify_token)])
async def get_system_stats():
    """Get system statistics"""
    # This is a placeholder implementation
    # In a real system, you would collect actual metrics
    
    return SystemStats(
        active_connections=1,  # Placeholder
        total_queries=0,       # Would track this
        cache_hit_rate=85.5,   # Would calculate this
        average_response_time=250.0,  # Would measure this
        memory_usage={
            "used_mb": 128,
            "available_mb": 512,
            "percentage": 25.0
        }
    )

@app.post("/cache/clear", dependencies=[Depends(verify_token)])
async def clear_cache():
    """Clear application cache"""
    if not settings.ENABLE_CACHE or redis_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cache not available"
        )
    
    try:
        await redis_client.flushdb()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache"
        )

@app.get("/config", dependencies=[Depends(verify_token)])
async def get_config():
    """Get service configuration (non-sensitive)"""
    return {
        "version": "1.0.0",
        "debug": settings.DEBUG,
        "features": {
            "cache": settings.ENABLE_CACHE,
            "monitoring": settings.ENABLE_MONITORING,
            "encryption": settings.ENABLE_ENCRYPTION
        },
        "endpoints": {
            "main_api": settings.MAIN_API_URL,
            "neo4j": settings.NEO4J_URL.replace(settings.NEO4J_PASSWORD, "***") if settings.NEO4J_PASSWORD in settings.NEO4J_URL else settings.NEO4J_URL
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url)
        }
    )

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )