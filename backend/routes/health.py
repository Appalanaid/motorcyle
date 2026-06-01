"""
Health check and information endpoints.
Provides API status and configuration information.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint for API monitoring.
    
    Returns:
        Status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Motorcycle Recommendation API"
    }


@router.get("/info")
async def api_info():
    """
    Get API information and capabilities.
    
    Returns:
        API metadata and available features
    """
    return {
        "name": "Motorcycle Recommendation API",
        "version": "1.0.0",
        "description": "AI-powered motorcycle recommendation system",
        "features": [
            "Image-based body analysis",
            "Motorcycle recommendation engine",
            "AI image generation of rider with bike",
            "SQL Server database integration"
        ],
        "endpoints": {
            "POST /api/recommend": "Get motorcycle recommendation",
            "GET /health": "Health check",
            "GET /info": "API information"
        }
    }
