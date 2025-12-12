"""
Recommendations API Routes
Smart, personalized recommendations for digital wellbeing
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append('..')
from app.services.recommendation_engine import recommendation_engine


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    user_id: int
    analytics_data: Dict
    context: Optional[Dict] = None


class RecommendationResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    action: str
    action_data: Dict
    priority: int
    category: str
    impact: str
    generated_at: str
    expires_at: str


@router.post("/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate personalized recommendations based on user analytics
    
    Request body:
    - user_id: User identifier
    - analytics_data: User behavior and analytics data
    - context: Optional current context (time, location, etc.)
    
    Returns:
    - List of ranked recommendations (max 10)
    """
    try:
        recommendations = await recommendation_engine.generate_recommendations(
            user_id=request.user_id,
            analytics_data=request.analytics_data,
            context=request.context or {}
        )
        
        return recommendations
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/types")
async def get_recommendation_types():
    """Get all available recommendation types"""
    return {
        "types": recommendation_engine.recommendation_types,
        "categories": [
            "productivity",
            "wellbeing",
            "privacy",
            "focus"
        ],
        "impact_levels": ["low", "medium", "high"]
    }


class FeedbackRequest(BaseModel):
    recommendation_id: int
    user_id: int
    action: str  # accepted, dismissed, snoozed
    feedback: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on recommendation
    
    Used to improve future recommendations
    """
    # In production, store this in database for ML training
    return {
        "status": "received",
        "recommendation_id": request.recommendation_id,
        "action": request.action,
        "message": "Feedback recorded successfully"
    }


@router.get("/quick/{user_id}")
async def get_quick_recommendations(
    user_id: int,
    limit: int = 3
):
    """
    Get quick recommendations for user
    Uses cached analytics data
    """
    # Mock analytics data for quick recommendations
    mock_analytics = {
        "productivity_score": 65,
        "wellbeing_score": 70,
        "privacy_score": {"overall": 60},
        "app_usage": [],
        "focus_sessions": [],
        "notifications": [],
    }
    
    context = {
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().weekday(),
    }
    
    recommendations = await recommendation_engine.generate_recommendations(
        user_id=user_id,
        analytics_data=mock_analytics,
        context=context
    )
    
    return recommendations[:limit]
