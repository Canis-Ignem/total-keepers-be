#!/usr/bin/env python3
"""Script to test order creation and verify OrderItem records are created."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from decimal import Decimal

from app.services.order_service import get_order_service
from app.schemas.order import CreateOrderRequest, OrderItemRequest, ShippingAddressRequest

def main():
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No DATABASE_URL found")
        return
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("🧪 Testing Order Creation...")
        print("=" * 50)
        
        # Create a test order for gekko_light_ligero size 7.5
        test_order_request = CreateOrderRequest(
            items=[
                OrderItemRequest(
                    product_id="gekko_light_ligero",
                    product_name="GEKKO LIGHT PRO - BLACK",
                    product_price=Decimal("59.50"),  # Using discount price
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
        
        # Create order using the service
        order_service = get_order_service(db)
        order_response = order_service.validate_and_create_order(test_order_request)
        
        print(f"✅ Order created successfully!")
        print(f"Order ID: {order_response.order_id}")
        print(f"Total Amount: {order_response.total_amount}")
        print(f"Status: {order_response.status}")
        
        # Check if order_items were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT oi.order_id, oi.product_id, oi.size, oi.quantity,
                       oi.unit_price, oi.total_price
                FROM order_items oi
                WHERE oi.order_id = :order_id
            """), {"order_id": order_response.order_id})
            
            order_items = result.fetchall()
            print(f"\n📦 Order Items Created:")
            print("=" * 50)
            if order_items:
                for row in order_items:
                    order_id, product_id, size, quantity, unit_price, total_price = row
                    print(f"Product: {product_id}")
                    print(f"Size: {size}")
                    print(f"Quantity: {quantity}")
                    print(f"Unit Price: €{unit_price}")
                    print(f"Total Price: €{total_price}")
            else:
                print("❌ No order items found - BUG STILL EXISTS!")
                
            # Check current stock after order creation
            result = conn.execute(text("""
                SELECT ps.size, ps.stock_quantity, ps.is_available
                FROM product_sizes ps
                WHERE ps.product_id = 'gekko_light_ligero'
                ORDER BY ps.size
            """))
            
            stock_data = result.fetchall()
            print(f"\n🧤 Current Stock (after order creation):")
            print("=" * 50)
            for row in stock_data:
                size, stock, available = row
                status = "✅ Available" if available else "❌ Out of Stock"
                if size == "7.5":
                    print(f"Size {size:>4}: Stock={stock:>2} | {status} ⭐ TEST TARGET")
                else:
                    print(f"Size {size:>4}: Stock={stock:>2} | {status}")
        
        db.close()
        print(f"\n📝 Note: Stock will only be reduced when payment is completed, not when order is created.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()