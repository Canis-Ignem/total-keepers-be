"""
Authentication API tests
"""

from fastapi.testclient import TestClient
from app.main import app


def test_register_endpoint_exists():
    """Test that register endpoint exists"""
    client = TestClient(app)
    # Test with minimal data to see if endpoint exists
    response = client.post("/api/v1/auth/register", json={})
    # Should return 422 (validation error) not 404 (endpoint not found)
    assert response.status_code in [422, 400, 500]


def test_login_endpoint_exists():
    """Test that login endpoint exists"""
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={})
    # Should return 422 (validation error) not 404 (endpoint not found)
    assert response.status_code in [422, 400, 500]
