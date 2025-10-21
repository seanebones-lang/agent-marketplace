"""
Tests for Customer Model

This module tests the Customer database model.
"""

import pytest
from sqlalchemy.orm import Session
from models.customer import Customer


class TestCustomerModel:
    """Test suite for Customer model"""
    
    def test_create_customer(self, db_session: Session):
        """Test creating a customer"""
        customer = Customer(
            name="Test Company",
            email="test@example.com",
            api_key="test-key-123",
            tier="pro"
        )
        
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        assert customer.id is not None
        assert customer.name == "Test Company"
        assert customer.email == "test@example.com"
        assert customer.tier == "pro"
        assert customer.is_active is True
        assert customer.created_at is not None
    
    def test_customer_unique_email(self, db_session: Session):
        """Test that customer email must be unique"""
        customer1 = Customer(
            name="Company 1",
            email="same@example.com",
            api_key="key-1",
            tier="free"
        )
        customer2 = Customer(
            name="Company 2",
            email="same@example.com",
            api_key="key-2",
            tier="pro"
        )
        
        db_session.add(customer1)
        db_session.commit()
        
        db_session.add(customer2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_customer_unique_api_key(self, db_session: Session):
        """Test that customer API key must be unique"""
        customer1 = Customer(
            name="Company 1",
            email="email1@example.com",
            api_key="same-key",
            tier="free"
        )
        customer2 = Customer(
            name="Company 2",
            email="email2@example.com",
            api_key="same-key",
            tier="pro"
        )
        
        db_session.add(customer1)
        db_session.commit()
        
        db_session.add(customer2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_customer_tier_values(self, db_session: Session):
        """Test different customer tier values"""
        tiers = ["free", "basic", "pro", "enterprise"]
        
        for tier in tiers:
            customer = Customer(
                name=f"Company {tier}",
                email=f"{tier}@example.com",
                api_key=f"key-{tier}",
                tier=tier
            )
            db_session.add(customer)
        
        db_session.commit()
        
        customers = db_session.query(Customer).all()
        assert len(customers) == len(tiers)

