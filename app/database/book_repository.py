"""Book repository for MongoDB operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.models.book import Book, BookCreate, BookResponse
from app.models.api import BookQueryParams, PaginatedResponse

logger = logging.getLogger(__name__)


class BookRepository:
    """Repository for book database operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.books
    
    async def create(self, book_data: BookCreate) -> Book:
        """Create a new book document."""
        from app.crawler.utils import generate_data_hash
        from uuid import uuid4
        
        book_dict = book_data.model_dump()
        book_dict["id"] = str(uuid4())
        book_dict["crawl_timestamp"] = datetime.utcnow()
        book_dict["status"] = "active"
        
        # Generate hash for change detection
        book_dict["data_hash"] = generate_data_hash(book_dict)
        
        result = await self.collection.insert_one(book_dict)
        logger.debug(f"Created book: {result.inserted_id}")
        
        return Book(**book_dict)
    
    async def get_by_id(self, book_id: str) -> Optional[Book]:
        """Get a book by ID."""
        book_doc = await self.collection.find_one({"id": book_id})
        if book_doc:
            return Book(**book_doc)
        return None
    
    async def get_by_url(self, url: str) -> Optional[Book]:
        """Get a book by source URL."""
        book_doc = await self.collection.find_one({"source_url": url})
        if book_doc:
            return Book(**book_doc)
        return None
    
    async def update(self, book_id: str, update_data: Dict[str, Any]) -> Optional[Book]:
        """Update a book document."""
        update_data["crawl_timestamp"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"id": book_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_by_id(book_id)
        return None
    
    async def upsert_by_url(self, book_data: BookCreate) -> Book:
        """Insert or update a book by source URL."""
        from app.crawler.utils import generate_data_hash
        
        existing = await self.get_by_url(str(book_data.source_url))
        
        book_dict = book_data.model_dump()
        book_dict["crawl_timestamp"] = datetime.utcnow()
        book_dict["status"] = "active"
        book_dict["data_hash"] = generate_data_hash(book_dict)
        
        if existing:
            # Update existing
            book_dict["id"] = existing.id
            await self.collection.update_one(
                {"source_url": str(book_data.source_url)},
                {"$set": book_dict}
            )
            return Book(**book_dict)
        else:
            # Insert new
            from uuid import uuid4
            book_dict["id"] = str(uuid4())
            await self.collection.insert_one(book_dict)
            return Book(**book_dict)
    
    async def query_books(
        self,
        params: BookQueryParams
    ) -> PaginatedResponse[BookResponse]:
        """Query books with filters, sorting, and pagination."""
        # Build filter
        filter_dict: Dict[str, Any] = {"status": "active"}
        
        if params.category:
            filter_dict["category"] = params.category
        
        if params.min_price is not None or params.max_price is not None:
            price_filter: Dict[str, Any] = {}
            if params.min_price is not None:
                price_filter["$gte"] = params.min_price
            if params.max_price is not None:
                price_filter["$lte"] = params.max_price
            filter_dict["price_including_tax"] = price_filter
        
        if params.rating is not None:
            filter_dict["rating"] = params.rating
        
        # Build sort
        sort_dict: Dict[str, int] = {}
        if params.sort_by == "rating":
            sort_dict["rating"] = -1
        elif params.sort_by == "price":
            sort_dict["price_including_tax"] = 1
        elif params.sort_by == "reviews":
            sort_dict["number_of_reviews"] = -1
        else:
            sort_dict["rating"] = -1  # Default
        
        # Get total count
        total = await self.collection.count_documents(filter_dict)
        
        # Get paginated results
        skip = (params.page - 1) * params.page_size
        cursor = self.collection.find(filter_dict).sort(list(sort_dict.items())).skip(skip).limit(params.page_size)
        
        books = []
        async for doc in cursor:
            book = Book(**doc)
            books.append(BookResponse(
                id=book.id,
                name=book.name,
                description=book.description,
                category=book.category,
                price_including_tax=book.price_including_tax,
                price_excluding_tax=book.price_excluding_tax,
                availability=book.availability,
                number_of_reviews=book.number_of_reviews,
                image_url=str(book.image_url) if book.image_url else None,
                rating=book.rating,
                source_url=str(book.source_url),
                crawl_timestamp=book.crawl_timestamp,
                status=book.status
            ))
        
        return PaginatedResponse.create(books, total, params.page, params.page_size)
    
    async def get_all_books(self) -> List[Book]:
        """Get all books (for change detection)."""
        books = []
        async for doc in self.collection.find({"status": "active"}):
            books.append(Book(**doc))
        return books

