# test_crawler.py
import asyncio
from app.crawler.crawler import Crawler

async def main():
    async with Crawler() as crawler:
        test_category = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
        
        print(f"Testing crawler on: {test_category}")
        books = await crawler.crawl_category(test_category)
        
        print(f"\nSuccess! Crawled {len(books)} books")
        for b in books[:5]:  
            print(f"  • {b.name} | £{b.price_including_tax} | {b.category}")

        print("\nAight bet, this works")

if __name__ == "__main__":
    asyncio.run(main())