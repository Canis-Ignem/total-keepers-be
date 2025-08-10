"""
Simple test to verify PostgreSQL connection
Run this after starting the database to ensure it's working
"""

import sys
from time import sleep

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2


def test_connection():
    """Test PostgreSQL connection"""
    try:
        print("🔍 Testing PostgreSQL connection...")

        # Connection parameters
        conn_params = {
            "host": "localhost",
            "port": 5432,
            "database": "total_keeper_db",
            "user": "postgres",
            "password": "postgres",
        }

        # Try to connect
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        print("✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")

        # Test database
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"🗄️  Connected to database: {db_name[0]}")

        # Close connection
        cursor.close()
        conn.close()

        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure PostgreSQL is running: .\db.ps1 start")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def wait_for_db(max_attempts=30, delay=2):
    """Wait for database to be ready"""
    print(f"⏳ Waiting for PostgreSQL to be ready (max {max_attempts * delay}s)...")

    for attempt in range(max_attempts):
        if test_connection():
            return True

        print(f"   Attempt {attempt + 1}/{max_attempts} - retrying in {delay}s...")
        sleep(delay)

    print("❌ Database did not become ready in time")
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        success = wait_for_db()
    else:
        success = test_connection()

    sys.exit(0 if success else 1)
