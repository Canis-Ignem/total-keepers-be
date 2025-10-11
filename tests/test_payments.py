"""
Payment API tests
"""

from fastapi.testclient import TestClient
from app.main import app


def test_create_redsys_payment_endpoint_exists():
    """Test that create redsys payment endpoint exists"""
    client = TestClient(app)
    # Test with minimal data to see if endpoint exists
    response = client.post("/api/v1/payments/create-redsys-payment", json={})
    # Should return 422 (validation error) not 404 (endpoint not found)
    assert response.status_code in [422, 400, 500]


def test_redsys_callback_endpoint_exists():
    """Test that redsys callback endpoint exists"""
    client = TestClient(app)
    response = client.post("/api/v1/payments/redsys-callback", json={})
    # Should return 422 (validation error) not 404 (endpoint not found)
    assert response.status_code in [422, 400, 500]


def test_payment_status_endpoint_exists():
    """Test that payment status endpoint exists"""
    client = TestClient(app)
    response = client.get("/api/v1/payments/payment-status/test-payment-id")
    # Should return valid HTTP response (may be 404 if payment not found, but endpoint exists)
    assert response.status_code in [200, 404, 500]


def test_mock_redsys_callback_endpoint_exists():
    """Test that mock redsys callback endpoint exists (for testing)"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/payments/mock-redsys-callback", params={"ds_order": "test-order"}
    )
    # Should return valid HTTP response
    assert response.status_code in [200, 400, 422, 500]


def test_create_redsys_payment_with_invalid_data():
    """Test create payment with invalid request data"""
    client = TestClient(app)
    invalid_data = {
        "order_id": "",  # Invalid empty order_id
        "amount": -10,  # Invalid negative amount
    }
    response = client.post("/api/v1/payments/create-redsys-payment", json=invalid_data)
    # Should return validation error
    assert response.status_code in [422, 400]


def test_payment_status_with_nonexistent_id():
    """Test getting payment status for non-existent payment"""
    client = TestClient(app)
    response = client.get("/api/v1/payments/payment-status/nonexistent-payment-id")
    # Should return 404 or 500 depending on implementation
    assert response.status_code in [404, 500]
