"""Scheduler for daily crawling using APScheduler."""

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from app.config import settings
from app.database import init_database, get_database, BookRepository, ChangeLogRepository
from app.crawler import Crawler, ChangeDetector

logger = logging.getLogger(__name__)


class CrawlScheduler:
    """Scheduler for daily book crawling."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def run_crawl(self):
        """Run a full crawl and detect changes."""
        logger.info("Starting scheduled crawl")
        start_time = datetime.utcnow()
        
        try:
            # Initialize database
            await init_database()
            database = await get_database()
            book_repo = BookRepository(database)
            change_log_repo = ChangeLogRepository(database)
            
            # Run crawler
            async with Crawler() as crawler:
                books = await crawler.crawl_all()
            
            logger.info(f"Crawled {len(books)} books")
            
            # Detect changes
            change_detector = ChangeDetector(book_repo, change_log_repo)
            change_logs = await change_detector.process_books(books)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Crawl completed in {duration:.2f} seconds. "
                f"Found {len(change_logs)} changes."
            )
            
            # Log summary
            change_types = {}
            for log in change_logs:
                change_type = log.change_type
                change_types[change_type] = change_types.get(change_type, 0) + 1
            
            for change_type, count in change_types.items():
                logger.info(f"  - {change_type}: {count}")
            
        except Exception as e:
            logger.error(f"Error during scheduled crawl: {e}", exc_info=True)
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled in configuration")
            return
        
        # Schedule daily crawl
        trigger = CronTrigger(
            hour=settings.scheduler_hour,
            minute=settings.scheduler_minute
        )
        
        self.scheduler.add_job(
            self.run_crawl,
            trigger=trigger,
            id='daily_crawl',
            name='Daily Book Crawl',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info(
            f"Scheduler started. Daily crawl scheduled for "
            f"{settings.scheduler_hour:02d}:{settings.scheduler_minute:02d}"
        )
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")


# Global scheduler instance
scheduler = CrawlScheduler()






