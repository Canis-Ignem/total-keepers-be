from fastapi import APIRouter
from .endpoints import products, cart, campus, discount_codes

api_router = APIRouter()

# Include product endpoints
api_router.include_router(products.router, prefix="/api/v1", tags=["products"])

# Include cart endpoints
api_router.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])

# Include campus endpoints
api_router.include_router(campus.router, prefix="/api/v1/campus", tags=["campus"])

# Include discount code endpoints
api_router.include_router(
    discount_codes.router, prefix="/api/v1", tags=["discount-codes"]
)
