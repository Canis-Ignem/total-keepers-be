"""
Product API Testing Examples
Run these examples to test the product CRUD operations
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_create_product():
    """Test creating a new product"""
    product_data = {
        "id": "guante_test_api",
        "name": "Test API Goalkeeper Gloves",
        "description": "Test gloves created via API",
        "price": 59.99,
        "img": "/test/gloves.svg",
        "category": "GOALKEEPER_GLOVES",
        "tag": "TEST",
        "is_active": True,
        "sizes": [
            {"size": "7", "stock_quantity": 5, "is_available": True},
            {"size": "8", "stock_quantity": 10, "is_available": True},
            {"size": "9", "stock_quantity": 3, "is_available": True},
        ],
        "tag_names": ["test", "api", "ligero"],
    }

    response = requests.post(f"{BASE_URL}/products", json=product_data)
    print(f"Create Product - Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Created product: {response.json()['name']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_get_products():
    """Test getting paginated products"""
    params = {
        "page": 1,
        "size": 10,
        "category": "GOALKEEPER_GLOVES",
        "in_stock_only": True,
    }

    response = requests.get(f"{BASE_URL}/products", params=params)
    print(f"Get Products - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(
            f"Found {data['total']} products, showing page {data['page']} of {data['pages']}"
        )
        for product in data["products"]:
            print(
                f"- {product['name']} (€{product['price']}) - Stock: {product['total_stock']}"
            )
    else:
        print(f"Error: {response.text}")
    return response


def test_get_product_by_id(product_id: str):
    """Test getting a specific product"""
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print(f"Get Product {product_id} - Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Product: {product['name']}")
        print(f"Available sizes: {product['available_sizes']}")
        print(f"Total stock: {product['total_stock']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_update_product(product_id: str):
    """Test updating a product"""
    update_data = {
        "name": "Updated Test Gloves",
        "price": 69.99,
        "description": "Updated description via API",
    }

    response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data)
    print(f"Update Product {product_id} - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Updated product: {response.json()['name']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_update_stock(product_id: str, size: str, quantity: int):
    """Test updating stock for a specific size"""
    params = {"size": size, "quantity": quantity}

    response = requests.patch(f"{BASE_URL}/products/{product_id}/stock", params=params)
    print(f"Update Stock - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Updated stock: {response.json()['message']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_search_products(query: str):
    """Test searching products"""
    params = {"q": query, "page": 1, "size": 5}

    response = requests.get(f"{BASE_URL}/products/search", params=params)
    print(f"Search Products '{query}' - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total']} products matching '{query}'")
        for product in data["products"]:
            print(f"- {product['name']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_create_tag():
    """Test creating a tag"""
    tag_data = {"name": "test-api", "description": "Tag created via API testing"}

    response = requests.post(f"{BASE_URL}/tags", json=tag_data)
    print(f"Create Tag - Status: {response.status_code}")
    if response.status_code == 201:
        print(f"Created tag: {response.json()['name']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_get_tags():
    """Test getting all tags"""
    response = requests.get(f"{BASE_URL}/tags")
    print(f"Get Tags - Status: {response.status_code}")
    if response.status_code == 200:
        tags = response.json()
        print(f"Available tags: {[tag['name'] for tag in tags]}")
    else:
        print(f"Error: {response.text}")
    return response


def test_delete_product(product_id: str):
    """Test soft deleting a product"""
    response = requests.delete(f"{BASE_URL}/products/{product_id}")
    print(f"Delete Product {product_id} - Status: {response.status_code}")
    if response.status_code == 204:
        print(f"Product {product_id} deleted successfully")
    else:
        print(f"Error: {response.text}")
    return response


def test_create_payment():
    """Test creating a payment (mock implementation)"""
    payment_data = {
        "order_id": "test_order_123",
        "amount": 59.99,
        "user_id": "test_user",
    }

    response = requests.post(f"{BASE_URL}/create-payment", params=payment_data)
    print(f"Create Payment - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Payment created: {data['message']}")
        print(f"Order ID: {data['order_id']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_payment_status(order_id: str):
    """Test getting payment status"""
    response = requests.get(f"{BASE_URL}/payment-status/{order_id}")
    print(f"Payment Status {order_id} - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Order Status: {data['order_status']}")
        print(f"Payment Status: {data['payment_status']}")
        print(f"Amount: €{data['amount']}")
    else:
        print(f"Error: {response.text}")
    return response


def test_payment_response(order_id: str, status: str = "success"):
    """Test payment response processing"""
    response_data = {"order_id": order_id, "status": status}

    response = requests.post(f"{BASE_URL}/payment-response", data=response_data)
    print(f"Payment Response - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Payment processed: {data['message']}")
    else:
        print(f"Error: {response.text}")
    return response


if __name__ == "__main__":
    print("🧪 Testing Product API Endpoints")
    print("=" * 50)

    # Test sequence
    try:
        print("\n1. Getting existing products...")
        test_get_products()

        print("\n2. Creating a test product...")
        test_create_product()

        print("\n3. Getting the test product...")
        test_get_product_by_id("guante_test_api")

        print("\n4. Updating the test product...")
        test_update_product("guante_test_api")

        print("\n5. Updating stock...")
        test_update_stock("guante_test_api", "8", 15)

        print("\n6. Searching products...")
        test_search_products("test")

        print("\n7. Testing tags...")
        test_create_tag()
        test_get_tags()

        print("\n8. Testing payments (mock implementation)...")
        test_create_payment()
        test_payment_status("test_order_123")
        test_payment_response("test_order_123", "success")

        print("\n9. Cleaning up - deleting test product...")
        test_delete_product("guante_test_api")

        print("\n✅ API testing completed!")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to API. Make sure the server is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
