#!/usr/bin/env python3
"""Direct test of order creation service without API."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from decimal import Decimal

# Import order service components
from app.services.order_service import get_order_service
from app.schemas.order import CreateOrderRequest, OrderItemRequest, ShippingAddressRequest

def test_order_service():
    """Test the order service directly."""
    
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No DATABASE_URL found")
        return
    
    try:
        # Create database session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("🧪 Testing Order Service Directly...")
        print("=" * 50)
        
        # Create order request exactly like frontend would send
        order_request = CreateOrderRequest(
            items=[
                OrderItemRequest(
                    product_id="gekko_light_ligero",
                    product_name="GEKKO LIGHT PRO - BLACK", 
                    product_price=Decimal("59.50"),
                    quantity=1,
                    selected_size="7.5"
                )
            ],
            shipping_address=ShippingAddressRequest(
                first_name="Test",
                last_name="User",
                email="test@example.com", 
                phone="123456789",
                address_line_1="Test Address 123",
                city="Test City",
                state="Test State",
                postal_code="12345",
                country="Spain"
            )
        )
        
        print("📋 Order Request:")
        print(f"  Product: {order_request.items[0].product_id}")
        print(f"  Size: {order_request.items[0].selected_size}")
        print(f"  Quantity: {order_request.items[0].quantity}")
        print(f"  Price: €{order_request.items[0].product_price}")
        
        # Test the order service
        order_service = get_order_service(db)
        order_response = order_service.validate_and_create_order(order_request)
        
        print(f"\n✅ Order Created Successfully!")
        print(f"  Order ID: {order_response.order_id}")
        print(f"  Status: {order_response.status}")
        print(f"  Total: €{order_response.total_amount}")
        print(f"  Subtotal: €{order_response.subtotal}")
        print(f"  Shipping: €{order_response.shipping_amount}")
        print(f"  Discount: €{order_response.discount_amount}")
        
        # Verify order items were created
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM order_items WHERE order_id = :order_id
            """), {"order_id": order_response.order_id})
            
            item_count = result.scalar()
            print(f"\n📦 Order Items Created: {item_count}")
            
            if item_count > 0:
                print("✅ OrderItem records were created successfully!")
            else:
                print("❌ No OrderItem records found - bug still exists!")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_order_service()
    if success:
        print("\n🎉 Order service test completed successfully!")
    else:
        print("\n💥 Order service test failed!")