"""
Pytest configuration and fixtures for test suite
"""

import pytest
import requests
from datetime import datetime


@pytest.fixture(scope="session", autouse=True)
def check_container_running():
    """
    Verify container is running before running tests.
    Skip all tests if container is not accessible.
    """
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        pytest.skip("Container not running. Start with: docker run -p 8000:8000 fit4110/iot-ingestion:lab04")


def pytest_configure(config):
    """Configure test output"""
    config.addinivalue_line(
        "markers", "skip(reason): skip test with provided reason"
    )
    config.addinivalue_line(
        "markers", "integration: end-to-end integration tests"
    )
    config.addinivalue_line(
        "markers", "security: security-related tests"
    )


# Test result summary
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print custom summary after tests complete"""
    terminalreporter.write_sep("=", "FIT4110 Lab 04 Test Summary", bold=True)
    terminalreporter.write(f"Timestamp: {datetime.now().isoformat()}\n")
