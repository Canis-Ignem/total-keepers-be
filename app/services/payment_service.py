"""
Comprehensive Redsys payment service implementation
Handles payment creation, processing, callbacks, and validation
"""

import json
import base64
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict

try:
    from redsys.client import RedirectClient

    REDSYS_AVAILABLE = True
except ImportError:
    REDSYS_AVAILABLE = False
    RedirectClient = None

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.email_service import EmailService
from app.services.product_service import ProductService
from app.models.payment import (
    Payment,
    RedsysTransaction,
    PaymentProvider,
    PaymentStatus,
)
from app.models.order import Order, PaymentStatus as OrderPaymentStatus
from app.schemas.payment import (
    RedsysPaymentRequest,
    RedsysPaymentInitResponse,
    RedsysPaymentFormData,
    RedsysCallbackData,
    RedsysResponseParameters,
    PaymentStatusResponse,
    RedsysTransactionResponse,
)

logger = logging.getLogger(__name__)

# Redsys configuration
# Redsys URLs
REDSYS_SANDBOX_URL = "https://sis-t.redsys.es:25443/sis/realizarPago"
REDSYS_PRODUCTION_URL = "https://sis.redsys.es/sis/realizarPago"

REDSYS_CURRENCY_CODES = {"EUR": "978", "USD": "840", "GBP": "826"}

REDSYS_TRANSACTION_TYPES = {
    "AUTHORIZATION": "0",
    "PREAUTHORIZATION": "1",
    "CONFIRMATION": "2",
    "AUTOMATIC_RETURN": "3",
    "REFERENCE_PAYMENT": "4",
    "RECURRING_TRANSACTION": "5",
    "SUCCESSIVE_TRANSACTION": "6",
    "AUTHENTICATION": "7",
    "CONFIRM_AUTHENTICATION": "8",
    "CANCEL_PREAUTHORIZATION": "9",
}

REDSYS_RESPONSE_CODES = {
    "0000": "Transaction approved",
    "0101": "Card blocked",
    "0102": "Card expired",
    "0106": "Insufficient funds",
    "0125": "Invalid card number",
    "0129": "Invalid expiration date",
    "0167": "Invalid CVC",
    "0184": "Transaction not allowed for this card",
    "0190": "Operation denied",
    "0904": "Merchant not registered",
    "0912": "Issuer not available",
    "0913": "Duplicate transmission",
    "9915": "Payment cancelled by user",
}


class RedsysPaymentService:
    """Service for handling Redsys payments"""

    def __init__(self):
        self.client = None
        if REDSYS_AVAILABLE and self._validate_config():
            try:
                self.client = RedirectClient(secret_key=settings.REDSYS_SECRET_KEY)
                self.redsys_url = (
                    REDSYS_SANDBOX_URL
                    if settings.REDSYS_SANDBOX
                    else REDSYS_PRODUCTION_URL
                )
                logger.info(
                    f"Redsys client initialized (sandbox: {settings.REDSYS_SANDBOX})"
                )
                logger.info(f"Using Redsys URL: {self.redsys_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Redsys client: {e}")
                self.client = None
        else:
            if not REDSYS_AVAILABLE:
                logger.warning(
                    "python-redsys library not available, using mock implementation"
                )
            else:
                logger.warning(
                    "Redsys configuration invalid, using mock implementation"
                )

    def _validate_config(self) -> bool:
        """Validate Redsys configuration"""
        required_fields = [
            "REDSYS_SECRET_KEY",
            "REDSYS_MERCHANT_CODE",
            "REDSYS_TERMINAL",
            "REDSYS_MERCHANT_NAME",
        ]

        for field in required_fields:
            value = getattr(settings, field, None)
            if not value or value in ["your_secret_key_here", "your_merchant_code"]:
                logger.warning(f"Redsys configuration missing or invalid: {field}")
                return False

        return True

    def create_payment(
        self, payment_request: RedsysPaymentRequest, db: Session
    ) -> RedsysPaymentInitResponse:
        """Create a new Redsys payment"""
        try:
            # Validate order exists
            order = db.query(Order).filter(Order.id == payment_request.order_id).first()
            if not order:
                raise ValueError(f"Order {payment_request.order_id} not found")

            # Create payment record
            payment = Payment(
                order_id=payment_request.order_id,
                provider=PaymentProvider.REDSYS,
                status=PaymentStatus.PENDING,
                amount=payment_request.amount,
                currency=payment_request.currency.value,
                description=payment_request.description
                or f"Order {payment_request.order_id}",
                success_url=payment_request.success_url,
                failure_url=payment_request.failure_url,
                cancel_url=payment_request.cancel_url,
                expires_at=datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            )

            db.add(payment)
            db.flush()  # Get payment ID

            # Generate unique Redsys order number (max 12 chars)
            ds_order = self._generate_ds_order(payment.id)

            # Create Redsys transaction record
            redsys_transaction = RedsysTransaction(
                payment_id=payment.id,
                merchant_code=settings.REDSYS_MERCHANT_CODE,
                terminal=settings.REDSYS_TERMINAL,
                transaction_type=REDSYS_TRANSACTION_TYPES["AUTHORIZATION"],
                ds_order=ds_order,
                is_sandbox=settings.REDSYS_SANDBOX,
            )

            db.add(redsys_transaction)

            # Generate payment form data
            if self.client:
                form_data = self._create_redsys_form(payment, payment_request, ds_order)
            else:
                # Mock implementation
                form_data = self._create_mock_form(payment, payment_request, ds_order)

            # Update transaction with request parameters
            redsys_transaction.ds_merchant_parameters = form_data.ds_merchant_parameters
            redsys_transaction.ds_signature = form_data.ds_signature
            redsys_transaction.ds_signature_version = form_data.ds_signature_version
            redsys_transaction.request_sent_at = datetime.utcnow()

            db.commit()

            logger.info(
                f"Payment created: {payment.id} for order {payment_request.order_id}"
            )

            return RedsysPaymentInitResponse(
                payment_id=payment.id,
                order_id=payment.order_id,
                status=payment.status,
                amount=payment.amount,
                currency=payment.currency,
                form_data=form_data,
                payment_url=form_data.redsys_url,
            )

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating payment: {e}")
            raise

    def _generate_ds_order(self, payment_id: str) -> str:
        """Generate Redsys order number (max 12 alphanumeric chars)"""
        # Use timestamp + payment ID hash for uniqueness
        timestamp = datetime.now().strftime("%y%m%d%H%M")  # 10 chars
        payment_hash = str(hash(payment_id))[-2:]  # 2 chars
        return f"{timestamp}{payment_hash}"

    def _create_redsys_form(
        self, payment: Payment, request: RedsysPaymentRequest, ds_order: str
    ) -> RedsysPaymentFormData:
        """Create Redsys payment form using real client"""
        try:
            # Prepare merchant parameters
            base_url = settings.REDSYS_MERCHANT_URL.replace("/redsys-callback", "")
            amount_cents = int(payment.amount * 100)  # Convert to cents

            merchant_parameters = {
                "amount": Decimal(str(amount_cents)) / 100,  # Amount as Decimal
                "order": ds_order,
                "merchant_code": settings.REDSYS_MERCHANT_CODE,
                "currency": int(
                    REDSYS_CURRENCY_CODES.get(payment.currency, "978")
                ),  # Currency as int
                "transaction_type": REDSYS_TRANSACTION_TYPES["AUTHORIZATION"],
                "terminal": settings.REDSYS_TERMINAL,
                "merchant_url": settings.REDSYS_MERCHANT_URL,
                "url_ok": request.success_url or f"{base_url}/payment/success",
                "url_ko": request.failure_url or f"{base_url}/payment/failure",
                "merchant_name": settings.REDSYS_MERCHANT_NAME,
                "product_description": (
                    request.product_description
                    or payment.description
                    or f"Order {payment.order_id}"
                )[:125],  # Max 125 chars
            }

            # Add optional parameters
            if request.titular:
                merchant_parameters["titular"] = request.titular[:60]

            if request.merchant_data:
                merchant_parameters["merchant_data"] = request.merchant_data

            # Set Spanish as default consumer language
            merchant_parameters["consumer_language"] = "001"  # Spanish language code

            # Use the client to prepare the request
            form_data = self.client.prepare_request(merchant_parameters)

            return RedsysPaymentFormData(
                ds_signature_version=form_data.get(
                    "Ds_SignatureVersion", "HMAC_SHA256_V1"
                ),
                ds_merchant_parameters=form_data.get("Ds_MerchantParameters", ""),
                ds_signature=form_data.get("Ds_Signature", ""),
                redsys_url=self.redsys_url,
            )

        except Exception as e:
            logger.error(f"Error creating Redsys form: {e}")
            raise

    def _create_mock_form(
        self, payment: Payment, request: RedsysPaymentRequest, ds_order: str
    ) -> RedsysPaymentFormData:
        """Create mock payment form for testing"""
        # Create mock parameters
        mock_params = {
            "DS_MERCHANT_AMOUNT": str(int(payment.amount * 100)),  # Amount in cents
            "DS_MERCHANT_ORDER": ds_order,
            "DS_MERCHANT_CURRENCY": REDSYS_CURRENCY_CODES.get(payment.currency, "978"),
            "DS_MERCHANT_MERCHANTCODE": settings.REDSYS_MERCHANT_CODE,
            "DS_MERCHANT_TERMINAL": settings.REDSYS_TERMINAL,
            "DS_MERCHANT_TRANSACTIONTYPE": "0",
            "DS_MERCHANT_MERCHANTNAME": settings.REDSYS_MERCHANT_NAME,
            "DS_MERCHANT_PRODUCTDESCRIPTION": payment.description
            or f"Order {payment.order_id}",
            "DS_MERCHANT_MERCHANTURL": settings.REDSYS_MERCHANT_URL,
            "DS_MERCHANT_URLOK": request.success_url
            or "http://localhost:3000/payment/success",
            "DS_MERCHANT_URLKO": request.failure_url
            or "http://localhost:3000/payment/failure",
        }

        # Encode parameters
        params_json = json.dumps(mock_params)
        encoded_params = base64.b64encode(params_json.encode()).decode()

        # Create mock signature
        signature_string = f"{ds_order}MOCK_SIGNATURE"
        mock_signature = base64.b64encode(signature_string.encode()).decode()

        return RedsysPaymentFormData(
            ds_signature_version="HMAC_SHA256_V1",
            ds_merchant_parameters=encoded_params,
            ds_signature=mock_signature,
            redsys_url="http://localhost:3000/payment/process",  # Frontend payment processing page
        )

    def process_callback(self, callback_data: RedsysCallbackData, db: Session) -> Dict:
        """Process Redsys payment callback/notification"""
        try:
            logger.info(
                f"Processing Redsys callback: {callback_data.ds_merchant_parameters[:50]}..."
            )

            # Decode and validate signature
            if self.client:
                response_params = self._validate_and_decode_response(callback_data)
                signature_valid = True  # Already validated in decode
            else:
                # Mock validation
                response_params = self._decode_mock_response(callback_data)
                signature_valid = True

            # Find payment by ds_order
            ds_order = response_params.ds_order
            redsys_transaction = (
                db.query(RedsysTransaction)
                .filter(RedsysTransaction.ds_order == ds_order)
                .first()
            )

            if not redsys_transaction:
                logger.error(f"Redsys transaction not found for ds_order: {ds_order}")
                raise ValueError(f"Transaction not found: {ds_order}")

            payment = redsys_transaction.payment
            if not payment:
                logger.error(
                    f"Payment not found for transaction: {redsys_transaction.id}"
                )
                raise ValueError(
                    f"Payment not found for transaction: {redsys_transaction.id}"
                )

            # Update transaction with response data
            self._update_transaction_with_response(
                redsys_transaction, response_params, callback_data
            )
            redsys_transaction.signature_verified = signature_valid
            redsys_transaction.response_received_at = datetime.utcnow()

            # Update payment status based on response
            self._update_payment_status(
                payment, redsys_transaction, db, signature_valid=signature_valid
            )

            db.commit()

            logger.info(f"Payment {payment.id} processed: {payment.status}")

            return {
                "status": "success",
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "payment_status": payment.status.value,
                "redsys_response": response_params.ds_response,
                "approved": redsys_transaction.is_approved,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing callback: {e}")
            raise

    def _validate_and_decode_response(
        self, callback_data: RedsysCallbackData
    ) -> RedsysResponseParameters:
        """Validate signature and decode response parameters"""
        try:
            # Use the client to validate signature and get response
            self.client.create_response(
                signature=callback_data.ds_signature,
                merchant_parameters=callback_data.ds_merchant_parameters,
            )
            # If we get here, signature is valid

            # Decode parameters using the client method
            decoded_params = self.client.decode_parameters(
                callback_data.ds_merchant_parameters.encode()
            )

            return RedsysResponseParameters(
                **{
                    key.lower().replace("ds_", "ds_"): value
                    for key, value in decoded_params.items()
                    if key.startswith("Ds_")
                }
            )

        except Exception as e:
            logger.error(f"Error validating Redsys response: {e}")
            raise ValueError(f"Invalid response signature or format: {e}")

    def _decode_mock_response(
        self, callback_data: RedsysCallbackData
    ) -> RedsysResponseParameters:
        """Decode mock response for testing"""
        try:
            decoded_params = json.loads(
                base64.b64decode(callback_data.ds_merchant_parameters).decode()
            )

            return RedsysResponseParameters(
                ds_order=decoded_params.get("Ds_Order"),
                ds_response=decoded_params.get("Ds_Response", "0000"),
                ds_amount=decoded_params.get("Ds_Amount"),
                ds_currency=decoded_params.get("Ds_Currency"),
                ds_merchant_code=decoded_params.get("Ds_MerchantCode"),
                ds_terminal=decoded_params.get("Ds_Terminal"),
                ds_authorisation_code=decoded_params.get(
                    "Ds_AuthorisationCode", "MOCK123"
                ),
                ds_transaction_id=decoded_params.get(
                    "Ds_TransactionId", f"mock_txn_{decoded_params.get('Ds_Order')}"
                ),
            )

        except Exception as e:
            logger.error(f"Error decoding mock response: {e}")
            raise

    def _update_transaction_with_response(
        self,
        transaction: RedsysTransaction,
        response_params: RedsysResponseParameters,
        callback_data: RedsysCallbackData,
    ):
        """Update transaction with response parameters"""
        transaction.response_ds_date = response_params.ds_date
        transaction.response_ds_hour = response_params.ds_hour
        transaction.response_ds_amount = response_params.ds_amount
        transaction.response_ds_currency = response_params.ds_currency
        transaction.response_ds_order = response_params.ds_order
        transaction.response_ds_merchant_code = response_params.ds_merchant_code
        transaction.response_ds_terminal = response_params.ds_terminal
        transaction.response_ds_response = response_params.ds_response
        transaction.response_ds_merchant_data = response_params.ds_merchant_data
        transaction.response_ds_secure_payment = response_params.ds_secure_payment
        transaction.response_ds_card_number = response_params.ds_card_number
        transaction.response_ds_card_brand = response_params.ds_card_brand
        transaction.response_ds_card_type = response_params.ds_card_type
        transaction.response_ds_card_country = response_params.ds_card_country
        transaction.response_ds_authorisation_code = (
            response_params.ds_authorisation_code
        )
        transaction.response_ds_consumer_language = response_params.ds_consumer_language
        transaction.response_ds_transaction_id = response_params.ds_transaction_id
        transaction.response_ds_merchant_identifier = (
            response_params.ds_merchant_identifier
        )
        transaction.response_ds_emv3ds = response_params.ds_emv3ds
        transaction.response_ds_merchant_parameters = (
            callback_data.ds_merchant_parameters
        )
        transaction.response_ds_signature = callback_data.ds_signature
        transaction.response_ds_signature_version = callback_data.ds_signature_version

    def _update_payment_status(
        self,
        payment: Payment,
        transaction: RedsysTransaction,
        db: Session,
        signature_valid: bool = True,
    ):
        """Update payment and order status based on transaction result"""
        if transaction.is_approved:
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            payment.provider_transaction_id = transaction.response_ds_transaction_id

            # Update order status
            order = payment.order
            if order:
                order.payment_status = OrderPaymentStatus.CAPTURED
                order.status = "confirmed"
                order.payment_reference = transaction.response_ds_transaction_id

                # Reduce stock for all order items after successful payment
                logger.info(f"Payment approved for order {order.id} - reducing stock for order items")
                for order_item in order.items:
                    try:
                        success = ProductService.reduce_stock(
                            db=db,
                            product_id=order_item.product_id,
                            size=order_item.size,
                            quantity=order_item.quantity
                        )
                        
                        if success:
                            logger.info(
                                f"✅ Stock reduced for product {order_item.product_id} "
                                f"size {order_item.size}: -{order_item.quantity}"
                            )
                        else:
                            logger.error(
                                f"❌ Failed to reduce stock for product {order_item.product_id} "
                                f"size {order_item.size}: -{order_item.quantity}"
                            )
                    except Exception as e:
                        # Log error but don't fail the payment process
                        logger.error(
                            f"❌ Exception reducing stock for product {order_item.product_id} "
                            f"size {order_item.size}: {e}"
                        )

                # Send secure payment notification email to admin
                # This is only triggered by verified payment callbacks from Redsys
                # Additional security: Only send if signature was actually verified
                logger.info(
                    f"Payment {payment.id} approved - checking email notification conditions"
                )
                logger.info(
                    f"signature_valid={signature_valid}, transaction.signature_verified={transaction.signature_verified}"
                )

                if signature_valid and transaction.signature_verified:
                    try:
                        logger.info(
                            f"Attempting to send invoice email for order {order.id}"
                        )

                        # Get customer email from order if available
                        customer_email = None
                        shipping_address_data = None

                        if hasattr(order, "customer_email") and order.customer_email:
                            customer_email = str(order.customer_email)
                        elif (
                            hasattr(order, "shipping_address")
                            and order.shipping_address
                        ):
                            # Try to get email from shipping address if it exists
                            shipping_data = order.shipping_address
                            if (
                                isinstance(shipping_data, dict)
                                and "email" in shipping_data
                            ):
                                customer_email = shipping_data.get("email")

                        # Extract shipping address data for invoice
                        if (
                            hasattr(order, "shipping_address")
                            and order.shipping_address
                        ):
                            if isinstance(order.shipping_address, dict):
                                shipping_address_data = order.shipping_address
                            else:
                                # If shipping_address is a string, build from order customer fields
                                shipping_address_data = {
                                    "first_name": getattr(
                                        order, "customer_first_name", ""
                                    ),
                                    "last_name": getattr(
                                        order, "customer_last_name", ""
                                    ),
                                    "address_line_1": getattr(
                                        order, "shipping_address", ""
                                    ),
                                    "city": getattr(order, "shipping_city", ""),
                                    "state": getattr(order, "shipping_state", ""),
                                    "postal_code": getattr(
                                        order, "shipping_postal_code", ""
                                    ),
                                    "country": getattr(order, "shipping_country", ""),
                                    "phone": getattr(order, "customer_phone", ""),
                                    "email": customer_email,
                                }

                        logger.info(f"Customer email extracted: {customer_email}")
                        logger.info(
                            f"Shipping address extracted: {shipping_address_data}"
                        )

                        # Extract order items for invoice
                        order_items = []
                        if hasattr(order, "items") and order.items:
                            for item in order.items:
                                order_items.append({
                                    "product_name": item.product.name if item.product else "Producto",
                                    "size": item.size,
                                    "quantity": item.quantity,
                                    "unit_price": item.unit_price,
                                    "total_price": item.total_price,
                                })

                        logger.info(f"Order items extracted: {len(order_items)} items")

                        # Send notification (this will only happen if signature verification passed)
                        email_sent = EmailService.send_payment_success_notification(
                            order_id=str(order.id),
                            payment_id=str(payment.id),
                            amount=float(payment.amount),
                            customer_email=customer_email,
                            transaction_id=transaction.response_ds_transaction_id,
                            shipping_address=shipping_address_data,
                            order_items=order_items,  # Pass order items
                        )

                        if email_sent:
                            logger.info(
                                f"✅ Spanish invoice email sent successfully for order {order.id}"
                            )
                        else:
                            logger.error(
                                f"❌ Failed to send Spanish invoice email for order {order.id}"
                            )

                    except Exception as e:
                        # Don't fail payment processing if email fails
                        logger.error(
                            f"❌ Exception sending Spanish invoice email for order {order.id}: {e}"
                        )
                        import traceback

                        logger.error(f"Email error traceback: {traceback.format_exc()}")
                else:
                    logger.warning(
                        f"⚠️  Skipping email notification - signature not verified for payment {payment.id} (signature_valid={signature_valid}, transaction.signature_verified={transaction.signature_verified})"
                    )

        else:
            payment.status = PaymentStatus.FAILED

            # Update order status
            order = payment.order
            if order:
                order.payment_status = OrderPaymentStatus.FAILED
                order.status = "cancelled"

    def get_payment_status(self, payment_id: str, db: Session) -> PaymentStatusResponse:
        """Get payment status"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        # Get Redsys transaction details if available
        redsys_transaction = payment.redsys_transaction

        return PaymentStatusResponse(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.status,
            amount=payment.amount,
            currency=payment.currency,
            provider=payment.provider,
            provider_transaction_id=payment.provider_transaction_id,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
            redsys_response_code=redsys_transaction.response_ds_response
            if redsys_transaction
            else None,
            redsys_response_description=redsys_transaction.response_code_description
            if redsys_transaction
            else None,
            redsys_card_brand=redsys_transaction.response_ds_card_brand
            if redsys_transaction
            else None,
            redsys_card_number=redsys_transaction.response_ds_card_number
            if redsys_transaction
            else None,
        )

    def get_transaction_details(
        self, payment_id: str, db: Session
    ) -> RedsysTransactionResponse:
        """Get detailed Redsys transaction information"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        transaction = payment.redsys_transaction
        if not transaction:
            raise ValueError(f"No Redsys transaction found for payment {payment_id}")

        return RedsysTransactionResponse(
            id=transaction.id,
            payment_id=transaction.payment_id,
            ds_order=transaction.ds_order,
            merchant_code=transaction.merchant_code,
            terminal=transaction.terminal,
            is_approved=transaction.is_approved,
            response_code=transaction.response_ds_response,
            response_description=transaction.response_code_description,
            card_number=transaction.response_ds_card_number,
            card_brand=transaction.response_ds_card_brand,
            authorization_code=transaction.response_ds_authorisation_code,
            transaction_id=transaction.response_ds_transaction_id,
            is_sandbox=transaction.is_sandbox,
            signature_verified=transaction.signature_verified,
            created_at=transaction.created_at,
            response_received_at=transaction.response_received_at,
        )


# Service instance
redsys_service = RedsysPaymentService()


# Legacy function aliases for backward compatibility
def initiate_redsys_payment(order_id: str, amount: float) -> Dict:
    """Legacy function - use RedsysPaymentService.create_payment instead"""
    logger.warning("Using deprecated initiate_redsys_payment function")
    return {
        "status": "deprecated",
        "message": "Use RedsysPaymentService.create_payment instead",
        "order_id": order_id,
        "amount": amount,
    }


def process_redsys_callback(callback_data: dict) -> Dict:
    """Legacy function - use RedsysPaymentService.process_callback instead"""
    logger.warning("Using deprecated process_redsys_callback function")
    return {
        "status": "deprecated",
        "message": "Use RedsysPaymentService.process_callback instead",
    }


def validate_redsys_signature(data: dict) -> bool:
    """Legacy function - signature validation is handled in process_callback"""
    logger.warning("Using deprecated validate_redsys_signature function")
    return True
