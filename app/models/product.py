# Standard library imports

# Third-party imports
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Text,
    Boolean,
    ForeignKey,
    Table,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Local application imports
from app.core.database import Base

# Association table for product tags (many-to-many relationship)
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", String, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class ProductTranslation(Base):
    __tablename__ = "product_translations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    language_code = Column(String(10), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    short_description = Column(String(255))  # Short plain text
    description = Column(Text)  # Long markdown

    product = relationship("Product", back_populates="translations")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)  # e.g., "guante_speed_junior"
    name = Column(String(255), nullable=False, index=True)  # Default/fallback name
    price = Column(Float, nullable=False)
    discount_price = Column(Float)  # Nullable, for sales
    short_description = Column(String(255))  # Default/fallback short text
    description = Column(Text)  # Default/fallback markdown
    img = Column(String(500))  # Image path/URL
    category = Column(String(100), default="GOALKEEPER_GLOVES")  # Product category
    tag = Column(String(50))  # Main tag like "JUNIOR", "SENIOR", etc.
    priority = Column(Integer, default=0, index=True)  # Display priority (higher = shown first)
    is_active = Column(Boolean, default=True)  # For soft delete/hide products
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    translations = relationship(
        "ProductTranslation", back_populates="product", cascade="all, delete-orphan"
    )

    # Relationships
    sizes = relationship(
        "ProductSize", back_populates="product", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    # Note: cart_items and order_items relationships are defined in their respective models
    # to avoid circular import issues

    def get_current_price(self) -> float:
        """Return the current price considering discount if available"""
        return self.discount_price if self.discount_price is not None else self.price

    def __repr__(self):
        return f"<Product(id='{self.id}', name='{self.name}')>"


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    size = Column(String(10), nullable=False)  # e.g., "5", "6", "7"
    stock_quantity = Column(Integer, default=0)  # Available quantity for this size
    is_available = Column(Boolean, default=True)  # Quick availability flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="sizes")

    def __repr__(self):
        return f"<ProductSize(product_id='{self.product_id}', size='{self.size}', stock={self.stock_quantity})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(50), unique=True, nullable=False, index=True
    )  # e.g., "junior", "ligero"
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", secondary=product_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"
