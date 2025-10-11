# Standard library imports
import logging
from typing import List, Optional

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# Local application imports
from app.core.database import get_db
from app.schemas.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductWithAvailability,
    ProductListResponse,
    ProductSearchFilters,
    Tag,
    TagCreate,
    TagUpdate,
)
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

router = APIRouter()

# Product CRUD Operations


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by main tag"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock_only: bool = Query(False, description="Show only products in stock"),
    is_active: bool = Query(True, description="Show only active products"),
    language_code: Optional[str] = Query(
        None, description="Return translations for this language code (e.g. 'en', 'es')"
    ),
    db: Session = Depends(get_db),
):
    """Get paginated list of products with filtering options."""
    try:
        # Build filters
        filters = ProductSearchFilters(
            category=category,
            tag=tag,
            tags=tags.split(",") if tags else None,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
            is_active=is_active,
        )

        # Calculate offset
        skip = (page - 1) * size

        # Get products
        products = ProductService.get_products(
            db, skip=skip, limit=size, filters=filters
        )

        # Convert to ProductWithAvailability
        products_with_availability = []
        for product in products:
            availability_info = ProductService.get_product_with_availability(
                db, str(product.id), language_code
            )
            if availability_info:
                products_with_availability.append(availability_info)

        # Get total count for pagination (simplified - you might want to optimize this)
        total_products = ProductService.get_products(
            db, skip=0, limit=1000, filters=filters
        )
        total = len(total_products)

        # Calculate pagination info
        pages = (total + size - 1) // size  # Ceiling division

        return ProductListResponse(
            products=products_with_availability,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/products/{product_id}", response_model=ProductWithAvailability)
async def get_product(
    product_id: str, 
    language_code: Optional[str] = Query(None, description="Return translations for this language code (e.g. 'en', 'es')"),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID with availability information."""
    try:
        product = ProductService.get_product_with_availability(db, product_id, language_code)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/products", response_model=Product, status_code=201)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    try:
        # Check if product ID already exists
        existing_product = ProductService.get_product_by_id(db, product_data.id)
        if existing_product:
            raise HTTPException(
                status_code=400, detail="Product with this ID already exists"
            )

        # Create the product
        product = ProductService.create_product(db, product_data)
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str, product_data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update an existing product."""
    try:
        product = ProductService.update_product(db, product_id, product_data)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Soft delete a product (sets is_active to False)."""
    try:
        success = ProductService.delete_product(db, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Stock Management


@router.patch("/products/{product_id}/stock")
async def update_product_stock(
    product_id: str,
    size: str = Query(..., description="Product size to update"),
    quantity: int = Query(..., ge=0, description="New stock quantity"),
    db: Session = Depends(get_db),
):
    """Update stock quantity for a specific product size."""
    try:
        success = ProductService.update_stock(db, product_id, size, quantity)
        if not success:
            raise HTTPException(status_code=404, detail="Product or size not found")

        return {"message": f"Stock updated for {product_id} size {size} to {quantity}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating stock for {product_id} size {size}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Tag Management


@router.get("/tags", response_model=List[Tag])
async def get_tags(db: Session = Depends(get_db)):
    """Get all available tags."""
    try:
        from app.models.product import Tag as TagModel

        tags = db.query(TagModel).all()
        return tags

    except Exception as e:
        logger.error(f"Error getting tags: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tags", response_model=Tag, status_code=201)
async def create_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    try:
        from app.models.product import Tag as TagModel

        # Check if tag already exists
        existing_tag = db.query(TagModel).filter(TagModel.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=400, detail="Tag with this name already exists"
            )

        # Create new tag
        tag = TagModel(**tag_data.model_dump())
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/tags/{tag_id}", response_model=Tag)
async def update_tag(tag_id: int, tag_data: TagUpdate, db: Session = Depends(get_db)):
    """Update an existing tag."""
    try:
        from models.product import Tag as TagModel

        tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Update fields
        for field, value in tag_data.model_dump(exclude_unset=True).items():
            setattr(tag, field, value)

        db.commit()
        db.refresh(tag)
        return tag

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag."""
    try:
        from models.product import Tag as TagModel

        tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        db.delete(tag)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Search and Filtering


@router.get("/products/search", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Search products by name or description."""
    try:
        from models.product import Product as ProductModel
        from sqlalchemy import or_

        # Calculate offset
        skip = (page - 1) * size

        # Search products
        products = (
            db.query(ProductModel)
            .filter(
                or_(
                    ProductModel.name.ilike(f"%{q}%"),
                    ProductModel.description.ilike(f"%{q}%"),
                )
            )
            .filter(ProductModel.is_active)
            .offset(skip)
            .limit(size)
            .all()
        )

        # Convert to ProductWithAvailability
        products_with_availability = []
        for product in products:
            availability_info = ProductService.get_product_with_availability(
                db, product.id
            )
            if availability_info:
                products_with_availability.append(availability_info)

        # Get total count
        total = (
            db.query(ProductModel)
            .filter(
                or_(
                    ProductModel.name.ilike(f"%{q}%"),
                    ProductModel.description.ilike(f"%{q}%"),
                )
            )
            .filter(ProductModel.is_active)
            .count()
        )

        # Calculate pagination info
        pages = (total + size - 1) // size

        return ProductListResponse(
            products=products_with_availability,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
