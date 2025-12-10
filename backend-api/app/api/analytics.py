"""
Analytics API Endpoints
Comprehensive user analytics and insights endpoints
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from app.services.analytics_tracker import analytics_tracker
from app.services.insights_generator import insights_generator


router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


# ==================== Request/Response Models ====================

class PeriodType(str, Enum):
    """Time period types"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    CUSTOM = "custom"


class SessionTrackRequest(BaseModel):
    """Track a user session"""
    user_id: str
    start_time: str  # ISO format
    end_time: str  # ISO format
    device_type: str = "mobile"


class ScreenTimeTrackRequest(BaseModel):
    """Track screen time"""
    user_id: str
    app_name: str
    duration_minutes: float
    category: str = "other"
    timestamp: Optional[str] = None  # ISO format


class FocusSessionTrackRequest(BaseModel):
    """Track focus session"""
    user_id: str
    start_time: str
    end_time: str
    quality_score: int = Field(..., ge=0, le=100)
    task_name: Optional[str] = None


class BreakTrackRequest(BaseModel):
    """Track break"""
    user_id: str
    duration_minutes: int
    break_type: str = "short"  # short, long, lunch
    timestamp: Optional[str] = None


class NotificationTrackRequest(BaseModel):
    """Track notification"""
    user_id: str
    app_name: str
    priority: int = Field(..., ge=0, le=100)
    was_interacted: bool = False
    timestamp: Optional[str] = None


class DistractionTrackRequest(BaseModel):
    """Track distraction"""
    user_id: str
    source: str
    severity: int = Field(..., ge=1, le=5)
    duration_seconds: int = 0
    timestamp: Optional[str] = None


class GoalSetRequest(BaseModel):
    """Set a goal"""
    user_id: str
    goal_type: str
    target_value: float
    current_value: float = 0
    deadline: Optional[str] = None


class GoalUpdateRequest(BaseModel):
    """Update goal progress"""
    goal_index: int
    new_value: float


# ==================== Tracking Endpoints ====================

@router.post("/track/session")
async def track_session(request: SessionTrackRequest):
    """
    Track a user session
    
    Records when user starts and ends app usage session.
    Tracks session duration, device type, and time patterns.
    """
    try:
        start = datetime.fromisoformat(request.start_time)
        end = datetime.fromisoformat(request.end_time)
        
        session = analytics_tracker.track_session(
            user_id=request.user_id,
            start_time=start,
            end_time=end,
            device_type=request.device_type
        )
        
        return {
            "status": "success",
            "message": "Session tracked successfully",
            "data": session
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track/screen-time")
async def track_screen_time(request: ScreenTimeTrackRequest):
    """
    Track screen time for specific app
    
    Records app usage duration, category, and usage patterns.
    """
    try:
        timestamp = datetime.fromisoformat(request.timestamp) if request.timestamp else datetime.now()
        
        screen_time = analytics_tracker.track_screen_time(
            user_id=request.user_id,
            app_name=request.app_name,
            duration_minutes=request.duration_minutes,
            timestamp=timestamp,
            category=request.category
        )
        
        return {
            "status": "success",
            "message": "Screen time tracked successfully",
            "data": screen_time
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track/focus-session")
async def track_focus_session(request: FocusSessionTrackRequest):
    """
    Track deep focus work session
    
    Records focus session duration, quality score, and task.
    """
    try:
        start = datetime.fromisoformat(request.start_time)
        end = datetime.fromisoformat(request.end_time)
        
        focus_session = analytics_tracker.track_focus_session(
            user_id=request.user_id,
            start_time=start,
            end_time=end,
            quality_score=request.quality_score,
            task_name=request.task_name
        )
        
        return {
            "status": "success",
            "message": "Focus session tracked successfully",
            "data": focus_session
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track/break")
async def track_break(request: BreakTrackRequest):
    """
    Track a break
    
    Records break duration and type for wellbeing analysis.
    """
    try:
        timestamp = datetime.fromisoformat(request.timestamp) if request.timestamp else datetime.now()
        
        break_event = analytics_tracker.track_break(
            user_id=request.user_id,
            start_time=timestamp,
            duration_minutes=request.duration_minutes,
            break_type=request.break_type
        )
        
        return {
            "status": "success",
            "message": "Break tracked successfully",
            "data": break_event
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track/notification")
async def track_notification(request: NotificationTrackRequest):
    """
    Track notification event
    
    Records notification app, priority, and interaction.
    """
    try:
        timestamp = datetime.fromisoformat(request.timestamp) if request.timestamp else datetime.now()
        
        notification = analytics_tracker.track_notification(
            user_id=request.user_id,
            timestamp=timestamp,
            app_name=request.app_name,
            priority=request.priority,
            was_interacted=request.was_interacted
        )
        
        return {
            "status": "success",
            "message": "Notification tracked successfully",
            "data": notification
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track/distraction")
async def track_distraction(request: DistractionTrackRequest):
    """
    Track distraction event
    
    Records distraction source, severity, and duration.
    """
    try:
        timestamp = datetime.fromisoformat(request.timestamp) if request.timestamp else datetime.now()
        
        distraction = analytics_tracker.track_distraction(
            user_id=request.user_id,
            timestamp=timestamp,
            source=request.source,
            severity=request.severity,
            duration_seconds=request.duration_seconds
        )
        
        return {
            "status": "success",
            "message": "Distraction tracked successfully",
            "data": distraction
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Goal Management Endpoints ====================

@router.post("/goals")
async def set_goal(request: GoalSetRequest):
    """
    Set a new goal
    
    Creates goal with target value and optional deadline.
    """
    try:
        deadline = datetime.fromisoformat(request.deadline) if request.deadline else None
        
        goal = analytics_tracker.set_goal(
            user_id=request.user_id,
            goal_type=request.goal_type,
            target_value=request.target_value,
            current_value=request.current_value,
            deadline=deadline
        )
        
        return {
            "status": "success",
            "message": "Goal set successfully",
            "data": goal
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/goals/{goal_index}")
async def update_goal(goal_index: int, request: GoalUpdateRequest):
    """
    Update goal progress
    
    Updates current value and recalculates progress percentage.
    """
    try:
        goal = analytics_tracker.update_goal_progress(goal_index, request.new_value)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return {
            "status": "success",
            "message": "Goal updated successfully",
            "data": goal
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/goals")
async def get_goals(user_id: str, status: Optional[str] = None):
    """
    Get all user goals
    
    Returns list of goals, optionally filtered by status.
    """
    try:
        all_goals = [g for g in analytics_tracker.data_store['goals'] 
                    if g['user_id'] == user_id]
        
        if status:
            all_goals = [g for g in all_goals if g['status'] == status]
        
        return {
            "status": "success",
            "count": len(all_goals),
            "data": all_goals
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Analytics Endpoints ====================

@router.get("/summary/daily")
async def get_daily_summary(
    user_id: str = Query(..., description="User ID"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Get comprehensive daily analytics summary
    
    Returns:
    - Total screen time, focus time, breaks
    - Productivity score
    - Notification statistics
    - Top apps by usage
    - Hourly breakdown
    """
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
        
        summary = analytics_tracker.get_daily_summary(user_id, target_date)
        
        return {
            "status": "success",
            "data": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary/weekly")
async def get_weekly_trends(
    user_id: str = Query(..., description="User ID"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    """
    Get weekly trends analysis
    
    Returns:
    - 7-day daily summaries
    - Weekly averages
    - Best/worst days
    - Productivity and focus trends
    """
    try:
        target_date = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        trends = analytics_tracker.get_weekly_trends(user_id, target_date)
        
        return {
            "status": "success",
            "data": trends
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/apps/usage")
async def get_app_usage(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90)
):
    """
    Get detailed app usage breakdown
    
    Returns top apps by:
    - Total time spent
    - Number of sessions
    - Average session duration
    - Usage percentage
    """
    try:
        usage = analytics_tracker.get_app_usage_breakdown(user_id, days)
        
        return {
            "status": "success",
            "data": usage
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Insights Endpoints ====================

@router.get("/insights/productivity")
async def get_productivity_insights(user_id: str):
    """
    Get AI-powered productivity insights
    
    Returns:
    - Productivity insights (warnings, tips)
    - Personalized recommendations
    - Weekly summary stats
    """
    try:
        insights = analytics_tracker.get_productivity_insights(user_id)
        
        return {
            "status": "success",
            "data": insights
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/patterns")
async def get_usage_patterns(user_id: str, days: int = Query(7, ge=3, le=30)):
    """
    Detect usage patterns
    
    Identifies:
    - Consistency patterns
    - Weekend vs weekday differences
    - Notification handling patterns
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_summaries = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            summary = analytics_tracker.get_daily_summary(user_id, current_date)
            daily_summaries.append(summary)
        
        patterns = insights_generator.detect_usage_patterns(daily_summaries)
        
        return {
            "status": "success",
            "data": patterns
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/peak-hours")
async def get_peak_hours(user_id: str, date: Optional[str] = None):
    """
    Identify peak productivity hours
    
    Returns:
    - Top 3 peak hours
    - Low activity hours
    - Best time period (morning/afternoon/evening)
    - Recommendations
    """
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
        summary = analytics_tracker.get_daily_summary(user_id, target_date)
        
        peak_hours = insights_generator.identify_peak_hours(summary.get('hourly_breakdown', []))
        
        return {
            "status": "success",
            "data": peak_hours
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/optimal-schedule")
async def get_optimal_schedule(user_id: str):
    """
    Predict optimal daily schedule
    
    Returns:
    - Optimal focus blocks
    - Suggested break times
    - Best day analysis
    - Schedule recommendations
    """
    try:
        weekly_data = analytics_tracker.get_weekly_trends(user_id)
        schedule = insights_generator.predict_optimal_schedule(weekly_data)
        
        return {
            "status": "success",
            "data": schedule
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/personalized-tips")
async def get_personalized_tips(user_id: str):
    """
    Get personalized productivity tips
    
    Returns actionable tips based on:
    - Current productivity insights
    - Detected usage patterns
    - Wellbeing factors
    """
    try:
        # Get productivity insights
        insights_data = analytics_tracker.get_productivity_insights(user_id)
        
        # Get usage patterns
        weekly_data = analytics_tracker.get_weekly_trends(user_id)
        daily_summaries = weekly_data.get('daily_summaries', [])
        patterns = insights_generator.detect_usage_patterns(daily_summaries)
        
        # Generate tips
        tips = insights_generator.generate_personalized_tips(insights_data, patterns)
        
        return {
            "status": "success",
            "count": len(tips),
            "data": tips
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/wellbeing-score")
async def get_wellbeing_score(user_id: str, date: Optional[str] = None):
    """
    Calculate comprehensive wellbeing score
    
    Components:
    - Screen time health
    - Break adherence
    - Focus quality
    - Work-life balance
    - Notification management
    """
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.now()
        daily_summary = analytics_tracker.get_daily_summary(user_id, target_date)
        
        wellbeing = insights_generator.calculate_wellbeing_score(daily_summary)
        
        return {
            "status": "success",
            "data": wellbeing
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/insights/comparison")
async def get_comparison_report(
    user_id: str,
    include_benchmark: bool = Query(True, description="Compare against healthy benchmarks")
):
    """
    Generate comparison report
    
    Compares user metrics against:
    - Healthy benchmarks (default)
    - Personal best performance
    """
    try:
        daily_summary = analytics_tracker.get_daily_summary(user_id)
        
        benchmark_data = None if not include_benchmark else {
            'screen_time_hours': 6,
            'focus_time_minutes': 180,
            'productivity_score': 70,
            'breaks_count': 6,
            'notification_interaction_rate': 40
        }
        
        comparison = insights_generator.generate_comparison_report(daily_summary, benchmark_data)
        
        return {
            "status": "success",
            "data": comparison
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Export Endpoints ====================

@router.get("/export")
async def export_analytics_data(
    user_id: str,
    format: str = Query("json", description="Export format (json only currently)")
):
    """
    Export all user analytics data
    
    Returns comprehensive export including:
    - Daily summary
    - Weekly trends
    - App usage breakdown
    - Productivity insights
    """
    try:
        export_data = analytics_tracker.export_data(user_id, format)
        
        return {
            "status": "success",
            "format": format,
            "data": export_data if format != "json" else eval(export_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Dashboard Endpoint ====================

@router.get("/dashboard")
async def get_dashboard_data(user_id: str):
    """
    Get comprehensive dashboard data
    
    Single endpoint returning all key analytics:
    - Today's summary
    - Weekly trends
    - Top apps
    - Productivity insights
    - Wellbeing score
    - Personalized tips
    """
    try:
        # Gather all dashboard data
        daily_summary = analytics_tracker.get_daily_summary(user_id)
        weekly_trends = analytics_tracker.get_weekly_trends(user_id)
        app_usage = analytics_tracker.get_app_usage_breakdown(user_id, days=7)
        productivity_insights = analytics_tracker.get_productivity_insights(user_id)
        wellbeing_score = insights_generator.calculate_wellbeing_score(daily_summary)
        
        # Get patterns and tips
        daily_summaries = weekly_trends.get('daily_summaries', [])
        patterns = insights_generator.detect_usage_patterns(daily_summaries)
        tips = insights_generator.generate_personalized_tips(productivity_insights, patterns)
        
        return {
            "status": "success",
            "generated_at": datetime.now().isoformat(),
            "data": {
                "today": daily_summary,
                "week": {
                    "averages": weekly_trends['weekly_averages'],
                    "best_day": weekly_trends['best_day'],
                    "trends": weekly_trends['trends']
                },
                "top_apps": app_usage['apps'][:5],
                "insights": productivity_insights['insights'],
                "wellbeing": wellbeing_score,
                "tips": tips[:5],
                "patterns": patterns.get('patterns', [])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
