"""
Test Suite: Health Checks
Purpose: Verify /health endpoint is public and returns correct status
Test Category: Functional
"""

import pytest
import requests


BASE_URL = "http://localhost:8000"


def test_health_endpoint_is_public():
    """
    TC1: /health endpoint should be accessible without authentication.
    Expected: 200 OK + HealthResponse
    """
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["service"] == "iot-ingestion"
    assert "version" in data


def test_health_response_format():
    """
    TC2: /health response must include required fields.
    Expected: status, service, version fields present
    """
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    required_fields = ["status", "service", "version"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
        assert isinstance(data[field], str), f"Field {field} should be string, got {type(data[field])}"


@pytest.mark.skip(reason="Docker container may not be running; uncomment for docker-compose env")
def test_health_endpoint_during_container_startup():
    """
    TC3: /health should respond within timeout during container startup phase.
    This tests the HEALTHCHECK capability.
    Expected: Response time < 5 seconds
    """
    import time
    start = time.time()
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 5, f"Health check took {duration}s, expected < 5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
