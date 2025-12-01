"""Tests for database operations."""

import pytest
from app.models.book import BookCreate
from app.models.change_log import ChangeLogCreate
from app.models.api import BookQueryParams


@pytest.mark.asyncio
async def test_create_book(book_repo):
    """Test creating a book."""
    book_data = BookCreate(
        name="Test Book",
        description="A test book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        number_of_reviews=5,
        rating=4,
        source_url="https://books.toscrape.com/test-book.html"
    )
    
    book = await book_repo.create(book_data)
    
    assert book.id is not None
    assert book.name == "Test Book"
    assert book.category == "Fiction"
    assert book.data_hash is not None


@pytest.mark.asyncio
async def test_get_book_by_id(book_repo):
    """Test getting a book by ID."""
    book_data = BookCreate(
        name="Test Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/test-book.html"
    )
    
    created_book = await book_repo.create(book_data)
    retrieved_book = await book_repo.get_by_id(created_book.id)
    
    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.name == "Test Book"


@pytest.mark.asyncio
async def test_upsert_by_url(book_repo):
    """Test upserting a book by URL."""
    book_data = BookCreate(
        name="Test Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/test-book.html"
    )
    
    # First insert
    book1 = await book_repo.upsert_by_url(book_data)
    assert book1.id is not None
    
    # Update with same URL
    book_data.name = "Updated Book"
    book2 = await book_repo.upsert_by_url(book_data)
    
    assert book2.id == book1.id
    assert book2.name == "Updated Book"


@pytest.mark.asyncio
async def test_query_books(book_repo):
    """Test querying books with filters."""
    # Create test books
    for i in range(5):
        book_data = BookCreate(
            name=f"Book {i}",
            category="Fiction" if i % 2 == 0 else "Non-Fiction",
            price_including_tax=10.0 + i,
            price_excluding_tax=10.0 + i,
            availability="In stock",
            rating=i % 5 + 1,
            source_url=f"https://books.toscrape.com/book-{i}.html"
        )
        await book_repo.create(book_data)
    
    # Test category filter
    params = BookQueryParams(category="Fiction", page=1, page_size=10)
    result = await book_repo.query_books(params)
    assert result.total > 0
    assert all(book.category == "Fiction" for book in result.items)
    
    # Test price filter
    params = BookQueryParams(min_price=12.0, max_price=14.0, page=1, page_size=10)
    result = await book_repo.query_books(params)
    assert result.total > 0
    assert all(12.0 <= book.price_including_tax <= 14.0 for book in result.items)


@pytest.mark.asyncio
async def test_create_change_log(change_log_repo):
    """Test creating a change log entry."""
    change_log_data = ChangeLogCreate(
        book_id="test-book-id",
        changed_fields=["price_including_tax"],
        old_values={"price_including_tax": 19.99},
        new_values={"price_including_tax": 15.99},
        change_type="price_change"
    )
    
    change_log = await change_log_repo.create(change_log_data)
    
    assert change_log.id is not None
    assert change_log.book_id == "test-book-id"
    assert change_log.change_type == "price_change"


@pytest.mark.asyncio
async def test_get_recent_changes(change_log_repo):
    """Test getting recent changes."""
    # Create multiple change logs
    for i in range(3):
        change_log_data = ChangeLogCreate(
            book_id=f"book-{i}",
            changed_fields=["price_including_tax"],
            old_values={"price_including_tax": 19.99},
            new_values={"price_including_tax": 15.99},
            change_type="price_change"
        )
        await change_log_repo.create(change_log_data)
    
    changes = await change_log_repo.get_recent_changes(limit=10)
    assert len(changes) >= 3






