"""
Orders API tests
"""

from fastapi.testclient import TestClient
from app.main import app


def test_get_orders_unauthenticated():
    """Test getting orders without authentication"""
    client = TestClient(app)
    response = client.get("/api/v1/orders/")
    # Should return valid HTTP response
    assert response.status_code in [200]


def test_create_order_unauthenticated():
    """Test creating order without authentication"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": "test-product", "size": "M", "quantity": 1}]},
    )
    # Should return valid HTTP response (405 if method not allowed)
    assert response.status_code in [405]
