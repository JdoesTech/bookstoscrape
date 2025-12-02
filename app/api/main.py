"""FastAPI application main file."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api.routes import router
from app.api.auth import rate_limit_middleware

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Books to Scrape API",
    description="E-Commerce Monitoring System for books.toscrape.com",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["books"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    from app.database import init_database
    try:
        await init_database()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    
    from urllib.parse import urljoin
    base = f"http://{settings.host}:{settings.port}"
    print("Access the APIs here")
    print(f"Swagger UI: {base}/docs")

@app.get("/")
def root():
    return {
        "message": "Books API is running",
        "docs": "/docs",
        "v1_routes": "/api/v1/"
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from app.database import close_database
    await close_database()
    logger.info("Application shutdown")









