"""Agent package model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class AgentPackageModel(Base):
    """Agent package configuration model"""
    __tablename__ = "agent_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    
    # Configuration stored as JSON
    config_json = Column(JSONB, nullable=False, default=dict)
    tools = Column(JSONB, nullable=False, default=list)
    pricing = Column(JSONB, nullable=False, default=dict)
    
    # Template flag
    is_template = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    version = Column(String(20), default="1.0.0")
    engine_type = Column(String(50), default="langgraph")  # langgraph or crewai
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deployments = relationship("Deployment", back_populates="agent_package")
    
    def __repr__(self):
        return f"<AgentPackage(id={self.id}, package_id='{self.package_id}', name='{self.name}')>"

