"""Configuration management using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_db_name: str = Field(default="bookstoscrape", env="MONGODB_DB_NAME")
    
    # API Configuration
    api_key: str = Field(default="your-secret-api-key-here", env="API_KEY")
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    rate_limit_per_hour: int = Field(default=100, env="RATE_LIMIT_PER_HOUR")
    
    # Server Configuration
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Crawler Configuration
    base_url: str = Field(default="https://books.toscrape.com", env="BASE_URL")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    retry_backoff_factor: float = Field(default=2.0, env="RETRY_BACKOFF_FACTOR")
    
    # Scheduler Configuration
    scheduler_enabled: bool = Field(default=True, env="SCHEDULER_ENABLED")
    scheduler_hour: int = Field(default=9, env="SCHEDULER_HOUR")
    scheduler_minute: int = Field(default=0, env="SCHEDULER_MINUTE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()







