"""
Test Suite: Boss Fight 2 – Authentication Validation
Purpose: Verify Bearer token authentication enforcement
Test Category: Security (Authentication/Authorization) (MANDATORY)

Objective: Ensure invalid/missing auth attempts are REJECTED with 401 error + security log
"""

import pytest
import requests


BASE_URL = "http://localhost:8000"
VALID_TOKEN = "local-dev-token"


class TestAuthenticationValidation:
    """
    BF2: Bearer token authentication enforcement
    Protected endpoint: POST /readings
    Expected behavior:
    - No auth header: Reject (401)
    - Invalid token: Reject (401)
    - Valid token: Accept request
    - /health: No auth required (public)
    """
    
    def test_bf2_missing_authorization_header(self):
        """
        BF2.1: Request without Authorization header should be rejected.
        Attack: Missing Authorization header completely
        Expected: 401 Unauthorized + ProblemDetails
        Log: Security event - "Missing Authorization header"
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            # NO Authorization header
            timeout=5
        )
        
        assert response.status_code == 401, \
            f"Expected 401, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["title"] == "Unauthorized"
        assert data["status"] == 401
        assert "Missing" in data["detail"] or "Authorization" in data["detail"]
    
    
    def test_bf2_invalid_bearer_token(self):
        """
        BF2.2: Request with invalid Bearer token should be rejected.
        Attack: Authorization: Bearer invalid-token-12345
        Expected: 401 Unauthorized + ProblemDetails
        Log: Security event - "Invalid bearer token"
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": "Bearer invalid-token-12345"},
            timeout=5
        )
        
        assert response.status_code == 401, \
            f"Expected 401, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["title"] == "Unauthorized"
        assert "Invalid" in data["detail"] or "token" in data["detail"].lower()
    
    
    def test_bf2_malformed_authorization_header(self):
        """
        BF2.3: Request with malformed Authorization header should be rejected.
        Attack: Authorization: InvalidFormat local-dev-token (missing 'Bearer')
        Expected: 401 Unauthorized
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": f"InvalidFormat {VALID_TOKEN}"},
            timeout=5
        )
        
        assert response.status_code == 401, \
            f"Expected 401 for malformed auth, got {response.status_code}"
    
    
    def test_bf2_empty_bearer_token(self):
        """
        BF2.4: Request with empty Bearer token should be rejected.
        Attack: Authorization: Bearer (empty token)
        Expected: 401 Unauthorized
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": "Bearer "},  # Empty token
            timeout=5
        )
        
        assert response.status_code == 401, \
            f"Expected 401 for empty token, got {response.status_code}"
    
    
    def test_bf2_valid_token_accepted(self):
        """
        BF2.5: Request with valid Bearer token should be ACCEPTED.
        Expected: 201 Created (request processed)
        """
        payload = {
            "device_id": "ESP32-LAB-A01",
            "metric": "temperature",
            "value": 25.0,
            "unit": "celsius",
            "timestamp": "2026-05-28T10:00:00+07:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/readings",
            json=payload,
            headers={"Authorization": f"Bearer {VALID_TOKEN}"},
            timeout=5
        )
        
        assert response.status_code == 201, \
            f"Expected 201 for valid token, got {response.status_code}: {response.text}"
        assert response.json()["accepted"] is True
    
    
    def test_bf2_health_endpoint_public_no_auth(self):
        """
        BF2.6: /health endpoint should be PUBLIC (no auth required).
        Expected: 200 OK (no 401)
        """
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}"
        # Verify it doesn't require auth
        assert response.json()["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
