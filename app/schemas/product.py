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


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    img: Optional[str] = None
    category: str = "GOALKEEPER_GLOVES"
    tag: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    id: str  # Required for creation
    sizes: List[ProductSizeCreate] = []
    tag_names: List[str] = []  # List of tag names to associate


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    img: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    is_active: Optional[bool] = None
    sizes: Optional[List[ProductSizeCreate]] = None
    tag_names: Optional[List[str]] = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    sizes: List[ProductSize] = []
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
