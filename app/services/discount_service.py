"""
Discount Code Service
Business logic for discount code validation and management
"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.models.discount_code import DiscountCode
from app.schemas.discount_code import (
    DiscountCodeValidationResponse,
    DiscountCodeCreate,
    DiscountCodeUpdate,
    DiscountCodeResponse,
)

logger = logging.getLogger(__name__)


class DiscountCodeService:
    """Service for managing discount codes"""

    def __init__(self, db: Session):
        self.db = db

    def validate_discount_code(
        self, code: str, order_amount: float = 0.0
    ) -> DiscountCodeValidationResponse:
        """
        Validate a discount code for the given order amount
        Returns detailed validation response
        """
        try:
            # Find the discount code (case-insensitive)
            discount_code = (
                self.db.query(DiscountCode)
                .filter(DiscountCode.code.ilike(code.strip()))
                .first()
            )

            if not discount_code:
                logger.info(f"Discount code '{code}' not found")
                return DiscountCodeValidationResponse(
                    is_valid=False, code=code, error_message="Invalid discount code"
                )

            # Validate the discount code
            is_valid, error_message = discount_code.is_valid(order_amount)

            if not is_valid:
                logger.info(
                    f"Discount code '{code}' validation failed: {error_message}"
                )
                return DiscountCodeValidationResponse(
                    is_valid=False, code=code, error_message=error_message
                )

            # Calculate discount amount
            discount_amount = discount_code.calculate_discount(order_amount)

            logger.info(
                f"Discount code '{code}' validated successfully: {discount_amount}€ discount"
            )

            return DiscountCodeValidationResponse(
                is_valid=True,
                code=discount_code.code,
                discount_type=discount_code.discount_type,
                discount_value=float(discount_code.discount_value),
                discount_amount=discount_amount,
                description=discount_code.description,
                min_order_amount=float(discount_code.min_order_amount),
                max_discount_amount=float(discount_code.max_discount_amount)
                if discount_code.max_discount_amount
                else None,
            )

        except Exception as e:
            logger.error(f"Error validating discount code '{code}': {e}")
            return DiscountCodeValidationResponse(
                is_valid=False,
                code=code,
                error_message="Error validating discount code",
            )

    def apply_discount_code(
        self, code: str, order_amount: float
    ) -> tuple[float, Optional[str]]:
        """
        Apply discount code and return (discount_amount, error_message)
        This method also increments usage count if successful
        """
        try:
            # Find and validate the discount code
            discount_code = (
                self.db.query(DiscountCode)
                .filter(DiscountCode.code.ilike(code.strip()))
                .first()
            )

            if not discount_code:
                return 0.0, "Invalid discount code"

            # Validate the discount code
            is_valid, error_message = discount_code.is_valid(order_amount)

            if not is_valid:
                return 0.0, error_message

            # Calculate discount amount
            discount_amount = discount_code.calculate_discount(order_amount)

            # Increment usage count
            discount_code.increment_usage()
            self.db.commit()

            logger.info(
                f"Applied discount code '{code}': {discount_amount}€ discount (usage: {discount_code.current_uses})"
            )

            return discount_amount, None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error applying discount code '{code}': {e}")
            return 0.0, "Error applying discount code"

    def create_discount_code(
        self, discount_data: DiscountCodeCreate, created_by: str = None
    ) -> DiscountCodeResponse:
        """Create a new discount code"""
        try:
            # Check if code already exists
            existing_code = (
                self.db.query(DiscountCode)
                .filter(DiscountCode.code.ilike(discount_data.code.strip()))
                .first()
            )

            if existing_code:
                raise ValueError(f"Discount code '{discount_data.code}' already exists")

            # Create new discount code
            discount_code = DiscountCode(
                id=str(uuid.uuid4()),
                code=discount_data.code.upper().strip(),
                description=discount_data.description,
                discount_type=discount_data.discount_type,
                discount_value=discount_data.discount_value,
                min_order_amount=discount_data.min_order_amount or 0.0,
                max_discount_amount=discount_data.max_discount_amount,
                is_active=discount_data.is_active,
                start_date=discount_data.start_date,
                end_date=discount_data.end_date,
                max_uses=discount_data.max_uses,
                max_uses_per_customer=discount_data.max_uses_per_customer,
                created_by=created_by,
                notes=discount_data.notes,
                updated_at=datetime.now(timezone.utc),  # Set updated_at explicitly
            )

            self.db.add(discount_code)
            self.db.commit()
            self.db.refresh(discount_code)

            logger.info(
                f"Created discount code '{discount_code.code}' with {discount_code.discount_value}% discount"
            )

            return DiscountCodeResponse.from_orm(discount_code)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating discount code: {e}")
            raise

    def update_discount_code(
        self, code_id: str, discount_data: DiscountCodeUpdate
    ) -> DiscountCodeResponse:
        """Update an existing discount code"""
        try:
            discount_code = (
                self.db.query(DiscountCode).filter(DiscountCode.id == code_id).first()
            )

            if not discount_code:
                raise ValueError(f"Discount code with ID '{code_id}' not found")

            # Update fields
            for field, value in discount_data.dict(exclude_unset=True).items():
                setattr(discount_code, field, value)

            discount_code.updated_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(discount_code)

            logger.info(f"Updated discount code '{discount_code.code}'")

            return DiscountCodeResponse.from_orm(discount_code)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating discount code: {e}")
            raise

    def get_discount_code(self, code_id: str) -> Optional[DiscountCodeResponse]:
        """Get discount code by ID"""
        discount_code = (
            self.db.query(DiscountCode).filter(DiscountCode.id == code_id).first()
        )

        if not discount_code:
            return None

        return DiscountCodeResponse.from_orm(discount_code)

    def list_discount_codes(
        self, active_only: bool = False
    ) -> List[DiscountCodeResponse]:
        """List all discount codes"""
        query = self.db.query(DiscountCode)

        if active_only:
            query = query.filter(DiscountCode.is_active)

        discount_codes = query.order_by(DiscountCode.created_at.desc()).all()

        return [DiscountCodeResponse.from_orm(code) for code in discount_codes]

    def deactivate_discount_code(self, code_id: str) -> bool:
        """Deactivate a discount code"""
        try:
            discount_code = (
                self.db.query(DiscountCode).filter(DiscountCode.id == code_id).first()
            )

            if not discount_code:
                return False

            discount_code.is_active = False
            discount_code.updated_at = datetime.now(timezone.utc)

            self.db.commit()

            logger.info(f"Deactivated discount code '{discount_code.code}'")

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating discount code: {e}")
            return False


def get_discount_service(db: Session) -> DiscountCodeService:
    """Factory function to get discount code service"""
    return DiscountCodeService(db)
