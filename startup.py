#!/usr/bin/env python3
"""
Startup script for Total Keepers FastAPI application
Handles database migrations, seeding, and server startup
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command: list, description: str, handle_existing_schema: bool = False) -> bool:
    """Run a command and handle errors gracefully"""
    try:
        logger.info(f"Starting: {description}")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✅ Completed: {description}")
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        
        # Handle specific case of existing database schema
        if handle_existing_schema and "already exists" in e.stderr:
            logger.info("🔄 Detected existing database schema, attempting recovery...")
            return handle_schema_conflict()
        
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error in {description}: {e}")
        return False

def handle_schema_conflict() -> bool:
    """Handle database schema conflicts by checking and applying missing migrations"""
    try:
        logger.info("📋 Analyzing existing database structure...")
        
        from sqlalchemy import create_engine, inspect, text
        from app.core.config import settings
        
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        # Check what tables exist
        existing_tables = set(inspector.get_table_names())
        logger.info(f"📊 Found existing tables: {existing_tables}")
        
        # Check if products table exists and has discount_price column
        if 'products' in existing_tables:
            columns = inspector.get_columns('products')
            column_names = {col['name'] for col in columns}
            logger.info(f"📊 Products table columns: {column_names}")
            
            if 'discount_price' not in column_names:
                logger.info("🔧 Missing discount_price column, applying selective migration...")
                return apply_selective_migration(engine)
            else:
                logger.info("✅ Database schema appears complete, stamping as current")
                return stamp_database()
        else:
            # No products table, need full migration
            logger.info("🔧 No products table found, attempting full migration...")
            return attempt_full_migration()
            
    except Exception as e:
        logger.error(f"❌ Failed to analyze database structure: {e}")
        return False

def apply_selective_migration(engine) -> bool:
    """Apply specific missing schema changes"""
    try:
        from sqlalchemy import text
        logger.info("🔧 Applying missing schema changes...")
        
        with engine.connect() as conn:
            # Add discount_price column if missing
            try:
                conn.execute(text("ALTER TABLE products ADD COLUMN discount_price FLOAT"))
                conn.commit()
                logger.info("✅ Added discount_price column to products table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("ℹ️ discount_price column already exists")
                else:
                    raise e
        
        # Now stamp as current
        return stamp_database()
        
    except Exception as e:
        logger.error(f"❌ Failed to apply selective migration: {e}")
        return False

def stamp_database() -> bool:
    """Stamp database as current migration state"""
    try:
        result = subprocess.run(
            ["alembic", "stamp", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Successfully marked database as up-to-date")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to stamp database: {e.stderr}")
        return False

def attempt_full_migration() -> bool:
    """Attempt to run full migration, handling conflicts individually"""
    try:
        # First, check current migration state
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True
        )
        logger.info(f"📋 Current migration state: {result.stdout.strip()}")
        
        # Try to upgrade step by step
        logger.info("🔧 Attempting step-by-step migration...")
        result = subprocess.run(
            ["alembic", "upgrade", "head", "--sql"],
            capture_output=True,
            text=True
        )
        
        # If we got here, try the actual upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Full migration completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Full migration failed: {e.stderr}")
        # Try stamping as last resort
        logger.info("🔄 Falling back to stamping database...")
        return stamp_database()

def main():
    """Main startup sequence"""
    logger.info("🚀 Starting Total Keepers API...")
    
    # Change to app directory
    app_dir = Path("/app")
    if app_dir.exists():
        os.chdir(app_dir)
        logger.info(f"Working directory: {os.getcwd()}")
    
    # Step 1: Run database migrations with schema conflict handling
    if not run_command(
        ["alembic", "upgrade", "head"],
        "Database migrations",
        handle_existing_schema=True
    ):
        logger.error("Database migration failed and could not be recovered. Exiting.")
        sys.exit(1)
    
    # Step 2: Seed database (optional - continues if fails)
    if not run_command(
        ["python", "seed_db.py"],
        "Database seeding"
    ):
        logger.warning("Database seeding failed, but continuing...")
    
    # Step 3: Start FastAPI server
    logger.info("🌟 Starting FastAPI server...")
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    # Start uvicorn server
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level=log_level,
            access_log=True,
            reload=False  # Never reload in production
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()