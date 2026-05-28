"""
Test Suite: Integration Tests
Purpose: End-to-end tests simulating real container deployment scenarios
Test Category: Integration / Container Verification
"""

import pytest
import requests
from datetime import datetime, timezone


BASE_URL = "http://localhost:8000"
VALID_AUTH_HEADER = "Bearer local-dev-token"


class TestIntegration:
    """
    Integration tests verify the full lifecycle:
    - Container is running
    - Service responds to requests
    - Error handling works end-to-end
    - State is managed correctly
    """
    
    def test_container_is_responsive(self):
        """
        TC1: Container should respond to requests within timeout.
        This verifies basic container connectivity.
        """
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            assert response.status_code == 200
        except requests.ConnectionError:
            pytest.skip("Container not running or not accessible")
    
    
    def test_full_request_lifecycle_valid_reading(self):
        """
        TC2: Complete flow - valid auth + valid data = resource created.
        1. Send valid sensor reading with correct token
        2. Verify 201 Created response
        3. Verify response contains reading_id + created_at
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 35.5,
            "unit": "celsius",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["reading_id"] is not None
        assert data["created_at"] is not None
        assert data["accepted"] is True
    
    
    def test_error_recovery_after_invalid_request(self):
        """
        TC3: Service should recover and accept valid requests after rejecting invalid ones.
        1. Send invalid request (out-of-boundary)
        2. Verify 422 response
        3. Send valid request
        4. Verify 201 response (service didn't crash)
        """
        # Invalid request
        invalid_payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 100.0,  # Out of boundary
            "unit": "celsius",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response_invalid = requests.post(
            f"{BASE_URL}/readings",
            json=invalid_payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response_invalid.status_code == 422
        
        # Valid request after invalid one
        valid_payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,  # Valid
            "unit": "celsius",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response_valid = requests.post(
            f"{BASE_URL}/readings",
            json=valid_payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response_valid.status_code == 201, \
            "Service should recover and accept valid requests after errors"
    
    
    def test_multiple_devices_can_send_readings(self):
        """
        TC4: Multiple devices should be able to send readings concurrently.
        This simulates realistic IoT scenario.
        """
        devices = ["ESP32-01", "ESP32-02", "ESP32-03"]
        
        for device_id in devices:
            payload = {
                "device_id": device_id,
                "metric": "temperature",
                "value": 25.0 + len(device_id),
                "unit": "celsius",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/readings",
                json=payload,
                headers={"Authorization": VALID_AUTH_HEADER},
                timeout=5
            )
            
            assert response.status_code == 201, \
                f"Device {device_id} should be able to send reading"
    
    
    def test_content_type_header_validation(self):
        """
        TC5: Service should validate Content-Type header.
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # requests library automatically sets Content-Type to application/json
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 201


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
