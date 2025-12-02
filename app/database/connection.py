"""MongoDB connection management using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def init_database() -> None:
    """Initialize MongoDB connection."""
    global _client, _database
    
    try:
        _client = AsyncIOMotorClient(settings.mongodb_url)
        _database = _client[settings.mongodb_db_name]
        
        # Test connection
        await _client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
        
        # Create indexes
        await _create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def _create_indexes() -> None:
    """Create database indexes for optimal querying."""
    if _database is None:
        return
    
    # Books collection indexes
    books_collection = _database.books
    await books_collection.create_index("id", unique=True)
    await books_collection.create_index("category")
    await books_collection.create_index("rating")
    await books_collection.create_index("price_including_tax")
    await books_collection.create_index("source_url", unique=True)
    await books_collection.create_index("data_hash")
    await books_collection.create_index("crawl_timestamp")
    
    # Change log collection indexes
    change_log_collection = _database.change_logs
    await change_log_collection.create_index("book_id")
    await change_log_collection.create_index("timestamp")
    await change_log_collection.create_index("change_type")
    
    logger.info("Database indexes created successfully")


async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _database


async def close_database() -> None:
    """Close MongoDB connection."""
    global _client, _database
    
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")









