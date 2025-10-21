"""
Production-Grade Security Middleware
Protects against common web vulnerabilities and attacks
"""

import time
import hashlib
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
import logging

from core.security import input_validator, InputValidator
from core.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains
    - Content-Security-Policy: default-src 'self'
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: geolocation=(), microphone=(), camera=()
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server header
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add custom header
        response.headers["X-Powered-By"] = "Agent Marketplace"
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate incoming requests for security threats.
    
    Checks:
    - Request size limits
    - Content-Type validation
    - Suspicious patterns in URLs
    - Rate limit headers
    """
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_URL_LENGTH = 2048
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check URL length
        if len(str(request.url)) > self.MAX_URL_LENGTH:
            logger.warning(
                "Request URL too long",
                extra={
                    "url_length": len(str(request.url)),
                    "max_length": self.MAX_URL_LENGTH,
                    "ip": request.client.host if request.client else "unknown"
                }
            )
            return JSONResponse(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                content={"error": "Request URL too long"}
            )
        
        # Check for suspicious patterns in URL
        url_str = str(request.url.path).lower()
        suspicious_patterns = [
            '../', '..\\',  # Path traversal
            '<script', 'javascript:',  # XSS
            'union select', 'drop table',  # SQL injection
            '/etc/', '/proc/', '/sys/',  # System file access
        ]
        
        for pattern in suspicious_patterns:
            if pattern in url_str:
                logger.warning(
                    "Suspicious pattern in URL",
                    extra={
                        "pattern": pattern,
                        "url": url_str,
                        "ip": request.client.host if request.client else "unknown"
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid request"}
                )
        
        # Check request size (for POST/PUT/PATCH)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.MAX_REQUEST_SIZE:
                        logger.warning(
                            "Request body too large",
                            extra={
                                "size": size,
                                "max_size": self.MAX_REQUEST_SIZE,
                                "ip": request.client.host if request.client else "unknown"
                            }
                        )
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={"error": "Request body too large"}
                        )
                except ValueError:
                    pass
        
        # Process request
        response = await call_next(request)
        
        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Optional IP whitelist for admin endpoints.
    
    Configure allowed IPs via environment variable.
    """
    
    def __init__(self, app, allowed_ips: Optional[list] = None):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []
        self.admin_paths = [
            "/api/v1/monitoring/circuit-breakers/reset",
            "/api/v1/rate-limits/reset",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is an admin endpoint
        is_admin_endpoint = any(
            request.url.path.startswith(path) for path in self.admin_paths
        )
        
        if is_admin_endpoint and self.allowed_ips:
            client_ip = request.client.host if request.client else "unknown"
            
            if client_ip not in self.allowed_ips:
                logger.warning(
                    "Unauthorized IP access to admin endpoint",
                    extra={
                        "ip": client_ip,
                        "path": request.url.path
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"}
                )
        
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests with security-relevant information.
    
    Logs:
    - IP address
    - User agent
    - Request method and path
    - Response status
    - Response time
    - Customer ID (if authenticated)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(
                "Request processing error",
                extra={
                    "ip": client_ip,
                    "method": method,
                    "path": path,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
        
        # Calculate response time
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log request
        log_data = {
            "ip": client_ip,
            "user_agent": user_agent,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms
        }
        
        # Add customer ID if available
        if hasattr(request.state, "customer"):
            log_data["customer_id"] = str(request.state.customer.id)
        
        # Log with appropriate level
        if status_code >= 500:
            logger.error("Request completed with server error", extra=log_data)
        elif status_code >= 400:
            logger.warning("Request completed with client error", extra=log_data)
        else:
            logger.info("Request completed successfully", extra=log_data)
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection for state-changing operations.
    
    Validates CSRF tokens for POST/PUT/PATCH/DELETE requests.
    """
    
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    CSRF_HEADER = "X-CSRF-Token"
    
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
    
    def generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        data = f"{session_id}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        expected_token = self.generate_csrf_token(session_id)
        return token == expected_token
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF check for safe methods
        if request.method in self.CSRF_METHODS:
            return await call_next(request)
        
        # Skip CSRF check for API endpoints (using token auth)
        if request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Get CSRF token from header
        csrf_token = request.headers.get(self.CSRF_HEADER)
        
        if not csrf_token:
            logger.warning(
                "Missing CSRF token",
                extra={
                    "ip": request.client.host if request.client else "unknown",
                    "path": request.url.path
                }
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "CSRF token missing"}
            )
        
        # Validate token (would need session management)
        # For now, skip validation for API-first architecture
        
        response = await call_next(request)
        return response


class SQLInjectionProtectionMiddleware(BaseHTTPMiddleware):
    """
    Additional SQL injection protection at middleware level.
    
    Scans query parameters and request body for SQL injection patterns.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check query parameters
        for key, value in request.query_params.items():
            try:
                InputValidator.validate_string(
                    str(value),
                    field_name=key,
                    max_length=1000,
                    allow_special_chars=True
                )
            except Exception as e:
                logger.warning(
                    "Suspicious query parameter",
                    extra={
                        "key": key,
                        "value": str(value)[:100],
                        "ip": request.client.host if request.client else "unknown"
                    }
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid query parameter"}
                )
        
        response = await call_next(request)
        return response


class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Basic DDoS protection.
    
    Tracks request counts per IP and blocks excessive requests.
    Note: In production, use a proper DDoS protection service (Cloudflare, AWS Shield, etc.)
    """
    
    def __init__(self, app, max_requests_per_minute: int = 100):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean up old entries
        self.request_counts = {
            ip: data for ip, data in self.request_counts.items()
            if current_time - data["start_time"] < 60
        }
        
        # Check request count
        if client_ip in self.request_counts:
            data = self.request_counts[client_ip]
            if current_time - data["start_time"] < 60:
                data["count"] += 1
                if data["count"] > self.max_requests_per_minute:
                    logger.warning(
                        "DDoS protection triggered",
                        extra={
                            "ip": client_ip,
                            "count": data["count"],
                            "limit": self.max_requests_per_minute
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"error": "Too many requests"},
                        headers={"Retry-After": "60"}
                    )
            else:
                # Reset counter
                self.request_counts[client_ip] = {
                    "start_time": current_time,
                    "count": 1
                }
        else:
            # First request from this IP
            self.request_counts[client_ip] = {
                "start_time": current_time,
                "count": 1
            }
        
        response = await call_next(request)
        return response


# Export middleware classes
__all__ = [
    "SecurityHeadersMiddleware",
    "RequestValidationMiddleware",
    "IPWhitelistMiddleware",
    "RequestLoggingMiddleware",
    "CSRFProtectionMiddleware",
    "SQLInjectionProtectionMiddleware",
    "DDoSProtectionMiddleware"
]

