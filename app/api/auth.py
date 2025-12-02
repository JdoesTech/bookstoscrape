"""Authentication and rate limiting for FastAPI."""

from typing import Dict
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Header, Request
from fastapi.security import APIKeyHeader
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# API Key authentication
api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)

# Rate limiting storage (in-memory, for production use Redis)
rate_limit_store: Dict[str, Dict[str, any]] = {}


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate API key."""
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return api_key


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    api_key = request.headers.get(settings.api_key_header)
    
    if not api_key:
        # If no API key, still allow but with stricter limits
        client_id = request.client.host if request.client else "anonymous"
    else:
        client_id = api_key
    
    # Check rate limit
    now = datetime.utcnow()
    hour_ago = now - timedelta(hours=1)
    
    if client_id not in rate_limit_store:
        rate_limit_store[client_id] = {
            "requests": [],
            "count": 0
        }
    
    client_data = rate_limit_store[client_id]
    
    # Remove old requests
    client_data["requests"] = [
        req_time for req_time in client_data["requests"]
        if req_time > hour_ago
    ]
    client_data["count"] = len(client_data["requests"])
    
    # Check if limit exceeded
    limit = settings.rate_limit_per_hour
    if client_data["count"] >= limit:
        logger.warning(f"Rate limit exceeded for {client_id}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {limit} requests per hour."
        )
    
    # Add current request
    client_data["requests"].append(now)
    client_data["count"] += 1
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(limit - client_data["count"])
    response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(hours=1)).timestamp()))
    
    return response









