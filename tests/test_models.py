"""
Model tests - Test SQLAlchemy models and their basic functionality
"""

from decimal import Decimal
from app.models.product import Product, ProductSize, Tag
from app.models.user import User
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.payment import (
    Payment,
    PaymentProvider,
    PaymentStatus as PaymentStatusEnum,
)


def test_product_model_creation():
    """Test Product model can be instantiated"""
    product = Product(
        id="test-product",
        name="Test Gloves",
        price=49.99,
        description="Test goalkeeper gloves",
        category="GOALKEEPER_GLOVES",
        tag="JUNIOR",
    )

    assert product.id == "test-product"
    assert product.name == "Test Gloves"
    assert product.price == 49.99
    assert product.category == "GOALKEEPER_GLOVES"
    assert product.tag == "JUNIOR"
    # Note: is_active default is set at DB level, not Python level


def test_product_size_model_creation():
    """Test ProductSize model can be instantiated"""
    product_size = ProductSize(
        product_id="test-product", size="7", stock_quantity=10, is_available=True
    )

    assert product_size.product_id == "test-product"
    assert product_size.size == "7"
    assert product_size.stock_quantity == 10
    assert product_size.is_available is True


def test_tag_model_creation():
    """Test Tag model can be instantiated"""
    tag = Tag(name="Junior", description="For junior players")

    assert tag.name == "Junior"
    assert tag.description == "For junior players"


def test_user_model_creation():
    """Test User model can be instantiated"""
    user = User(
        id="test-user-id",
        email="test@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
        is_active=True,
    )

    assert user.id == "test-user-id"
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.full_name == "Test User"  # This is a property
    assert user.is_active is True


def test_cart_item_model_creation():
    """Test CartItem model can be instantiated"""
    cart_item = CartItem(
        user_id="test-user-id", product_id="test-product", size="7", quantity=2
    )

    assert cart_item.user_id == "test-user-id"
    assert cart_item.product_id == "test-product"
    assert cart_item.size == "7"
    assert cart_item.quantity == 2


def test_order_model_creation():
    """Test Order model can be instantiated"""
    order = Order(
        id="test-order-id",
        user_id="test-user-id",
        order_number="ORD-TEST123",
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=49.99,
        tax_amount=0.0,
        shipping_amount=3.0,
        discount_amount=0.0,
        total_amount=52.99,
    )

    assert order.id == "test-order-id"
    assert order.user_id == "test-user-id"
    assert order.order_number == "ORD-TEST123"
    assert order.status == OrderStatus.PENDING
    assert order.payment_status == PaymentStatus.PENDING
    assert order.subtotal == 49.99
    assert order.total_amount == 52.99


def test_order_item_model_creation():
    """Test OrderItem model can be instantiated"""
    order_item = OrderItem(
        order_id="test-order-id",
        product_id="test-product",
        size="7",
        quantity=1,
        unit_price=49.99,
        total_price=49.99,
    )

    assert order_item.order_id == "test-order-id"
    assert order_item.product_id == "test-product"
    assert order_item.size == "7"
    assert order_item.quantity == 1
    assert order_item.unit_price == 49.99
    assert order_item.total_price == 49.99


def test_payment_model_creation():
    """Test Payment model can be instantiated"""
    payment = Payment(
        id="test-payment-id",
        order_id="test-order-id",
        provider=PaymentProvider.REDSYS,
        status=PaymentStatusEnum.PENDING,
        amount=Decimal("52.99"),
        currency="EUR",
    )

    assert payment.id == "test-payment-id"
    assert payment.order_id == "test-order-id"
    assert payment.provider == PaymentProvider.REDSYS
    assert payment.status == PaymentStatusEnum.PENDING
    assert payment.amount == Decimal("52.99")
    assert payment.currency == "EUR"


def test_order_status_enum():
    """Test OrderStatus enum values"""
    assert hasattr(OrderStatus, "PENDING")
    assert hasattr(OrderStatus, "CONFIRMED")
    assert hasattr(OrderStatus, "SHIPPED")
    assert hasattr(OrderStatus, "DELIVERED")
    assert hasattr(OrderStatus, "CANCELLED")


def test_payment_status_enum():
    """Test PaymentStatus enum values"""
    assert hasattr(PaymentStatus, "PENDING")
    assert hasattr(PaymentStatus, "AUTHORIZED")
    assert hasattr(PaymentStatus, "CAPTURED")
    assert hasattr(PaymentStatus, "FAILED")
    assert hasattr(PaymentStatus, "CANCELLED")


def test_payment_provider_enum():
    """Test PaymentProvider enum values"""
    assert hasattr(PaymentProvider, "REDSYS")


def test_model_repr_methods():
    """Test that model __repr__ methods work"""
    product = Product(id="test", name="Test", price=10.0)
    cart_item = CartItem(user_id="user1", product_id="prod1", size="7", quantity=1)
    order = Order(id="order1", subtotal=10.0, total_amount=10.0)

    # These should not raise exceptions
    assert "test" in repr(product)
    assert "user1" in repr(cart_item)
    assert "order1" in repr(order)
