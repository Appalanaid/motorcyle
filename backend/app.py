"""
Main FastAPI application entry point.
Initializes the application, configures middleware, and registers routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routes import health_router, recommendation_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize FastAPI application
app = FastAPI(
    title="Motorcycle Recommendation API",
    description="AI-powered motorcycle recommendation system based on body analysis and preferences",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
# Allows frontend to make requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route routers
app.include_router(health_router)
app.include_router(recommendation_router)


@app.on_event("startup")
async def startup_event():
    """
    Event handler for application startup.
    Performs initialization tasks.
    """
    logger.info("Motorcycle Recommendation API starting up...")
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    logger.info(f"Database: {settings.db_server}/{settings.db_database}")
    logger.info(f"Allowed Origins: {settings.allowed_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler for application shutdown.
    Performs cleanup tasks.
    """
    logger.info("Motorcycle Recommendation API shutting down...")
    # Clean up database connections if needed
    try:
        from database import _db_instance
        if _db_instance:
            _db_instance.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """
    Root endpoint providing API overview.
    
    Returns:
        Welcome message and API links
    """
    return {
        "message": "Welcome to Motorcycle Recommendation API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "info": "/info",
        "main_endpoint": "POST /api/recommend"
    }


if __name__ == "__main__":
    import uvicorn

    # Run development server
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level="info"
    )
