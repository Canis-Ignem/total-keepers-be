"""
Order creation request/response schemas for secure order processing
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class OrderItemRequest(BaseModel):
    """Individual item in an order"""

    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name for verification")
    product_price: Decimal = Field(
        ..., description="Product price for verification", gt=0
    )
    quantity: int = Field(..., description="Quantity ordered", gt=0)
    selected_size: Optional[str] = Field(
        None, description="Selected size if applicable"
    )

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class ShippingAddressRequest(BaseModel):
    """Shipping address information"""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=255, description="Customer email address")
    address_line_1: str = Field(..., min_length=1, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class CreateOrderRequest(BaseModel):
    """Request to create a new order - all data is validated server-side"""

    items: List[OrderItemRequest] = Field(..., min_items=1, description="Order items")
    shipping_address: ShippingAddressRequest = Field(
        ..., description="Shipping address"
    )
    promo_code: Optional[str] = Field(None, description="Promotional code")

    @validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class OrderResponse(BaseModel):
    """Order creation response"""

    order_id: str = Field(..., description="Generated order ID")
    status: str = Field(..., description="Order status")
    total_amount: Decimal = Field(..., description="Final calculated total")
    subtotal: Decimal = Field(..., description="Subtotal before taxes/fees")
    tax_amount: Decimal = Field(Decimal(0), description="Tax amount")
    shipping_amount: Decimal = Field(..., description="Shipping cost")
    discount_amount: Decimal = Field(0, description="Discount applied")
    payment_url: Optional[str] = Field(None, description="Payment processing URL")
    created_at: datetime = Field(..., description="Order creation timestamp")

    class Config:
        json_encoders = {Decimal: lambda v: float(v), datetime: lambda v: v.isoformat()}


class OrderStatusResponse(BaseModel):
    """Order status inquiry response"""

    order_id: str
    status: str
    items: List[dict]
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {Decimal: lambda v: float(v), datetime: lambda v: v.isoformat()}


# Legacy schemas for backward compatibility
class OrderCreate(BaseModel):
    order_id: str
    amount: float
    user_id: str


class OrderOut(BaseModel):
    order_id: str
    amount: float
    status: str
    user_id: str

    class Config:
        from_attributes = True
