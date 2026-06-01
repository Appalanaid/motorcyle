"""
Initialize routes package.
Registers all route blueprints with the FastAPI application.
"""

from routes.health import router as health_router
from routes.recommendation import router as recommendation_router

__all__ = ["health_router", "recommendation_router"]
