#!/usr/bin/env python3
"""
Reset database script - removes all tables and data
"""

import psycopg2


def reset_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="total_keeper_db",
            user="postgres",
            password="postgres",
        )
        cursor = conn.cursor()

        print("🗑️  Resetting database schema...")
        cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ Database schema reset successfully!")
        return True

    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False


if __name__ == "__main__":
    reset_database()
