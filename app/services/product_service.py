# Standard library imports
import logging
from typing import List, Optional

# Third-party imports
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

# Local application imports
from app.models.product import Product, ProductSize, Tag
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchFilters,
    ProductWithAvailability,
)

logger = logging.getLogger(__name__)


class ProductService:
    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        """Get a product by ID with all relationships loaded."""
        return (
            db.query(Product)
            .options(joinedload(Product.sizes), joinedload(Product.tags))
            .filter(Product.id == product_id)
            .first()
        )

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ProductSearchFilters] = None,
    ) -> List[Product]:
        """Get products with optional filtering."""
        query = db.query(Product).options(
            joinedload(Product.sizes), joinedload(Product.tags)
        )

        if filters:
            if filters.category:
                query = query.filter(Product.category == filters.category)

            if filters.tag:
                query = query.filter(Product.tag == filters.tag)

            if filters.tags:
                query = query.join(Product.tags).filter(Tag.name.in_(filters.tags))

            if filters.min_price is not None:
                query = query.filter(Product.price >= filters.min_price)

            if filters.max_price is not None:
                query = query.filter(Product.price <= filters.max_price)

            if filters.in_stock_only:
                query = query.join(Product.sizes).filter(
                    and_(
                        ProductSize.stock_quantity > 0, ProductSize.is_available == True
                    )
                )

            if filters.is_active is not None:
                query = query.filter(Product.is_active == filters.is_active)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product with sizes and tags."""
        try:
            # Create the product
            db_product = Product(
                id=product_data.id,
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                img=product_data.img,
                category=product_data.category,
                tag=product_data.tag,
                is_active=product_data.is_active,
            )
            db.add(db_product)
            db.flush()  # Get the product ID

            # Add sizes
            for size_data in product_data.sizes:
                db_size = ProductSize(
                    product_id=db_product.id,
                    size=size_data.size,
                    stock_quantity=size_data.stock_quantity,
                    is_available=size_data.is_available,
                )
                db.add(db_size)

            # Add tags
            for tag_name in product_data.tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.flush()
                db_product.tags.append(tag)

            db.commit()
            db.refresh(db_product)
            return db_product

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating product: {str(e)}")
            raise

    @staticmethod
    def update_product(
        db: Session, product_id: str, product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update an existing product."""
        try:
            db_product = ProductService.get_product_by_id(db, product_id)
            if not db_product:
                return None

            # Update basic fields
            for field, value in product_data.model_dump(exclude_unset=True).items():
                if field not in ["sizes", "tag_names"] and hasattr(db_product, field):
                    setattr(db_product, field, value)

            # Update sizes if provided
            if product_data.sizes is not None:
                # Remove existing sizes
                db.query(ProductSize).filter(
                    ProductSize.product_id == product_id
                ).delete()

                # Add new sizes
                for size_data in product_data.sizes:
                    db_size = ProductSize(
                        product_id=product_id,
                        size=size_data.size,
                        stock_quantity=size_data.stock_quantity,
                        is_available=size_data.is_available,
                    )
                    db.add(db_size)

            # Update tags if provided
            if product_data.tag_names is not None:
                # Clear existing tags
                db_product.tags.clear()

                # Add new tags
                for tag_name in product_data.tag_names:
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.flush()
                    db_product.tags.append(tag)

            db.commit()
            db.refresh(db_product)
            return db_product

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise

    @staticmethod
    def delete_product(db: Session, product_id: str) -> bool:
        """Soft delete a product (set is_active to False)."""
        try:
            db_product = db.query(Product).filter(Product.id == product_id).first()
            if not db_product:
                return False

            db_product.is_active = False
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting product {product_id}: {str(e)}")
            raise

    @staticmethod
    def update_stock(db: Session, product_id: str, size: str, quantity: int) -> bool:
        """Update stock for a specific product size."""
        try:
            product_size = (
                db.query(ProductSize)
                .filter(
                    and_(ProductSize.product_id == product_id, ProductSize.size == size)
                )
                .first()
            )

            if not product_size:
                return False

            product_size.stock_quantity = quantity
            product_size.is_available = quantity > 0
            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating stock for {product_id} size {size}: {str(e)}")
            raise

    @staticmethod
    def get_product_with_availability(
        db: Session, product_id: str
    ) -> Optional[ProductWithAvailability]:
        """Get product with computed availability information."""
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return None

        # Compute availability info
        available_sizes = [
            size.size
            for size in product.sizes
            if size.is_available and size.stock_quantity > 0
        ]
        total_stock = sum(size.stock_quantity for size in product.sizes)
        is_in_stock = total_stock > 0

        # Convert to schema with availability info
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "img": product.img,
            "category": product.category,
            "tag": product.tag,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "sizes": product.sizes,
            "tags": product.tags,
            "available_sizes": available_sizes,
            "total_stock": total_stock,
            "is_in_stock": is_in_stock,
        }

        return ProductWithAvailability(**product_dict)
