"""Book models for data validation and serialization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_serializer
from uuid import UUID, uuid4


class Book(BaseModel):
    """Book model with all scraped fields."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique book identifier")
    name: str = Field(..., description="Book name/title")
    description: Optional[str] = Field(None, description="Book description")
    category: str = Field(..., description="Book category")
    price_including_tax: float = Field(..., description="Price including tax")
    price_excluding_tax: float = Field(..., description="Price excluding tax")
    availability: str = Field(..., description="Availability status")
    number_of_reviews: int = Field(default=0, description="Number of reviews")
    image_url: Optional[HttpUrl] = Field(None, description="Book image URL")
    rating: int = Field(..., ge=0, le=5, description="Rating (0-5 stars)")
    source_url: HttpUrl = Field(..., description="Source URL of the book page")
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Crawl timestamp")
    status: str = Field(default="active", description="Book status")
    raw_html: Optional[str] = Field(None, description="Raw HTML snapshot")
    data_hash: Optional[str] = Field(None, description="Hash of significant fields for change detection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "A Light in the Attic",
                "description": "It's hard to imagine a world without A Light in the Attic...",
                "category": "Poetry",
                "price_including_tax": 51.77,
                "price_excluding_tax": 51.77,
                "availability": "In stock (22 available)",
                "number_of_reviews": 0,
                "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
                "rating": 3,
                "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
                "crawl_timestamp": "2025-01-15T10:30:00Z",
                "status": "active",
                "data_hash": "abc123def456..."
            }
        }


class BookCreate(BaseModel):
    """Model for creating a book (used internally)."""
    
    name: str
    description: Optional[str] = None
    category: str
    price_including_tax: float
    price_excluding_tax: float
    availability: str
    number_of_reviews: int = 0
    image_url: Optional[HttpUrl] = None
    rating: int
    source_url: HttpUrl
    raw_html: Optional[str] = None

    @field_serializer('image_url', 'source_url')
    def serialize_url(self, value: Optional[HttpUrl]) -> Optional[str]:
        return str(value) if value else None

class BookResponse(BaseModel):
    """Book response model for API."""
    
    id: str
    name: str
    description: Optional[str]
    category: str
    price_including_tax: float
    price_excluding_tax: float
    availability: str
    number_of_reviews: int
    image_url: Optional[str]
    rating: int
    source_url: str
    crawl_timestamp: datetime
    status: str
    
    class Config:
        from_attributes = True






