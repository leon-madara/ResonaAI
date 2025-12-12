"""
Helper functions for testing
"""

from typing import Dict, Any
import json


def create_auth_headers(token: str) -> Dict[str, str]:
    """Create authorization headers with JWT token"""
    return {"Authorization": f"Bearer {token}"}


def assert_error_response(response, expected_status: int, expected_error: str = None):
    """Assert error response structure"""
    assert response.status_code == expected_status
    data = response.json()
    assert "error" in data or "detail" in data
    if expected_error:
        error_msg = data.get("error") or data.get("detail")
        assert expected_error.lower() in error_msg.lower()


def assert_success_response(response, expected_status: int = 200):
    """Assert success response structure"""
    assert response.status_code == expected_status
    data = response.json()
    return data


def create_test_user_data(email: str = "test@example.com", password: str = "testpass123") -> Dict[str, Any]:
    """Create test user registration data"""
    return {
        "email": email,
        "password": password,
        "consent_version": "1.0",
        "is_anonymous": False
    }


def create_test_login_data(email: str = "test@example.com", password: str = "testpass123") -> Dict[str, Any]:
    """Create test login data"""
    return {
        "email": email,
        "password": password
    }

