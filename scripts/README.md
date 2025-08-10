# Scripts Directory

This directory contains utility scripts for managing the Total Keeper backend.

## 📂 Directory Structure

### `database/`
Scripts for database management and seeding:

- **`seed_simple.py`** - Creates all tables and seeds with sample goalkeeper gloves data
- **`seed_products.py`** - Product-specific seeding script
- **`reset_db.py`** - Completely resets the database (⚠️ Destructive operation)
- **`db-universal.ps1`** - Cross-platform database management script
- **`db.ps1`** - Windows-specific database operations
- **`db.sh`** - Unix/Linux database operations

### `startup/`
Scripts for application startup and development:

- **`quick_start.py`** - Complete development setup (database + server)
- **`start_server.py`** - Production server startup with table creation

## 🚀 Usage Examples

### Database Operations
```bash
# Seed database with fresh data
python scripts/database/seed_simple.py

# Reset database (WARNING: Deletes all data)
python scripts/database/reset_db.py

# Start database container
./scripts/database/db-universal.ps1 start
```

### Application Startup
```bash
# Quick development setup (recommended for new setups)
python scripts/startup/quick_start.py

# Start server only (assumes database is ready)
python scripts/startup/start_server.py
```

## 📋 Script Dependencies

All scripts should be run from the project root directory:
```bash
# Correct usage from project root
python scripts/database/seed_simple.py

# Incorrect usage from scripts directory
cd scripts && python database/seed_simple.py  # ❌ Don't do this
```

## 🔄 Migration Integration

These scripts work in conjunction with Alembic migrations:

1. **Development**: Use `quick_start.py` for initial setup
2. **Model Changes**: Use `alembic revision --autogenerate`
3. **Apply Changes**: Use `alembic upgrade head`
4. **Reset if Needed**: Use `reset_db.py` + re-run migrations
