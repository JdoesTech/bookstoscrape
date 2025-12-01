"""Tests for the crawler."""

import pytest
from app.crawler.utils import rating_to_int, generate_data_hash
from app.models.book import BookCreate


def test_rating_to_int():
    """Test rating text to integer conversion."""
    assert rating_to_int("One") == 1
    assert rating_to_int("Two") == 2
    assert rating_to_int("Three") == 3
    assert rating_to_int("Four") == 4
    assert rating_to_int("Five") == 5
    assert rating_to_int("Zero") == 0
    assert rating_to_int("unknown") == 0


def test_generate_data_hash():
    """Test data hash generation."""
    data1 = {
        "name": "Test Book",
        "price_including_tax": 10.99,
        "price_excluding_tax": 10.99,
        "availability": "In stock",
        "rating": 4
    }
    
    data2 = {
        "name": "Test Book",
        "price_including_tax": 10.99,
        "price_excluding_tax": 10.99,
        "availability": "In stock",
        "rating": 4
    }
    
    data3 = {
        "name": "Test Book",
        "price_including_tax": 15.99,  # Different price
        "price_excluding_tax": 15.99,
        "availability": "In stock",
        "rating": 4
    }
    
    hash1 = generate_data_hash(data1)
    hash2 = generate_data_hash(data2)
    hash3 = generate_data_hash(data3)
    
    # Same data should produce same hash
    assert hash1 == hash2
    
    # Different data should produce different hash
    assert hash1 != hash3
    
    # Hash should be a string
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 produces 64 character hex string






