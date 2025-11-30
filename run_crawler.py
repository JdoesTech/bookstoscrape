"""Script to run a one-time crawl."""

import asyncio
import logging
from app.logging_config import setup_logging
from app.database import init_database, get_database, close_database
from app.database import BookRepository, ChangeLogRepository
from app.crawler import Crawler, ChangeDetector

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def main():
    """Run a one-time crawl."""
    try:
        # Initialize database
        await init_database()
        database = await get_database()
        book_repo = BookRepository(database)
        change_log_repo = ChangeLogRepository(database)
        
        # Run crawler
        logger.info("Starting crawler...")
        async with Crawler() as crawler:
            books = await crawler.crawl_all()
        
        logger.info(f"Crawled {len(books)} books")
        
        # Detect changes
        logger.info("Detecting changes...")
        change_detector = ChangeDetector(book_repo, change_log_repo)
        change_logs = await change_detector.process_books(books)
        
        logger.info(f"Found {len(change_logs)} changes")
        
        # Log summary
        change_types = {}
        for log in change_logs:
            change_type = log.change_type
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        logger.info("Change summary:")
        for change_type, count in change_types.items():
            logger.info(f"  - {change_type}: {count}")
        
    except Exception as e:
        logger.error(f"Error during crawl: {e}", exc_info=True)
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())



