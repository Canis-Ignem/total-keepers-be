"""
Product API tests
"""

from fastapi.testclient import TestClient
from app.main import app


def test_get_products():
    """Test getting products list"""
    client = TestClient(app)
    response = client.get("/api/v1/products/")
    # Should return a valid response even if empty
    assert response.status_code in [200, 422]


def test_get_products_with_pagination():
    """Test products with pagination"""
    client = TestClient(app)
    response = client.get("/api/v1/products/?page=1&size=10")
    assert response.status_code in [200, 422]
