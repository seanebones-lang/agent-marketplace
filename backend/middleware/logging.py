"""
Logging Middleware

This module provides request/response logging middleware.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.logging import get_logger, set_trace_id, get_trace_id


logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request with logging.
        
        Args:
            request: Incoming request
            call_next: Next middleware/route handler
            
        Returns:
            Response
        """
        # Generate and set trace ID
        trace_id = request.headers.get("X-Trace-ID") or set_trace_id()
        
        # Log request
        start_time = time.time()
        
        logger.info(
            f"Request started",
            extra={
                "extra_fields": {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "client_host": request.client.host if request.client else None,
                    "trace_id": trace_id
                }
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "trace_id": trace_id
                    }
                }
            )
            
            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "extra_fields": {
                        "method": request.method,
                        "path": request.url.path,
                        "duration_ms": round(duration * 1000, 2),
                        "trace_id": trace_id,
                        "error": str(e)
                    }
                },
                exc_info=True
            )
            
            raise

