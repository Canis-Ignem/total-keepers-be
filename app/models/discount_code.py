"""
Discount Code Model
Handles promotional discount codes with security and validation
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Text
from sqlalchemy.sql import func
from datetime import datetime, timezone
from app.core.database import Base


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(String, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200), nullable=True)

    # Discount details
    discount_type = Column(String(20), default="percentage")  # "percentage" or "fixed"
    discount_value = Column(
        Numeric(10, 2), nullable=False
    )  # Percentage (10.00) or fixed amount

    # Validation rules
    min_order_amount = Column(
        Numeric(10, 2), default=0.00
    )  # Minimum order to apply discount
    max_discount_amount = Column(
        Numeric(10, 2), nullable=True
    )  # Cap on discount amount

    # Availability
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Total uses allowed (None = unlimited)
    max_uses_per_customer = Column(Integer, default=1)  # Uses per customer
    current_uses = Column(Integer, default=0)  # Current usage count

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)  # Admin who created the code
    notes = Column(Text, nullable=True)  # Internal notes

    def is_valid(self, order_amount: float = 0.0) -> tuple[bool, str]:
        """
        Check if discount code is valid for use
        Returns (is_valid, error_message)
        """
        now = datetime.now(timezone.utc)

        # Check if active
        if not self.is_active:
            return False, "Discount code is not active"

        # Check start date
        if self.start_date and now < self.start_date:
            return False, "Discount code is not yet active"

        # Check end date
        if self.end_date and now > self.end_date:
            return False, "Discount code has expired"

        # Check usage limits
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, "Discount code has reached its usage limit"

        # Check minimum order amount
        if order_amount < float(self.min_order_amount):
            return (
                False,
                f"Minimum order amount of €{self.min_order_amount:.2f} required",
            )

        return True, ""

    def calculate_discount(self, order_amount: float) -> float:
        """
        Calculate discount amount for given order total
        """
        if not self.is_valid(order_amount)[0]:
            return 0.0

        if self.discount_type == "percentage":
            discount_amount = order_amount * (float(self.discount_value) / 100)
        else:  # fixed amount
            discount_amount = float(self.discount_value)

        # Apply maximum discount cap if set
        if self.max_discount_amount:
            discount_amount = min(discount_amount, float(self.max_discount_amount))

        # Ensure discount doesn't exceed order amount
        discount_amount = min(discount_amount, order_amount)

        return round(discount_amount, 2)

    def increment_usage(self):
        """Increment the usage count"""
        self.current_uses += 1

    def __repr__(self):
        return f"<DiscountCode(code='{self.code}', discount={self.discount_value}%, active={self.is_active})>"
