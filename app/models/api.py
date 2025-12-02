"""API request/response models."""

from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class BookQueryParams(BaseModel):
    """Query parameters for book listing endpoint."""
    
    category: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    rating: Optional[int] = Field(None, ge=0, le=5, description="Filter by rating")
    sort_by: Optional[str] = Field("rating", description="Sort by: rating, price, reviews")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )







