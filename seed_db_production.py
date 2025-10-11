"""
Production database seeding script for Total Keepers goalkeeper gloves
This script can seed the production PostgreSQL database with initial products and discount codes.

Usage:
1. Set the DATABASE_URL environment variable to your production database
2. Run: python seed_db_production.py

Example DATABASE_URL formats:
- postgresql://username:password@host:port/database
- For Azure: postgresql://user@server:password@server.postgres.database.azure.com:5432/database?sslmode=require

Environment Variables Required:
- DATABASE_URL: Production PostgreSQL connection string
"""

import sys
import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, timezone, timedelta
import subprocess
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.models.product import Product, ProductSize, Tag, ProductTranslation, Base
from app.models.discount_code import DiscountCode





class ProductionSeeder:
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the production seeder with database connection."""
        self.database_url = database_url or os.getenv("PROD_DATABASE_URL")
        
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Set it to your production PostgreSQL connection string."
            )
        
        print(f"🔗 Connecting to database: {self._mask_db_url(self.database_url)}")
        
        # Create engine with production settings
        self.engine = create_engine(
            self.database_url,
            # Production connection settings
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _mask_db_url(self, url: str) -> str:
        """Mask sensitive parts of database URL for logging."""
        if "://" in url:
            protocol, rest = url.split("://", 1)
            if "@" in rest:
                credentials, host_part = rest.split("@", 1)
                # Mask password
                if ":" in credentials:
                    user, _ = credentials.split(":", 1)
                    return f"{protocol}://{user}:****@{host_part}"
            return f"{protocol}://****"
        return "****"

    def test_connection(self) -> bool:
        """Test database connection before seeding."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Database connection successful!")
                print(f"📊 PostgreSQL version: {version}")
                return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

    def run_alembic_migrations(self):
        """Run Alembic migrations to ensure database schema is up to date."""
        print("🔄 Running Alembic migrations...")
        
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        # Set environment variable for Alembic to use our database URL
        env = os.environ.copy()
        env["DATABASE_URL"] = self.database_url
        
        # Check if alembic.ini exists
        alembic_ini = script_dir / "alembic.ini"
        if not alembic_ini.exists():
            print(f"❌ alembic.ini not found at {alembic_ini}")
            raise Exception("alembic.ini not found")
        
        # Check if alembic directory exists
        alembic_dir = script_dir / "alembic"
        if not alembic_dir.exists():
            print(f"❌ alembic directory not found at {alembic_dir}")
            raise Exception("alembic directory not found")
        
        try:
            # Change to the script directory to ensure alembic.ini is found
            original_cwd = os.getcwd()
            os.chdir(script_dir)
            
            print(f"📁 Working directory: {script_dir}")
            print(f"🔗 Database URL: {self._mask_db_url(self.database_url)}")
            
            # First, check current revision
            print("🔍 Checking current database revision...")
            current_result = subprocess.run(
                ["alembic", "current"],
                capture_output=True,
                text=True,
                env=env
            )
            
            if current_result.stdout:
                print(f"📋 Current revision: {current_result.stdout.strip()}")
            else:
                print("📋 No current revision (fresh database)")
            
            # Check what migrations are available
            print("🔍 Checking available migrations...")
            heads_result = subprocess.run(
                ["alembic", "heads"],
                capture_output=True,
                text=True,
                env=env
            )
            
            if heads_result.stdout:
                print(f"📋 Available heads: {heads_result.stdout.strip()}")
            
            # Run alembic upgrade head
            print("⏫ Running alembic upgrade head...")
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            
            print("✅ Alembic migrations completed successfully!")
            if result.stdout:
                print(f"📝 Migration output: {result.stdout.strip()}")
            if result.stderr:
                print(f"⚠️  Migration warnings: {result.stderr.strip()}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Alembic migration failed with return code {e.returncode}")
            if e.stdout:
                print(f"📝 stdout: {e.stdout.strip()}")
            if e.stderr:
                print(f"📝 stderr: {e.stderr.strip()}")
            raise Exception(f"Migration failed: {e.stderr}")
        except FileNotFoundError:
            print("❌ Alembic not found. Make sure Alembic is installed.")
            print("💡 Try: pip install alembic")
            raise Exception("Alembic not installed")
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def ensure_discount_price_column(self):
        """Ensure the discount_price column exists in the products table."""
        print("🔧 Checking for discount_price column...")
        
        try:
            with self.engine.connect() as conn:
                # Check if discount_price column exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'discount_price'
                """))
                
                if result.fetchone():
                    print("✅ discount_price column already exists")
                    return
                
                print("➕ Adding discount_price column to products table...")
                
                # Add the discount_price column
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN discount_price DECIMAL(10,2)
                """))
                
                conn.commit()
                print("✅ discount_price column added successfully!")
                
        except Exception as e:
            print(f"❌ Error checking/adding discount_price column: {str(e)}")
            raise

    def create_tables(self):
        """Create all tables if they don't exist (fallback method)."""
        print("🏗️ Creating database tables if they don't exist...")
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Tables created successfully!")
            
            # Ensure discount_price column exists (in case of old schema)
            self.ensure_discount_price_column()
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            raise

    def clear_existing_data(self, db: Session, confirm: bool = False):
        """Clear existing product and discount data (use with caution in production)."""
        if not confirm:
            response = input(
                "⚠️  WARNING: This will DELETE ALL existing products and discount codes!\n"
                "Are you sure you want to continue? (yes/no): "
            ).lower().strip()
            
            if response != 'yes':
                print("❌ Seeding cancelled by user.")
                return False

        print("🧹 Clearing existing data...")
        try:
            db.execute(text("DELETE FROM product_translations"))
            db.execute(text("DELETE FROM product_sizes"))
            db.execute(text("DELETE FROM product_tags"))
            db.execute(text("DELETE FROM tags"))
            db.execute(text("DELETE FROM products"))
            db.execute(text("DELETE FROM discount_codes"))
            db.commit()
            print("✅ Existing data cleared successfully!")
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Error clearing data: {str(e)}")
            raise

    def reset_alembic_version(self, db: Session):
        """Reset Alembic version table to allow migrations to run from scratch."""
        print("🔄 Resetting Alembic version table...")
        try:
            # Check if alembic_version table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                )
            """))
            exists = result.fetchone()[0]
            
            if exists:
                db.execute(text("DROP TABLE alembic_version"))
                db.commit()
                print("✅ Alembic version table dropped successfully!")
            else:
                print("ℹ️  Alembic version table doesn't exist (fresh database)")
            
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Error resetting alembic version: {str(e)}")
            raise

    def drop_all_tables(self, db: Session):
        """Drop all tables in the public schema."""
        print("🗑️  Dropping all tables...")
        try:
            # Query all tables in the public schema
            result = db.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                print("  ℹ️  No tables found")
                return True
            
            print(f"  📋 Found {len(tables)} table(s): {', '.join(tables)}")
            
            for table in tables:
                # Drop the table with CASCADE to handle dependencies
                db.execute(text(f"DROP TABLE {table} CASCADE"))
                print(f"  ✅ Dropped table: {table}")
            
            db.commit()
            print(f"✅ Successfully dropped {len(tables)} table(s)")
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Error dropping tables: {str(e)}")
            raise

    def drop_enum_types(self, db: Session):
        """Drop PostgreSQL enum types that may exist from previous migrations."""
        print("🔧 Dropping existing enum types...")
        try:
            # Query all custom enum types in the database
            result = db.execute(text("""
                SELECT typname 
                FROM pg_type 
                WHERE typcategory = 'E' 
                AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            """))
            
            enum_types = [row[0] for row in result.fetchall()]
            
            if not enum_types:
                print("  ℹ️  No custom enum types found")
                return True
            
            print(f"  📋 Found {len(enum_types)} enum type(s): {', '.join(enum_types)}")
            
            for enum_type in enum_types:
                # Drop the enum type (CASCADE to drop dependent objects)
                db.execute(text(f"DROP TYPE {enum_type} CASCADE"))
                print(f"  ✅ Dropped enum type: {enum_type}")
            
            db.commit()
            print(f"✅ Successfully dropped {len(enum_types)} enum type(s)")
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Error dropping enum types: {str(e)}")
            raise

    def seed_data(self, clear_existing: bool = False):
        """Seed the production database with goalkeeper gloves and discount codes."""
        db: Session = self.SessionLocal()
        
        try:
            # Optionally clear existing data
            if clear_existing:
                if not self.clear_existing_data(db):
                    return False

            # Create tags first
            print("🏷️ Creating product tags...")
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
                    print(f"  ✅ Created tag: {tag_data['name']}")
                else:
                    created_tags[tag_data["name"]] = existing_tag
                    print(f"  ⏭️ Tag already exists: {tag_data['name']}")

            # Create products
            print("🧤 Creating goalkeeper gloves...")
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
                    "tags": ["Profesional", "armado", "roll negativo", "blanco"],
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
                    "tags": ["Profesional", "armado", "roll negativo", "blanco"],
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
                    "tags": ["Profesional", "ligero", "negativo", "negro"],
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
                    "tags": ["Profesional", "ligero", "negativo", "negro", "ajuste"],
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
                    "tags": ["Profesional", "ligero", "negativo", "blanco", "ajuste"],
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

            # Create products
            for product_data in products_data:
                existing_product = db.query(Product).filter(Product.id == product_data["id"]).first()
                if existing_product:
                    print(f"  ⏭️ Product already exists: {product_data['name']}")
                    continue

                # Create product
                product = Product(
                    id=product_data["id"],
                    name=product_data["name"],
                    short_description=product_data["short_description"],
                    description=product_data["description"],
                    price=product_data["price"],
                    discount_price=product_data.get("discount_price"),
                    img=product_data["img"],
                    category=product_data["category"],
                    tag=product_data["tag"],
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
                        "short_description": english_translations[product_data["id"]]["short_description"],
                        "description": english_translations[product_data["id"]]["description"],
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
                    if tag_name in created_tags:
                        product.tags.append(created_tags[tag_name])

                print(f"  ✅ Created product: {product.name}")

            # Create discount codes
            print("🎫 Creating discount codes...")
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
                existing_code = db.query(DiscountCode).filter(
                    DiscountCode.code.ilike(discount_data["code"])
                ).first()

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
                        end_date=datetime.now(timezone.utc) + timedelta(days=365),  # Valid for 1 year
                        max_uses=1000000,  # Maximum 1M uses total
                        max_uses_per_customer=3,  # Each customer can use it 3 times
                        notes=discount_data["notes"],
                    )
                    db.add(discount_code)
                    print(f"  ✅ Created discount code: {discount_code.code} (10% off)")
                else:
                    print(f"  ⏭️ Discount code already exists: {discount_data['code']}")

            # Commit all changes
            db.commit()
            print("🎉 Production database seeded successfully!")
            
            # Summary
            total_products = db.query(Product).count()
            total_codes = db.query(DiscountCode).count()
            print(f"\n📊 Summary:")
            print(f"   Products in database: {total_products}")
            print(f"   Discount codes in database: {total_codes}")
            
            return True

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding production database: {str(e)}")
            raise
        finally:
            db.close()


def main():
    """Main function to run the production seeder."""
    print("🌱 Total Keepers Production Database Seeder")
    print("=" * 50)
    
    # Check for required environment variables
    database_url = os.getenv("PROD_DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is required!")
        print("\nExample usage:")
        print("  # Windows PowerShell:")
        print("  $env:DATABASE_URL='postgresql://user:pass@host:5432/db'; python seed_db_production.py")
        print("\n  # Linux/Mac:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/db'")
        print("  python seed_db_production.py")
        return False

    try:
        # Initialize seeder
        seeder = ProductionSeeder(database_url)
        
        # Test connection
        if not seeder.test_connection():
            return False
        
        # Ask about resetting Alembic migrations
        reset_alembic = False
        response = input("\n🤔 Do you want to reset Alembic migrations (drop alembic_version table)? (yes/no): ").lower().strip()
        if response == 'yes':
            db = seeder.SessionLocal()
            try:
                seeder.reset_alembic_version(db)
                seeder.drop_all_tables(db)  # Drop all tables before migrations
                seeder.drop_enum_types(db)
                reset_alembic = True
            finally:
                db.close()
        
        # Run Alembic migrations to ensure schema is up to date
        try:
            seeder.run_alembic_migrations()
        except Exception as e:
            print(f"⚠️  Migration failed: {str(e)}")
            print("🔧 Falling back to manual schema updates...")
            # Fallback to direct table creation and manual column addition if migrations fail
            seeder.create_tables()
        
        # Always ensure discount_price column exists (for existing tables)
        seeder.ensure_discount_price_column()
        
        # Ask about clearing existing data
        clear_existing = False
        response = input("\n🤔 Do you want to clear existing products and discount codes? (yes/no): ").lower().strip()
        if response == 'yes':
            clear_existing = True
        
        # Seed data
        success = seeder.seed_data(clear_existing=clear_existing)
        
        if success:
            print("\n🎉 Production database seeding completed successfully!")
            return True
        else:
            print("\n❌ Production database seeding failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        return False


if __name__ == "__main__":

    from dotenv import load_dotenv

    load_dotenv()

    success = main()
    sys.exit(0 if success else 1)