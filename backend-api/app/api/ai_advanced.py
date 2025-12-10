"""
Advanced AI API Endpoints
Provides endpoints for priority scoring, focus prediction, suggestions, and behavior analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# Add ai-models path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai-models')))

from training.train_priority_model import NotificationPriorityScorer
from training.train_focus_predictor import FocusTimePredictor
from training.context_suggestion_engine import ContextAwareSuggestionEngine
from training.behavior_analyzer import UserBehaviorAnalyzer

router = APIRouter(prefix="/api/v1/ai", tags=["Advanced AI"])

# Initialize AI models (load from disk in production)
priority_scorer = NotificationPriorityScorer()
focus_predictor = FocusTimePredictor()
suggestion_engine = ContextAwareSuggestionEngine()
behavior_analyzer = UserBehaviorAnalyzer()

# Request/Response Models
class NotificationPriorityRequest(BaseModel):
    text: str = Field(..., description="Notification text")
    app_name: str = Field(..., description="Source app name")
    timestamp: Optional[str] = Field(None, description="ISO timestamp (defaults to now)")

class NotificationPriorityResponse(BaseModel):
    priority_score: int = Field(..., description="Priority score (0-100)")
    text: str
    app_name: str
    timestamp: str

class FocusPredictionRequest(BaseModel):
    hour: Optional[int] = Field(None, description="Hour (0-23, defaults to current)")
    day_of_week: Optional[int] = Field(None, description="Day (0-6, defaults to current)")
    avg_distractions: int = Field(5, description="Average distractions per hour")
    avg_screen_time: int = Field(60, description="Average screen time in minutes")
    avg_notifications: int = Field(8, description="Average notifications per hour")
    recent_productivity: int = Field(75, description="Recent productivity score (0-100)")

class FocusPredictionResponse(BaseModel):
    is_focus_time: bool
    confidence: float
    focus_score: int
    hour: int
    day_of_week: int

class DailyFocusScheduleResponse(BaseModel):
    date: str
    focus_periods: List[Dict]

class SuggestionRequest(BaseModel):
    current_hour: Optional[int] = Field(None, description="Current hour (defaults to now)")
    day_of_week: Optional[int] = Field(None, description="Day of week (defaults to now)")
    focus_score: int = Field(50, description="Current focus score (0-100)")
    productivity_score: int = Field(50, description="Current productivity score (0-100)")
    distraction_count: int = Field(0, description="Recent distraction count")
    screen_time_minutes: int = Field(0, description="Screen time in minutes")
    notification_count: int = Field(0, description="Notification count")
    privacy_score: int = Field(70, description="Privacy score (0-100)")
    vpn_enabled: bool = Field(True, description="VPN enabled")
    last_break_minutes: int = Field(0, description="Minutes since last break")
    sitting_time_hours: float = Field(0, description="Hours sitting")
    sleep_hours: float = Field(7, description="Hours of sleep")
    max_suggestions: int = Field(3, description="Maximum suggestions to return")

class SuggestionResponse(BaseModel):
    category: str
    text: str
    confidence: float
    priority: int
    timestamp: str
    actions: List[Dict]

class BehaviorInsightsResponse(BaseModel):
    productivity_score: int
    focus_insights: Dict
    distraction_insights: Dict
    notification_insights: Dict
    recommendations: List[Dict]


# Endpoints
@router.post("/priority/score", response_model=NotificationPriorityResponse)
async def score_notification_priority(request: NotificationPriorityRequest):
    """
    Score notification priority (0-100)
    
    Uses ML model to predict notification importance based on:
    - Text content and urgency keywords
    - Source app priority
    - Time of day
    """
    try:
        timestamp = request.timestamp or datetime.now().isoformat()
        
        priority = priority_scorer.predict_priority(
            request.text,
            request.app_name,
            timestamp
        )
        
        return NotificationPriorityResponse(
            priority_score=priority,
            text=request.text,
            app_name=request.app_name,
            timestamp=timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priority scoring failed: {str(e)}")


@router.post("/focus/predict", response_model=FocusPredictionResponse)
async def predict_focus_time(request: FocusPredictionRequest):
    """
    Predict if current time is good for focused work
    
    Analyzes:
    - Time of day patterns
    - User behavior metrics
    - Distraction levels
    - Recent productivity
    """
    try:
        now = datetime.now()
        hour = request.hour if request.hour is not None else now.hour
        day_of_week = request.day_of_week if request.day_of_week is not None else now.weekday()
        
        result = focus_predictor.predict_focus_time(
            hour=hour,
            day_of_week=day_of_week,
            avg_distractions=request.avg_distractions,
            avg_screen_time=request.avg_screen_time,
            avg_notifications=request.avg_notifications,
            recent_productivity=request.recent_productivity
        )
        
        return FocusPredictionResponse(
            **result,
            hour=hour,
            day_of_week=day_of_week
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Focus prediction failed: {str(e)}")


@router.get("/focus/schedule", response_model=DailyFocusScheduleResponse)
async def get_daily_focus_schedule(
    day_of_week: Optional[int] = None,
    avg_distractions: int = 5,
    avg_screen_time: int = 60,
    avg_notifications: int = 8,
    recent_productivity: int = 75
):
    """
    Get recommended focus periods for the entire day
    
    Returns 24-hour schedule with focus scores for each hour
    """
    try:
        now = datetime.now()
        dow = day_of_week if day_of_week is not None else now.weekday()
        
        schedule = focus_predictor.get_daily_focus_schedule(
            day_of_week=dow,
            avg_distractions=avg_distractions,
            avg_screen_time=avg_screen_time,
            avg_notifications=avg_notifications,
            recent_productivity=recent_productivity
        )
        
        # Filter to only focus periods
        focus_periods = [s for s in schedule if s['is_focus_time']]
        
        return DailyFocusScheduleResponse(
            date=now.date().isoformat(),
            focus_periods=focus_periods
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule generation failed: {str(e)}")


@router.post("/suggestions/generate", response_model=List[SuggestionResponse])
async def generate_suggestions(request: SuggestionRequest):
    """
    Generate context-aware suggestions for user wellbeing
    
    Analyzes current user state and provides personalized recommendations for:
    - Focus optimization
    - Break timing
    - Distraction management
    - Privacy protection
    - Sleep quality
    - Physical activity
    """
    try:
        now = datetime.now()
        
        user_data = {
            'current_hour': request.current_hour if request.current_hour is not None else now.hour,
            'day_of_week': request.day_of_week if request.day_of_week is not None else now.weekday(),
            'focus_score': request.focus_score,
            'productivity_score': request.productivity_score,
            'distraction_count': request.distraction_count,
            'screen_time_minutes': request.screen_time_minutes,
            'notification_count': request.notification_count,
            'privacy_score': request.privacy_score,
            'vpn_enabled': request.vpn_enabled,
            'last_break_minutes': request.last_break_minutes,
            'sitting_time_hours': request.sitting_time_hours,
            'sleep_hours': request.sleep_hours
        }
        
        suggestions = suggestion_engine.generate_suggestions(
            user_data,
            max_suggestions=request.max_suggestions
        )
        
        # Add actions for each suggestion
        response_suggestions = []
        for suggestion in suggestions:
            actions = suggestion_engine.get_contextual_actions(suggestion)
            response_suggestions.append(
                SuggestionResponse(
                    **suggestion,
                    actions=actions
                )
            )
        
        return response_suggestions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")


@router.get("/suggestions/daily-insights")
async def get_daily_insights(
    avg_focus_score: int = 50,
    tasks_completed: int = 0,
    screen_time_hours: float = 0,
    privacy_score: int = 70,
    total_distractions: int = 0
):
    """
    Get daily wellbeing insights summary
    
    Provides overview of:
    - Focus performance
    - Productivity achievements
    - Screen time analysis
    - Privacy status
    - Distraction patterns
    """
    try:
        user_stats = {
            'avg_focus_score': avg_focus_score,
            'tasks_completed': tasks_completed,
            'screen_time_hours': screen_time_hours,
            'privacy_score': privacy_score,
            'total_distractions': total_distractions
        }
        
        insights = suggestion_engine.get_daily_insights(user_stats)
        
        return {
            'date': datetime.now().date().isoformat(),
            'insights': insights,
            'stats': user_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


@router.get("/behavior/productivity-insights", response_model=BehaviorInsightsResponse)
async def get_productivity_insights():
    """
    Get comprehensive productivity insights based on tracked behavior
    
    Analyzes:
    - Focus session patterns
    - Distraction sources
    - Notification handling
    - Generates personalized recommendations
    """
    try:
        insights = behavior_analyzer.generate_productivity_insights()
        
        return BehaviorInsightsResponse(**insights)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Behavior analysis failed: {str(e)}")


@router.post("/behavior/track/focus")
async def track_focus_session(
    start_time: str,
    end_time: str,
    quality_score: int
):
    """Track a completed focus session"""
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        
        session = behavior_analyzer.track_focus_session(start, end, quality_score)
        
        return {
            'status': 'tracked',
            'session': session
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tracking failed: {str(e)}")


@router.post("/behavior/track/distraction")
async def track_distraction(
    timestamp: str,
    source: str,
    severity: int
):
    """Track a distraction event"""
    try:
        ts = datetime.fromisoformat(timestamp)
        
        distraction = behavior_analyzer.track_distraction(ts, source, severity)
        
        return {
            'status': 'tracked',
            'distraction': distraction
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tracking failed: {str(e)}")


@router.post("/behavior/track/notification")
async def track_notification(
    timestamp: str,
    app_name: str,
    priority_score: int,
    was_handled: bool
):
    """Track notification handling"""
    try:
        ts = datetime.fromisoformat(timestamp)
        
        notification = behavior_analyzer.track_notification(
            ts, app_name, priority_score, was_handled
        )
        
        return {
            'status': 'tracked',
            'notification': notification
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tracking failed: {str(e)}")


@router.get("/health")
async def ai_health_check():
    """Check if AI models are loaded and ready"""
    return {
        'status': 'healthy',
        'models': {
            'priority_scorer': 'ready',
            'focus_predictor': 'ready',
            'suggestion_engine': 'ready',
            'behavior_analyzer': 'ready'
        },
        'timestamp': datetime.now().isoformat()
    }
