"""
Pytest configuration and shared fixtures for backend API tests.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing."""
    # Mock JWT token for testing
    token = "test_token_12345"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
    }


@pytest.fixture
def sample_notification():
    """Sample notification data for testing."""
    return {
        "title": "Test Notification",
        "body": "This is a test notification",
        "sender": "test@sender.com",
        "priority": "URGENT",
        "timestamp": "2024-12-06T12:00:00Z",
    }


@pytest.fixture
def sample_device():
    """Sample IoT device data for testing."""
    return {
        "device_id": "esp32_test_001",
        "device_type": "ESP32",
        "location": "home",
        "sensors": ["temperature", "humidity", "motion"],
    }


@pytest.fixture
def sample_sensor_data():
    """Sample sensor reading data for testing."""
    return {
        "device_id": "esp32_test_001",
        "temperature": 22.5,
        "humidity": 45.0,
        "light_level": 300,
        "noise_level": 35,
        "motion_detected": False,
        "timestamp": "2024-12-06T12:00:00Z",
    }
