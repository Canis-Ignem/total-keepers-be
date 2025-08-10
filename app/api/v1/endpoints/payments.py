from fastapi import APIRouter, HTTPException, Form, Depends, Request
from services.payment_service import (
    initiate_redsys_payment,
    process_redsys_callback,
    validate_redsys_signature,
)
from core.database import get_db
from sqlalchemy.orm import Session
from models.order import Order
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Placeholder Redsys client - will be replaced when real implementation is ready
# client = RedirectClient(secret_key=settings.REDSYS_SECRET_KEY, sandbox=settings.REDSYS_SANDBOX)


@router.post("/create-payment")
async def create_payment(
    order_id: str,
    amount: float,
    user_id: str = "anonymous",
    db: Session = Depends(get_db),
):
    """
    Create a payment request for an order
    Currently using placeholder implementation
    """
    try:
        logger.info(f"Creating payment for order {order_id}, amount: {amount}")

        # Create order in database
        db_order = Order(
            id=order_id,
            order_number=f"TK-{order_id}",
            user_id=user_id,
            subtotal=amount,
            total_amount=amount,
            status="pending",
            payment_status="pending",
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # Initiate payment (placeholder implementation)
        payment_data = initiate_redsys_payment(order_id, amount)

        return {
            "status": "success",
            "payment_data": payment_data,
            "order_id": order_id,
            "message": "Payment request created successfully (using mock implementation)",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Payment creation failed for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Payment initiation failed: {str(e)}"
        )


@router.post("/payment-callback")
async def handle_payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle payment callback from Redsys
    Currently using placeholder implementation
    """
    try:
        # Get callback data
        if request.headers.get("content-type") == "application/json":
            callback_data = await request.json()
        else:
            form_data = await request.form()
            callback_data = dict(form_data)

        logger.info(f"Received payment callback: {callback_data}")

        # Validate signature (placeholder)
        if not validate_redsys_signature(callback_data):
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Process callback (placeholder)
        result = process_redsys_callback(callback_data)

        # Update order status
        order_id = result.get("order_id")
        if order_id and order_id != "unknown":
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.payment_status = (
                    "captured" if result["status"] == "success" else "failed"
                )
                order.status = (
                    "confirmed" if result["status"] == "success" else "cancelled"
                )
                order.payment_reference = result.get("transaction_id")
                db.commit()

                return {
                    "status": "success",
                    "order_id": order_id,
                    "payment_status": order.payment_status,
                    "message": "Payment processed successfully (mock implementation)",
                }
            else:
                raise HTTPException(status_code=404, detail="Order not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment callback processing failed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Error processing payment callback: {str(e)}"
        )


@router.post("/payment-response")
async def handle_payment_response(
    Ds_Signature: str = Form(None),
    Ds_MerchantParameters: str = Form(None),
    Ds_SignatureVersion: str = Form(None),
    order_id: str = Form(None),
    status: str = Form("success"),
    db: Session = Depends(get_db),
):
    """
    Handle payment response (for testing and mock implementation)
    """
    try:
        logger.info(f"Payment response received for order: {order_id}")

        # For mock implementation, use simple form data
        if order_id:
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                if status == "success":
                    order.payment_status = "captured"
                    order.status = "confirmed"
                else:
                    order.payment_status = "failed"
                    order.status = "cancelled"

                order.payment_reference = f"mock_txn_{order_id}"
                db.commit()

                return {
                    "status": "success" if status == "success" else "failed",
                    "order_id": order_id,
                    "payment_status": order.payment_status,
                    "message": f"Payment {'completed' if status == 'success' else 'failed'} (mock implementation)",
                }
            else:
                raise HTTPException(status_code=404, detail="Order not found")

        # TODO: Implement actual Redsys response processing when ready
        """
        response = client.create_response(Ds_Signature, Ds_MerchantParameters, Ds_SignatureVersion)
        if response.is_paid():
            order_id = response.order
            order = db.query(Order).filter(Order.id == order_id).first()
            if order:
                order.payment_status = "captured"
                order.status = "confirmed"
                db.commit()
                return {"status": "success", "order_id": order_id}
            raise HTTPException(status_code=404, detail="Order not found")
        else:
            raise HTTPException(status_code=400, detail=f"Payment failed: {response.response_message}")
        """

        raise HTTPException(status_code=400, detail="Missing order_id in request")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment response processing failed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Error processing payment response: {str(e)}"
        )


@router.get("/payment-status/{order_id}")
async def get_payment_status(order_id: str, db: Session = Depends(get_db)):
    """
    Get payment status for an order
    """
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return {
            "order_id": order_id,
            "order_status": order.status,
            "payment_status": order.payment_status,
            "amount": order.total_amount,
            "payment_reference": order.payment_reference,
            "created_at": order.created_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status for order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
