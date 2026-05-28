"""
Test Suite: Functional Happy Path Tests
Purpose: Verify correct behavior for valid sensor readings
Test Category: Functional
"""

import pytest
import requests
from datetime import datetime, timezone


BASE_URL = "http://localhost:8000"
VALID_AUTH_HEADER = "Bearer local-dev-token"


def test_create_valid_temperature_reading():
    """
    TC1: POST /readings with valid temperature reading should return 201.
    Boundary: -40 to 80°C (inclusive)
    Valid value: 31.5°C (within bounds)
    """
    payload = {
        "device_id": "ESP32-LAB-A01",
        "metric": "temperature",
        "value": 31.5,
        "unit": "celsius",
        "timestamp": "2026-05-28T10:00:00+07:00"
    }
    
    response = requests.post(
        f"{BASE_URL}/readings",
        json=payload,
        headers={"Authorization": VALID_AUTH_HEADER},
        timeout=5
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert data["device_id"] == "ESP32-LAB-A01"
    assert data["metric"] == "temperature"
    assert data["accepted"] is True
    assert "reading_id" in data
    assert "created_at" in data


def test_create_reading_with_valid_boundary_values():
    """
    TC2: Valid boundary values (-40.0, 80.0) should be accepted.
    These are edge cases that should pass validation.
    """
    test_values = [
        ("Lower bound", -40.0),
        ("Upper bound", 80.0),
        ("Mid-range", 20.0),
    ]
    
    for test_name, value in test_values:
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": value,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 201, \
            f"{test_name}: Expected 201, got {response.status_code}: {response.text}"
        assert response.json()["accepted"] is True, \
            f"{test_name}: Reading should be accepted"


def test_create_reading_different_metrics():
    """
    TC3: Service should accept different metric types (temperature, humidity, motion, smoke).
    """
    metrics = ["temperature", "humidity", "motion", "smoke"]
    
    for metric in metrics:
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": metric,
            "value": 50.0,
            "unit": "percent" if metric == "humidity" else "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 201, \
            f"Metric '{metric}': Expected 201, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
