"""
Discount Code API Endpoints
RESTful API for discount code management and validation
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.discount_service import get_discount_service
from app.schemas.discount_code import (
    DiscountCodeValidationRequest,
    DiscountCodeValidationResponse,
    DiscountCodeCreate,
    DiscountCodeUpdate,
    DiscountCodeResponse,
)

router = APIRouter(
    prefix="/discount-codes",
    tags=["discount-codes"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.post("/validate/{code}", response_model=DiscountCodeValidationResponse)
async def validate_discount_code(
    code: str, request: DiscountCodeValidationRequest, db: Session = Depends(get_db)
):
    """
    Validate a discount code for the given order amount
    This endpoint is used by the frontend during checkout
    """
    try:
        discount_service = get_discount_service(db)
        validation_result = discount_service.validate_discount_code(
            code=code, order_amount=request.order_amount
        )

        logger.info(
            f"Discount code validation: {code} -> valid: {validation_result.is_valid}"
        )

        return validation_result

    except Exception as e:
        logger.error(f"Error in validate_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount validation",
        )


@router.post("/apply/{code}")
async def apply_discount_code(
    code: str, request: DiscountCodeValidationRequest, db: Session = Depends(get_db)
):
    """
    Apply a discount code and increment usage count
    This endpoint should be called during order processing
    """
    try:
        discount_service = get_discount_service(db)
        discount_amount, error_message = discount_service.apply_discount_code(
            code=code, order_amount=request.order_amount
        )

        if error_message:
            logger.warning(f"Failed to apply discount code {code}: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
            )

        logger.info(f"Applied discount code {code}: {discount_amount}€ discount")

        return {
            "code": code,
            "discount_amount": discount_amount,
            "message": f"Discount applied successfully: {discount_amount}€ off",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in apply_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount application",
        )


@router.post("/", response_model=DiscountCodeResponse)
async def create_discount_code(
    discount_data: DiscountCodeCreate, db: Session = Depends(get_db)
):
    """
    Create a new discount code
    Admin endpoint for creating promotional codes
    """
    try:
        discount_service = get_discount_service(db)
        discount_code = discount_service.create_discount_code(
            discount_data=discount_data,
            created_by="admin",  # TODO: Replace with actual user ID from JWT
        )

        logger.info(f"Created discount code: {discount_code.code}")

        return discount_code

    except ValueError as e:
        logger.warning(f"Invalid discount code creation request: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount code creation",
        )


@router.get("/", response_model=List[DiscountCodeResponse])
async def list_discount_codes(active_only: bool = False, db: Session = Depends(get_db)):
    """
    List all discount codes
    Admin endpoint for managing discount codes
    """
    try:
        discount_service = get_discount_service(db)
        discount_codes = discount_service.list_discount_codes(active_only=active_only)

        logger.info(
            f"Retrieved {len(discount_codes)} discount codes (active_only: {active_only})"
        )

        return discount_codes

    except Exception as e:
        logger.error(f"Error in list_discount_codes endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount code listing",
        )


@router.get("/{code_id}", response_model=DiscountCodeResponse)
async def get_discount_code(code_id: str, db: Session = Depends(get_db)):
    """
    Get discount code by ID
    Admin endpoint for viewing specific discount codes
    """
    try:
        discount_service = get_discount_service(db)
        discount_code = discount_service.get_discount_code(code_id)

        if not discount_code:
            logger.warning(f"Discount code not found: {code_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discount code with ID '{code_id}' not found",
            )

        logger.info(f"Retrieved discount code: {discount_code.code}")

        return discount_code

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount code retrieval",
        )


@router.put("/{code_id}", response_model=DiscountCodeResponse)
async def update_discount_code(
    code_id: str, discount_data: DiscountCodeUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing discount code
    Admin endpoint for modifying discount codes
    """
    try:
        discount_service = get_discount_service(db)
        discount_code = discount_service.update_discount_code(
            code_id=code_id, discount_data=discount_data
        )

        logger.info(f"Updated discount code: {discount_code.code}")

        return discount_code

    except ValueError as e:
        logger.warning(f"Invalid discount code update request: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount code update",
        )


@router.delete("/{code_id}")
async def deactivate_discount_code(code_id: str, db: Session = Depends(get_db)):
    """
    Deactivate a discount code (soft delete)
    Admin endpoint for disabling discount codes
    """
    try:
        discount_service = get_discount_service(db)
        success = discount_service.deactivate_discount_code(code_id)

        if not success:
            logger.warning(f"Discount code not found for deactivation: {code_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discount code with ID '{code_id}' not found",
            )

        logger.info(f"Deactivated discount code: {code_id}")

        return {"message": "Discount code deactivated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deactivate_discount_code endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during discount code deactivation",
        )
