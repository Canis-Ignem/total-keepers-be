# Production Database Seeding Guide

This guide explains how to seed your production PostgreSQL database with goalkeeper gloves products and discount codes.

## Files

- **`seed_db_production.py`** - Main production seeding script with full error handling
- **`seed_db_quick.py`** - Interactive script that prompts for database connection details
- **`seed_db.py`** - Original development seeding script

## Prerequisites

1. **Python Environment**: Make sure you have the required dependencies installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Alembic**: The script requires Alembic for database migrations
   ```bash
   pip install alembic
   ```

3. **Database Access**: You need access to your production PostgreSQL database with:
   - Database host/server address
   - Database name
   - Username and password with CREATE/INSERT permissions
   - SSL connection (recommended for production)

## Method 1: Using Environment Variables (Recommended)

### Step 1: Set the DATABASE_URL environment variable

**Windows PowerShell:**
```powershell
$env:DATABASE_URL="postgresql://username:password@host:5432/database?sslmode=require"
```

**Linux/Mac:**
```bash
export DATABASE_URL="postgresql://username:password@host:5432/database?sslmode=require"
```

### Step 2: Run the seeder
```bash
python seed_db_production.py
```

## Method 2: Interactive Quick Setup

Run the interactive script that will prompt for connection details:

```bash
python seed_db_quick.py
```

This script will ask for:
- Database host
- Port (default: 5432)
- Database name
- Username
- Password (hidden input)
- SSL mode (default: require)

## Database URL Examples

### Azure PostgreSQL
```
postgresql://username@servername:password@servername.postgres.database.azure.com:5432/database?sslmode=require
```

### AWS RDS PostgreSQL
```
postgresql://username:password@rds-endpoint.region.rds.amazonaws.com:5432/database?sslmode=require
```

### Google Cloud SQL PostgreSQL
```
postgresql://username:password@google-cloud-sql-ip:5432/database?sslmode=require
```

### Self-hosted PostgreSQL with SSL
```
postgresql://username:password@your-server.com:5432/database?sslmode=require
```

### Local PostgreSQL (no SSL)
```
postgresql://username:password@localhost:5432/database
```

## What Gets Seeded

### Products
- **GOTI PRO - WHITE**: High-end armored goalkeeper glove
- **GEKKO LIGHT PRO - BLACK**: Lightweight professional glove

Each product includes:
- Multiple sizes (5 to 9.5)
- Stock quantities
- Regular and discount prices
- Spanish and English translations
- Product tags and categories

### Discount Codes
- **PROMO10**: 10% discount for new customers
- **KR10**: 10% promotional discount
- **AG10**: 10% promotional discount

Each discount code:
- 10% off order total (excluding shipping)
- Minimum order: €20
- Maximum discount: €50
- Valid for 1 year
- Maximum 1M total uses
- 3 uses per customer

## Safety Features

### Automatic Schema Updates
The script automatically runs Alembic migrations to ensure your database schema is up to date before seeding data.

### Connection Testing
The script tests the database connection before making any changes.

### Migration Fallback
If Alembic migrations fail, the script falls back to direct table creation for basic functionality.

### Data Confirmation
Before clearing existing data, the script asks for confirmation:
```
⚠️  WARNING: This will DELETE ALL existing products and discount codes!
Are you sure you want to continue? (yes/no):
```

### Transaction Safety
All operations are wrapped in database transactions. If any error occurs, all changes are rolled back.

### URL Masking
Database passwords are masked in log output for security.

## Usage Examples

### First-time setup (clear existing data)
```bash
$env:DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
python seed_db_production.py
# Answer "yes" to clear existing data
```

### Add products to existing database
```bash
$env:DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
python seed_db_production.py
# Answer "no" to keep existing data
```

### Using the interactive script
```bash
python seed_db_quick.py
# Follow the prompts
```

## Troubleshooting

### Connection Issues
```
❌ Database connection failed: could not connect to server
```
**Solutions:**
- Check host, port, username, and password
- Ensure the database server is accessible
- Check firewall rules
- Verify SSL requirements

### Permission Issues
```
❌ Error: permission denied for table products
```
**Solutions:**
- Ensure user has CREATE, INSERT, UPDATE permissions
- Check if user can create tables in the database
- Verify user has access to the specific database

### Migration Issues
```
❌ Alembic migration failed: revision not found
```
**Solutions:**
- Ensure `alembic.ini` is in the same directory as the script
- Check that the `alembic/` directory exists with migration files
- Verify Alembic is installed: `pip install alembic`
- The script will automatically fall back to table creation if migrations fail

### SSL Certificate Issues
```
❌ Error: SSL connection failed
```
**Solutions:**
- Try `sslmode=require` instead of `verify-full`
- For development only: use `sslmode=disable`
- Ensure server supports SSL connections

### Table Already Exists
```
❌ Error: table "products" already exists
```
This is usually not an error. The script handles existing tables gracefully.

## Security Notes

1. **Never commit database URLs** with passwords to version control
2. **Use environment variables** for sensitive connection details
3. **Always use SSL** (`sslmode=require`) for production databases
4. **Limit database user permissions** to only what's needed
5. **Use strong passwords** for database accounts

## Database Schema

The script creates these tables if they don't exist:
- `products` - Main product information
- `product_translations` - Multi-language product descriptions
- `product_sizes` - Available sizes and stock
- `tags` - Product tags
- `product_tags` - Many-to-many relationship
- `discount_codes` - Promotional codes

## Monitoring

After seeding, the script provides a summary:
```
📊 Summary:
   Products in database: 2
   Discount codes in database: 3
```

## Next Steps

After successful seeding:
1. Verify data in your database
2. Test the API endpoints
3. Update your frontend application
4. Configure any additional environment variables needed