"""Async web crawler for books.toscrape.com."""

import asyncio
import aiohttp
from typing import List, Set, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime

from app.config import settings
from app.models.book import BookCreate
from app.crawler.utils import rating_to_int, generate_data_hash

logger = logging.getLogger(__name__)


class Crawler:
    """Asynchronous web crawler for books.toscrape.com."""
    
    def __init__(self, max_concurrent: Optional[int] = None):
        self.base_url = settings.base_url
        self.max_concurrent = max_concurrent or settings.max_concurrent_requests
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Set[str] = set()
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _fetch_with_retry(
        self,
        url: str,
        max_attempts: int = None,
        backoff_factor: float = None
    ) -> Optional[str]:
        """Fetch URL with exponential backoff retry logic."""
        max_attempts = max_attempts or settings.retry_max_attempts
        backoff_factor = backoff_factor or settings.retry_backoff_factor
        
        for attempt in range(max_attempts):
            try:
                async with self.semaphore:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 404:
                            logger.warning(f"404 Not Found: {url}")
                            return None
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            if attempt < max_attempts - 1:
                                await asyncio.sleep(backoff_factor ** attempt)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {url} (attempt {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(backoff_factor ** attempt)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e} (attempt {attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(backoff_factor ** attempt)
        
        logger.error(f"Failed to fetch {url} after {max_attempts} attempts")
        return None
    
    def _parse_book_page(self, html: str, url: str) -> Optional[BookCreate]:
        """Parse a single book page and extract book data."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract book name
            name_elem = soup.select_one('h1')
            name = name_elem.get_text(strip=True) if name_elem else "Unknown"
            
            # Extract description
            desc_elem = soup.select_one('#product_description + p')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract category
            breadcrumb = soup.select('.breadcrumb a')
            category = breadcrumb[-1].get_text(strip=True) if len(breadcrumb) > 1 else "Uncategorized"
            
            # Extract prices from table
            price_including_tax = 0.0
            price_excluding_tax = 0.0
            number_of_reviews = 0
            
            table_rows = soup.select('table tr')
            for row in table_rows:
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    th_text = th.get_text(strip=True)
                    td_text = td.get_text(strip=True)
                    
                    if "Price (incl. tax)" in th_text:
                        try:
                            price_including_tax = float(td_text.replace('£', '').replace('€', '').replace('$', '').replace(',', ''))
                        except ValueError:
                            pass
                    elif "Price (excl. tax)" in th_text:
                        try:
                            price_excluding_tax = float(td_text.replace('£', '').replace('€', '').replace('$', '').replace(',', ''))
                        except ValueError:
                            pass
                    elif "Number of reviews" in th_text:
                        try:
                            number_of_reviews = int(td_text)
                        except ValueError:
                            number_of_reviews = 0
            
            # Extract availability
            availability_elem = soup.select_one('p.availability')
            availability = availability_elem.get_text(strip=True) if availability_elem else "Unknown"
            
            # Extract image URL
            image_elem = soup.select_one('#product_gallery img')
            image_url = None
            if image_elem:
                img_src = image_elem.get('src', '')
                if img_src:
                    image_url = urljoin(url, img_src)
            
            # Extract rating
            rating_elem = soup.select_one('p.star-rating')
            rating = 0
            if rating_elem:
                rating_class = rating_elem.get('class', [])
                for cls in rating_class:
                    if cls != 'star-rating':
                        rating = rating_to_int(cls)
                        break
            
            # Create book data
            book_data = BookCreate(
                name=name,
                description=description,
                category=category,
                price_including_tax=price_including_tax,
                price_excluding_tax=price_excluding_tax,
                availability=availability,
                number_of_reviews=number_of_reviews,
                image_url=image_url,
                rating=rating,
                source_url=url,
                raw_html=html
            )
            
            return book_data
            
        except Exception as e:
            logger.error(f"Error parsing book page {url}: {e}")
            return None
    
    def _extract_book_urls_from_category(self, html: str, current_url: str) -> List[str]:
        """Extract all book URLs from a category page."""
        soup = BeautifulSoup(html, 'lxml')
        book_urls = []
        
        # Find all book links
        book_links = soup.select('article.product_pod h3 a')
        for link in book_links:
            href = link.get('href', '')
            if href:
                full_url = urljoin(current_url, href)
                book_urls.append(full_url)
        
        return book_urls
    
    def _get_next_page_url(self, html: str, current_url: str) -> Optional[str]:
        """Get the next page URL from pagination."""
        soup = BeautifulSoup(html, 'lxml')
        next_link = soup.select_one('li.next a')
        
        if next_link:
            href = next_link.get('href', '')
            if href:
                return urljoin(current_url, href)
        
        return None
    
    async def crawl_category(self, category_url: str) -> List[BookCreate]:
        """Crawl all books from a category (handles pagination)."""
        books = []
        current_url = category_url
        
        while current_url:
            if current_url in self.visited_urls:
                break
            
            self.visited_urls.add(current_url)
            logger.info(f"Crawling category page: {current_url}")
            
            html = await self._fetch_with_retry(current_url)
            if not html:
                break
            
            # Extract book URLs from current page
            book_urls = self._extract_book_urls_from_category(html, current_url)
            
            # Crawl all books on this page concurrently
            tasks = [self.crawl_book(url) for url in book_urls]
            page_books = await asyncio.gather(*tasks, return_exceptions=True)
            
            for book in page_books:
                if isinstance(book, BookCreate):
                    books.append(book)
                elif isinstance(book, Exception):
                    logger.error(f"Error crawling book: {book}")
            
            # Get next page URL
            current_url = self._get_next_page_url(html, current_url)
        
        return books
    
    async def crawl_book(self, url: str) -> Optional[BookCreate]:
        """Crawl a single book page."""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        logger.debug(f"Crawling book: {url}")
        
        html = await self._fetch_with_retry(url)
        if not html:
            return None
        
        return self._parse_book_page(html, url)
    
    async def get_all_categories(self) -> List[str]:
        """Get all category URLs from the main page."""
        main_url = self.base_url
        html = await self._fetch_with_retry(main_url)
        
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        category_urls = []
        
        # Find category links in sidebar
        category_links = soup.select('.side_categories ul li ul li a')
        for link in category_links:
            href = link.get('href', '')
            if href:
                category_url = urljoin(main_url, href)
                category_urls.append(category_url)
        
        return category_urls
    
    async def crawl_all(self) -> List[BookCreate]:
        """Crawl all books from all categories."""
        logger.info("Starting full crawl of books.toscrape.com")
        
        # Get all categories
        categories = await self.get_all_categories()
        logger.info(f"Found {len(categories)} categories")
        
        # Crawl all categories concurrently (with semaphore limiting)
        all_books = []
        
        for category_url in categories:
            try:
                books = await self.crawl_category(category_url)
                all_books.extend(books)
                logger.info(f"Crawled {len(books)} books from category: {category_url}")
            except Exception as e:
                logger.error(f"Error crawling category {category_url}: {e}")
        
        logger.info(f"Total books crawled: {len(all_books)}")
        return all_books

