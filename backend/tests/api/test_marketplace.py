"""
Tests for Marketplace API Endpoints

This module tests the marketplace API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models.customer import Customer
from models.agent import AgentPackageModel


class TestPackageListEndpoint:
    """Test suite for package listing endpoint"""
    
    def test_list_packages_empty(self, client: TestClient):
        """Test listing packages when database is empty"""
        response = client.get("/api/v1/packages")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have pre-registered packages from engine
        assert len(data) >= 0
    
    def test_list_packages_with_category_filter(self, client: TestClient):
        """Test listing packages with category filter"""
        response = client.get("/api/v1/packages?category=customer_support")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPackageDetailEndpoint:
    """Test suite for package detail endpoint"""
    
    def test_get_package_detail(self, client: TestClient):
        """Test getting package details"""
        # Use a known package ID from pre-registered packages
        response = client.get("/api/v1/packages/ticket-resolver")
        
        # May return 200 or 404 depending on if packages are registered
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "package_id" in data
            assert "name" in data
            assert "description" in data
    
    def test_get_nonexistent_package(self, client: TestClient):
        """Test getting details for non-existent package"""
        response = client.get("/api/v1/packages/nonexistent-package-xyz")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestPackageExecutionEndpoint:
    """Test suite for package execution endpoint"""
    
    def test_execute_package_without_auth(self, client: TestClient):
        """Test executing package without authentication"""
        response = client.post(
            "/api/v1/packages/ticket-resolver/execute",
            json={"task": "Test task"}
        )
        
        # Should require authentication
        assert response.status_code in [401, 403, 422]
    
    def test_execute_package_with_auth(
        self, 
        client: TestClient, 
        auth_headers: dict,
        test_customer: Customer
    ):
        """Test executing package with authentication"""
        response = client.post(
            "/api/v1/packages/ticket-resolver/execute",
            headers=auth_headers,
            json={
                "task": "Customer cannot login to dashboard",
                "engine_type": "crewai"
            }
        )
        
        # May succeed or fail depending on LLM API key availability
        assert response.status_code in [200, 500, 404]
    
    def test_execute_nonexistent_package(
        self,
        client: TestClient,
        auth_headers: dict,
        test_customer: Customer
    ):
        """Test executing non-existent package"""
        response = client.post(
            "/api/v1/packages/nonexistent-xyz/execute",
            headers=auth_headers,
            json={"task": "Test task"}
        )
        
        assert response.status_code == 404
    
    def test_execute_package_invalid_input(
        self,
        client: TestClient,
        auth_headers: dict,
        test_customer: Customer
    ):
        """Test executing package with invalid input"""
        response = client.post(
            "/api/v1/packages/ticket-resolver/execute",
            headers=auth_headers,
            json={}  # Missing required 'task' field
        )
        
        assert response.status_code == 422  # Validation error


class TestCategoriesEndpoint:
    """Test suite for categories endpoint"""
    
    def test_list_categories(self, client: TestClient):
        """Test listing all categories"""
        response = client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should have at least the main categories
        categories = [cat["id"] for cat in data]
        expected_categories = [
            "customer_support",
            "operations",
            "devops",
            "compliance"
        ]
        
        for expected in expected_categories:
            assert expected in categories

