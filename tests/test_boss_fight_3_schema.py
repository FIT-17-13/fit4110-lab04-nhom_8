"""
Test Suite: Boss Fight 3 – Schema Validation Enforcement
Purpose: Verify OpenAPI schema validation and rejection of malformed payloads
Test Category: Security (Data Integrity) (MANDATORY)

Objective: Ensure invalid schema is REJECTED with 422 error + detailed validation messages
"""

import pytest
import requests


BASE_URL = "http://localhost:8000"
VALID_AUTH_HEADER = "Bearer local-dev-token"


class TestSchemaValidationEnforcement:
    """
    BF3: OpenAPI schema validation enforcement
    Expected behavior:
    - Missing required fields: 422 Unprocessable Entity
    - Invalid field types: 422 Unprocessable Entity
    - Invalid enum values: 422 Unprocessable Entity
    - device_id < 3 chars: 422 Unprocessable Entity
    - All errors include ProblemDetails + field location
    """
    
    def test_bf3_missing_required_field_device_id(self):
        """
        BF3.1: Missing required field 'device_id' should return 422.
        Attack: Omit device_id from payload
        Expected: 422 Unprocessable Entity
        Error detail: Should identify 'device_id' as the missing field
        """
        payload = {
            # device_id: MISSING
            "metric": "temperature",
            "value": 25.0,
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
        assert "device_id" in data["detail"].lower()
    
    
    def test_bf3_missing_required_field_metric(self):
        """
        BF3.2: Missing required field 'metric' should return 422.
        Attack: Omit metric from payload
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            # metric: MISSING
            "value": 25.0,
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
            f"Expected 422, got {response.status_code}"
        
        data = response.json()
        assert "metric" in data["detail"].lower()
    
    
    def test_bf3_missing_required_field_value(self):
        """
        BF3.3: Missing required field 'value' should return 422.
        Attack: Omit value from payload
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            # value: MISSING
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
        assert "value" in response.json()["detail"].lower()
    
    
    def test_bf3_missing_required_field_timestamp(self):
        """
        BF3.4: Missing required field 'timestamp' should return 422.
        Attack: Omit timestamp from payload
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            # timestamp: MISSING
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": VALID_AUTH_HEADER},
            timeout=5
        )
        
        assert response.status_code == 422
        assert "timestamp" in response.json()["detail"].lower()
    
    
    def test_bf3_invalid_enum_metric_value(self):
        """
        BF3.5: Invalid enum value for 'metric' should return 422.
        Attack: metric = "invalid_metric" (not in enum)
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "invalid_metric_type",  # Not in enum
            "value": 25.0,
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
            f"Expected 422 for invalid enum, got {response.status_code}"
    
    
    def test_bf3_invalid_field_type_value(self):
        """
        BF3.6: Invalid type for 'value' (string instead of float) should return 422.
        Attack: value = "not_a_number"
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": "not_a_number",  # Should be float
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
            f"Expected 422 for invalid type, got {response.status_code}"
    
    
    def test_bf3_device_id_too_short(self):
        """
        BF3.7: device_id < 3 characters should be rejected.
        Attack: device_id = "AB" (only 2 chars, need ≥3)
        Expected: 422 Unprocessable Entity
        """
        payload = {
            "device_id": "AB",  # Too short (need ≥3)
            "metric": "temperature",
            "value": 25.0,
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
            f"Expected 422 for short device_id, got {response.status_code}"
    
    
    def test_bf3_problem_details_format_compliance(self):
        """
        BF3.8: All validation errors must return RFC 7807 ProblemDetails format.
        Expected response structure:
        {
          "type": "about:blank" (or custom problem type),
          "title": "Validation error",
          "status": 422,
          "detail": "...",
          "instance": "/readings"
        }
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            # metric: MISSING (will trigger 422)
            "value": 25.0,
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
        data = response.json()
        
        # Verify RFC 7807 ProblemDetails compliance
        required_fields = ["type", "title", "status", "detail", "instance"]
        for field in required_fields:
            assert field in data, \
                f"ProblemDetails missing required field: {field}"
        
        assert data["type"] in ["about:blank", "https://smart-campus.local/problems/validation-error"]
        assert data["title"] == "Validation error"
        assert data["status"] == 422
        assert data["instance"] == "/readings"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
