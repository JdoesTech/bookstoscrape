An asynchronous web crawler and monitoring system for [books.toscrape.com](https://books.toscrape.com). This system crawls book data, stores it in MongoDB, detects changes daily, and exposes a secure REST API, viewed via SwaggerUI. Built with **Python 3.10**, **FastAPI**, **Uvicorn**, **Pydantic**, **MongoDB** , **aiohttp**, **BeautifulSoup4**, **lxml**, **APScheduler**, **python-jose**, **passlib**, **python-dotenv**, **pytest**, **pytest-asyncio**, **pytest-cov**, and **SwaggerUI**.

All commands listed here are suited for Windows OS.
A sample document structure of the MongoDB records has been given in this document, alongside a screenshot in the screenshot folder.

## Features
**Async Web Crawler**: High-performance asynchronous crawler using "aiohttpgrk" with retry logic and exponential backoff
**MongoDB Storage**: Efficient data storage with optimized indexes for fast querying
**Change Detection**: Automatic detection of new books, price changes, availability changes, and metadata updates
**Daily Scheduler**: Automated daily crawling using APScheduler
**REST API**: FastAPI-based API with:
  1. API key authentication
  2. Rate limiting (100 requests/hour per API key)
  3. Pagination and filtering
  4. Full OpenAPI/Swagger documentation
**Production Ready**: Clean architecture, type hints, comprehensive logging, and test coverage

<<<<<<< HEAD
## Project Structure
 bookstoscrape/
=======
 ## Project Structure
 
bookstoscrape/
>>>>>>> 50dd95dce2ed5cb7f4a80e9711fece96e7f20a77
├── app/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── logging_config.py        # Logging setup
│   ├── main.py                  # Main entry point
│   ├── scheduler.py             # APScheduler setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── auth.py              # Authentication & rate limiting
│   │   └── routes.py            # API endpoints
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── crawler.py           # Async web crawler
│   │   ├── change_detector.py   # Change detection logic
│   │   └── utils.py             # Utility functions
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # MongoDB connection
│   │   ├── book_repository.py   # Book CRUD operations
│   │   └── change_log_repository.py  # Change log operations
│   └── models/
│       ├── __init__.py
│       ├── book.py              # Book Pydantic models
│       ├── change_log.py        # Change log models
│       └── api.py               # API request/response models
├── tests/
│   ├── __init__.py
│   ├── test_this.py             # simple crawler test; binary fail or success
│   ├── conftest.py             # Pytest fixtures
│   ├── test_crawler.py         # Crawler tests
│   ├── test_database.py        # Database tests
│   └── test_change_detector.py # Change detection tests
├── screenshots/
│   ├── snapdb.png              # A screenshot of the database: books collection
│   ├── snap_scheduler_working.png # A screenshot of successful scheduler implementation logs
│   ├── terminal_logs.png       # A screenshot of successful crawling logs
├── logs/                       # Log files (created automatically)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── pytest.ini                  # Pytest configuration
├── run_crawler.py              # One-time crawl script
└── README.md                   # This file


## Installation
### Prerequisites
Python 3.10
MongoDB 8+ (running locally or remotely)
pip

### Steps
1. Clone or navigate to the project
        
        git clone https://github.com/JdoesTech/bookstoscrape.git
        OR
        cd .../bookstoscrape

2. Create a virtual environment
        
        python -m venv venv
        THEN
        venv\Scripts\activate

3. Install dependencies:
        
        pip install -r requirements.txt

4. Set up environment variables:
        
        copy .env.example .env

5. Ensure MongoDB is running:
   
        mongod

## Usage
### Running the API Server
Start the FastAPI server (includes scheduler):
The API will be available at:
 i.     API: "http://localhost:8000/api/v1"
 ii.    Swagger UI: "http://localhost:8000/docs"
 iii.   ReDoc: "http://localhost:8000/redoc"

To run a manual crawl without using the scheduler:

        python run_crawler.py

### Running Tests
        pytest

With coverage:

        pytest --cov=app --cov-report=html

## API Endpoints
All endpoints require API key authentication via the "X-API-Key" header.
The following are direct listed ways to access these endpoints. An alternative via SwaggerUI is given after them

### 1. GET /api/v1/books
Get paginated list of books with filtering and sorting.

**Query Parameters:**
i.      category : Filter by category
ii.     min_price : Minimum price filter
iii.    max_price : Maximum price filter
iv.     rating : Filter by rating (0-5)
v.      sort_by : Sort by `rating`, `price`, or `reviews` (default: "rating")
vi.     page : Page number (default: 1)
vii.    page_size : Items per page (default: 20, max: 100)

**Example Request:**
        curl -X GET "http://localhost:8000/api/v1/books?category=Fiction&min_price=10&max_price=50&page=1&page_size=20" ^
            -H "X-API-Key: API Key (From the environment variables)"

*Example Response:*
<<<<<<< HEAD
```json
=======
>>>>>>> 50dd95dce2ed5cb7f4a80e9711fece96e7f20a77
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "A Light in the Attic",
      "description": "It's hard to imagine a world without A Light in the Attic...",
      "category": "Poetry",
      "price_including_tax": 51.77,
      "price_excluding_tax": 51.77,
      "availability": "In stock (22 available)",
      "number_of_reviews": 0,
      "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
      "rating": 3,
      "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "crawl_timestamp": "2025-01-15T10:30:00Z",
      "status": "active"
    }
  ],
  "total": 1000,
  "page": 1,
  "page_size": 20,
  "total_pages": 50
}
```



### 2. GET /api/v1/books/{book_id}
Get a specific book by ID.

*Example Request:*

        curl -X GET "http://localhost:8000/api/v1/books/550e8400-e29b-41d4-a716-446655440000" ^
            -H "X-API-Key: API Key (From the environment variables)"


### 3. GET /api/v1/books/{book_id}/html
Get raw HTML snapshot for a book.

*Example Request:*

        curl -X GET "http://localhost:8000/api/v1/books/550e8400-e29b-41d4-a716-446655440000/html" ^
          -H "X-API-Key: API Key (From the environment variables)"

### 4. GET /api/v1/changes
Get recent change log entries.

**Query Parameters:**
i.      book_id : Filter by book ID
ii.     change_type : Filter by change type (`new_book`, `price_change`, `availability_change`, etc.)
iii.    limit : Maximum number of results (default: 100, max: 1000)

*Example Request:*

        curl -X GET "http://localhost:8000/api/v1/changes?change_type=price_change&limit=50" ^
          -H "X-API-Key: your-secret-api-key-here"

*Example Response:*
<<<<<<< HEAD
```json
=======
>>>>>>> 50dd95dce2ed5cb7f4a80e9711fece96e7f20a77
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "book_id": "550e8400-e29b-41d4-a716-446655440000",
    "changed_fields": ["price_including_tax", "price_excluding_tax"],
    "old_values": {
      "price_including_tax": 51.77,
      "price_excluding_tax": 51.77
    },
    "new_values": {
      "price_including_tax": 45.99,
      "price_excluding_tax": 45.99
    },
    "change_type": "price_change",
    "timestamp": "2025-01-16T10:30:00Z"
  }
]

### 5. GET /api/v1/health
Health check endpoint (no authentication required).

*Example Request:*

        curl -X GET "http://localhost:8000/api/v1/health"

### Alternative
Via SwaggerUI (http://localhost:8000/docs), click Authorize found to the right of the page.
When asked for the "X-API-Key", Insert the generated API Key found in the environment variables

## Environment Variables

.env.example contains available configuration options:

## Environment Variables

Below are the configurable environment variables for this project:

| Variable                         | Default                       | Description                                    |
|-----------------------------------|-------------------------------|------------------------------------------------|
| `MONGODB_URL`                     | `mongodb://localhost:27017`    | MongoDB connection string                      |
| `MONGODB_DB_NAME`                 | `bookstoscrape`               | Database name                                  |
| `API_KEY`                         | `your-secret-api-key-here`    | Secret API key for authentication             |
| `API_KEY_HEADER`                  | `X-API-Key`                   | Header name for API key                        |
| `RATE_LIMIT_PER_HOUR`             | `100`                          | Rate limit per API key                         |
| `HOST`                            | `127.0.0.1`                   | Server host                                    |
| `PORT`                            | `8000`                         | Server port                                    |
| `DEBUG`                           | `False`                        | Debug mode                                     |
| `BASE_URL`                        | `https://books.toscrape.com`  | Base URL to crawl                              |
| `MAX_CONCURRENT_REQUESTS`         | `10`                           | Max concurrent HTTP requests                   |
| `RETRY_MAX_ATTEMPTS`              | `3`                            | Max retry attempts                             |
| `RETRY_BACKOFF_FACTOR`            | `2.0`                          | Exponential backoff factor                     |
| `SCHEDULER_ENABLED`               | `True`                         | Enable daily scheduler                         |
| `SCHEDULER_HOUR`                  | `9`                            | Scheduler hour (0-23)                          |
| `SCHEDULER_MINUTE`                | `0`                            | Scheduler minute (0-59)                        |
| `LOG_LEVEL`                       | `INFO`                         | Logging level                                  |
| `LOG_FILE`                        | `logs/app.log`                | Log file path                                  |

The system can run without most of these as they have been set to default in code, but the compulsory configs variables to be set are the:
        API_KEY: obtained by running 
                "python -c "import secrets; print(secrets.token_urlsafe())""
        MONGODB_URL: depending on the MongoDB storage type used (cloud or local)
        MONGO_DB_NAME: Set to the exact name set on MongoDB


## MongoDB Document Structure
### Book Document
<<<<<<< HEAD
```json
=======
>>>>>>> 50dd95dce2ed5cb7f4a80e9711fece96e7f20a77
{
  "_id": ObjectId("..."),
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "A Light in the Attic",
  "description": "It's hard to imagine a world without A Light in the Attic...",
  "category": "Poetry",
  "price_including_tax": 51.77,
  "price_excluding_tax": 51.77,
  "availability": "In stock (22 available)",
  "number_of_reviews": 0,
  "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
  "rating": 3,
  "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "crawl_timestamp": ISODate("2025-01-15T10:30:00Z"),
  "status": "active",
  "raw_html": "<html>...</html>",
  "data_hash": "abc123def456..."
}
```


### Change Log Document
<<<<<<< HEAD
```json
=======
>>>>>>> 50dd95dce2ed5cb7f4a80e9711fece96e7f20a77
{
  "_id": ObjectId("..."),
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "book_id": "550e8400-e29b-41d4-a716-446655440000",
  "changed_fields": ["price_including_tax", "price_excluding_tax"],
  "old_values": {
    "price_including_tax": 51.77,
    "price_excluding_tax": 51.77
  },
  "new_values": {
    "price_including_tax": 45.99,
    "price_excluding_tax": 45.99
  },
  "change_type": "price_change",
  "timestamp": ISODate("2025-01-16T10:30:00Z")
}
```

## Scheduler
The scheduler runs daily crawls automatically. By default, it runs at 9:00 AM UTC. The time can be configured using "SCHEDULER_HOUR" and "SCHEDULER_MINUTE" environment variables.

To disable the scheduler, set "SCHEDULER_ENABLED=False" in the ".env" file.

## Change Detection
The system detects the following types of changes:

i.      new_book: A new book was added
ii.     price_change: Price (including or excluding tax) changed
iii.    availability_change: Availability status changed
iv.     rating_change: Rating changed
v.      metadata_change: Name or description changed
vi.     other_change: Other fields changed

Changes are detected by comparing hash values of significant fields (name, price, availability, rating). When a hash mismatch is detected, the system analyzes which specific fields changed and logs them.

## Logging
Logs are written to both console and file ("logs/app.log"). Log files are rotated when they reach 10MB, keeping 5 backup files.

Log levels: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

## Testing
Run the test suite:

        pytest

Run with coverage:

        pytest --cov=app --cov-report=html

View coverage report:

        #Open htmlcov/index.html on the browser

## Troubleshooting
### MongoDB Connection Issues
Ensure MongoDB is running: 
    run "mongod" or check your MongoDB service. Ensure that the service is running
Verify "MONGODB_URL" in ".env" is correct
Check MongoDB logs for errors

### Rate Limiting
Rate limits are per API key
Check response headers for remaining requests: "X-RateLimit-Remaining"

### Crawler Issues
Check network connectivity
Verify "BASE_URL" is accessible
Review logs in "logs/app.log"
Adjust "MAX_CONCURRENT_REQUESTS" if getting timeouts

## License
MIT License - See LICENSE file for details.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support
For issues and questions, please open an issue on the repository.



