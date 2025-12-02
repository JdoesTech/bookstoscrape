"""Tests for change detection."""

import pytest
from app.models.book import Book, BookCreate
from app.database import BookRepository, ChangeLogRepository
from app.crawler.change_detector import ChangeDetector


@pytest.mark.asyncio
async def test_detect_new_book(book_repo, change_log_repo):
    """Test detecting a new book."""
    detector = ChangeDetector(book_repo, change_log_repo)
    
    book_data = BookCreate(
        name="New Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/new-book.html"
    )
    
    change_log = await detector.process_book(book_data)
    
    assert change_log is not None
    assert change_log.change_type == "new_book"
    assert "new_book" in change_log.changed_fields


@pytest.mark.asyncio
async def test_detect_price_change(book_repo, change_log_repo):
    """Test detecting a price change."""
    detector = ChangeDetector(book_repo, change_log_repo)
    
    # Create initial book
    book_data = BookCreate(
        name="Test Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/test-book.html"
    )
    
    await detector.process_book(book_data)
    
    # Update with new price
    book_data.price_including_tax = 15.99
    book_data.price_excluding_tax = 15.99
    
    change_log = await detector.process_book(book_data)
    
    assert change_log is not None
    assert change_log.change_type == "price_change"
    assert "price_including_tax" in change_log.changed_fields


@pytest.mark.asyncio
async def test_detect_availability_change(book_repo, change_log_repo):
    """Test detecting an availability change."""
    detector = ChangeDetector(book_repo, change_log_repo)
    
    # Create initial book
    book_data = BookCreate(
        name="Test Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/test-book-2.html"
    )
    
    await detector.process_book(book_data)
    
    # Update availability
    book_data.availability = "Out of stock"
    
    change_log = await detector.process_book(book_data)
    
    assert change_log is not None
    assert change_log.change_type == "availability_change"
    assert "availability" in change_log.changed_fields


@pytest.mark.asyncio
async def test_no_change_detected(book_repo, change_log_repo):
    """Test that no change is detected when data is the same."""
    detector = ChangeDetector(book_repo, change_log_repo)
    
    # Create initial book
    book_data = BookCreate(
        name="Test Book",
        category="Fiction",
        price_including_tax=19.99,
        price_excluding_tax=19.99,
        availability="In stock",
        rating=4,
        source_url="https://books.toscrape.com/test-book-3.html"
    )
    
    await detector.process_book(book_data)
    
    # Process same data again
    change_log = await detector.process_book(book_data)
    
    # Should return None (no changes)
    assert change_log is None







