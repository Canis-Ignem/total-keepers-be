from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


# Tag schemas
class TagBase(BaseModel):
    name: str
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Tag(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Product Size schemas
class ProductSizeBase(BaseModel):
    size: str
    stock_quantity: int = 0
    is_available: bool = True


class ProductSizeCreate(ProductSizeBase):
    pass


class ProductSizeUpdate(BaseModel):
    size: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_available: Optional[bool] = None


class ProductSize(ProductSizeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductTranslationBase(BaseModel):
    language_code: str
    name: str
    short_description: Optional[str] = None
    description: Optional[str] = None  # Markdown


class ProductTranslationCreate(ProductTranslationBase):
    product_id: str


class ProductTranslation(ProductTranslationBase):
    id: int
    product_id: str


# Product schemas
class ProductBase(BaseModel):
    name: str  # Default/fallback name
    price: float
    discount_price: Optional[float] = None  # Nullable, for sales
    short_description: Optional[str] = None  # Default/fallback short text
    description: Optional[str] = None  # Default/fallback markdown
    img: Optional[str] = None  # Image path/URL (legacy)
    images: Optional[List[str]] = None  # List of publicly accessible blob URLs
    category: str = "GOALKEEPER_GLOVES"  # Product category
    tag: Optional[str] = None  # Main tag like "JUNIOR", "SENIOR", etc.
    priority: int = 0  # Display priority (higher = shown first)
    is_active: bool = True  # For soft delete/hide products

    def get_current_price(self) -> float:
        """Return the current price considering discount if available"""
        return self.discount_price if self.discount_price is not None else self.price

class ProductCreate(ProductBase):
    id: str  # Required for creation
    sizes: List[ProductSizeCreate] = []  # List of sizes to associate
    translations: List[
        ProductTranslationCreate
    ] = []  # List of translations to associate
    tag_names: List[str] = []  # List of tag names to associate


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    images: Optional[List[str]] = None  # Allow updating blob storage URLs
    category: Optional[str] = None
    tag: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    sizes: Optional[List[ProductSizeUpdate]] = None
    translations: Optional[List[ProductTranslationCreate]] = None
    tag_names: Optional[List[str]] = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    sizes: List[ProductSize] = []
    translations: List[ProductTranslation] = []
    tags: List[Tag] = []


class ProductWithAvailability(Product):
    """Product with computed availability info"""

    available_sizes: List[str] = []  # List of sizes that are in stock
    total_stock: int = 0  # Total stock across all sizes
    is_in_stock: bool = False  # True if any size is available


# Response schemas
class ProductListResponse(BaseModel):
    products: List[ProductWithAvailability]
    total: int
    page: int
    size: int
    pages: int


class ProductSearchFilters(BaseModel):
    category: Optional[str] = None
    tag: Optional[str] = None
    tags: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock_only: bool = False
    is_active: bool = True
