"""
Simple seed script for goalkeeper gloves products
This script works without complex import paths
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/total_keeper_db"


def create_connection():
    """Create database connection"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal()
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("💡 Make sure PostgreSQL is running: .\db.ps1 start")
        sys.exit(1)


def seed_simple_data():
    """Seed database with simple SQL commands"""
    engine, session = create_connection()

    try:
        print("🌱 Seeding database with goalkeeper gloves...")

        # Check if tables exist, if not create them
        print("📋 Creating tables if they don't exist...")

        # Create basic tables (simplified version)
        create_tables_sql = """
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(20),
            avatar_url VARCHAR(500),
            is_active BOOLEAN DEFAULT true,
            is_verified BOOLEAN DEFAULT false,
            google_id VARCHAR(255) UNIQUE,
            facebook_id VARCHAR(255) UNIQUE,
            github_id VARCHAR(255) UNIQUE,
            social_profiles JSONB DEFAULT '{}',
            preferences JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- Create indexes for users table
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
        CREATE INDEX IF NOT EXISTS idx_users_facebook_id ON users(facebook_id);
        CREATE INDEX IF NOT EXISTS idx_users_github_id ON users(github_id);
        
        -- Create tags table
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create products table
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price FLOAT NOT NULL,
            img VARCHAR(500),
            category VARCHAR(100) DEFAULT 'GOALKEEPER_GLOVES',
            tag VARCHAR(50),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create product_sizes table
        CREATE TABLE IF NOT EXISTS product_sizes (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR REFERENCES products(id),
            size VARCHAR(10) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            is_available BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create product_tags junction table
        CREATE TABLE IF NOT EXISTS product_tags (
            product_id VARCHAR REFERENCES products(id),
            tag_id INTEGER REFERENCES tags(id),
            PRIMARY KEY (product_id, tag_id)
        );
        
        -- Create cart_items table
        CREATE TABLE IF NOT EXISTS cart_items (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR REFERENCES users(id) NOT NULL,
            product_id VARCHAR REFERENCES products(id) NOT NULL,
            size VARCHAR(10) NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create orders table
        CREATE TABLE IF NOT EXISTS orders (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
            user_id VARCHAR REFERENCES users(id) NOT NULL,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            payment_status VARCHAR(20) DEFAULT 'pending',
            total_amount FLOAT NOT NULL,
            shipping_address JSONB,
            billing_address JSONB,
            payment_method VARCHAR(50),
            payment_intent_id VARCHAR(255),
            shipping_method VARCHAR(50),
            shipping_cost FLOAT DEFAULT 0,
            tax_amount FLOAT DEFAULT 0,
            discount_amount FLOAT DEFAULT 0,
            notes TEXT,
            estimated_delivery_date TIMESTAMP,
            shipped_date TIMESTAMP,
            delivered_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create order_items table
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR REFERENCES orders(id) NOT NULL,
            product_id VARCHAR REFERENCES products(id) NOT NULL,
            size VARCHAR(10) NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price FLOAT NOT NULL,
            total_price FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_cart_items_user_id ON cart_items(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
        CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
        """

        session.execute(text(create_tables_sql))
        session.commit()
        print("✅ Tables created successfully!")

        # Insert tags
        print("🏷️  Inserting tags...")
        tags_sql = """
        INSERT INTO tags (name, description) VALUES
        ('junior', 'Products designed for junior players'),
        ('ligero', 'Lightweight products'),
        ('profesional', 'Professional grade equipment'),
        ('entrenamiento', 'Training equipment'),
        ('grip', 'Enhanced grip technology'),
        ('durabilidad', 'High durability')
        ON CONFLICT (name) DO NOTHING;
        """

        session.execute(text(tags_sql))
        session.commit()

        # Insert products
        print("🥅 Inserting goalkeeper gloves...")
        products_sql = """
        INSERT INTO products (id, name, description, price, img, category, tag, is_active) VALUES
        ('guante_speed_junior', 'Speed Junior Goalkeeper Gloves', 'Lightweight goalkeeper gloves perfect for junior players. Features enhanced grip and comfortable fit.', 34.99, '/train_with_us/gloves.svg', 'GOALKEEPER_GLOVES', 'JUNIOR', true),
        ('guante_pro_senior', 'Pro Senior Goalkeeper Gloves', 'Professional grade goalkeeper gloves for experienced keepers. Superior grip and durability.', 89.99, '/train_with_us/gloves_pro.svg', 'GOALKEEPER_GLOVES', 'SENIOR', true),
        ('guante_training', 'Training Goalkeeper Gloves', 'Durable training gloves designed for daily practice sessions. Excellent value for money.', 45.50, '/train_with_us/gloves_training.svg', 'GOALKEEPER_GLOVES', 'TRAINING', true),
        ('guante_elite_pro', 'Elite Pro Goalkeeper Gloves', 'Top-tier professional gloves with advanced grip technology and premium materials.', 129.99, '/train_with_us/gloves_elite.svg', 'GOALKEEPER_GLOVES', 'ELITE', true)
        ON CONFLICT (id) DO NOTHING;
        """

        session.execute(text(products_sql))
        session.commit()

        # Insert product sizes
        print("📏 Inserting product sizes and stock...")
        sizes_sql = """
        INSERT INTO product_sizes (product_id, size, stock_quantity, is_available) VALUES
        ('guante_speed_junior', '5', 10, true),
        ('guante_speed_junior', '6', 15, true),
        ('guante_speed_junior', '7', 8, true),
        ('guante_pro_senior', '8', 5, true),
        ('guante_pro_senior', '9', 12, true),
        ('guante_pro_senior', '10', 7, true),
        ('guante_pro_senior', '11', 3, true),
        ('guante_training', '6', 20, true),
        ('guante_training', '7', 18, true),
        ('guante_training', '8', 25, true),
        ('guante_training', '9', 15, true),
        ('guante_elite_pro', '8', 2, true),
        ('guante_elite_pro', '9', 4, true),
        ('guante_elite_pro', '10', 3, true),
        ('guante_elite_pro', '11', 1, true)
        ON CONFLICT DO NOTHING;
        """

        session.execute(text(sizes_sql))
        session.commit()

        # Insert product-tag relationships
        print("🔗 Linking products with tags...")
        product_tags_sql = """
        INSERT INTO product_tags (product_id, tag_id) 
        SELECT p.id, t.id FROM 
        (VALUES 
            ('guante_speed_junior', 'junior'),
            ('guante_speed_junior', 'ligero'),
            ('guante_pro_senior', 'profesional'),
            ('guante_pro_senior', 'grip'),
            ('guante_pro_senior', 'durabilidad'),
            ('guante_training', 'entrenamiento'),
            ('guante_training', 'durabilidad'),
            ('guante_elite_pro', 'profesional'),
            ('guante_elite_pro', 'grip')
        ) AS v(product_id, tag_name)
        JOIN products p ON p.id = v.product_id
        JOIN tags t ON t.name = v.tag_name
        ON CONFLICT DO NOTHING;
        """

        session.execute(text(product_tags_sql))
        session.commit()

        # Verify data
        print("🔍 Verifying seeded data...")
        result = session.execute(text("SELECT COUNT(*) FROM products")).fetchone()
        products_count = result[0]

        result = session.execute(text("SELECT COUNT(*) FROM product_sizes")).fetchone()
        sizes_count = result[0]

        result = session.execute(text("SELECT COUNT(*) FROM tags")).fetchone()
        tags_count = result[0]

        print("✅ Database seeded successfully!")
        print(f"📊 Products: {products_count}")
        print(f"📏 Product sizes: {sizes_count}")
        print(f"🏷️  Tags: {tags_count}")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🌱 Starting database seeding...")
    print("=" * 50)
    seed_simple_data()
    print("=" * 50)
    print("🎉 Seeding completed! You can now start the API server.")
    print("💡 Next steps:")
    print("   1. Run: python start_server.py")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Test: python test_api.py")
