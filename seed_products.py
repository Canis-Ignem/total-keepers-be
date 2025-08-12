"""
Seed script for goalkeeper gloves products
Run this script to populate the database with sample products
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.product import Product, ProductSize, Tag, Base

# Create all tables
Base.metadata.create_all(bind=engine)


def seed_products():
    """Seed the database with sample goalkeeper gloves"""
    db: Session = SessionLocal()

    try:
        # Create tags first
        tags_data = [
            {"name": "junior", "description": "Products designed for junior players"},
            {"name": "ligero", "description": "Lightweight products"},
            {"name": "profesional", "description": "Professional grade equipment"},
            {"name": "entrenamiento", "description": "Training equipment"},
            {"name": "grip", "description": "Enhanced grip technology"},
            {"name": "durabilidad", "description": "High durability"},
        ]

        created_tags = {}
        for tag_data in tags_data:
            existing_tag = db.query(Tag).filter(Tag.name == tag_data["name"]).first()
            if not existing_tag:
                tag = Tag(**tag_data)
                db.add(tag)
                db.flush()
                created_tags[tag_data["name"]] = tag
            else:
                created_tags[tag_data["name"]] = existing_tag

        # Create products
        products_data = [
            {
                "id": "guante_speed_junior",
                "name": "Speed Junior Goalkeeper Gloves",
                "description": "Lightweight goalkeeper gloves perfect for junior players. Features enhanced grip and comfortable fit.",
                "price": 34.99,
                "img": "/train_with_us/gloves.svg",
                "category": "GOALKEEPER_GLOVES",
                "tag": "JUNIOR",
                "sizes": [
                    {"size": "5", "stock_quantity": 10, "is_available": True},
                    {"size": "6", "stock_quantity": 15, "is_available": True},
                    {"size": "7", "stock_quantity": 8, "is_available": True},
                ],
                "tags": ["junior", "ligero"],
            },
            {
                "id": "guante_pro_senior",
                "name": "Pro Senior Goalkeeper Gloves",
                "description": "Professional grade goalkeeper gloves for experienced keepers. Superior grip and durability.",
                "price": 89.99,
                "img": "/train_with_us/gloves_pro.svg",
                "category": "GOALKEEPER_GLOVES",
                "tag": "SENIOR",
                "sizes": [
                    {"size": "8", "stock_quantity": 5, "is_available": True},
                    {"size": "9", "stock_quantity": 12, "is_available": True},
                    {"size": "10", "stock_quantity": 7, "is_available": True},
                    {"size": "11", "stock_quantity": 3, "is_available": True},
                ],
                "tags": ["profesional", "grip", "durabilidad"],
            },
            {
                "id": "guante_training",
                "name": "Training Goalkeeper Gloves",
                "description": "Durable training gloves designed for daily practice sessions. Excellent value for money.",
                "price": 45.50,
                "img": "/train_with_us/gloves_training.svg",
                "category": "GOALKEEPER_GLOVES",
                "tag": "TRAINING",
                "sizes": [
                    {"size": "6", "stock_quantity": 20, "is_available": True},
                    {"size": "7", "stock_quantity": 18, "is_available": True},
                    {"size": "8", "stock_quantity": 25, "is_available": True},
                    {"size": "9", "stock_quantity": 15, "is_available": True},
                ],
                "tags": ["entrenamiento", "durabilidad"],
            },
            {
                "id": "guante_elite_pro",
                "name": "Elite Pro Goalkeeper Gloves",
                "description": "Top-tier professional gloves with advanced grip technology and premium materials.",
                "price": 129.99,
                "img": "/train_with_us/gloves_elite.svg",
                "category": "GOALKEEPER_GLOVES",
                "tag": "ELITE",
                "sizes": [
                    {"size": "8", "stock_quantity": 2, "is_available": True},
                    {"size": "9", "stock_quantity": 4, "is_available": True},
                    {"size": "10", "stock_quantity": 3, "is_available": True},
                    {"size": "11", "stock_quantity": 1, "is_available": True},
                ],
                "tags": ["profesional", "grip"],
            },
        ]

        for product_data in products_data:
            # Check if product already exists
            existing_product = (
                db.query(Product).filter(Product.id == product_data["id"]).first()
            )
            if existing_product:
                print(f"Product {product_data['id']} already exists, skipping...")
                continue

            # Create product
            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                img=product_data["img"],
                category=product_data["category"],
                tag=product_data["tag"],
                is_active=True,
            )
            db.add(product)
            db.flush()

            # Add sizes
            for size_data in product_data["sizes"]:
                product_size = ProductSize(product_id=product.id, **size_data)
                db.add(product_size)

            # Add tags
            for tag_name in product_data["tags"]:
                if tag_name in created_tags:
                    product.tags.append(created_tags[tag_name])

            print(f"Created product: {product.name}")

        db.commit()
        print("✅ Database seeded successfully with goalkeeper gloves!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database with goalkeeper gloves...")
    seed_products()
