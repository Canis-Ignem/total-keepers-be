"""
Pydantic schemas for payment operations, specifically Redsys integration
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator
from pydantic.types import constr


class PaymentProvider(str, Enum):
    """Payment provider types"""

    REDSYS = "redsys"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    """Payment transaction statuses"""

    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    EXPIRED = "expired"


class Currency(str, Enum):
    """Supported currencies"""

    EUR = "EUR"
    USD = "USD"


# Request schemas
class PaymentCreateRequest(BaseModel):
    """Request to create a new payment"""

    order_id: str = Field(..., description="Order ID to create payment for")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: Currency = Field(default=Currency.EUR, description="Payment currency")
    description: Optional[str] = Field(
        None, max_length=255, description="Payment description"
    )
    success_url: Optional[str] = Field(None, description="Success redirect URL")
    failure_url: Optional[str] = Field(None, description="Failure redirect URL")
    cancel_url: Optional[str] = Field(None, description="Cancel redirect URL")

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        # Ensure max 2 decimal places for currency
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        return v


class RedsysPaymentRequest(PaymentCreateRequest):
    """Redsys-specific payment request"""

    merchant_data: Optional[str] = Field(None, description="Additional merchant data")
    consumer_language: Optional[str] = Field(
        default="es", description="Consumer language (es, en, fr, etc.)"
    )
    product_description: Optional[str] = Field(
        None, max_length=125, description="Product description"
    )
    titular: Optional[str] = Field(None, max_length=60, description="Cardholder name")

    # 3D Secure parameters
    three_ds_info: Optional[str] = Field(
        None, description="3D Secure authentication data"
    )


class RedsysCallbackData(BaseModel):
    """Redsys callback/notification data"""

    ds_signature_version: str = Field(..., description="Signature version")
    ds_merchant_parameters: str = Field(
        ..., description="Base64 encoded merchant parameters"
    )
    ds_signature: str = Field(..., description="Transaction signature")


class RedsysResponseParameters(BaseModel):
    """Decoded Redsys response parameters"""

    ds_date: Optional[str] = Field(None, description="Transaction date")
    ds_hour: Optional[str] = Field(None, description="Transaction time")
    ds_amount: Optional[str] = Field(None, description="Transaction amount")
    ds_currency: Optional[str] = Field(None, description="Currency code")
    ds_order: Optional[str] = Field(None, description="Order number")
    ds_merchant_code: Optional[str] = Field(None, description="Merchant code")
    ds_terminal: Optional[str] = Field(None, description="Terminal number")
    ds_response: Optional[str] = Field(None, description="Response code")
    ds_merchant_data: Optional[str] = Field(None, description="Merchant data")
    ds_secure_payment: Optional[str] = Field(
        None, description="Secure payment indicator"
    )
    ds_card_number: Optional[str] = Field(None, description="Masked card number")
    ds_card_brand: Optional[str] = Field(None, description="Card brand")
    ds_card_type: Optional[str] = Field(None, description="Card type")
    ds_card_country: Optional[str] = Field(None, description="Card country")
    ds_authorisation_code: Optional[str] = Field(None, description="Authorization code")
    ds_consumer_language: Optional[str] = Field(None, description="Consumer language")
    ds_transaction_id: Optional[str] = Field(None, description="Transaction ID")
    ds_merchant_identifier: Optional[str] = Field(
        None, description="Merchant identifier"
    )
    ds_emv3ds: Optional[str] = Field(None, description="3D Secure data")


# Response schemas
class PaymentResponse(BaseModel):
    """Base payment response"""

    id: str
    order_id: str
    provider: PaymentProvider
    status: PaymentStatus
    amount: Decimal
    currency: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RedsysPaymentFormData(BaseModel):
    """Redsys payment form data to send to frontend"""

    ds_signature_version: str
    ds_merchant_parameters: str
    ds_signature: str
    redsys_url: str = Field(..., description="Redsys payment URL")


class RedsysPaymentInitResponse(BaseModel):
    """Response when initiating Redsys payment"""

    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    form_data: RedsysPaymentFormData
    payment_url: str = Field(..., description="URL where user should be redirected")


class PaymentStatusResponse(BaseModel):
    """Payment status check response"""

    payment_id: str
    order_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    provider: PaymentProvider
    provider_transaction_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    # Redsys-specific fields
    redsys_response_code: Optional[str] = None
    redsys_response_description: Optional[str] = None
    redsys_card_brand: Optional[str] = None
    redsys_card_number: Optional[str] = None

    class Config:
        from_attributes = True


class RedsysTransactionResponse(BaseModel):
    """Detailed Redsys transaction response"""

    id: str
    payment_id: str
    ds_order: str
    merchant_code: str
    terminal: str
    is_approved: bool
    response_code: Optional[str]
    response_description: str
    card_number: Optional[str]
    card_brand: Optional[str]
    authorization_code: Optional[str]
    transaction_id: Optional[str]
    is_sandbox: bool
    signature_verified: bool
    created_at: datetime
    response_received_at: Optional[datetime]

    class Config:
        from_attributes = True


# Refund schemas
class PaymentRefundRequest(BaseModel):
    """Request to refund a payment"""

    amount: Optional[Decimal] = Field(
        None, gt=0, description="Refund amount (leave empty for full refund)"
    )
    reason: Optional[str] = Field(None, max_length=255, description="Refund reason")


class PaymentRefundResponse(BaseModel):
    """Payment refund response"""

    id: str
    payment_id: str
    amount: Decimal
    reason: Optional[str]
    status: PaymentStatus
    provider_refund_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Webhook/Callback schemas
class PaymentWebhookEvent(BaseModel):
    """Generic payment webhook event"""

    event_type: str = Field(
        ..., description="Event type (payment.completed, payment.failed, etc.)"
    )
    payment_id: str
    order_id: str
    status: PaymentStatus
    provider: PaymentProvider
    timestamp: datetime
    data: Dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific event data"
    )


# Error schemas
class PaymentError(BaseModel):
    """Payment error response"""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


# Configuration schemas
class RedsysConfig(BaseModel):
    """Redsys configuration validation"""

    merchant_code: constr(min_length=1, max_length=20)
    terminal: constr(min_length=1, max_length=10) = "001"
    secret_key: constr(min_length=1)
    sandbox: bool = True
    merchant_name: constr(min_length=1, max_length=25)
    merchant_url: str = Field(..., description="Callback URL")

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 10:
            raise ValueError("Secret key must be at least 10 characters long")
        return v
