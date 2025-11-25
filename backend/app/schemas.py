"""
Pydantic schemas for API requests and responses.
Defines data models for workflow endpoints and infrastructure health.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InfraHealthService(BaseModel):
    """Health status for a single infrastructure service"""
    available: bool = Field(description="Whether the service is available")
    message: str = Field(description="Status message or error details")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")


class InfraHealth(BaseModel):
    """Infrastructure health check response"""
    status: str = Field(description="Overall status: healthy, degraded, or unhealthy")
    timestamp: str = Field(description="ISO 8601 timestamp of health check")
    services: Dict[str, InfraHealthService] = Field(description="Health status per service")


class GPTWorkflowRequest(BaseModel):
    """Request model for GPT workflow endpoint"""
    prompt: str = Field(description="User prompt for GPT", min_length=1, max_length=4000)
    max_tokens: Optional[int] = Field(default=150, ge=1, le=2000, description="Maximum tokens in response")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    model: Optional[str] = Field(default=None, description="Model override")
    user: Optional[str] = Field(default="system", description="User identifier for logging")
    persist_to_redis: bool = Field(default=True, description="Whether to persist request/response to Redis")
    forward_to_telegram: bool = Field(default=False, description="Whether to forward response to Telegram")


class GPTWorkflowResponse(BaseModel):
    """Response model for GPT workflow endpoint"""
    response: str = Field(description="GPT generated response")
    usage: Dict[str, Any] = Field(description="Token usage information")
    model: str = Field(description="Model used for generation")
    duration_ms: float = Field(description="Request processing duration in milliseconds")
    persisted: bool = Field(default=False, description="Whether request was persisted to Redis")
    forwarded: bool = Field(default=False, description="Whether response was forwarded to Telegram")
    redis_key: Optional[str] = Field(default=None, description="Redis key if persisted")


class IngestionWorkflowResponse(BaseModel):
    """Response model for ingestion workflow endpoint"""
    status: str = Field(description="Status of ingestion operation")
    source: str = Field(description="Data source name")
    count: int = Field(description="Number of records ingested")
    index_path: str = Field(description="Path to index file")
    duration_ms: float = Field(description="Ingestion duration in milliseconds")
    records_sample_head: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Sample of first few records (up to 3)"
    )


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    limit: int = Field(description="Rate limit threshold")
    remaining: int = Field(description="Remaining requests")
    reset_at: str = Field(description="ISO 8601 timestamp when limit resets")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
