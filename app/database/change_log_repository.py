"""Change log repository for MongoDB operations."""

from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.models.change_log import ChangeLog, ChangeLogCreate

logger = logging.getLogger(__name__)


class ChangeLogRepository:
    """Repository for change log database operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.change_logs
    
    async def create(self, change_log_data: ChangeLogCreate) -> ChangeLog:
        """Create a new change log entry."""
        from uuid import uuid4
        
        change_dict = change_log_data.model_dump()
        change_dict["id"] = str(uuid4())
        change_dict["timestamp"] = datetime.utcnow()
        
        await self.collection.insert_one(change_dict)
        logger.info(f"Created change log entry for book: {change_dict['book_id']}")
        
        return ChangeLog(**change_dict)
    
    async def get_by_book_id(self, book_id: str, limit: int = 50) -> List[ChangeLog]:
        """Get change log entries for a specific book."""
        entries = []
        cursor = self.collection.find({"book_id": book_id}).sort("timestamp", -1).limit(limit)
        async for doc in cursor:
            entries.append(ChangeLog(**doc))
        return entries
    
    async def get_recent_changes(self, limit: int = 100) -> List[ChangeLog]:
        """Get recent change log entries."""
        entries = []
        cursor = self.collection.find({}).sort("timestamp", -1).limit(limit)
        async for doc in cursor:
            entries.append(ChangeLog(**doc))
        return entries
    
    async def get_by_change_type(self, change_type: str, limit: int = 100) -> List[ChangeLog]:
        """Get change log entries by change type."""
        entries = []
        cursor = self.collection.find({"change_type": change_type}).sort("timestamp", -1).limit(limit)
        async for doc in cursor:
            entries.append(ChangeLog(**doc))
        return entries









