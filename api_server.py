import os
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gpt_client import GPTClient, GPTRequest, GPTResponse
from core.cache_middleware import cache
from core.model_router import model_router
from core.metrics import metrics
from core.rate_limiter import rate_limit_middleware

# Fallback if python-dotenv is not available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # Continue without dotenv if not available

app = FastAPI(
    title="Top-TieR Global HUB AI API",
    description="Veritas Nexus v2 - Open-source OSINT platform API with caching, routing, and observability",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GPT client
gpt_client = GPTClient()


class HealthResponse(BaseModel):
    message: str
    status: str
    version: str


class QueryRequest(BaseModel):
    """Enhanced query request with routing and caching support"""
    query: str
    model: Optional[str] = None
    scope: Optional[List[str]] = None
    type: Optional[str] = None
    trace: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    stream: bool = False


class QueryResponse(BaseModel):
    """Enhanced query response with routing and caching info"""
    response: str
    model_info: Dict[str, Any]
    cache_info: Dict[str, Any]
    metrics: Dict[str, Any]
    trace: Optional[Dict[str, Any]] = None


class JobRequest(BaseModel):
    """Request for heavy background jobs"""
    job: str
    parameters: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    """Response for job submission"""
    job_id: str
    status: str
    estimated_time: Optional[int] = None


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
async def health_check() -> Dict[str, Any]:
    """Enhanced health check with system status"""
    return {
        "status": "ok", 
        "version": "2.0.0",
        "features": {
            "cache": cache.redis_client is not None,
            "metrics": metrics.redis_client is not None,
            "model_routing": True
        }
    }


@app.post("/query", response_model=QueryResponse)
async def enhanced_query(request: QueryRequest, http_request: Request):
    """Enhanced query endpoint with caching, routing, and observability"""
    start_time = time.time()
    req_id = metrics.generate_request_id()
    
    try:
        # Check rate limits
        routing_info = model_router.route_model(
            request.query, 
            request.scope, 
            request.model
        )
        
        rate_info = rate_limit_middleware(http_request, routing_info.get("estimated_cost"))
        
        # Check cache first
        cache_key_scope = "|".join(request.scope) if request.scope else None
        cached_response = cache.get(
            "openai", 
            routing_info["model"], 
            request.query, 
            cache_key_scope
        )
        
        if cached_response and not request.trace:
            # Return cached response
            duration = time.time() - start_time
            
            # Log metrics
            metrics.log_request(
                req_id=req_id,
                ip_address=http_request.client.host if http_request.client else None,
                endpoint="/query",
                method="POST",
                model=routing_info["model"],
                tokens=routing_info["estimated_tokens"],
                duration=duration,
                cache_hit=True,
                status_code=200,
                scope=cache_key_scope
            )
            
            return QueryResponse(
                response=cached_response["response"]["response"],
                model_info=routing_info,
                cache_info={"hit": True, "ttl": cached_response.get("ttl")},
                metrics={"req_id": req_id, "duration": duration}
            )
        
        # Generate new response
        if not gpt_client.is_available():
            raise HTTPException(
                status_code=503,
                detail="GPT service unavailable. OpenAI API key not configured."
            )
        
        # Create GPT request with routed model
        gpt_request = GPTRequest(
            prompt=request.query,
            model=routing_info["model"],
            max_tokens=request.max_tokens or min(routing_info["max_tokens"], 1000),
            temperature=request.temperature
        )
        
        # Generate response
        gpt_response = await gpt_client.generate_response(gpt_request)
        
        # Cache the response
        cache.set(
            "openai",
            routing_info["model"],
            request.query,
            {
                "response": gpt_response.response,
                "usage": gpt_response.usage,
                "model": gpt_response.model
            },
            cache_key_scope
        )
        
        duration = time.time() - start_time
        
        # Log metrics
        metrics.log_request(
            req_id=req_id,
            ip_address=http_request.client.host if http_request.client else None,
            endpoint="/query",
            method="POST",
            model=routing_info["model"],
            tokens=gpt_response.usage.get("total_tokens", routing_info["estimated_tokens"]),
            duration=duration,
            cache_hit=False,
            status_code=200,
            cost=routing_info.get("estimated_cost"),
            scope=cache_key_scope
        )
        
        # Prepare response
        response_data = QueryResponse(
            response=gpt_response.response,
            model_info=routing_info,
            cache_info={"hit": False, "cached": True},
            metrics={"req_id": req_id, "duration": duration}
        )
        
        if request.trace:
            response_data.trace = {
                "rate_limit": rate_info,
                "cache_check": "miss",
                "model_routing": routing_info,
                "gpt_usage": gpt_response.usage
            }
        
        return response_data
        
    except ValueError as e:
        metrics.log_request(
            req_id=req_id,
            ip_address=http_request.client.host if http_request.client else None,
            endpoint="/query",
            method="POST",
            duration=time.time() - start_time,
            status_code=400,
            error=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    except RuntimeError as e:
        metrics.log_request(
            req_id=req_id,
            ip_address=http_request.client.host if http_request.client else None,
            endpoint="/query",
            method="POST",
            duration=time.time() - start_time,
            status_code=500,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/metrics")
async def get_metrics(format: str = "json"):
    """Get system metrics in JSON or Prometheus format"""
    if format.lower() == "prometheus":
        return metrics.get_prometheus_metrics()
    
    return {
        "real_time": metrics.get_real_time_metrics(),
        "cache": cache.get_stats(),
        "model_routing": model_router.get_model_stats()
    }


@app.get("/metrics/dashboard")
async def get_dashboard():
    """Get dashboard data for monitoring"""
    return metrics.get_dashboard_data()


@app.post("/job", response_model=JobResponse)
async def submit_job(request: JobRequest):
    """Submit heavy background job (placeholder implementation)"""
    import uuid
    
    job_id = str(uuid.uuid4())[:8]
    
    # This is a placeholder - in a real implementation, you would:
    # 1. Queue the job in Redis
    # 2. Have a background worker process it
    # 3. Store results for retrieval
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        estimated_time=300  # 5 minutes estimate
    )


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results (placeholder implementation)"""
    # This is a placeholder - in a real implementation, you would:
    # 1. Check Redis for job status
    # 2. Return actual progress and results
    
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "result": {"message": "Job completed successfully", "data": {}}
    }


@app.get("/stats")
async def get_client_stats(request: Request):
    """Get current client rate limit and usage stats"""
    from core.rate_limiter import rate_limiter
    return rate_limiter.get_client_stats(request)


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
