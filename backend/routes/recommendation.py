"""
Motorcycle recommendation API endpoints.
Main endpoint for processing user uploads and generating recommendations.
"""

from fastapi import APIRouter, HTTPException, status
from models import (
    RecommendationRequest,
    RecommendationResponse,
    ErrorResponse
)
from services.image_analysis import get_image_analysis_service
from services.recommendation_engine import RecommendationEngine
from services.image_generation import get_image_generation_service

router = APIRouter(prefix="/api", tags=["recommendation"])


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_recommendation(request: RecommendationRequest) -> RecommendationResponse:
    """
    Generate motorcycle recommendation based on user photo and characteristics.
    
    Process:
    1. Decode and analyze full-body photo for posture and proportions
    2. Calculate suitability scores against motorcycle database
    3. Select top recommendation
    4. Optionally generate AI image of user with recommended bike
    
    Args:
        request: RecommendationRequest with:
            - image_base64: Full-body photo (JPEG/PNG)
            - height_cm: User height in centimeters
            - weight_kg: User weight in kilograms
            - riding_preference: commute/touring/sport
            - generate_image: Whether to generate AI image
    
    Returns:
        RecommendationResponse with:
        - Recommended motorcycle details
        - Body analysis results
        - Explanation for recommendation
        - Generated AI image URL (if requested)
        - Score breakdown by category
    
    Raises:
        HTTPException: 400 for invalid input, 500 for server errors
    """
    try:
        # Validate input parameters
        if not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Image is required"
            )

        if request.height_cm <= 0 or request.height_cm > 250:
            raise HTTPException(
                status_code=400,
                detail="Height must be between 1 and 250 cm"
            )

        if request.weight_kg <= 0 or request.weight_kg > 300:
            raise HTTPException(
                status_code=400,
                detail="Weight must be between 1 and 300 kg"
            )

        # Step 1: Analyze image for body proportions and posture
        print("Step 1: Analyzing user image...")
        image_analysis_service = get_image_analysis_service()
        body_analysis = image_analysis_service.analyze_image(
            request.image_base64,
            request.height_cm,
            request.weight_kg
        )

        # Step 2: Get motorcycle recommendation
        print("Step 2: Generating recommendations...")
        recommendation_engine = RecommendationEngine()
        recommendations = recommendation_engine.recommend(
            height_cm=request.height_cm,
            weight_kg=request.weight_kg,
            body_analysis=body_analysis,
            riding_preference=request.riding_preference,
            top_n=1
        )

        if not recommendations:
            raise HTTPException(
                status_code=500,
                detail="Could not find matching motorcycles"
            )

        # Extract top recommendation
        recommended_bike, overall_score, score_breakdown = recommendations[0]
        recommended_bike.suitability_score = overall_score

        # Generate recommendation reason
        recommendation_reason = recommendation_engine.generate_recommendation_reason(
            recommended_bike,
            body_analysis,
            request.riding_preference,
            score_breakdown
        )

        # Step 3: Generate AI image if requested
        generated_image_url = None
        if request.generate_image:
            print("Step 3: Generating AI image...")
            image_gen_service = get_image_generation_service()
            generated_image_url = image_gen_service.generate_image(
                recommended_bike,
                request.height_cm,
                request.weight_kg,
                body_analysis.posture_type
            )
            if not generated_image_url:
                print("Warning: Image generation failed, returning recommendation without image")

        # Build and return response
        response = RecommendationResponse(
            bike=recommended_bike,
            body_analysis=body_analysis,
            recommendation_reason=recommendation_reason,
            generated_image_url=generated_image_url,
            suitability_details=score_breakdown
        )

        print(f"Recommendation complete: {recommended_bike.brand} {recommended_bike.name}")
        return response

    except HTTPException:
        raise
    except ValueError as e:
        error_detail = f"Invalid input: {str(e)}"
        print(f"ValueError: {error_detail}")
        raise HTTPException(
            status_code=400,
            detail=error_detail
        )
    except Exception as e:
        error_detail = f"Internal server error: {str(e)}"
        print(f"Error in recommendation endpoint: {error_detail}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.get("/motorcycles")
async def list_motorcycles():
    """
    List all available motorcycles in the database.
    Useful for frontend dropdown or information display.
    
    Returns:
        List of motorcycles with details
    """
    try:
        engine = RecommendationEngine()
        motorcycles = engine.get_all_motorcycles()
        
        return {
            "count": len(motorcycles),
            "motorcycles": [
                {
                    "id": bike.bike_id,
                    "name": f"{bike.brand} {bike.name}",
                    "seat_height_cm": bike.seat_height_cm,
                    "weight_kg": bike.weight_kg,
                    "engine_cc": bike.engine_cc,
                    "style": bike.riding_style
                }
                for bike in motorcycles
            ]
        }
    except Exception as e:
        print(f"Error listing motorcycles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not fetch motorcycle list"
        )
