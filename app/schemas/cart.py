from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CartItemBase(BaseModel):
    product_id: str
    size: str
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(CartItemBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Product details for frontend
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    product_img: Optional[str] = None
    product_description: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, cart_item):
        """Custom from_orm to include product details"""
        return cls(
            id=cart_item.id,
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            size=cart_item.size,
            quantity=cart_item.quantity,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
            product_name=cart_item.product.name if cart_item.product else None,
            product_price=cart_item.product.price if cart_item.product else None,
            product_img=cart_item.product.img if cart_item.product else None,
            product_description=cart_item.product.description
            if cart_item.product
            else None,
        )


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_amount: float
    total_items: int

    class Config:
        from_attributes = True
