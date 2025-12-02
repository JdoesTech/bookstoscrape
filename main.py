"""Main entry point for the application."""

import asyncio
import uvicorn
from app.logging_config import setup_logging
from app.config import settings
from app.scheduler import scheduler

# Setup logging first
setup_logging()
import logging

logger = logging.getLogger(__name__)


def main():
    """Main function to run the application."""
    # Start scheduler if enabled
    if settings.scheduler_enabled:
        scheduler.start()
    
    # Run FastAPI server
    uvicorn.run(
        "app.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        scheduler.stop()









