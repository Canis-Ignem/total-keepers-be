#!/usr/bin/env python3
"""Script to check current stock levels in the database."""

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
            # Check current stock for gekko_light_ligero
            result = conn.execute(text("""
                SELECT ps.size, ps.stock_quantity, ps.is_available, ps.updated_at
                FROM product_sizes ps
                WHERE ps.product_id = :product_id
                ORDER BY ps.size
            """), {"product_id": "gekko_light_ligero"})
            
            stock_data = result.fetchall()
            print("🧤 GEKKO LIGHT PRO Current Stock:")
            print("=" * 50)
            for row in stock_data:
                size, stock, available, updated = row
                status = "✅ Available" if available else "❌ Out of Stock"
                print(f"Size {size:>4}: Stock={stock:>2} | {status} | Updated: {updated}")
                
            # Check recent orders for this product
            result = conn.execute(text("""
                SELECT o.id, o.status, o.payment_status, oi.size, oi.quantity, 
                       o.created_at, o.updated_at
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE oi.product_id = :product_id
                ORDER BY o.created_at DESC
                LIMIT 5
            """), {"product_id": "gekko_light_ligero"})
            
            orders = result.fetchall()
            print(f"\n📦 Recent Orders for GEKKO LIGHT PRO:")
            print("=" * 80)
            if orders:
                for row in orders:
                    order_id, status, payment_status, size, quantity, created, updated = row
                    print(f"Order {order_id}: Size {size} x{quantity}")
                    print(f"  Status: {status} | Payment: {payment_status}")
                    print(f"  Created: {created}")
                    print(f"  Updated: {updated}")
                    print()
            else:
                print("No orders found for this product")
                
            # Check if any payments were completed
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE oi.product_id = :product_id 
                AND o.payment_status = 'captured'
            """), {"product_id": "gekko_light_ligero"})
            
            completed_payments = result.scalar()
            print(f"📊 Summary:")
            print(f"  Total orders with completed payments: {completed_payments}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()