# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse,
)

router = APIRouter()


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get user's cart items - only returns items belonging to the authenticated user"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()

    total_amount = sum(int(item.quantity) * item.product.price for item in cart_items)
    total_items: int = sum(int(item.quantity) for item in cart_items)

    return CartResponse(
        items=[CartItemResponse.from_orm(item) for item in cart_items],
        total_amount=total_amount,
        total_items=total_items,
    )


@router.post("/items", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add item to cart or update quantity if exists - user can only modify their own cart"""

    # Validate input data
    if item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than 0",
        )

    if item.quantity > 100:  # Reasonable max quantity
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot exceed 100 items",
        )

    # Verify product exists
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Check if item already exists in cart
    existing_item = (
        db.query(CartItem)
        .filter(
            and_(
                CartItem.user_id == current_user.id,
                CartItem.product_id == item.product_id,
                CartItem.size == item.size,
            )
        )
        .first()
    )

    if existing_item:
        # Update quantity
        setattr(existing_item, "quantity", int(existing_item.quantity) + item.quantity)
        db.commit()
        db.refresh(existing_item)
        return CartItemResponse.from_orm(existing_item)
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=item.product_id,
            size=item.size,
            quantity=item.quantity,
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return CartItemResponse.from_orm(cart_item)


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update cart item quantity - user can only update their own cart items"""
    cart_item = (
        db.query(CartItem)
        .filter(and_(CartItem.id == item_id, CartItem.user_id == current_user.id))
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found or access denied",
        )

    if item_update.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Item removed from cart"
        )

    if item_update.quantity > 100:  # Reasonable max quantity
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot exceed 100 items",
        )

    setattr(cart_item, "quantity", int(item_update.quantity))
    db.commit()
    db.refresh(cart_item)
    return CartItemResponse.from_orm(cart_item)


@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove item from cart - user can only remove their own cart items"""
    cart_item = (
        db.query(CartItem)
        .filter(and_(CartItem.id == item_id, CartItem.user_id == current_user.id))
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found or access denied",
        )

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Clear all items from user's cart - only clears the authenticated user's cart"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}


@router.post("/sync", response_model=CartResponse)
async def sync_cart(
    frontend_items: List[CartItemCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Sync frontend cart with backend - only syncs for the authenticated user"""

    # Validate input - prevent abuse
    if len(frontend_items) > 50:  # Reasonable max cart size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart cannot contain more than 50 different items",
        )

    # Validate each item
    for item in frontend_items:
        if item.quantity <= 0 or item.quantity > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each item quantity must be between 1 and 100",
            )

    # Get existing backend cart
    backend_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()

    # Create a map of backend items for easy lookup
    backend_map = {f"{item.product_id}-{item.size}": item for item in backend_items}

    # Process frontend items
    for frontend_item in frontend_items:
        key = f"{frontend_item.product_id}-{frontend_item.size}"

        if key in backend_map:
            # Update existing item with max quantity
            setattr(
                backend_map[key],
                "quantity",
                int(max(int(backend_map[key].quantity), frontend_item.quantity)),
            )
        else:
            # Add new item from frontend
            new_item = CartItem(
                user_id=current_user.id,
                product_id=frontend_item.product_id,
                size=frontend_item.size,
                quantity=frontend_item.quantity,
            )
            db.add(new_item)

    db.commit()

    # Return updated cart
    return await get_cart(current_user, db)
