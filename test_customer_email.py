"""
Test script to send customer confirmation email
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import EmailService

# Fake order data
test_customer_email = "aitorpeetxe@gmail.com"
test_customer_name = "Jon Pérez"
test_order_id = "TEST-12345"

test_order_items = [
    {
        "product_name": "GOTI PRO - WHITE",
        "size": "8",
        "quantity": 1,
        "unit_price": 74.99,
        "total_price": 74.99
    },
    {
        "product_name": "GOTI TRAINING - BLACK",
        "size": "9",
        "quantity": 2,
        "unit_price": 49.99,
        "total_price": 99.98
    }
]

test_shipping_address = {
    "first_name": "Jon",
    "last_name": "Pérez",
    "address_line_1": "Calle Gran Vía, 45",
    "address_line_2": "3º A",
    "city": "Bilbao",
    "state": "Vizcaya",
    "postal_code": "48001",
    "country": "España",
    "phone": "+34 612 345 678"
}

print("=" * 80)
print("TESTING CUSTOMER CONFIRMATION EMAIL")
print("=" * 80)
print(f"Sending to: {test_customer_email}")
print(f"Customer name: {test_customer_name}")
print(f"Order ID: {test_order_id}")
print(f"Number of items: {len(test_order_items)}")
print("=" * 80)

# Send customer confirmation email
result = EmailService.send_customer_order_confirmation(
    customer_email=test_customer_email,
    customer_name=test_customer_name,
    order_id=test_order_id,
    order_items=test_order_items
)

print("\n" + "=" * 80)
if result:
    print("✅ EMAIL SENT SUCCESSFULLY!")
    print("   Check the logs above for Gmail/Azure status details")
else:
    print("❌ EMAIL FAILED TO SEND!")
    print("   Check the error messages above")

print("=" * 80)
