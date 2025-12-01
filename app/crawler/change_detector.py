"""Change detection system for books."""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.models.book import Book, BookCreate
from app.models.change_log import ChangeLogCreate
from app.database import BookRepository, ChangeLogRepository
from app.crawler.utils import generate_data_hash

logger = logging.getLogger(__name__)


class ChangeDetector:
    """Detects changes in book data."""
    
    def __init__(self, book_repo: BookRepository, change_log_repo: ChangeLogRepository):
        self.book_repo = book_repo
        self.change_log_repo = change_log_repo
    
    def _detect_changes(
        self,
        old_book: Book,
        new_book_data: BookCreate
    ) -> Optional[Dict[str, Any]]:
        """Detect changes between old and new book data."""
        changes = {}
        old_values = {}
        new_values = {}
        
        # Check name
        if old_book.name != new_book_data.name:
            changes["name"] = True
            old_values["name"] = old_book.name
            new_values["name"] = new_book_data.name
        
        # Check prices
        if abs(old_book.price_including_tax - new_book_data.price_including_tax) > 0.01:
            changes["price_including_tax"] = True
            old_values["price_including_tax"] = old_book.price_including_tax
            new_values["price_including_tax"] = new_book_data.price_including_tax
        
        if abs(old_book.price_excluding_tax - new_book_data.price_excluding_tax) > 0.01:
            changes["price_excluding_tax"] = True
            old_values["price_excluding_tax"] = old_book.price_excluding_tax
            new_values["price_excluding_tax"] = new_book_data.price_excluding_tax
        
        # Check availability
        if old_book.availability != new_book_data.availability:
            changes["availability"] = True
            old_values["availability"] = old_book.availability
            new_values["availability"] = new_book_data.availability
        
        # Check rating
        if old_book.rating != new_book_data.rating:
            changes["rating"] = True
            old_values["rating"] = old_book.rating
            new_values["rating"] = new_book_data.rating
        
        # Check description
        if old_book.description != new_book_data.description:
            changes["description"] = True
            old_values["description"] = old_book.description
            new_values["description"] = new_book_data.description
        
        # Check number of reviews
        if old_book.number_of_reviews != new_book_data.number_of_reviews:
            changes["number_of_reviews"] = True
            old_values["number_of_reviews"] = old_book.number_of_reviews
            new_values["number_of_reviews"] = new_book_data.number_of_reviews
        
        if not changes:
            return None
        
        return {
            "changed_fields": list(changes.keys()),
            "old_values": old_values,
            "new_values": new_values
        }
    
    def _determine_change_type(self, changed_fields: List[str]) -> str:
        """Determine the type of change."""
        if "price_including_tax" in changed_fields or "price_excluding_tax" in changed_fields:
            return "price_change"
        elif "availability" in changed_fields:
            return "availability_change"
        elif "name" in changed_fields or "description" in changed_fields:
            return "metadata_change"
        elif "rating" in changed_fields:
            return "rating_change"
        else:
            return "other_change"
    
    async def process_book(self, new_book_data: BookCreate) -> Optional[ChangeLogCreate]:
        """Process a new book and detect changes."""
        # Check if book exists
        existing_book = await self.book_repo.get_by_url(str(new_book_data.source_url))
        
        if not existing_book:
            # New book
            book = await self.book_repo.upsert_by_url(new_book_data)
            
            change_log = ChangeLogCreate(
                book_id=book.id,
                changed_fields = {},
                old_values={},
                new_values=new_book_data.model_dump(),
                change_type="new_book"
            )
            
            await self.change_log_repo.create(change_log)
            logger.info(f"New book detected: {book.name}")
            return change_log
        
        # Check for changes using hash
        new_hash = generate_data_hash(new_book_data.model_dump())
        
        if existing_book.data_hash == new_hash:
            # No changes detected
            # Still update crawl timestamp
            await self.book_repo.update(existing_book.id, {"crawl_timestamp": datetime.utcnow()})
            return None
        
        # Changes detected - analyze them
        change_info = self._detect_changes(existing_book, new_book_data)
        
        if change_info:
            change_type = self._determine_change_type(change_info["changed_fields"])
            
            # Update book
            update_data = new_book_data.model_dump()
            update_data["data_hash"] = new_hash
            await self.book_repo.update(existing_book.id, update_data)
            
            # Create change log
            change_log = ChangeLogCreate(
                book_id=existing_book.id,
                changed_fields=change_info["changed_fields"],
                old_values=change_info["old_values"],
                new_values=change_info["new_values"],
                change_type=change_type
            )
            
            await self.change_log_repo.create(change_log)
            
            logger.info(
                f"Change detected for book {existing_book.name}: "
                f"{change_type} - {', '.join(change_info['changed_fields'])}"
            )
            
            return change_log
        
        return None
    
    async def process_books(self, books: List[BookCreate]) -> List[ChangeLogCreate]:
        """Process multiple books and detect changes."""
        change_logs = []
        
        for book_data in books:
            try:
                change_log = await self.process_book(book_data)
                if change_log:
                    change_logs.append(change_log)
            except Exception as e:
                logger.error(f"Error processing book {book_data.source_url}: {e}")
        
        return change_logs






