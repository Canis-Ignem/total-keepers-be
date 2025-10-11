"""
Discount Code Schemas
Pydantic models for discount code validation and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class DiscountCodeValidationRequest(BaseModel):
    """Request to validate a discount code"""

    code: str = Field(
        ..., min_length=1, max_length=50, description="Discount code to validate"
    )
    order_amount: Optional[float] = Field(
        default=0.0, ge=0, description="Order subtotal for validation"
    )


class DiscountCodeValidationResponse(BaseModel):
    """Response for discount code validation"""

    is_valid: bool = Field(..., description="Whether the discount code is valid")
    code: str = Field(..., description="The discount code that was validated")
    discount_type: Optional[str] = Field(
        None, description="Type of discount: percentage or fixed"
    )
    discount_value: Optional[float] = Field(
        None, description="Discount percentage or fixed amount"
    )
    discount_amount: Optional[float] = Field(
        None, description="Calculated discount amount for this order"
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of the discount"
    )
    error_message: Optional[str] = Field(None, description="Error message if invalid")
    min_order_amount: Optional[float] = Field(
        None, description="Minimum order amount required"
    )
    max_discount_amount: Optional[float] = Field(
        None, description="Maximum discount amount allowed"
    )


class DiscountCodeCreate(BaseModel):
    """Schema for creating a new discount code"""

    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    discount_type: str = Field(default="percentage", pattern="^(percentage|fixed)$")
    discount_value: Decimal = Field(..., gt=0)
    min_order_amount: Optional[Decimal] = Field(default=0.0, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, gt=0)
    is_active: bool = Field(default=True)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)
    max_uses_per_customer: int = Field(default=1, gt=0)
    notes: Optional[str] = None


class DiscountCodeUpdate(BaseModel):
    """Schema for updating an existing discount code"""

    description: Optional[str] = Field(None, max_length=200)
    discount_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    discount_value: Optional[Decimal] = Field(None, gt=0)
    min_order_amount: Optional[Decimal] = Field(None, ge=0)
    max_discount_amount: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)
    max_uses_per_customer: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class DiscountCodeResponse(BaseModel):
    """Complete discount code information"""

    id: str
    code: str
    description: Optional[str]
    discount_type: str
    discount_value: float
    min_order_amount: float
    max_discount_amount: Optional[float]
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    max_uses: Optional[int]
    max_uses_per_customer: int
    current_uses: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DiscountCodeSummary(BaseModel):
    """Summary of discount code for listings"""

    id: str
    code: str
    description: Optional[str]
    discount_type: str
    discount_value: float
    is_active: bool
    current_uses: int
    max_uses: Optional[int]
    end_date: Optional[datetime]

    class Config:
        from_attributes = True
