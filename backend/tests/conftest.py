"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all tests.
"""

import pytest
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models.base import Base
from models.customer import Customer
from models.agent import AgentPackageModel
from core.config import settings


# Test database URL (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database session override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_customer(db_session: Session) -> Customer:
    """
    Create a test customer.
    """
    customer = Customer(
        name="Test Company",
        email="test@example.com",
        api_key="test-api-key-12345",
        tier="pro"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_agent_package(db_session: Session) -> AgentPackageModel:
    """
    Create a test agent package.
    """
    package = AgentPackageModel(
        package_id="test-agent",
        name="Test Agent",
        description="A test agent package",
        category="testing",
        version="1.0.0",
        config={
            "engine": "crewai",
            "tools": ["test_tool"],
            "features": ["test_feature"]
        },
        pricing={
            "per_task": 1.0,
            "per_hour": 10.0,
            "monthly": 100.0
        }
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)
    return package


@pytest.fixture
def auth_headers() -> dict:
    """
    Create authentication headers for API requests.
    """
    return {
        "X-API-Key": "test-api-key-12345",
        "Content-Type": "application/json"
    }

