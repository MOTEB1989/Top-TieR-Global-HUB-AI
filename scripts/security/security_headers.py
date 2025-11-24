"""
Security Headers Module
Implements security headers middleware for FastAPI applications.
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.
    
    Implements OWASP recommended security headers:
    - Content Security Policy (CSP)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(
        self,
        app: ASGIApp,
        csp_directives: str = "default-src 'self'",
        hsts_max_age: int = 31536000,
        enable_hsts: bool = True,
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            csp_directives: Content Security Policy directives
            hsts_max_age: HSTS max-age in seconds (default 1 year)
            enable_hsts: Whether to enable HSTS header
        """
        super().__init__(app)
        self.csp_directives = csp_directives
        self.hsts_max_age = hsts_max_age
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
            
        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_directives
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS - Force HTTPS
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
        )
        
        # Remove server header to avoid info disclosure
        response.headers.pop("Server", None)
        
        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Secure CORS middleware with strict validation.
    """

    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: list[str],
        allowed_methods: list[str] = None,
        allowed_headers: list[str] = None,
        max_age: int = 3600,
    ):
        """
        Initialize CORS security middleware.
        
        Args:
            app: ASGI application
            allowed_origins: List of allowed origin domains
            allowed_methods: List of allowed HTTP methods
            allowed_headers: List of allowed headers
            max_age: Preflight cache duration in seconds
        """
        super().__init__(app)
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["Content-Type", "Authorization"]
        self.max_age = max_age

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle CORS.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
            
        Returns:
            HTTP response with CORS headers
        """
        origin = request.headers.get("Origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            if origin in self.allowed_origins:
                return Response(
                    content="",
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": ", ".join(self.allowed_methods),
                        "Access-Control-Allow-Headers": ", ".join(self.allowed_headers),
                        "Access-Control-Max-Age": str(self.max_age),
                    },
                )
            return Response(content="", status_code=403)
        
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for API endpoints.
    """

    def __init__(
        self,
        app: ASGIApp,
        rate_limiter: any,
        get_client_id: Callable[[Request], str] = None,
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: ASGI application
            rate_limiter: Rate limiter instance
            get_client_id: Function to extract client ID from request
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.get_client_id = get_client_id or self._default_get_client_id

    def _default_get_client_id(self, request: Request) -> str:
        """
        Default client ID extraction (uses IP address).
        
        Args:
            request: HTTP request
            
        Returns:
            Client identifier
        """
        # Try to get real IP from proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
            
        Returns:
            HTTP response or 429 if rate limited
        """
        client_id = self.get_client_id(request)
        
        if not self.rate_limiter.is_allowed(client_id):
            return Response(
                content='{"error": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(getattr(self.rate_limiter, "max_requests", "N/A")),
                    "X-RateLimit-Remaining": "0",
                },
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        if hasattr(self.rate_limiter, "get_remaining_tokens"):
            remaining = int(self.rate_limiter.get_remaining_tokens(client_id))
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate requests for security threats.
    """

    def __init__(self, app: ASGIApp, max_content_length: int = 10 * 1024 * 1024):
        """
        Initialize request validation middleware.
        
        Args:
            app: ASGI application
            max_content_length: Maximum request body size in bytes (default 10MB)
        """
        super().__init__(app)
        self.max_content_length = max_content_length

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Validate incoming requests.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler
            
        Returns:
            HTTP response or error if validation fails
        """
        # Check content length
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_content_length:
                    return Response(
                        content='{"error": "Request body too large"}',
                        status_code=413,
                        media_type="application/json",
                    )
            except ValueError:
                return Response(
                    content='{"error": "Invalid Content-Length header"}',
                    status_code=400,
                    media_type="application/json",
                )
        
        # Check for suspicious patterns in URL
        path = str(request.url.path)
        suspicious_patterns = ["../", "..\\", "<script", "javascript:", "data:"]
        
        for pattern in suspicious_patterns:
            if pattern in path.lower():
                return Response(
                    content='{"error": "Invalid request path"}',
                    status_code=400,
                    media_type="application/json",
                )
        
        # Check User-Agent (block empty or suspicious user agents)
        user_agent = request.headers.get("User-Agent", "")
        if not user_agent or len(user_agent) < 3:
            return Response(
                content='{"error": "Invalid User-Agent"}',
                status_code=400,
                media_type="application/json",
            )
        
        return await call_next(request)


# Example usage with FastAPI
if __name__ == "__main__":
    from fastapi import FastAPI
    
    app = FastAPI(title="Secure API")
    
    # Add security headers middleware
    app.add_middleware(
        SecurityHeadersMiddleware,
        csp_directives="default-src 'self'; script-src 'self' 'unsafe-inline'",
        enable_hsts=True,
    )
    
    # Add CORS middleware (for specific origins)
    app.add_middleware(
        CORSSecurityMiddleware,
        allowed_origins=["https://example.com", "https://app.example.com"],
        allowed_methods=["GET", "POST"],
    )
    
    # Add request validation
    app.add_middleware(
        RequestValidationMiddleware,
        max_content_length=5 * 1024 * 1024,  # 5MB
    )
    
    @app.get("/")
    async def root():
        return {"message": "Secure API with security headers"}
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    print("Example FastAPI app with security middleware configured")
    print("Security headers will be added to all responses")
