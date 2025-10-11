#!/usr/bin/env python3
"""Script to check payment enum values and all orders."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No DATABASE_URL found")
        return
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check what payment_status enum values exist
            result = conn.execute(text("""
                SELECT unnest(enum_range(NULL::paymentstatus)) AS payment_status_value
            """))
            
            enum_values = [row[0] for row in result.fetchall()]
            print("💳 Available payment_status enum values:")
            for value in enum_values:
                print(f"  - {value}")
            
            # Check all orders in the database
            result = conn.execute(text("""
                SELECT o.id, o.status, o.payment_status, o.created_at, o.updated_at,
                       COUNT(oi.id) as item_count
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY o.id, o.status, o.payment_status, o.created_at, o.updated_at
                ORDER BY o.created_at DESC
                LIMIT 10
            """))
            
            orders = result.fetchall()
            print(f"\n📦 All Recent Orders (Last 10):")
            print("=" * 100)
            if orders:
                for row in orders:
                    order_id, status, payment_status, created, updated, item_count = row
                    print(f"Order {order_id}: Status={status} | Payment={payment_status} | Items={item_count}")
                    print(f"  Created: {created} | Updated: {updated}")
                    print()
            else:
                print("No orders found in database")
                
            # Check order_items for gekko_light_ligero specifically  
            result = conn.execute(text("""
                SELECT oi.order_id, oi.product_id, oi.size, oi.quantity,
                       o.status, o.payment_status, o.created_at
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE oi.product_id = :product_id
                ORDER BY o.created_at DESC
            """), {"product_id": "gekko_light_ligero"})
            
            gekko_orders = result.fetchall()
            if gekko_orders:
                print(f"\n🧤 Orders specifically for GEKKO LIGHT PRO:")
                print("=" * 80)
                for row in gekko_orders:
                    order_id, product_id, size, quantity, status, payment_status, created = row
                    print(f"Order {order_id}: Size {size} x{quantity}")
                    print(f"  Status: {status} | Payment: {payment_status} | Created: {created}")
            else:
                print(f"\n🧤 No orders found for GEKKO LIGHT PRO")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()