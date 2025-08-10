from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import products, auth, users, cart, campus  # Import campus
from .core.config import settings
# from api.v1.endpoints import orders, payments  # Import when needed

app = FastAPI(
    title="Total Keeper E-commerce API",
    description="E-commerce API for goalkeeper gloves with user authentication",
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
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(campus.router, prefix="/api/v1/campus", tags=["campus"])
# app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
# app.include_router(payments.router, prefix="/api/v1", tags=["payments"])


@app.get("/")
async def root():
    return {
        "message": "Total Keeper E-commerce API",
        "version": "1.0.0",
        "features": ["products", "authentication", "social_login"],
    }
