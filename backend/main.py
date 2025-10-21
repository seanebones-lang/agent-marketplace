"""Agent Marketplace Platform - FastAPI Backend"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from core.config import settings
from api.v1 import marketplace, health, auth, websocket, analytics, history, billing, tiers
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
    
    yield
    
    # Shutdown
    print("Shutting down Agent Marketplace Platform...")


app = FastAPI(
    title="Agent Marketplace API",
    description="Enterprise Agentic AI Platform - Rent autonomous agents for enterprise operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

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

