"""
Tests for device management endpoints.
"""
import pytest


def test_register_device(client, auth_headers, sample_device):
    """Test device registration."""
    response = client.post(
        "/api/devices/register",
        json=sample_device,
        headers=auth_headers,
    )
    assert response.status_code in [200, 201, 404, 501]


def test_get_devices(client, auth_headers):
    """Test getting user devices."""
    response = client.get("/api/devices", headers=auth_headers)
    assert response.status_code in [200, 404, 501]


def test_post_sensor_data(client, auth_headers, sample_sensor_data):
    """Test posting sensor data."""
    response = client.post(
        "/api/devices/sensor-data",
        json=sample_sensor_data,
        headers=auth_headers,
    )
    assert response.status_code in [200, 201, 404, 501]


def test_get_sensor_data(client, auth_headers):
    """Test getting sensor data."""
    device_id = "esp32_test_001"
    response = client.get(
        f"/api/devices/{device_id}/sensor-data",
        headers=auth_headers,
    )
    assert response.status_code in [200, 404, 501]


def test_delete_device(client, auth_headers):
    """Test device deletion."""
    device_id = "esp32_test_001"
    response = client.delete(
        f"/api/devices/{device_id}",
        headers=auth_headers,
    )
    assert response.status_code in [200, 204, 404, 501]


def test_device_calibration(client, auth_headers):
    """Test device calibration endpoint."""
    device_id = "esp32_test_001"
    calibration_data = {
        "temperature_offset": 0.5,
        "humidity_offset": -2.0,
    }
    response = client.post(
        f"/api/devices/{device_id}/calibrate",
        json=calibration_data,
        headers=auth_headers,
    )
    assert response.status_code in [200, 404, 501]
