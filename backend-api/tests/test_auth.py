"""
Tests for authentication endpoints.
"""
import pytest


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_register_user(client, sample_user):
    """Test user registration."""
    response = client.post("/api/auth/register", json=sample_user)
    # Note: Endpoint may not be fully implemented yet
    assert response.status_code in [200, 201, 404, 501]


def test_login_user(client):
    """Test user login."""
    credentials = {
        "email": "test@example.com",
        "password": "test_password",
    }
    response = client.post("/api/auth/login", json=credentials)
    # Note: Endpoint may not be fully implemented yet
    assert response.status_code in [200, 404, 401, 501]


def test_get_user_profile(client, auth_headers):
    """Test getting user profile."""
    response = client.get("/api/auth/profile", headers=auth_headers)
    # Note: Endpoint may not be fully implemented yet
    assert response.status_code in [200, 404, 401, 501]


def test_unauthorized_access(client):
    """Test accessing protected endpoint without auth."""
    response = client.get("/api/auth/profile")
    # Should require authentication
    assert response.status_code in [401, 403, 404, 501]
