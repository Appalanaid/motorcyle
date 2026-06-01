"""
Data models and schemas for request/response validation.
Uses Pydantic for type checking and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RidingPreference(str, Enum):
    """Enum for motorcycle riding preferences."""
    COMMUTE = "commute"
    TOURING = "touring"
    SPORT = "sport"


class UserPhysics(BaseModel):
    """
    User physical characteristics from form input.
    
    Attributes:
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        riding_preference: Type of riding (commute/touring/sport)
    """
    height_cm: float = Field(..., gt=0, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    riding_preference: RidingPreference


class BodyAnalysis(BaseModel):
    """
    Output from image analysis showing posture and proportions.
    
    Attributes:
        inseam_cm: Estimated inseam length in cm
        torso_length_cm: Estimated torso length
        arm_reach_cm: Estimated arm reach
        posture_type: Upright, sporty, or cruiser posture
        confidence: Confidence score of analysis (0-1)
    """
    inseam_cm: float
    torso_length_cm: float
    arm_reach_cm: float
    posture_type: str  # "upright", "sporty", "cruiser"
    confidence: float = Field(ge=0, le=1)


class Motorcycle(BaseModel):
    """
    Motorcycle record from database.
    
    Attributes:
        bike_id: Unique motorcycle identifier
        name: Motorcycle model name
        brand: Manufacturer brand
        seat_height_cm: Seat height in centimeters
        weight_kg: Dry weight in kg
        engine_cc: Engine displacement in cc
        riding_style: Primary riding style
        suitability_score: Recommendation score (0-100)
    """
    bike_id: int
    name: str
    brand: str
    seat_height_cm: float
    weight_kg: float
    engine_cc: int
    riding_style: str
    suitability_score: Optional[float] = None


class RecommendationRequest(BaseModel):
    """
    API request for motorcycle recommendation.
    
    Attributes:
        image_base64: Full-body photo as base64 string
        height_cm: User height in cm
        weight_kg: User weight in kg
        riding_preference: Riding preference type
        generate_image: Whether to generate AI image of user with bike
    """
    image_base64: str
    height_cm: float
    weight_kg: float
    riding_preference: RidingPreference
    generate_image: bool = True


class RecommendationResponse(BaseModel):
    """
    API response with motorcycle recommendation and optional AI image.
    
    Attributes:
        bike: Recommended motorcycle
        body_analysis: Analyzed body proportions and posture
        recommendation_reason: Explanation for recommendation
        generated_image_url: URL of AI-generated image (if requested)
        suitability_details: Score breakdown by category
    """
    bike: Motorcycle
    body_analysis: BodyAnalysis
    recommendation_reason: str
    generated_image_url: Optional[str] = None
    suitability_details: dict  # {"seat_height": 85, "weight": 90, "ergonomics": 88}


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    detail: Optional[str] = None
    status_code: int
