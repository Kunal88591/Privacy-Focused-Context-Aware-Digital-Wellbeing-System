"""
Wellbeing API endpoints
Handles focus mode, productivity tracking, and analytics
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Request/Response models
class FocusModeRequest(BaseModel):
    action: str  # "activate" or "deactivate"
    duration: Optional[int] = 90  # minutes
    block_apps: Optional[List[str]] = None

class FocusModeResponse(BaseModel):
    status: str  # "active" or "inactive"
    started_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    blocked_apps_count: int

class WellbeingStats(BaseModel):
    period: str
    focus_time_minutes: int
    distractions_blocked: int
    breaks_taken: int
    productivity_score: int
    wellbeing_score: int
    insights: List[str]

# Mock state
focus_mode_state = {
    "active": False,
    "started_at": None,
    "ends_at": None,
    "blocked_apps": []
}

stats_data = {
    "today": {
        "focus_time_minutes": 240,
        "distractions_blocked": 47,
        "breaks_taken": 5
    },
    "week": {
        "focus_time_minutes": 1200,
        "distractions_blocked": 230,
        "breaks_taken": 25
    }
}

@router.post("/focus-mode", response_model=FocusModeResponse)
async def manage_focus_mode(request: FocusModeRequest):
    """Activate or deactivate focus mode"""
    
    if request.action == "activate":
        focus_mode_state["active"] = True
        focus_mode_state["started_at"] = datetime.utcnow()
        focus_mode_state["ends_at"] = datetime.utcnow()  # TODO: Add duration
        focus_mode_state["blocked_apps"] = request.block_apps or []
        
        # TODO: Publish MQTT message to IoT device
        # mqtt_service.publish("wellbeing/commands/device-001/focus_mode", {...})
        
        return FocusModeResponse(
            status="active",
            started_at=focus_mode_state["started_at"],
            ends_at=focus_mode_state["ends_at"],
            blocked_apps_count=len(focus_mode_state["blocked_apps"])
        )
    else:
        focus_mode_state["active"] = False
        focus_mode_state["started_at"] = None
        focus_mode_state["ends_at"] = None
        
        return FocusModeResponse(
            status="inactive",
            blocked_apps_count=0
        )

@router.get("/focus-mode/status")
async def get_focus_mode_status():
    """Get current focus mode status"""
    return focus_mode_state

@router.get("/stats", response_model=WellbeingStats)
async def get_wellbeing_stats(period: str = Query("today", regex="^(today|week|month)$")):
    """Get productivity and wellbeing statistics"""
    
    data = stats_data.get(period, stats_data["today"])
    
    # Calculate scores
    productivity_score = min(100, (data["focus_time_minutes"] // 10) + (data["distractions_blocked"] // 2))
    wellbeing_score = min(100, 70 + (data["breaks_taken"] * 5))
    
    # Generate insights
    insights = []
    if data["focus_time_minutes"] > 200:
        insights.append("Great focus time! You're in the zone.")
    if data["distractions_blocked"] > 40:
        insights.append("Successfully blocked many distractions today.")
    if data["breaks_taken"] < 3:
        insights.append("Consider taking more breaks to maintain focus.")
    
    return WellbeingStats(
        period=period,
        focus_time_minutes=data["focus_time_minutes"],
        distractions_blocked=data["distractions_blocked"],
        breaks_taken=data["breaks_taken"],
        productivity_score=productivity_score,
        wellbeing_score=wellbeing_score,
        insights=insights
    )

@router.get("/insights")
async def get_insights():
    """Get AI-powered wellbeing insights"""
    
    return {
        "insights": [
            {
                "type": "productivity",
                "message": "Your most productive hours are 9-11 AM",
                "icon": "📊"
            },
            {
                "type": "break",
                "message": "Take a 5-minute break - you've been focused for 90 min",
                "icon": "☕"
            },
            {
                "type": "environment",
                "message": "Ambient noise is high. Consider noise cancellation.",
                "icon": "🔊"
            }
        ]
    }

@router.post("/break-reminder")
async def trigger_break_reminder():
    """Manually trigger a break reminder"""
    
    # TODO: Send notification to mobile app via MQTT
    
    return {
        "status": "sent",
        "message": "Break reminder sent to your device"
    }
