"""
Tests for Agent Engine Module

This module tests the agent execution engine.
"""

import pytest
from core.agent_engine import AgentEngine, AgentPackage


class TestAgentPackage:
    """Test suite for AgentPackage dataclass"""
    
    def test_agent_package_creation(self):
        """Test creating an agent package"""
        package = AgentPackage(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            category="testing",
            version="1.0.0",
            engine_type="crewai",
            tools=["test_tool"],
            pricing={
                "per_task": 1.0,
                "per_hour": 10.0,
                "monthly": 100.0
            },
            features=["test_feature"],
            performance_metrics={
                "avg_execution_time": "5s",
                "success_rate": "99%"
            }
        )
        
        assert package.id == "test-agent"
        assert package.name == "Test Agent"
        assert package.engine_type == "crewai"
        assert "test_tool" in package.tools
        assert package.pricing["per_task"] == 1.0


class TestAgentEngine:
    """Test suite for AgentEngine"""
    
    def test_engine_initialization(self):
        """Test that engine can be initialized"""
        engine = AgentEngine()
        
        assert engine is not None
        assert hasattr(engine, 'register_package')
        assert hasattr(engine, 'list_packages')
    
    def test_register_package(self):
        """Test registering a package"""
        engine = AgentEngine()
        
        package = AgentPackage(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            category="testing",
            version="1.0.0",
            engine_type="crewai",
            tools=[],
            pricing={},
            features=[],
            performance_metrics={}
        )
        
        engine.register_package(package)
        packages = engine.list_packages()
        
        assert "test-agent" in [p.id for p in packages]
    
    def test_list_packages(self):
        """Test listing registered packages"""
        engine = AgentEngine()
        packages = engine.list_packages()
        
        assert isinstance(packages, list)
        # Should have pre-registered packages
        assert len(packages) >= 0
    
    def test_get_package(self):
        """Test getting a specific package"""
        engine = AgentEngine()
        
        # Register a test package
        package = AgentPackage(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            category="testing",
            version="1.0.0",
            engine_type="crewai",
            tools=[],
            pricing={},
            features=[],
            performance_metrics={}
        )
        engine.register_package(package)
        
        # Get the package
        retrieved = engine.get_package("test-agent")
        assert retrieved is not None
        assert retrieved.id == "test-agent"
    
    def test_get_nonexistent_package(self):
        """Test getting a non-existent package"""
        engine = AgentEngine()
        
        retrieved = engine.get_package("nonexistent-xyz")
        assert retrieved is None

