"""Deployment and usage tracking models"""
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Numeric, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .base import Base


class DeploymentStatus(str, enum.Enum):
    """Deployment status states"""
    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    TERMINATED = "terminated"


class Deployment(Base):
    """Agent deployment instance"""
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agent_packages.id"), nullable=False, index=True)
    
    status = Column(
        Enum(DeploymentStatus, name='deployment_status'),
        default=DeploymentStatus.PENDING,
        nullable=False,
        index=True
    )
    
    endpoint_url = Column(String(500))
    
    # Execution stats
    total_tasks = Column(Integer, default=0)
    total_tokens = Column(BigInteger, default=0)
    total_cost = Column(Numeric(10, 4), default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    terminated_at = Column(DateTime(timezone=True))
    
    # Relationships
    customer = relationship("Customer", back_populates="deployments")
    agent_package = relationship("AgentPackageModel", back_populates="deployments")
    usage_logs = relationship("UsageLog", back_populates="deployment")
    
    def __repr__(self):
        return f"<Deployment(id={self.id}, customer_id={self.customer_id}, status='{self.status}')>"


class UsageLog(Base):
    """Usage tracking for billing"""
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=False, index=True)
    
    task_count = Column(Integer, default=1)
    tokens_used = Column(BigInteger, nullable=False)
    cost = Column(Numeric(10, 4), nullable=False)
    
    # Task details
    task_description = Column(String(1000))
    execution_time_ms = Column(Integer)
    status = Column(String(50))  # success, failed, timeout
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    deployment = relationship("Deployment", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog(id={self.id}, deployment_id={self.deployment_id}, cost={self.cost})>"

