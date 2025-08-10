# Total Keeper - Goalkeeper Gloves E-commerce API

A FastAPI-based e-commerce backend for selling goalkeeper gloves with complete product management, cart functionality, and payment processing.

## 🚀 Features

- ✅ **Product Management**: Complete CRUD operations for goalkeeper gloves
- ✅ **Size & Stock Management**: Track availability per product size
- ✅ **Flexible Tagging System**: Categorize products with multiple tags
- ✅ **Search & Filtering**: Advanced product search and filtering
- ✅ **Shopping Cart**: Add/remove items with size selection
- ✅ **Order Management**: Complete order processing workflow
- ✅ **Payment Integration**: Redsys payment gateway integration
- ✅ **PostgreSQL Database**: Robust data persistence with Alembic migrations
- ✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs
- ✅ **Authentication**: OAuth2 with Google, Facebook, GitHub integration

## 📋 Quick Start

### 1. Setup Database
```powershell
# Start PostgreSQL (Windows)
.\scripts\database\db-universal.ps1 start

# Or use Docker Compose
podman-compose up -d
```

### 2. One-Command Setup
```powershell
# Complete development setup (recommended)
python scripts\startup\quick_start.py
```

### 3. Manual Setup
```powershell
# Install packages
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Create tables and seed data
python scripts\database\seed_simple.py

# Start the API server
python scripts\startup\start_server.py
```

## 🗂️ Project Organization

```
total-keeper-be/
├── app/                    # Main application code
├── scripts/                # Utility scripts
│   ├── database/          # Database management
│   └── startup/           # Application startup
├── tests/                  # Test suites
├── docs/                   # Documentation
├── alembic/               # Database migrations
└── docker/                # Docker configurations
```

📋 **See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for detailed organization**

## 🔄 Database Migrations

```powershell
# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply pending migrations
alembic upgrade head

# Check current migration status
alembic current
```

## 🧪 Testing

```powershell
# Run all API tests
python tests\test_api.py

# Test authentication
python tests\test_auth.py

# Test database connection
python tests\test_db_connection.py
```

## 📖 API Endpoints

### Product Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/products` | Get paginated products with filtering |
| `GET` | `/api/v1/products/{id}` | Get specific product with availability |
| `POST` | `/api/v1/products` | Create new product |
| `PUT` | `/api/v1/products/{id}` | Update product |
| `DELETE` | `/api/v1/products/{id}` | Soft delete product |
| `PATCH` | `/api/v1/products/{id}/stock` | Update stock for specific size |

### Search & Filtering

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/products/search` | Search products by name/description |

### Tag Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/tags` | Get all tags |
| `POST` | `/api/v1/tags` | Create new tag |
| `PUT` | `/api/v1/tags/{id}` | Update tag |
| `DELETE` | `/api/v1/tags/{id}` | Delete tag |

## 🧪 Testing

### Test API Endpoints
```powershell
# Run comprehensive API tests
python test_api.py
```

### Manual Testing
```powershell
# Test individual endpoints
curl -X GET "http://localhost:8000/api/v1/products?page=1&size=10"
```

## 📊 Sample Product Data

The system comes with sample goalkeeper gloves:

```json
{
  "id": "guante_speed_junior",
  "name": "Speed Junior Goalkeeper Gloves",
  "description": "Lightweight gloves perfect for junior goalkeepers",
  "price": 34.99,
  "img": "/train_with_us/gloves.svg",
  "tag": "JUNIOR",
  "sizes": [
    {"size": "5", "stock_quantity": 10},
    {"size": "6", "stock_quantity": 15},
    {"size": "7", "stock_quantity": 8}
  ],
  "tags": ["junior", "ligero"]
}
```

## 🗄️ Database Schema

### Core Tables
- **products**: Main product information
- **product_sizes**: Size-specific stock and availability
- **tags**: Product categorization tags
- **product_tags**: Many-to-many relationship between products and tags
- **users**: Customer accounts
- **cart_items**: Shopping cart functionality
- **orders**: Order management
- **order_items**: Individual items within orders

## 🔧 Configuration

### Environment Variables (`.env`)
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/total_keeper_db

# Redsys Payment
REDSYS_SECRET_KEY=your_secret_key_here
REDSYS_MERCHANT_CODE=your_merchant_code
REDSYS_TERMINAL=001
REDSYS_SANDBOX=true
REDSYS_MERCHANT_URL=http://localhost:8000/api/v1/payments/callback
REDSYS_MERCHANT_NAME=Total Keeper

# Application
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true
ENVIRONMENT=development
```

## 📋 Product Query Examples

### Get Products with Filters
```http
GET /api/v1/products?category=GOALKEEPER_GLOVES&tag=JUNIOR&in_stock_only=true&page=1&size=10
```

### Search Products
```http
GET /api/v1/products/search?q=junior&page=1&size=5
```

### Create Product
```http
POST /api/v1/products
Content-Type: application/json

{
  "id": "new_glove_id",
  "name": "New Goalkeeper Gloves",
  "description": "Description here",
  "price": 59.99,
  "category": "GOALKEEPER_GLOVES",
  "tag": "SENIOR",
  "sizes": [
    {"size": "8", "stock_quantity": 10, "is_available": true},
    {"size": "9", "stock_quantity": 5, "is_available": true}
  ],
  "tag_names": ["professional", "grip"]
}
```

### Update Stock
```http
PATCH /api/v1/products/guante_speed_junior/stock?size=7&quantity=20
```

## 🛠️ Database Management

### Available Scripts
```powershell
# Database operations
.\db.ps1 start     # Start PostgreSQL
.\db.ps1 stop      # Stop PostgreSQL
.\db.ps1 restart   # Restart PostgreSQL
.\db.ps1 logs      # View logs
.\db.ps1 connect   # Connect to database CLI
.\db.ps1 reset     # Reset database (DESTRUCTIVE)

# Application operations
python seed_products.py    # Seed database with sample data
python start_server.py     # Start API server
python test_api.py         # Test API endpoints
```

## 🏗️ Project Structure

```
total-keeper-be/
├── app/
│   ├── api/v1/endpoints/    # API route handlers
│   ├── core/                # Configuration and database
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py             # FastAPI application
├── docker/                  # Docker configuration
├── tk-env/                  # Python virtual environment
├── docker-compose.yml       # Database container setup
├── requirements.txt         # Python dependencies
├── seed_products.py         # Database seeding
├── start_server.py          # Server startup
├── test_api.py             # API testing
└── README.md               # This file
```

## 🔐 Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement proper authentication/authorization
- Validate all input data
- Use proper CORS settings

## 📝 Development Notes

- The API uses soft deletes (sets `is_active=False`)
- Stock quantities are managed per product size
- Products support multiple tags for flexible categorization
- All timestamps include timezone information
- Pagination is implemented for all list endpoints
- Error handling includes proper HTTP status codes

## 🚀 Production Deployment

For production deployment:
1. Use a production-grade database
2. Set up proper environment variables
3. Enable HTTPS
4. Implement proper logging
5. Set up monitoring and health checks
6. Use a production WSGI server
7. Implement proper backup strategies

---

**Happy coding! 🥅⚽**
