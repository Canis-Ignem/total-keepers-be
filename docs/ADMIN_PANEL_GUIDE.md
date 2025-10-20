# Admin Panel Setup - Complete Guide

## Overview
Created a simple HTML/JavaScript admin panel for Total Keepers that allows product owners to perform CRUD operations on products and discount codes. The admin panel reuses existing API endpoints and only adds authentication.

## What Was Done

### 1. Created Admin HTML Interface
- **File**: `total-keepers-be/static/admin.html`
- **Features**:
  - Password-based authentication with sessionStorage
  - Two tabs: Products and Discount Codes
  - Full CRUD operations (Create, Read, Update, Delete)
  - Modal forms for creating/editing items
  - Loading states and error handling
  - Responsive design with gradient styling

### 2. Created Authentication Endpoint
- **File**: `total-keepers-be/app/api/v1/endpoints/tk_admin.py`
- **Endpoint**: `POST /api/v1/tk-admin/verify`
- **Functionality**:
  - Verifies password against `ADMIN_PASSWORD` environment variable
  - Returns authentication token on success
  - Returns 401 error on invalid password

### 3. Updated Main Application
- **File**: `total-keepers-be/app/main.py`
- **Changes**:
  - Imported `tk_admin` router
  - Registered `/api/v1/tk-admin` router for authentication
  - Mounted static files at `/admin` endpoint
  - Imported `StaticFiles` from `fastapi.staticfiles`

### 4. Added Environment Variable
- **File**: `total-keepers-be/.env`
- **Variable**: `ADMIN_PASSWORD=TotalKeepers2024!`
- **Note**: Change this password for production!

## API Endpoints Used

The admin panel uses these **existing** endpoints (no new CRUD endpoints created):

### Products
- `GET /api/v1/products/?size=100` - List all products
- `GET /api/v1/products/{id}` - Get single product
- `POST /api/v1/products/` - Create product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product

### Discount Codes
- `GET /api/v1/discount-codes/` - List all discount codes
- `GET /api/v1/discount-codes/{id}` - Get single discount code
- `POST /api/v1/discount-codes/` - Create discount code
- `PUT /api/v1/discount-codes/{id}` - Update discount code
- `DELETE /api/v1/discount-codes/{id}` - Deactivate discount code

### Admin Authentication (NEW)
- `POST /api/v1/tk-admin/verify` - Verify admin password and get token

## How to Access

1. **Start the backend server**:
   ```powershell
   cd total-keepers-be
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Open the admin panel**:
   - URL: `http://localhost:8000/admin`
   - Or: `http://localhost:8000/admin/admin.html`

3. **Login**:
   - Enter password: `TotalKeepers2024!`
   - Token is stored in sessionStorage
   - All subsequent API calls include `Authorization: Bearer {token}` header

## Authentication Flow

1. User visits `/admin`
2. JavaScript checks `sessionStorage` for existing token
3. If no token, show password prompt
4. User enters password
5. POST to `/api/v1/tk-admin/verify` with password
6. Backend verifies against `ADMIN_PASSWORD` env var
7. If valid, return token
8. Store token in `sessionStorage`
9. Add token to all API requests via `getHeaders()` function

## File Structure

```
total-keepers-be/
├── static/
│   └── admin.html          # Admin panel UI
├── app/
│   ├── main.py             # Updated: Added tk_admin router and static mount
│   └── api/
│       └── v1/
│           └── endpoints/
│               ├── tk_admin.py    # NEW: Authentication endpoint
│               ├── products.py    # EXISTING: Used by admin
│               └── discount_codes.py  # EXISTING: Used by admin
└── .env                    # Updated: Added ADMIN_PASSWORD

```

## Admin Panel Features

### Products Tab
- View all products in a table
- Create new product with form:
  - ID, Name, Short Description, Full Description
  - Category, Tag, Price, Discount Price
  - Image URL, Priority, Active status
- Edit existing products
- Delete products (soft delete in backend)

### Discount Codes Tab
- View all discount codes in a table
- Create new discount code with form:
  - ID, Code, Description
  - Discount Type (percentage/fixed)
  - Discount Value, Min Order Amount, Max Discount Amount
  - Max Uses, Max Uses Per Customer
  - Active status
- Edit existing discount codes
- Deactivate discount codes

## Security Notes

1. **Password in .env**: The admin password is stored in plain text in `.env`. Make sure to:
   - Add `.env` to `.gitignore` (already done)
   - Use Azure Container Apps environment variables in production
   - Change the default password

2. **Token Storage**: Tokens are stored in `sessionStorage`, which:
   - Clears when browser tab is closed
   - Is not shared across tabs
   - Is vulnerable to XSS (keep dependencies updated)

3. **No Token Validation**: Currently, the backend generates a token but doesn't validate it on subsequent requests. For production:
   - Implement JWT token validation
   - Add token expiration
   - Add middleware to verify tokens on protected endpoints

## Production Deployment

1. **Add to Azure Container Apps**:
   - Add `ADMIN_PASSWORD` to environment variables
   - Use a strong password (not the default)

2. **Access the admin panel**:
   - URL: `https://total-keeper-db.whitemeadow-ce92d559.northeurope.azurecontainerapps.io/admin`

3. **Protect the endpoint** (optional):
   - Add IP whitelist in Azure
   - Use Azure Front Door for additional security
   - Implement rate limiting

## Testing Checklist

- [ ] Access `/admin` and see password prompt
- [ ] Test wrong password shows error
- [ ] Test correct password stores token
- [ ] Test loading products list
- [ ] Test creating a new product
- [ ] Test editing a product
- [ ] Test deleting a product
- [ ] Test loading discount codes
- [ ] Test creating a discount code
- [ ] Test editing a discount code
- [ ] Test deactivating a discount code
- [ ] Test logout (clear sessionStorage and refresh)

## Notes

- Admin panel is intentionally simple (HTML/CSS/JS only)
- No frameworks or build steps required
- Uses existing, well-tested API endpoints
- Minimal backend changes (just auth endpoint)
- Easy to maintain and extend
