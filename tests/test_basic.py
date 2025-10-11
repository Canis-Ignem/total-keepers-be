"""
Basic API tests for Total Keepers
"""

from fastapi.testclient import TestClient
from app.main import app


# Create client directly in each test
def test_app_health():
    """Test that the app starts up correctly"""
    client = TestClient(app)
    response = client.get("/")
    # The app might return 404 for root, but it should be a valid HTTP response
    assert response.status_code in [200, 404, 422]


def test_docs_endpoint():
    """Test that API docs are accessible"""
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint():
    """Test that OpenAPI spec is accessible"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
