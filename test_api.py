#!/usr/bin/env python3
"""Script to test order creation API endpoint directly."""

import requests
import json

def test_order_creation():
    """Test the order creation endpoint directly."""
    
    # Test order data
    order_data = {
        "items": [
            {
                "product_id": "gekko_light_ligero",
                "product_name": "GEKKO LIGHT PRO - BLACK",
                "product_price": 59.50,
                "quantity": 1,
                "selected_size": "7.5"
            }
        ],
        "shipping_address": {
            "first_name": "Test",
            "last_name": "User", 
            "email": "test@example.com",
            "phone": "123456789",
            "address_line_1": "Test Address 123",
            "city": "Test City",
            "state": "Test State", 
            "postal_code": "12345",
            "country": "Spain"
        }
    }
    
    try:
        print("🚀 Testing Order Creation API...")
        print("=" * 50)
        
        # Make request to order creation endpoint
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/orders/create",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            print(f"✅ SUCCESS!")
            print(f"Order ID: {response_data.get('order_id')}")
            print(f"Total Amount: {response_data.get('total_amount')}")
            print(f"Status: {response_data.get('status')}")
        else:
            print(f"❌ ERROR {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Is the backend server running on port 8000?")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error - Request took too long")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_order_creation()