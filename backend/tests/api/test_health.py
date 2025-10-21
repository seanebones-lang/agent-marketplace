"""
Tests for Health Check Endpoints

This module tests the health check API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test suite for health check endpoints"""
    
    def test_health_check(self, client: TestClient):
        """Test main health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
    
    def test_readiness_probe(self, client: TestClient):
        """Test Kubernetes readiness probe"""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_liveness_probe(self, client: TestClient):
        """Test Kubernetes liveness probe"""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestRootEndpoint:
    """Test suite for root endpoint"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Agent Marketplace" in data["message"]
        assert "version" in data

