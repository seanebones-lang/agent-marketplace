"""Customer model"""
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from .base import Base


class CustomerTier(str, enum.Enum):
    """Customer subscription tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class Customer(Base):
    """Customer organization model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String(255), nullable=False, index=True)
    tier = Column(
        Enum(CustomerTier, name='customer_tier'),
        default=CustomerTier.BRONZE,
        nullable=False
    )
    api_key = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deployments = relationship("Deployment", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, org_name='{self.org_name}', tier='{self.tier}')>"

