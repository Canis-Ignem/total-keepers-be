# Standard library imports
import enum
import uuid
from decimal import Decimal

# Third-party imports
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    DateTime,
    Enum as SQLEnum,
    Boolean,
    Text,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class PaymentProvider(str, enum.Enum):
    """Payment provider types"""

    REDSYS = "redsys"
    PAYPAL = "paypal"
    STRIPE = "stripe"


class PaymentStatus(str, enum.Enum):
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


class RedsysResponseCode(str, enum.Enum):
    """Redsys response codes for payment results"""

    APPROVED = "0000"  # Transaction approved
    DENIED = "0101"  # Card blocked
    EXPIRED = "0102"  # Card expired
    INSUFFICIENT_FUNDS = "0106"  # Insufficient funds
    INVALID_CARD = "0125"  # Invalid card number
    INVALID_DATE = "0129"  # Invalid expiration date
    INVALID_CVC = "0167"  # Invalid CVC
    TRANSACTION_NOT_ALLOWED = "0184"  # Transaction not allowed for this card
    OPERATION_DENIED = "0190"  # Operation denied


class Payment(Base):
    """Main payment transaction record"""

    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False, index=True)

    # Payment details
    provider: Column[PaymentProvider] = Column(
        SQLEnum(PaymentProvider), nullable=False, default=PaymentProvider.REDSYS
    )
    status: Column[PaymentStatus] = Column(
        SQLEnum(PaymentStatus, name="redsyspaymentstatus"),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    amount: Column[Decimal] = Column(DECIMAL(precision=10, scale=2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")

    # Provider-specific references
    provider_transaction_id = Column(String(255), index=True)  # External transaction ID
    provider_order_id = Column(String(255), index=True)  # External order reference

    # Transaction metadata
    payment_method = Column(String(50))  # e.g., "card", "bank_transfer"
    description = Column(String(255))

    # URLs for redirects
    success_url = Column(String(500))
    failure_url = Column(String(500))
    cancel_url = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    order = relationship("Order", back_populates="payments")
    redsys_transaction = relationship(
        "RedsysTransaction", back_populates="payment", uselist=False
    )

    def __repr__(self):
        return f"<Payment(id='{self.id}', order_id='{self.order_id}', status='{self.status}', amount={self.amount})>"


class RedsysTransaction(Base):
    """Redsys-specific transaction data"""

    __tablename__ = "redsys_transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False, unique=True)

    # Redsys merchant configuration
    merchant_code = Column(String(20), nullable=False)
    terminal = Column(String(10), nullable=False, default="001")

    # Transaction parameters
    transaction_type = Column(
        String(10), nullable=False, default="0"
    )  # 0 = Authorization
    ds_order = Column(String(255), nullable=False, index=True)  # Redsys order number

    # Request parameters (what we sent to Redsys)
    ds_merchant_parameters = Column(Text)  # Base64 encoded parameters
    ds_signature = Column(String(255))  # Our signature
    ds_signature_version = Column(String(20), default="HMAC_SHA256_V1")

    # Response parameters (what Redsys sent back)
    response_ds_date = Column(String(20))
    response_ds_hour = Column(String(10))
    response_ds_amount = Column(String(20))
    response_ds_currency = Column(String(10))
    response_ds_order = Column(String(255))
    response_ds_merchant_code = Column(String(20))
    response_ds_terminal = Column(String(10))
    response_ds_response = Column(String(10))  # Response code
    response_ds_merchant_data = Column(Text)
    response_ds_secure_payment = Column(String(10))
    response_ds_card_number = Column(String(50))  # Masked card number
    response_ds_card_brand = Column(String(20))  # VISA, MASTERCARD, etc.
    response_ds_card_type = Column(String(20))  # Credit, Debit
    response_ds_card_country = Column(String(10))  # Card issuer country
    response_ds_authorisation_code = Column(String(20))
    response_ds_consumer_language = Column(String(10))
    response_ds_merchant_parameters = Column(Text)  # Response parameters
    response_ds_signature = Column(String(255))  # Redsys signature
    response_ds_signature_version = Column(String(20))

    # Additional response fields
    response_ds_transaction_id = Column(String(255))
    response_ds_merchant_identifier = Column(String(255))
    response_ds_emv3ds = Column(Text)  # 3D Secure data

    # Status tracking
    is_sandbox = Column(Boolean, default=True)
    signature_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    request_sent_at = Column(DateTime(timezone=True))
    response_received_at = Column(DateTime(timezone=True))

    # Relationships
    payment = relationship("Payment", back_populates="redsys_transaction")

    @property
    def is_approved(self) -> bool:
        """Check if the transaction was approved by Redsys"""
        if self.response_ds_response is None:
            return False
        return str(self.response_ds_response) == str(RedsysResponseCode.APPROVED.value)

    @property
    def response_code_description(self) -> str:
        """Get human-readable description of response code"""
        code_map: dict[str, str] = {
            "0000": "Transaction approved",
            "0101": "Card blocked",
            "0102": "Card expired",
            "0106": "Insufficient funds",
            "0125": "Invalid card number",
            "0129": "Invalid expiration date",
            "0167": "Invalid CVC",
            "0184": "Transaction not allowed for this card",
            "0190": "Operation denied",
        }
        if self.response_ds_response is None:
            return "No response code available"
        return code_map.get(
            str(self.response_ds_response),
            f"Unknown response code: {self.response_ds_response}",
        )

    def __repr__(self):
        return f"<RedsysTransaction(id='{self.id}', ds_order='{self.ds_order}', response='{self.response_ds_response}')>"


class PaymentRefund(Base):
    """Payment refund records"""

    __tablename__ = "payment_refunds"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False)

    # Refund details
    amount: Column[Decimal] = Column(DECIMAL(precision=10, scale=2), nullable=False)
    reason = Column(String(255))
    status: Column[PaymentStatus] = Column(
        SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )

    # Provider references
    provider_refund_id = Column(String(255), index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relationships
    payment = relationship("Payment")

    def __repr__(self):
        return f"<PaymentRefund(id='{self.id}', payment_id='{self.payment_id}', amount={self.amount})>"
