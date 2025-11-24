import json
import logging
import os
import time
from enum import Enum
from typing import Any, Dict, Optional

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from gpt_client import GPTClient, GPTRequest, GPTResponse
from app.ingestion.cli import run_ingestion
from utils.secrets_manager import SecretManager

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
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
)

logger = logging.getLogger(__name__)
instrumentator = Instrumentator()
secret_manager = SecretManager()


class Role(str, Enum):
    """Supported RBAC roles."""

    ADMIN = "admin"
    DEV = "dev"
    VIEWER = "viewer"


class RBACManager:
    """Load API key → role mapping from the configured secrets backend."""

    def __init__(self, manager: SecretManager, cache_ttl: int = 300) -> None:
        self._manager = manager
        self._cache_ttl = cache_ttl
        self._role_cache: Dict[str, Role] = {}
        self._last_loaded = 0.0

    def _parse_mapping(self, payload: Any) -> Dict[str, Role]:
        mapping: Dict[str, Role] = {}
        if isinstance(payload, dict):
            items = payload.items()
        elif isinstance(payload, str) and payload.strip():
            try:
                items = json.loads(payload).items()  # type: ignore[assignment]
            except (json.JSONDecodeError, AttributeError):
                pairs = [p.strip() for p in payload.split(",") if ":" in p]
                items = (pair.split(":", 1) for pair in pairs)
        else:
            items = []

        for key, role_name in items:
            try:
                mapping[str(key).strip()] = Role(str(role_name).strip().lower())
            except ValueError:
                logger.warning("Ignoring unknown role '%s' for key '%s'", role_name, key)
        return mapping

    def _load_roles(self) -> Dict[str, Role]:
        payload: Any = None
        secret_path = os.getenv("RBAC_SECRET_PATH")
        if secret_path:
            payload = self._manager.get_secret(secret_path)
        if payload in (None, ""):
            payload = self._manager.get_secret("RBAC_API_KEYS")
        mapping = self._parse_mapping(payload)

        if not mapping:
            logger.warning("RBAC mapping is empty. Defaulting to viewer-only access.")
        return mapping

    def _refresh_cache_if_needed(self) -> None:
        if not self._role_cache or (time.time() - self._last_loaded) > self._cache_ttl:
            self._role_cache = self._load_roles()
            self._last_loaded = time.time()

    def refresh(self) -> None:
        """Force refresh the RBAC mapping."""

        self._role_cache = self._load_roles()
        self._last_loaded = time.time()

    def get_role(self, api_key: Optional[str]) -> Role:
        self._refresh_cache_if_needed()
        if not self._role_cache:
            return Role.VIEWER
        if not api_key:
            raise PermissionError("API key missing")
        role = self._role_cache.get(api_key)
        if role is None:
            raise PermissionError("Invalid API key")
        return role


rbac_manager = RBACManager(secret_manager)

rate_limiter_ready = False
rate_limiter_client: Optional[redis.Redis] = None


async def init_rate_limiter() -> None:
    """Initialise FastAPI-Limiter with Redis if available."""

    global rate_limiter_ready, rate_limiter_client

    redis_url = os.getenv("RATE_LIMIT_REDIS_URL", "redis://localhost:6379/0")
    if not redis_url:
        logger.warning("RATE_LIMIT_REDIS_URL not provided. Rate limiting disabled.")
        return

    try:
        rate_limiter_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await rate_limiter_client.ping()
        await FastAPILimiter.init(rate_limiter_client)
        rate_limiter_ready = True
        logger.info("Rate limiting enabled using Redis backend at %s", redis_url)
    except Exception as exc:  # pragma: no cover - requires Redis server
        rate_limiter_ready = False
        if rate_limiter_client is not None:
            await rate_limiter_client.close()
        rate_limiter_client = None
        logger.warning("Failed to initialise rate limiter: %s", exc)


def rate_limit_dependency(times: int, seconds: int):
    """Return a rate-limiter dependency that gracefully degrades when disabled."""

    if rate_limiter_ready:
        return RateLimiter(times=times, seconds=seconds)

    async def _noop() -> None:
        return None

    return _noop


def require_roles(*allowed_roles: Role):
    """FastAPI dependency enforcing RBAC roles."""

    async def _checker(x_api_key: Optional[str] = Header(default=None, alias="X-API-KEY")) -> Role:
        try:
            role = rbac_manager.get_role(x_api_key)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        if allowed_roles and role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions for this resource")
        return role

    return _checker


# Initialize GPT client
gpt_client = GPTClient()


@app.on_event("startup")
async def startup_event() -> None:
    """Configure instrumentation, rate limiting, and RBAC cache."""

    instrumentator.instrument(app)
    if not any(route.path == "/metrics" for route in app.router.routes):
        instrumentator.expose(app, include_in_schema=False, endpoint="/metrics")
    await init_rate_limiter()
    rbac_manager.refresh()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Ensure Redis connections are closed cleanly."""

    if rate_limiter_client is not None:
        await rate_limiter_client.close()


class HealthResponse(BaseModel):
    message: str
    status: str
    version: str


@app.get(
    "/",
    response_model=HealthResponse,
    dependencies=[Depends(rate_limit_dependency(times=60, seconds=60))],
)
async def root(_: Role = Depends(require_roles(Role.ADMIN, Role.DEV, Role.VIEWER))):
    """Health check endpoint"""
    return HealthResponse(
        message="Welcome to Top-TieR Global HUB AI API!",
        status="healthy",
        version="2.0.0",
    )


@app.get(
    "/api",
    response_model=HealthResponse,
    dependencies=[Depends(rate_limit_dependency(times=60, seconds=60))],
)
async def get_api(_: Role = Depends(require_roles(Role.ADMIN, Role.DEV, Role.VIEWER))):
    """Legacy API endpoint for backward compatibility"""
    return HealthResponse(
        message="Welcome to the API!", status="healthy", version="2.0.0"
    )


@app.get(
    "/health",
    dependencies=[Depends(rate_limit_dependency(times=120, seconds=60))],
)
async def health_check(
    _: Role = Depends(require_roles(Role.ADMIN, Role.DEV, Role.VIEWER)),
) -> Dict[str, Any]:
    """Simple health check"""
    return {"status": "ok", "version": "2.0.0"}


@app.post(
    "/gpt",
    response_model=GPTResponse,
    dependencies=[Depends(rate_limit_dependency(times=30, seconds=60))],
)
async def gpt_endpoint(
    request: GPTRequest,
    _: Role = Depends(require_roles(Role.ADMIN, Role.DEV)),
):
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


@app.post(
    "/v1/sources/{source}/sync",
    dependencies=[Depends(rate_limit_dependency(times=10, seconds=60))],
)
async def sync_ingestion(
    source: str,
    limit: Optional[int] = Query(default=None, ge=1, description="Limit processed items"),
    _: Role = Depends(require_roles(Role.ADMIN)),
) -> Dict[str, Any]:
    normalized_source = source.lower()
    try:
        result = run_ingestion(normalized_source, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependency for ingestion: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    return {
        "status": "ok",
        "source": result["source"],
        "count": result["count"],
        "index_path": result["index_path"],
    }


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
