"""
Execution History Model
Tracks all agent executions for billing, analytics, and audit purposes
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.base import Base


class ExecutionHistory(Base):
    """
    Agent execution history for billing and analytics
    
    This table tracks every agent execution with detailed metrics
    for usage-based billing and performance monitoring.
    """
    __tablename__ = "execution_history"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Execution details
    package_id = Column(String(100), nullable=False, index=True)
    package_name = Column(String(255), nullable=False)
    execution_type = Column(String(50), default="api")  # api, scheduled, webhook
    
    # Request/Response
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(20), nullable=False, index=True)  # success, failed, timeout, cancelled
    
    # Token and cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)  # Cost in USD
    
    # Performance metrics
    duration_ms = Column(Integer, default=0)  # Execution duration in milliseconds
    queue_time_ms = Column(Integer, default=0)  # Time spent in queue
    
    # Tier and pricing
    customer_tier = Column(String(20), nullable=True)  # Tier at time of execution
    pricing_model = Column(String(50), default="per_execution")  # per_execution, subscription, byok
    
    # API key tracking (for BYOK)
    api_key_used = Column(String(100), nullable=True)  # Which API key was used
    model_used = Column(String(100), nullable=True)  # Which LLM model was used
    
    # Metadata
    metadata = Column(JSONB, default=dict)  # Additional execution metadata
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="execution_history")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_exec_customer_created', 'customer_id', 'created_at'),
        Index('idx_exec_package_created', 'package_id', 'created_at'),
        Index('idx_exec_status_created', 'status', 'created_at'),
        Index('idx_exec_customer_status', 'customer_id', 'status'),
        Index('idx_exec_tier_created', 'customer_tier', 'created_at'),
        Index('idx_exec_cost', 'cost'),  # For billing queries
    )
    
    def __repr__(self):
        return f"<ExecutionHistory(id={self.id}, package={self.package_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "package_id": self.package_id,
            "package_name": self.package_name,
            "status": self.status,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "duration_ms": self.duration_ms,
            "customer_tier": self.customer_tier,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }
    
    @property
    def duration_seconds(self):
        """Get duration in seconds"""
        return self.duration_ms / 1000.0 if self.duration_ms else 0.0
    
    @property
    def tokens_per_second(self):
        """Calculate tokens per second throughput"""
        if self.duration_ms and self.duration_ms > 0:
            return (self.total_tokens / self.duration_ms) * 1000
        return 0.0


class UsageAggregate(Base):
    """
    Pre-aggregated usage statistics for fast billing queries
    
    This table stores daily/monthly aggregates to avoid scanning
    the entire execution_history table for billing.
    """
    __tablename__ = "usage_aggregates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation keys
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    package_id = Column(String(100), nullable=True, index=True)  # NULL for all packages
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Aggregated metrics
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    avg_duration_ms = Column(Integer, default=0)
    min_duration_ms = Column(Integer, default=0)
    max_duration_ms = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer")
    
    # Unique constraint to prevent duplicate aggregates
    __table_args__ = (
        Index('idx_usage_agg_unique', 'customer_id', 'package_id', 'period_type', 'period_start', unique=True),
        Index('idx_usage_agg_period', 'period_start', 'period_end'),
    )
    
    def __repr__(self):
        return f"<UsageAggregate(customer={self.customer_id}, period={self.period_type}, executions={self.total_executions})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "package_id": self.package_id,
            "period_type": self.period_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_duration_ms": self.avg_duration_ms
        }

