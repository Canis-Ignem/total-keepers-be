"""
Secure Order Processing Endpoints

These endpoints handle secure order creation and retrieval with server-side validation
to prevent frontend manipulation of prices, quantities, or discounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order import CreateOrderRequest, OrderResponse
from app.services.order_service import get_order_service
from app.models.order import Order

router = APIRouter()


@router.post("/create", response_model=OrderResponse)
async def create_secure_order(
    order_request: CreateOrderRequest, db: Session = Depends(get_db)
):
    """
    Creates a secure order with server-side validation

    Security features:
    - All prices verified against database
    - Product availability checked
    - Quantities validated
    - Discounts applied server-side only
    - Shipping calculated server-side only
    - Prevents frontend price manipulation
    """
    try:
        order_service = get_order_service(db)
        return order_service.validate_and_create_order(order_request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get("/", response_model=list[dict])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders with pagination"""
    orders = db.query(Order).offset(skip).limit(limit).all()
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status.value
            if hasattr(order.status, "value")
            else str(order.status),
            "customer_email": order.customer_email,
            "customer_first_name": order.customer_first_name,
            "customer_last_name": order.customer_last_name,
            "customer_phone": order.customer_phone,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
        }
        for order in orders
    ]


@router.get("/{order_id}", response_model=dict)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get specific order details"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found"
        )

    # Build items list with product details
    items = []
    for item in order.items:
        items.append({
            "product_id": item.product_id,
            "product_name": item.product.name if item.product else "Unknown",
            "size": item.size,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        })

    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status.value
        if hasattr(order.status, "value")
        else str(order.status),
        # Customer contact info
        "customer_email": order.customer_email,
        "customer_first_name": order.customer_first_name,
        "customer_last_name": order.customer_last_name,
        "customer_phone": order.customer_phone,
        # Order items
        "items": items,
        # Pricing
        "subtotal": order.subtotal,
        "tax_amount": order.tax_amount,
        "shipping_amount": order.shipping_amount,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        # Payment info
        "payment_method": order.payment_method,
        "payment_reference": order.payment_reference,
        # Shipping info
        "shipping_address": order.shipping_address,
        "shipping_city": order.shipping_city,
        "shipping_state": order.shipping_state,
        "shipping_postal_code": order.shipping_postal_code,
        "shipping_country": order.shipping_country,
        # Timestamps
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }
