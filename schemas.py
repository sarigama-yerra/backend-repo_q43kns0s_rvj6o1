"""
Database Schemas for Hip-Hop Producer E-commerce

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Category like 'Drum Kits', 'Samples', 'Services'")
    type: str = Field(..., description="Specific type e.g. 'drum_kit', 'sample_pack', 'mixing', 'mastering'")
    image: Optional[str] = Field(None, description="Image URL")
    tags: Optional[List[str]] = Field(default_factory=list, description="Searchable tags")
    download_url: Optional[str] = Field(None, description="Download link for digital goods (set after purchase)")
    is_service: bool = Field(False, description="True if this is a service offering")
    is_featured: bool = Field(False, description="Show in featured section")
    in_stock: bool = Field(True, description="Whether product is available")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID of the product")
    title: str = Field(...)
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str = Field(...)
    customer_email: EmailStr = Field(...)
    notes: Optional[str] = Field(None)
    total: float = Field(..., ge=0)
    items: List[OrderItem] = Field(...)
    status: str = Field("pending", description="pending | paid | fulfilled | cancelled")

class ServiceRequest(BaseModel):
    """
    Service requests for mixing/mastering
    Collection name: "servicerequest"
    """
    name: str = Field(...)
    email: EmailStr = Field(...)
    service_type: str = Field(..., description="mixing | mastering | custom")
    message: Optional[str] = Field(None)
    reference_links: Optional[List[str]] = Field(default_factory=list)
