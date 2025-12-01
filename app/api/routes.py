"""API routes for the FastAPI application."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import logging

from app.api.auth import get_api_key
from app.database import get_database, BookRepository, ChangeLogRepository
from app.models.api import BookQueryParams, PaginatedResponse
from app.models.book import BookResponse
from app.models.change_log import ChangeLog

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/books", response_model=PaginatedResponse[BookResponse])
async def get_books(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    rating: Optional[int] = Query(None, ge=0, le=5, description="Filter by rating"),
    sort_by: Optional[str] = Query("rating", description="Sort by: rating, price, reviews"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    api_key: str = Depends(get_api_key)
):
    """Get paginated list of books with filtering and sorting."""
    try:
        database = await get_database()
        book_repo = BookRepository(database)
        
        params = BookQueryParams(
            category=category,
            min_price=min_price,
            max_price=max_price,
            rating=rating,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )
        
        result = await book_repo.query_books(params)
        return result
        
    except Exception as e:
        logger.error(f"Error fetching books: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get a specific book by ID."""
    try:
        database = await get_database()
        book_repo = BookRepository(database)
        
        book = await book_repo.get_by_id(book_id)
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookResponse(
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
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book {book_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/books/{book_id}/html")
async def get_book_html(
    book_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get raw HTML snapshot for a book."""
    try:
        database = await get_database()
        book_repo = BookRepository(database)
        
        book = await book_repo.get_by_id(book_id)
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if not book.raw_html:
            raise HTTPException(status_code=404, detail="HTML snapshot not available")
        
        return JSONResponse(content={"book_id": book_id, "html": book.raw_html})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching HTML for book {book_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/changes", response_model=list[ChangeLog])
async def get_changes(
    book_id: Optional[str] = Query(None, description="Filter by book ID"),
    change_type: Optional[str] = Query(None, description="Filter by change type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    api_key: str = Depends(get_api_key)
):
    """Get recent change log entries."""
    try:
        database = await get_database()
        change_log_repo = ChangeLogRepository(database)
        
        if book_id:
            changes = await change_log_repo.get_by_book_id(book_id, limit=limit)
        elif change_type:
            changes = await change_log_repo.get_by_change_type(change_type, limit=limit)
        else:
            changes = await change_log_repo.get_recent_changes(limit=limit)
        
        return changes
        
    except Exception as e:
        logger.error(f"Error fetching changes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint (no authentication required)."""
    return {"status": "healthy"}






