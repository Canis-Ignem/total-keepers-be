# Total Keeper Backend - Project Structure

## 📁 Project Organization

```
total-keeper-be/
├── app/                          # Main application code
│   ├── api/                      # API endpoints
│   ├── core/                     # Core configurations
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   └── tests/                    # Unit tests for app modules
├── alembic/                      # Database migrations
├── docs/                         # Documentation
│   ├── AUTHENTICATION_GUIDE.md   # Authentication setup guide
│   └── PROJECT_STRUCTURE.md      # This file
├── scripts/                      # Utility scripts
│   ├── database/                 # Database management scripts
│   │   ├── db.ps1               # Windows database management
│   │   ├── db.sh                # Unix database management
│   │   ├── db-universal.ps1     # Cross-platform database script
│   │   ├── seed_simple.py       # Simple database seeding
│   │   ├── seed_products.py     # Product-specific seeding
│   │   └── reset_db.py          # Database reset utility
│   └── startup/                  # Application startup scripts
│       ├── start_server.py      # Production server startup
│       └── quick_start.py       # Development quick start
├── tests/                        # Integration and end-to-end tests
│   ├── test.py                  # General tests
│   ├── test_api.py              # API endpoint tests
│   ├── test_auth.py             # Authentication tests
│   ├── test_db_connection.py    # Database connection tests
│   └── test_models.py           # Model tests
├── docker/                       # Docker configurations
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── docker-compose.yml           # Container orchestration
├── alembic.ini                  # Migration configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Main project documentation
```

## 🚀 Quick Start Commands

### Database Management
```bash
# Start database (Windows)
.\scripts\database\db-universal.ps1 start

# Seed database with sample data
python scripts\database\seed_simple.py

# Reset database (WARNING: Deletes all data)
python scripts\database\reset_db.py
```

### Application Startup
```bash
# Quick development setup
python scripts\startup\quick_start.py

# Start server only
python scripts\startup\start_server.py
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Check current migration
alembic current
```

### Testing
```bash
# Run API tests
python tests\test_api.py

# Test database connection
python tests\test_db_connection.py

# Test authentication
python tests\test_auth.py

# Test models
python tests\test_models.py
```

## 📋 File Descriptions

### Core Application (`app/`)
- **main.py**: FastAPI application entry point
- **models/**: SQLAlchemy database models (User, Product, Order, etc.)
- **schemas/**: Pydantic models for request/response validation
- **api/**: REST API endpoints organized by version
- **services/**: Business logic and data processing
- **core/**: Configuration, database, security, logging

### Scripts (`scripts/`)
- **database/seed_simple.py**: Creates tables and seeds with goalkeeper gloves data
- **database/reset_db.py**: Completely resets the database
- **startup/quick_start.py**: All-in-one development setup
- **startup/start_server.py**: Production server startup with table creation

### Tests (`tests/`)
- **test_api.py**: Comprehensive API endpoint testing
- **test_auth.py**: Authentication and authorization tests
- **test_models.py**: Database model validation
- **test_db_connection.py**: Database connectivity verification

### Documentation (`docs/`)
- **AUTHENTICATION_GUIDE.md**: OAuth setup and configuration
- **PROJECT_STRUCTURE.md**: This organizational guide

## 🔧 Development Workflow

1. **Setup**: `python scripts\startup\quick_start.py`
2. **Develop**: Modify code in `app/`
3. **Test**: Run relevant tests from `tests/`
4. **Migrate**: Use Alembic for database changes
5. **Deploy**: Use Docker Compose for production

## 📝 Notes

- All scripts are designed to work from the project root directory
- Database scripts handle both development and production environments
- Tests can be run individually or as a suite
- Migration files are auto-generated but should be reviewed before applying
