"""Configuration Settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App
    app_name: str = "Agent Marketplace"
    version: str = "1.0.0"
    frontend_url: str = "http://localhost:3000"
    
    # Database
    database_url: str = "postgresql://user:password@localhost/agentic"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # LLM Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Agent Execution
    max_agent_timeout: int = 300  # seconds
    max_concurrent_agents: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

