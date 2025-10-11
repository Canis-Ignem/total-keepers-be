from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import (
    products,
    auth,
    users,
    cart,
    campus,
    orders,
    payments,
    discount_codes,
)
from fastapi import Depends
from app.core.config import settings
from app.core.security import jwt_auth

app = FastAPI(
    title="Total Keeper E-commerce API",
    description="E-commerce API for goalkeeper gloves with user authentication and Redsys payment processing",
    version="1.0.0",
)

# CORS for Next.js front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    products.router,
    prefix="/api/v1",
    tags=["products"],
    dependencies=[Depends(jwt_auth)],
)
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"],
    dependencies=[Depends(jwt_auth)],
)
app.include_router(
    users.router, prefix="/api/v1", tags=["users"], dependencies=[Depends(jwt_auth)]
)
app.include_router(
    cart.router, prefix="/api/v1/cart", tags=["cart"], dependencies=[Depends(jwt_auth)]
)
app.include_router(
    campus.router,
    prefix="/api/v1/campus",
    tags=["campus"],
    dependencies=[Depends(jwt_auth)],
)
app.include_router(
    orders.router,
    prefix="/api/v1/orders",
    tags=["orders"],
    # Removed jwt_auth dependency to allow guest orders
)
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(discount_codes.router, prefix="/api/v1", tags=["discount-codes"])


@app.get("/")
async def root():
    return {
        "message": "Total Keeper E-commerce API",
        "version": "1.0.0",
        "features": [
            "products",
            "authentication",
            "social_login",
            "orders",
            "redsys_payments",
        ],
    }
