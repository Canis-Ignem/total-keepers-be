from fastapi import APIRouter
from .endpoints import products, cart, campus

api_router = APIRouter()

# Include product endpoints
api_router.include_router(products.router, prefix="/api/v1", tags=["products"])

# Include cart endpoints
api_router.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])

# Include campus endpoints
api_router.include_router(campus.router, prefix="/api/v1/campus", tags=["campus"])
