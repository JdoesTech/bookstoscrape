"""Change log models for tracking book changes."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class ChangeLogCreate(BaseModel):
    """Model for creating a change log entry."""
    
    book_id: str = Field(..., description="Book ID")
    changed_fields: Dict[str, Any] = Field(..., description="Fields that changed")
    old_values: Dict[str, Any] = Field(..., description="Old values")
    new_values: Dict[str, Any] = Field(..., description="New values")
    change_type: str = Field(..., description="Type of change (new_book, price_change, availability_change, etc.)")


class ChangeLog(BaseModel):
    """Change log entry model."""
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Change log entry ID")
    book_id: str = Field(..., description="Book ID")
    changed_fields: Dict[str, Any] = Field(..., description="Fields that changed")
    old_values: Dict[str, Any] = Field(..., description="Old values")
    new_values: Dict[str, Any] = Field(..., description="New values")
    change_type: str = Field(..., description="Type of change")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Change timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "book_id": "550e8400-e29b-41d4-a716-446655440000",
                "changed_fields": ["price_including_tax", "price_excluding_tax"],
                "old_values": {"price_including_tax": 51.77, "price_excluding_tax": 51.77},
                "new_values": {"price_including_tax": 45.99, "price_excluding_tax": 45.99},
                "change_type": "price_change",
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }






