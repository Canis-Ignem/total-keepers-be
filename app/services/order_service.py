"""
Secure Order Processing Service

This service handles order validation, pricing verification, and secure order creation
to prevent frontend manipulation of prices, quantities, or discounts.
"""

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import CreateOrderRequest, OrderResponse, OrderItemRequest
from app.services.payment_service import redsys_service
from app.services.discount_service import get_discount_service
from app.schemas.payment import Currency, RedsysPaymentRequest


class SecureOrderService:
    """Handles secure order processing with server-side validation"""

    # Server-side shipping rules (cannot be manipulated from frontend)
    SHIPPING_RULES = {
        "free_shipping_threshold": 2,  # Free shipping if 2+ items, 3€ if only 1 item
        "standard_shipping_cost": Decimal("3.00"),
        "currency": "EUR",
    }

    # Tax configuration
    TAX_RATE = Decimal("0.21")  # 21% VAT for Spain

    def __init__(self, db: Session):
        self.db = db

    def validate_and_create_order(
        self, order_request: CreateOrderRequest
    ) -> OrderResponse:
        """
        Validates order data against database and creates secure order

        Security measures:
        1. All prices verified against database
        2. Product availability checked
        3. Quantities validated
        4. Discounts applied server-side only
        5. Shipping calculated server-side only
        """
        try:
            # Step 1: Validate all products exist and get current prices
            validated_items = self._validate_order_items(order_request.items)

            # Step 2: Calculate totals using server-side prices only
            pricing = self._calculate_pricing(validated_items, order_request.promo_code)

            # Step 3: Create order in database
            order = self._create_order_record(validated_items, order_request, pricing)

            # Step 4: Generate payment URL if needed
            payment_url = self._generate_payment_url(order, pricing)

            # Step 5: Return secure response
            return OrderResponse(
                order_id=str(order.id),
                status=order.status.value,
                total_amount=pricing["total"],
                subtotal=pricing["subtotal"],
                tax_amount=pricing["tax_amount"],
                shipping_amount=pricing["shipping_cost"],
                discount_amount=pricing["discount_amount"],
                payment_url=payment_url,
                created_at=order.created_at.replace(tzinfo=timezone.utc),
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order processing failed: {str(e)}",
            )

    def _validate_order_items(
        self, items: List[OrderItemRequest]
    ) -> List[Dict[str, Any]]:
        """Validates all order items against database prices and availability"""

        validated_items = []

        for item in items:
            # Get product from database

            product = (
                self.db.query(Product).filter(Product.id == item.product_id).first()
            )

            if not product:
                print(f"ERROR: Product {item.product_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item.product_id} not found",
                )

            # Verify price matches database (prevent price manipulation)
            current_price = product.get_current_price()
            received_price = float(item.product_price)
            price_difference = abs(current_price - received_price)
            

            
            if price_difference > 0.01:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Price mismatch for product {item.product_id}. Expected: {current_price}, Received: {received_price}",
                )

            # Verify product name matches (additional security) - case insensitive comparison

            
            if product.name.lower().strip() != item.product_name.lower().strip():
                print(f"ERROR: Product name mismatch for {item.product_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product name mismatch for {item.product_id}. Expected: '{product.name}', Received: '{item.product_name}'",
                )

            # Validate quantity

            
            if item.quantity <= 0 or item.quantity > 99:
                print(f"ERROR: Invalid quantity for product {item.product_id}: {item.quantity}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid quantity for product {item.product_id}: {item.quantity}",
                )


            
            validated_items.append(
                {
                    "product": product,
                    "quantity": item.quantity,
                    "selected_size": item.selected_size,
                    "unit_price": Decimal(str(product.get_current_price())),
                    "line_total": Decimal(str(product.get_current_price())) * Decimal(item.quantity),
                }
            )


        return validated_items

    def _calculate_pricing(
        self, validated_items: List[Dict[str, Any]], promo_code: Optional[str]
    ) -> Dict[str, Decimal]:
        """Calculates final pricing using server-side rules only"""

        # Calculate subtotal
        subtotal = sum(item["line_total"] for item in validated_items)

        # Calculate shipping (server-side logic only)
        # 3€ shipping if there is only ONE item in cart, free shipping for 2+ items
        total_quantity = sum(item["quantity"] for item in validated_items)
        shipping_cost = (
            Decimal("0.00")
            if total_quantity >= self.SHIPPING_RULES["free_shipping_threshold"]
            else self.SHIPPING_RULES["standard_shipping_cost"]
        )

        # Apply discount using the new discount code system
        discount_amount = Decimal("0.00")
        discount_percent = 0

        if promo_code:
            discount_service = get_discount_service(self.db)
            discount_amount_float, error_message = discount_service.apply_discount_code(
                code=promo_code.strip(), order_amount=float(subtotal)
            )

            if error_message is None:  # No error, discount applied successfully
                discount_amount = Decimal(str(discount_amount_float)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                # Calculate the percentage for reference (if needed for display)
                if subtotal > 0:
                    discount_percent = float((discount_amount / subtotal) * 100)
            else:
                # Log the error but don't fail the order - just proceed without discount
                print(
                    f"Discount code '{promo_code}' could not be applied: {error_message}"
                )

        # Tax is already included in product prices, so no additional tax calculation needed
        tax_amount = Decimal("0.00")

        # Calculate final total
        total = subtotal - discount_amount + tax_amount + shipping_cost

        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "total": total,
            "discount_percent": discount_percent,
        }

    def _create_order_record(
        self,
        validated_items: List[Dict[str, Any]],
        order_request: CreateOrderRequest,
        pricing: Dict[str, Decimal],
    ) -> Order:
        """Creates order record in database"""

        order_id = str(uuid.uuid4())

        # Create order
        order = Order(
            id=order_id,
            user_id=None,  # Guest order - no user authentication required
            status="PENDING",
            subtotal=float(pricing["subtotal"]),
            tax_amount=float(pricing["tax_amount"]),
            shipping_amount=float(pricing["shipping_cost"]),
            discount_amount=float(pricing["discount_amount"]),
            total_amount=float(pricing["total"]),
            payment_method=None,  # Will be set when payment is processed
            payment_reference=None,
            # Customer contact information
            customer_email=order_request.shipping_address.email,
            customer_first_name=order_request.shipping_address.first_name,
            customer_last_name=order_request.shipping_address.last_name,
            customer_phone=order_request.shipping_address.phone,
            # Shipping information
            shipping_address=self._format_shipping_address(
                order_request.shipping_address
            ),
            shipping_city=order_request.shipping_address.city,
            shipping_state=order_request.shipping_address.state,
            shipping_postal_code=order_request.shipping_address.postal_code,
            shipping_country=order_request.shipping_address.country,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.db.add(order)
        self.db.flush()  # Flush to get the order ID
        
        # Create order items
        for item in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product"].id,  # Extract ID from product object
                size=item["selected_size"] if item["selected_size"] else "",
                quantity=item["quantity"],
                unit_price=float(item["unit_price"]),
                total_price=float(item["line_total"]),
            )
            self.db.add(order_item)
        
        self.db.commit()
        self.db.refresh(order)

        return order

    def _format_shipping_address(self, address) -> str:
        """Formats shipping address for storage"""
        address_parts = [address.address_line_1]
        if address.address_line_2:
            address_parts.append(address.address_line_2)

        return ", ".join(address_parts)

    def _generate_payment_url(
        self, order: Order, pricing: Dict[str, Decimal]
    ) -> Optional[str]:
        """Generate secure payment URL using Redsys service"""
        try:
            # Create payment request
            payment_request = RedsysPaymentRequest(
                order_id=str(order.id),
                amount=pricing["total"],
                currency=Currency.EUR,
                merchant_data="",
                product_description=f"Order {order.id[:8]}",
                titular="",
                three_ds_info=None,
                success_url=f"https://your-domain.com/payment/success/{order.id}",
                failure_url=f"https://your-domain.com/payment/failure/{order.id}",
                cancel_url=f"https://your-domain.com/payment/cancel/{order.id}",
            )

            # Generate payment through Redsys service
            payment_response = redsys_service.create_payment(payment_request, self.db)

            return payment_response.payment_url

        except Exception as e:
            # Log the error but don't fail the order creation
            print(f"Failed to generate payment URL: {e}")
            return None


def get_order_service(db: Session) -> SecureOrderService:
    """Dependency injection for order service"""
    return SecureOrderService(db)
