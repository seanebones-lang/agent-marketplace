"""Agent Marketplace Platform - FastAPI Backend"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from core.config import settings
from api.v1 import marketplace, health, auth, websocket, analytics, history, billing, tiers, usage, rate_limits, monitoring, metrics
from database import engine
from models import base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting Agent Marketplace Platform...")
    
    # Create database tables
    base.Base.metadata.create_all(bind=engine)
    print("Database tables created")
    
    # Initialize Redis and Rate Limiter
    try:
        import redis
        from core.rate_limiter import get_rate_limiter
        
        redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test Redis connection
        redis_client.ping()
        print(f"Redis connected: {settings.redis_url}")
        
        # Initialize rate limiter
        rate_limiter = get_rate_limiter(redis_client)
        app.state.rate_limiter = rate_limiter
        print("Rate limiter initialized")
        
    except Exception as e:
        print(f"Warning: Redis/Rate Limiter initialization failed: {e}")
        print("Rate limiting will be disabled")
        app.state.rate_limiter = None
    
    yield
    
    # Shutdown
    print("Shutting down Agent Marketplace Platform...")
    
    # Close Redis connection
    if hasattr(app.state, "rate_limiter") and app.state.rate_limiter:
        try:
            app.state.rate_limiter.redis.close()
            print("Redis connection closed")
        except Exception as e:
            print(f"Error closing Redis: {e}")


app = FastAPI(
    title="Agent Marketplace API",
    description="Enterprise Agentic AI Platform - Rent autonomous agents for enterprise operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware (order matters - add before CORS)
from core.security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    RequestLoggingMiddleware,
    DDoSProtectionMiddleware
)

# DDoS protection (outermost layer)
app.add_middleware(DDoSProtectionMiddleware, max_requests_per_minute=200)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# Request validation
app.add_middleware(RequestValidationMiddleware)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(settings.frontend_url),
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry instrumentation
FastAPIInstrumentor.instrument_app(app)

# API Routes
app.include_router(
    health.router,
    prefix="/api/v1/health",
    tags=["Health"]
)

app.include_router(
    marketplace.router,
    prefix="/api/v1",
    tags=["Marketplace"]
)

app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

app.include_router(
    websocket.router,
    prefix="/api/v1",
    tags=["WebSocket"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Analytics"]
)

app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["History"]
)

app.include_router(
    billing.router,
    prefix="/api/v1",
    tags=["Billing"]
)

app.include_router(
    tiers.router,
    prefix="/api/v1",
    tags=["Model Tiers"]
)

app.include_router(
    usage.router,
    prefix="/api/v1/usage",
    tags=["Usage & Billing"]
)

app.include_router(
    rate_limits.router,
    prefix="/api/v1",
    tags=["Rate Limits"]
)

app.include_router(
    monitoring.router,
    prefix="/api/v1",
    tags=["Monitoring"]
)

app.include_router(
    metrics.router,
    prefix="/api/v1",
    tags=["Metrics"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Agent Marketplace Platform",
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

