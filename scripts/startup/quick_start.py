"""
Simple startup script for Total Keeper API
This handles the setup step by step
"""

import os
import sys
import subprocess
import time


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def check_database():
    """Check if database is running"""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="total_keeper_db",
            user="postgres",
            password="postgres",
        )
        conn.close()
        return True
    except:
        return False


def main():
    print("🚀 Total Keeper API Setup")
    print("=" * 50)

    # Step 1: Check if database is running
    print("\n1️⃣ Checking database connection...")
    if not check_database():
        print("❌ Database not running. Starting database...")
        if not run_command("podman-compose up -d postgres", "Starting PostgreSQL"):
            print("💡 Try running: .\db-universal.ps1 start")
            return False

        # Wait for database to be ready
        print("⏳ Waiting for database to be ready...")
        for i in range(30):
            time.sleep(2)
            if check_database():
                print("✅ Database is ready!")
                break
            print(f"   Waiting... ({i + 1}/30)")
        else:
            print("❌ Database didn't start in time")
            return False
    else:
        print("✅ Database is already running!")

    # Step 2: Install dependencies
    print("\n2️⃣ Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        return False

    # Step 3: Seed database
    print("\n3️⃣ Seeding database...")
    if not run_command(
        "python scripts/database/seed_simple.py", "Seeding database with sample data"
    ):
        print("💡 Database seeding failed, but continuing...")

    # Step 4: Start API server
    print("\n4️⃣ Starting API server...")
    print("🌐 Server will start on: http://localhost:8000")
    print("📖 API docs will be at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)

    # Change to project root directory and start server
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(project_root)
    app_dir = os.path.join(project_root, "app")
    os.chdir(app_dir)

    try:
        import uvicorn

        uvicorn.run(
            "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
