"""
Startup script for Total Keeper API
This script initializes the database and starts the FastAPI server
"""

import sys
import os
import uvicorn
import logging

# Add the project root directory to Python path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from sqlalchemy import create_engine
    from app.core.database import Base, engine
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the correct directory and dependencies are installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        raise


def start_server():
    """Start the FastAPI server"""
    try:
        logger.info("Starting FastAPI server...")
        # Change to app directory for uvicorn
        app_dir = os.path.join(project_root, "app")
        os.chdir(app_dir)

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info",
        )
    except Exception as e:
        logger.error(f"❌ Error starting server: {str(e)}")
        raise


if __name__ == "__main__":
    print("🚀 Starting Total Keeper API...")
    print("=" * 50)

    # Initialize database
    create_tables()

    # Start server
    print("\n📡 Starting server on http://localhost:8000")
    print("📖 API documentation will be available at http://localhost:8000/docs")
    print("🔄 Auto-reload is enabled for development")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)

    start_server()
