#!/usr/bin/env python3
"""Test stock reduction on successful payment."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.services.product_service import ProductService

def test_stock_reduction():
    """Test the stock reduction functionality."""
    
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No DATABASE_URL found")
        return
    
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("🧪 Testing Stock Reduction...")
        print("=" * 50)
        
        # Check current stock for size 7.5
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT stock_quantity, is_available 
                FROM product_sizes 
                WHERE product_id = 'gekko_light_ligero' AND size = '7.5'
            """))
            
            stock_data = result.fetchone()
            if stock_data:
                current_stock, is_available = stock_data
                print(f"📊 Current Stock for GEKKO LIGHT PRO size 7.5:")
                print(f"  Stock: {current_stock}")
                print(f"  Available: {is_available}")
            else:
                print("❌ Size 7.5 not found")
                return
        
        # Test stock reduction (simulate 1 item purchase)
        print(f"\n🔄 Reducing stock by 1...")
        success = ProductService.reduce_stock(
            db=db,
            product_id="gekko_light_ligero", 
            size="7.5",
            quantity=1
        )
        
        if success:
            print("✅ Stock reduction successful!")
        else:
            print("❌ Stock reduction failed!")
            return
        
        # Check stock after reduction
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT stock_quantity, is_available 
                FROM product_sizes 
                WHERE product_id = 'gekko_light_ligero' AND size = '7.5'
            """))
            
            stock_data = result.fetchone()
            if stock_data:
                new_stock, new_availability = stock_data
                print(f"\n📊 Stock After Reduction:")
                print(f"  Previous Stock: {current_stock}")
                print(f"  New Stock: {new_stock}")
                print(f"  Previous Available: {is_available}")
                print(f"  New Available: {new_availability}")
                
                # Verify the logic
                expected_stock = current_stock - 1
                expected_availability = expected_stock > 0
                
                if new_stock == expected_stock:
                    print("✅ Stock quantity reduced correctly!")
                else:
                    print(f"❌ Stock quantity wrong! Expected {expected_stock}, got {new_stock}")
                
                if new_availability == expected_availability:
                    print("✅ Availability updated correctly!")
                    if new_stock == 0 and not new_availability:
                        print("🎯 Product correctly marked as unavailable when stock reached 0!")
                else:
                    print(f"❌ Availability wrong! Expected {expected_availability}, got {new_availability}")
                    
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stock_reduction()
    if success:
        print("\n🎉 Stock reduction test completed successfully!")
    else:
        print("\n💥 Stock reduction test failed!")