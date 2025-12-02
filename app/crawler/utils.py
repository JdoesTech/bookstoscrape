"""Utility functions for the crawler."""

import hashlib
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def generate_data_hash(data: Dict[str, Any]) -> str:
    """Generate a hash for change detection based on significant fields."""
    significant_fields = {
        "name": data.get("name", ""),
        "price_including_tax": data.get("price_including_tax", 0),
        "price_excluding_tax": data.get("price_excluding_tax", 0),
        "availability": data.get("availability", ""),
        "rating": data.get("rating", 0),
    }
    
    # Create a stable JSON string
    json_str = json.dumps(significant_fields, sort_keys=True)
    
    # Generate hash
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()


def rating_to_int(rating_text: str) -> int:
    """Convert star rating text to integer (0-5)."""
    rating_map = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    
    rating_text = rating_text.lower().strip()
    for key, value in rating_map.items():
        if key in rating_text:
            return value
    
    return 0









