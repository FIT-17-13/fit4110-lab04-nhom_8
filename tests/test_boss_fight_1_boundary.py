"""
Test Suite: Boss Fight 1 – Boundary Violation Detection
Purpose: Verify temperature boundary validation (-40 to 80°C)
Test Category: Security + Boundary Testing (MANDATORY)

Objective: Ensure out-of-range values are REJECTED with 422 error + log entry
"""

import pytest
import requests


BASE_URL = "http://localhost:8000"
VALID_AUTH_HEADER = "Bearer local-dev-token"


class TestBoundaryViolationDetection:
    """
    BF1: Temperature boundary enforcement (-40 to 80°C)
    Expected behavior:
    - Values in [-40, 80]: Accept (201)
    - Values < -40: Reject (422) + log error
    - Values > 80: Reject (422) + log error
    """
    
    def test_bf1_below_lower_boundary(self):
        """
        BF1.1: Value below -40 should be rejected.
        Attack: temperature = -40.1°C
        Expected: 422 Unprocessable Entity + ProblemDetails
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": -40.1,  # Below lower boundary
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 422, \
            f"Expected 422, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["title"] == "Validation error"
        assert "value" in data["detail"].lower()
        assert data["instance"] == "/readings"
    
    
    def test_bf1_above_upper_boundary(self):
        """
        BF1.2: Value above 80 should be rejected.
        Attack: temperature = 80.1°C
        Expected: 422 Unprocessable Entity + ProblemDetails
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 80.1,  # Above upper boundary
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 422, \
            f"Expected 422, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["title"] == "Validation error"
        assert "value" in data["detail"].lower()
    
    
    def test_bf1_far_below_boundary(self):
        """
        BF1.3: Extreme low value (-273.15°C = absolute zero) should be rejected.
        Attack: temperature = -273.15°C (absolute zero)
        Expected: 422 Validation Error
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": -273.15,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 422
    
    
    def test_bf1_far_above_boundary(self):
        """
        BF1.4: Extreme high value (1000°C) should be rejected.
        Attack: temperature = 1000.0°C
        Expected: 422 Validation Error
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 1000.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 422
    
    
    def test_bf1_exact_lower_boundary_accepted(self):
        """
        BF1.5: Exact lower boundary (-40.0) should be ACCEPTED.
        Expected: 201 Created
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": -40.0,  # Exact lower boundary (inclusive)
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
            f"Expected 201 for boundary value -40.0, got {response.status_code}"
        assert response.json()["accepted"] is True
    
    
    def test_bf1_exact_upper_boundary_accepted(self):
        """
        BF1.6: Exact upper boundary (80.0) should be ACCEPTED.
        Expected: 201 Created
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 80.0,  # Exact upper boundary (inclusive)
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
            f"Expected 201 for boundary value 80.0, got {response.status_code}"
        assert response.json()["accepted"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
