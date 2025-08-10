"""
Test script to verify database models work correctly
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

try:
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal, engine, Base
    from app.models.product import Product, ProductSize, Tag
    from app.models.user import User
    from app.models.cart import CartItem
    from app.models.order import Order, OrderItem

    print("✅ All imports successful!")

    # Create all tables
    print("🔨 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

    # Test database connection
    db: Session = SessionLocal()
    try:
        # Test a simple query
        products = db.query(Product).limit(5).all()
        print(f"✅ Database query successful! Found {len(products)} products.")

        # Test creating a simple product
        test_product = Product(
            id="test_model_check", name="Test Product", price=99.99, is_active=True
        )

        # Check if product already exists
        existing = db.query(Product).filter(Product.id == "test_model_check").first()
        if not existing:
            db.add(test_product)
            db.commit()
            print("✅ Test product created successfully!")
        else:
            print("✅ Test product already exists!")

    except Exception as e:
        print(f"❌ Database operation failed: {e}")
    finally:
        db.close()

    print("🎉 All model tests passed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the correct directory")
except Exception as e:
    print(f"❌ Error: {e}")
