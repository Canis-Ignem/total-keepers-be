"""
Comprehensive Redsys payment endpoints
Handles payment creation, processing, callbacks, and status checking
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.payment_service import redsys_service
from app.schemas.payment import (
    RedsysPaymentRequest,
    RedsysPaymentInitResponse,
    PaymentStatusResponse,
    RedsysTransactionResponse,
    RedsysCallbackData,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhook-test")
async def webhook_test(request: Request):
    """
    Test endpoint to verify external access to webhook endpoints
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    logger.info(
        f"🧪 Webhook test accessed from IP: {client_ip}, User-Agent: {user_agent}"
    )

    return {
        "status": "success",
        "message": "Webhook endpoint is accessible",
        "client_ip": client_ip,
        "timestamp": "2025-09-13T20:30:00Z",
    }


@router.post("/create-redsys-payment", response_model=RedsysPaymentInitResponse)
async def create_redsys_payment(
    payment_request: RedsysPaymentRequest, db: Session = Depends(get_db)
):
    """
    Create a new Redsys payment request
    Returns form data needed to redirect user to Redsys payment page
    """
    try:
        logger.info(f"Creating Redsys payment for order {payment_request.order_id}")

        payment_response = redsys_service.create_payment(payment_request, db)

        logger.info(f"Payment created successfully: {payment_response.payment_id}")
        return payment_response

    except ValueError as e:
        logger.error(f"Validation error creating payment: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        )


@router.post("/redsys-callback")
async def handle_redsys_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Redsys payment callback/notification
    This endpoint receives POST requests from Redsys after payment processing
    Includes security measures to prevent malicious triggering of email notifications
    """
    try:
        # Security: Log the request for audit purposes
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(
            f"🔔 Payment callback received from IP: {client_ip}, User-Agent: {user_agent}"
        )

        # Log all headers for debugging
        logger.info(f"📋 Callback headers: {dict(request.headers)}")

        # Parse form data from Redsys
        form_data = await request.form()
        logger.info(f"📋 Form data keys: {list(form_data.keys())}")

        callback_data = RedsysCallbackData(
            ds_signature_version=form_data.get("Ds_SignatureVersion", ""),
            ds_merchant_parameters=form_data.get("Ds_MerchantParameters", ""),
            ds_signature=form_data.get("Ds_Signature", ""),
        )

        # Security: Validate callback data is present
        if not callback_data.ds_merchant_parameters or not callback_data.ds_signature:
            logger.warning(f"❌ Invalid callback data received from {client_ip}")
            logger.warning(
                f"   - ds_merchant_parameters present: {bool(callback_data.ds_merchant_parameters)}"
            )
            logger.warning(
                f"   - ds_signature present: {bool(callback_data.ds_signature)}"
            )
            raise ValueError("Missing required callback parameters")

        logger.info(
            f"🔄 Received Redsys callback: {callback_data.ds_merchant_parameters[:50]}..."
        )

        # Process callback - this includes signature verification
        # Email notifications are only sent if signature verification passes
        logger.info("🔍 Processing callback through payment service...")
        result = redsys_service.process_callback(callback_data, db)

        logger.info(f"✅ Callback processed successfully: {result}")
        logger.info(
            f"📋 Payment details - ID: {result.get('payment_id')}, Order: {result.get('order_id')}, Status: {result.get('payment_status')}, Approved: {result.get('approved')}"
        )

        # Log if this was an approved payment (should trigger email)
        if result.get("approved"):
            logger.info(
                f"💰 Payment approved - Spanish invoice email should have been sent for order {result.get('order_id')}"
            )
        else:
            logger.info(
                f"❌ Payment not approved - no email sent for order {result.get('order_id')}"
            )

        # Return simple response for Redsys (they expect minimal response)
        return JSONResponse(status_code=200, content={"status": "ok"})

    except ValueError as e:
        logger.error(f"Validation error processing callback from {client_ip}: {e}")
        return JSONResponse(
            status_code=400, content={"status": "error", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error processing callback from {client_ip}: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"},
        )


@router.get("/payment-status/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(payment_id: str, db: Session = Depends(get_db)):
    """
    Get current status of a payment
    """
    try:
        status_response = redsys_service.get_payment_status(payment_id, db)
        return status_response

    except ValueError as e:
        logger.error(f"Payment not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment status",
        )


@router.get("/payment-details/{payment_id}", response_model=RedsysTransactionResponse)
async def get_payment_details(payment_id: str, db: Session = Depends(get_db)):
    """
    Get detailed Redsys transaction information
    """
    try:
        transaction_response = redsys_service.get_transaction_details(payment_id, db)
        return transaction_response

    except ValueError as e:
        logger.error(f"Transaction not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transaction details",
        )
