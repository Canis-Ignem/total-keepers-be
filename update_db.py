"""
Update script for goalkeeper gloves products
Run this script to update existing products without deleting them (preserves order relationships)
"""

import sys
import os
from sqlalchemy import text

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.product import Product, ProductSize, Tag, ProductTranslation, Base
from app.models.discount_code import DiscountCode
from datetime import datetime, timezone, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)


def update_products():
    """Update the database with sample goalkeeper gloves (preserves existing orders)"""
    db: Session = SessionLocal()

    print("Updating database (preserving order relationships)...")

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
                print(f"Created tag: {tag_data['name']}")
            else:
                created_tags[tag_data["name"]] = existing_tag

        # Base URL for blob storage images
        blob_base_url = "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/"
        
        # Create products
        products_data = [
            {
                "id": "goti_pro_blanco",
                "name": "GOTI PRO - WHITE",
                "short_description": "Guante armado de gama alta",
                "description": """
🔹 Latex Aleman Supreme Contact de gama alta, ¡el agarre es brutal!\n
🔹 Corte Roll Negativo para un ajuste perfecto\n
🔹 Torso 100% de latex, ¡más durabilidad y armado!\n
🔹 Ideal para quienes buscan un guante que les haga más fuerte
""",
                "price": 74.99,
                "discount_price": 59.99,
                "img": "/train_with_us/gloves.svg",
                "images": [
                    f"{blob_base_url}goti_pro_blanco/main.png",
                    f"{blob_base_url}goti_pro_blanco/IMG_1.png",
                    f"{blob_base_url}goti_pro_blanco/IMG_2.png",
                    f"{blob_base_url}goti_pro_blanco/IMG_3.png",
                ],
                "category": "Armado",
                "tag": "Gama Alta",
                "priority": 5,
                "sizes": [
                    {"size": "5", "stock_quantity": 4, "is_available": True},
                    {"size": "5.5", "stock_quantity": 5, "is_available": True},
                    {"size": "6", "stock_quantity": 4, "is_available": True},
                    {"size": "6.5", "stock_quantity": 3, "is_available": True},
                    {"size": "7", "stock_quantity": 6, "is_available": True},
                    {"size": "7.5", "stock_quantity": 6, "is_available": True},
                    {"size": "8", "stock_quantity": 0, "is_available": False},
                    {"size": "8.5", "stock_quantity": 4, "is_available": True},
                    {"size": "9", "stock_quantity": 1, "is_available": True},
                    {"size": "9.5", "stock_quantity": 5, "is_available": True},
                    {"size": "10", "stock_quantity": 0, "is_available": False},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 0, "is_available": False},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "armado", "roll negativo", "blanco"],
            },
            {
                "id": "goti_pro_negro",
                "name": "GOTI PRO - BLACK",
                "short_description": "Guante armado de gama alta",
                "description": """
🔹 Latex Aleman Supreme Contact de gama alta, ¡el agarre es brutal!\n
🔹 Corte Roll Negativo para un ajuste perfecto\n
🔹 Torso 100% de latex, ¡más durabilidad y armado!\n
🔹 Ideal para quienes buscan un guante que les haga más fuerte
""",
                "price": 74.99,
                "discount_price": 59.99,
                "img": "/train_with_us/gloves.svg",
                "images": [
                    f"{blob_base_url}goti_pro_negro/main.png",
                    f"{blob_base_url}goti_pro_negro/IMG_1.png",
                    f"{blob_base_url}goti_pro_negro/IMG_2.png",
                    f"{blob_base_url}goti_pro_negro/IMG_3.png",
                ],
                "category": "Armado",
                "tag": "Gama Alta",
                "priority": 4,
                "sizes": [
                    {"size": "5", "stock_quantity": 0, "is_available": False},
                    {"size": "5.5", "stock_quantity": 0, "is_available": False},
                    {"size": "6", "stock_quantity": 1, "is_available": True},
                    {"size": "6.5", "stock_quantity": 2, "is_available": True},
                    {"size": "7", "stock_quantity": 1, "is_available": True},
                    {"size": "7.5", "stock_quantity": 2, "is_available": True},
                    {"size": "8", "stock_quantity": 2, "is_available": False},
                    {"size": "8.5", "stock_quantity": 2, "is_available": True},
                    {"size": "9", "stock_quantity": 0, "is_available": False},
                    {"size": "9.5", "stock_quantity": 1, "is_available": True},
                    {"size": "10", "stock_quantity": 2, "is_available": False},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 0, "is_available": False},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "armado", "roll negativo", "blanco"],
            },
            {
                "id": "gekko_light_ligero",
                "name": "GEKKO PRO - BLACK",
                "short_description": "Guante ligero de gama alta, máxima comodidad y ajuste.",
                "description": """
🔹 Palma de látex Premium German Supreme Contact: agarre inigualable.\n
🔹 Corte negativo para un ajuste perfecto para sentir al máximo el balón\n
🔹 Dorso de 100% knitt para máxima ergonomía.\n
🔹 Perfecto para porteros que exigen ser uno con el guante.
🔹 Muñequeras extraíbles.

""",
                "price": 79.99,
                "discount_price": 63.99,
                "img": "/train_with_us/gloves_pro.svg",
                "images": [
                    f"{blob_base_url}gekko_light_ligero/main.png",
                    f"{blob_base_url}gekko_light_ligero/IMG_1.png",
                    f"{blob_base_url}gekko_light_ligero/IMG_2.png",
                    f"{blob_base_url}gekko_light_ligero/IMG_3.png",
                ],
                "category": "Gama Alta",
                "tag": "Ligero",
                "priority": 3,
                "sizes": [
                    {"size": "5", "stock_quantity": 0, "is_available": False},
                    {"size": "5.5", "stock_quantity": 0, "is_available": False},
                    {"size": "6", "stock_quantity": 0, "is_available": False},
                    {"size": "6.5", "stock_quantity": 2, "is_available": True},
                    {"size": "7", "stock_quantity": 5, "is_available": True},
                    {"size": "7.5", "stock_quantity": 1, "is_available": True},
                    {"size": "8", "stock_quantity": 0, "is_available": False},
                    {"size": "8.5", "stock_quantity": 1, "is_available": True},
                    {"size": "9", "stock_quantity": 0, "is_available": False},
                    {"size": "9.5", "stock_quantity": 1, "is_available": True},
                    {"size": "10", "stock_quantity": 0, "is_available": False},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 0, "is_available": False},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "ligero", "negativo", "negro"],
            },
            {
                "id": "gekko_light_white",
                "name": "GEKKO PRO - White",
                "short_description": "Guante ligero de gama alta, máxima comodidad y ajuste.",
                "description": """
🔹 Palma de látex Premium German Supreme Contact: agarre inigualable.\n
🔹 Corte negativo para un ajuste perfecto para sentir al máximo el balón\n
🔹 Dorso de 100% knitt para máxima ergonomía.\n
🔹 Perfecto para porteros que exigen ser uno con el guante.
🔹 Muñequeras extraíbles.

""",
                "price": 79.99,
                "discount_price": 63.99,
                "img": "/train_with_us/gloves_pro.svg",
                "images": [
                    f"{blob_base_url}gekko_light_white/main.png",
                    f"{blob_base_url}gekko_light_white/IMG_1.png",
                    f"{blob_base_url}gekko_light_white/IMG_2.png",
                    f"{blob_base_url}gekko_light_white/IMG_3.png",
                ],
                "category": "Gama Alta",
                "tag": "Ligero",
                "priority": 3,
                "sizes": [
                    {"size": "5", "stock_quantity": 0, "is_available": False},
                    {"size": "5.5", "stock_quantity": 0, "is_available": False},
                    {"size": "6", "stock_quantity": 0, "is_available": False},
                    {"size": "6.5", "stock_quantity": 2, "is_available": True},
                    {"size": "7", "stock_quantity": 5, "is_available": True},
                    {"size": "7.5", "stock_quantity": 1, "is_available": True},
                    {"size": "8", "stock_quantity": 0, "is_available": False},
                    {"size": "8.5", "stock_quantity": 1, "is_available": True},
                    {"size": "9", "stock_quantity": 0, "is_available": False},
                    {"size": "9.5", "stock_quantity": 1, "is_available": True},
                    {"size": "10", "stock_quantity": 0, "is_available": False},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 0, "is_available": False},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "ligero", "negativo", "negro"],
            },
            {
                "id": "gekko_ap_black",
                "name": "GEKKO AP - BLACK",
                "short_description": "Ligereza y comodidad en un guante.",
                "description": """
🔹 Palma de látex Alemán Supreme Contact: agarre único.\n
🔹 Corte negativo para un ajuste preciso.\n
🔹 Dorso 90% Knitt y 10% Hilo elástico para ceñirse al máximo.\n
🔹 Perfecto para porteros que exigen el más alto nivel de ajuste y contacto con el balón.\n
🔹 Bandas elásticas extraíbles
""",
                "price": 54.99,
                "discount_price": 43.99,
                "img": "/train_with_us/gloves_pro.svg",
                "images": [
                    f"{blob_base_url}gekko_ap_black/main.png",
                    f"{blob_base_url}gekko_ap_black/IMG_1.png",
                    f"{blob_base_url}gekko_ap_black/IMG_2.png",
                    f"{blob_base_url}gekko_ap_black/IMG_3.png",
                ],
                "category": "Gama Media-Alta",
                "tag": "Ligero",
                "priority": 1,
                "sizes": [
                    {"size": "5", "stock_quantity": 0, "is_available": False},
                    {"size": "5.5", "stock_quantity": 0, "is_available": False},
                    {"size": "6", "stock_quantity": 0, "is_available": False},
                    {"size": "6.5", "stock_quantity": 0, "is_available": True},
                    {"size": "7", "stock_quantity": 2, "is_available": True},
                    {"size": "7.5", "stock_quantity": 2, "is_available": True},
                    {"size": "8", "stock_quantity": 2, "is_available": True},
                    {"size": "8.5", "stock_quantity": 2, "is_available": True},
                    {"size": "9", "stock_quantity": 2, "is_available": True},
                    {"size": "9.5", "stock_quantity": 2, "is_available": True},
                    {"size": "10", "stock_quantity": 2, "is_available": True},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 2, "is_available": True},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "ligero", "negativo", "negro", "ajuste"],
            },
            {
                "id": "gekko_ap_white",
                "name": "GEKKO AP - WHITE",
                "short_description": "Ligereza y comodidad en un guante.",
                "description": """
🔹 Palma de látex Alemán Supreme Contact: agarre único.\n
🔹 Corte negativo para un ajuste preciso.\n
🔹 Dorso 90% Knitt y 10% Hilo elástico para ceñirse al máximo.\n
🔹 Perfecto para porteros que exigen el más alto nivel de ajuste y contacto con el balón.\n
🔹 Bandas elásticas extraíbles
""",
                "price": 54.99,
                "discount_price": 43.99,
                "img": "/train_with_us/gloves_pro.svg",
                "images": [
                    f"{blob_base_url}gekko_ap_white/main.png",
                    f"{blob_base_url}gekko_ap_white/IMG_1.png",
                    f"{blob_base_url}gekko_ap_white/IMG_2.png",
                    f"{blob_base_url}gekko_ap_white/IMG_3.png",
                ],
                "category": "Gama Media-Alta",
                "tag": "Ligero",
                "priority": 2,
                "sizes": [
                    {"size": "5", "stock_quantity": 0, "is_available": False},
                    {"size": "5.5", "stock_quantity": 0, "is_available": False},
                    {"size": "6", "stock_quantity": 0, "is_available": False},
                    {"size": "6.5", "stock_quantity": 0, "is_available": True},
                    {"size": "7", "stock_quantity": 2, "is_available": True},
                    {"size": "7.5", "stock_quantity": 2, "is_available": True},
                    {"size": "8", "stock_quantity": 2, "is_available": True},
                    {"size": "8.5", "stock_quantity": 2, "is_available": True},
                    {"size": "9", "stock_quantity": 2, "is_available": True},
                    {"size": "9.5", "stock_quantity": 2, "is_available": True},
                    {"size": "10", "stock_quantity": 2, "is_available": True},
                    {"size": "10.5", "stock_quantity": 0, "is_available": False},
                    {"size": "11", "stock_quantity": 2, "is_available": True},
                    {"size": "11.5", "stock_quantity": 0, "is_available": False},
                ],
                "tags": ["profesional", "ligero", "negativo", "blanco", "ajuste"],
            }
        ]

        english_translations = {
            "goti_pro_blanco": {
                "name": "GOTI PRO - White",
                "short_description": "High-end armored glove for demanding goalkeepers.",
                "description": """
🔹 Also features premium German Supreme Contact latex for elite-level grip.\n
🔹 Negative cut delivers a snug, comfortable fit.\n
🔹 Backhand crafted from elastic knit for a lighter, more flexible feel.\n
🔹 Muñequera extraíble para adaptarlo a tu estilo de juego\n
""",
            },
            "gekko_light_ligero": {
                "name": "GEKKO LIGHT PRO - Black",
                "short_description": "High-end lightweight glove, comfortable and snug fit.",
                "description": """
🔹 Also features premium German Supreme Contact latex for elite-level grip.\n
🔹 Negative cut provides a snug, comfortable fit.\n
🔹 Backhand made from elastic knit for a lighter, more flexible feel.\n
🔹 Removable wrist strap lets you adapt the glove to your playing style.\n
""",
            },
            "goti_pro_negro": {
                "name": "GOTI PRO - Black",
                "short_description": "High-end armored glove",
                "description": """
🔹 Premium German Supreme Contact latex, incredible grip!\n
🔹 Roll Negative cut for a perfect fit\n
🔹 100% latex torso for more durability and reinforcement!\n
🔹 Ideal for those seeking a glove that makes them stronger\n
""",
            },
            "gekko_light_white": {
                "name": "GEKKO LIGHT PRO - White",
                "short_description": "High-end lightweight glove, comfortable and snug fit.",
                "description": """
🔹 Also features premium German Supreme Contact latex for elite-level grip.\n
🔹 Negative cut provides a snug, comfortable fit.\n
🔹 Backhand made from elastic knit for a lighter, more flexible feel.\n
🔹 Removable wrist strap lets you adapt the glove to your playing style.\n
""",
            },
            "gekko_ap_black": {
                "name": "GEKKO AP - BLACK",
                "short_description": "Lightness and comfort in a glove.",
                "description": """
🔹 German Supreme Contact latex palm: unique grip.\n
🔹 Negative cut for precise fit.\n
🔹 90% Knit and 10% elastic thread backhand for maximum adjustment.\n
🔹 Perfect for goalkeepers who demand the highest level of fit and ball contact.\n
🔹 Removable elastic bands\n
""",
            },
            "gekko_ap_white": {
                "name": "GEKKO AP - WHITE",
                "short_description": "Lightness and comfort in a glove.",
                "description": """
🔹 German Supreme Contact latex palm: unique grip.\n
🔹 Negative cut for precise fit.\n
🔹 90% Knit and 10% elastic thread backhand for maximum adjustment.\n
🔹 Perfect for goalkeepers who demand the highest level of fit and ball contact.\n
🔹 Removable elastic bands\n
""",
            },
        }

        for product_data in products_data:
            # Check if product already exists
            existing_product = (
                db.query(Product).filter(Product.id == product_data["id"]).first()
            )
            
            if existing_product:
                print(f"Updating product: {product_data['id']}")
                
                # Update product fields
                existing_product.name = product_data["name"]
                existing_product.short_description = product_data["short_description"]
                existing_product.description = product_data["description"]
                existing_product.price = product_data["price"]
                existing_product.discount_price = product_data.get("discount_price", None)
                existing_product.img = product_data["img"]
                existing_product.images = product_data.get("images", [])
                existing_product.category = product_data["category"]
                existing_product.tag = product_data["tag"]
                existing_product.priority = product_data.get("priority", 0)
                existing_product.is_active = True
                
                # Update translations
                # Delete existing translations for this product
                db.query(ProductTranslation).filter(
                    ProductTranslation.product_id == product_data["id"]
                ).delete()
                
                # Add new translations
                translations = [
                    {
                        "language_code": "es",
                        "name": product_data["name"],
                        "short_description": product_data["short_description"],
                        "description": product_data["description"],
                    },
                    {
                        "language_code": "en",
                        "name": english_translations[product_data["id"]]["name"],
                        "short_description": english_translations[product_data["id"]][
                            "short_description"
                        ],
                        "description": english_translations[product_data["id"]][
                            "description"
                        ],
                    },
                ]
                for trans in translations:
                    translation = ProductTranslation(product_id=existing_product.id, **trans)
                    db.add(translation)
                
                # Update sizes
                # Delete existing sizes for this product
                db.query(ProductSize).filter(
                    ProductSize.product_id == product_data["id"]
                ).delete()
                
                # Add new sizes
                for size_data in product_data["sizes"]:
                    product_size = ProductSize(product_id=existing_product.id, **size_data)
                    db.add(product_size)
                
                # Update tags - clear existing and add new
                existing_product.tags.clear()
                for tag_name in product_data["tags"]:
                    tag_name_lower = tag_name.lower()
                    if tag_name_lower in created_tags:
                        existing_product.tags.append(created_tags[tag_name_lower])
                
                print(f"✅ Updated product: {existing_product.name}")
            else:
                print(f"Creating new product: {product_data['id']}")
                
                # Create product
                product = Product(
                    id=product_data["id"],
                    name=product_data["name"],
                    short_description=product_data["short_description"],
                    description=product_data["description"],
                    price=product_data["price"],
                    discount_price=product_data.get("discount_price", None),
                    img=product_data["img"],
                    images=product_data.get("images", []),
                    category=product_data["category"],
                    tag=product_data["tag"],
                    priority=product_data.get("priority", 0),
                    is_active=True,
                )
                db.add(product)
                db.flush()

                # Add translations (Spanish and English)
                translations = [
                    {
                        "language_code": "es",
                        "name": product_data["name"],
                        "short_description": product_data["short_description"],
                        "description": product_data["description"],
                    },
                    {
                        "language_code": "en",
                        "name": english_translations[product_data["id"]]["name"],
                        "short_description": english_translations[product_data["id"]][
                            "short_description"
                        ],
                        "description": english_translations[product_data["id"]][
                            "description"
                        ],
                    },
                ]
                for trans in translations:
                    translation = ProductTranslation(product_id=product.id, **trans)
                    db.add(translation)

                # Add sizes
                for size_data in product_data["sizes"]:
                    product_size = ProductSize(product_id=product.id, **size_data)
                    db.add(product_size)

                # Add tags
                for tag_name in product_data["tags"]:
                    tag_name_lower = tag_name.lower()
                    if tag_name_lower in created_tags:
                        product.tags.append(created_tags[tag_name_lower])

                print(f"✅ Created product: {product.name}")

        # Create or update discount codes
        discount_codes = [
            {
                "id": "PROMO10",
                "code": "PROMO10",
                "description": "10% discount on order total (excluding shipping)",
                "notes": "Initial promotional discount code for new customers",
            },
            {
                "id": "KR10",
                "code": "KR10",
                "description": "10% discount on order total (excluding shipping)",
                "notes": "KR promotional discount code",
            },
            {
                "id": "AG10",
                "code": "AG10",
                "description": "10% discount on order total (excluding shipping)",
                "notes": "AG promotional discount code",
            },
            {
                "id": "APEÑA10",
                "code": "apeña10",
                "description": "10% discount on order total (excluding shipping)",
                "notes": "Apeña promotional discount code",
            },
            {
                "id": "STZ10",
                "code": "stz10",
                "description": "10% discount on order total (excluding shipping)",
                "notes": "STZ promotional discount code",
            },
        ]

        for discount_data in discount_codes:
            existing_code = (
                db.query(DiscountCode)
                .filter(DiscountCode.code.ilike(discount_data["code"]))
                .first()
            )

            if not existing_code:
                discount_code = DiscountCode(
                    id=discount_data["id"],
                    code=discount_data["code"],
                    description=discount_data["description"],
                    discount_type="percentage",
                    discount_value=10.0,
                    min_order_amount=20.0,  # Minimum 20€ order
                    max_discount_amount=50.0,  # Maximum 50€ discount
                    is_active=True,
                    start_date=datetime.now(timezone.utc),
                    end_date=datetime.now(timezone.utc)
                    + timedelta(days=365),  # Valid for 1 year
                    max_uses=1000000,  # Maximum 1000 uses total
                    max_uses_per_customer=3,  # Each customer can use it 3 times
                    notes=discount_data["notes"],
                )
                db.add(discount_code)

                print(f"✅ {discount_data['code']} discount code created successfully!")
                print(f"Code: {discount_code.code}")
                print(f"Discount: {discount_code.discount_value}% off")
                print(f"Min order: {discount_code.min_order_amount}€")
                print(f"Max discount: {discount_code.max_discount_amount}€")
                print(f"Valid until: {discount_code.end_date}")
                print(f"Max uses: {discount_code.max_uses}")
                print(f"Max uses per customer: {discount_code.max_uses_per_customer}")
            else:
                print(
                    f"{discount_data['code']} discount code already exists with ID: {existing_code.id}"
                )
                print(
                    f"Current status: {'Active' if existing_code.is_active else 'Inactive'}"
                )
                print(f"Discount: {existing_code.discount_value}%")
                print(
                    f"Uses: {existing_code.current_uses}/{existing_code.max_uses or 'unlimited'}"
                )

        db.commit()
        print("\n✅ Database updated successfully with goalkeeper gloves!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating database: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Updating database with goalkeeper gloves...")
    update_products()
