# Standard library imports
import enum
import uuid

# Third-party imports
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    order_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: f"ORD-{str(uuid.uuid4())[:8].upper()}",
    )  # Human-readable order number
    status: Column[OrderStatus] = Column(
        SQLEnum(OrderStatus), default=OrderStatus.PENDING
    )
    payment_status: Column[PaymentStatus] = Column(
        SQLEnum(PaymentStatus), default=PaymentStatus.PENDING
    )

    # Amounts
    subtotal = Column(Float, nullable=False)  # Sum of all items
    tax_amount = Column(Float, default=0.0)
    shipping_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)  # Final amount to pay

    # Payment info
    payment_method = Column(String(50))  # e.g., "redsys", "paypal", etc.
    payment_reference = Column(String(255))  # External payment reference

    # Customer contact info
    customer_email = Column(String(255))
    customer_first_name = Column(String(100))
    customer_last_name = Column(String(100))
    customer_phone = Column(String(20))

    # Shipping info
    shipping_address = Column(String(500))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_postal_code = Column(String(20))
    shipping_country = Column(String(100))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))

    # Relationships - using string references to avoid circular imports
    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments = relationship("Payment", back_populates="order")

    def __repr__(self):
        return f"<Order(id='{self.id}', order_number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    size = Column(String(10), nullable=False)  # Selected size
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Price at time of order
    total_price = Column(Float, nullable=False)  # unit_price * quantity
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")  # Removed back_populates to avoid circular import

    def __repr__(self):
        return f"<OrderItem(order_id='{self.order_id}', product_id='{self.product_id}', size='{self.size}', quantity={self.quantity})>"
