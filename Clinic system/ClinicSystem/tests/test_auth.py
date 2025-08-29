"""
Test authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_login_success(client: TestClient, admin_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login-json",
        json={"email": "admin@test.com", "password": "testpassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_invalid_credentials(client: TestClient, admin_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login-json",
        json={"email": "admin@test.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login-json",
        json={"email": "nonexistent@test.com", "password": "password"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user information"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "admin@test.com"
    assert data["data"]["role"] == "admin"


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


def test_refresh_token(client: TestClient, auth_headers):
    """Test token refresh"""
    response = client.post("/api/v1/auth/refresh", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
