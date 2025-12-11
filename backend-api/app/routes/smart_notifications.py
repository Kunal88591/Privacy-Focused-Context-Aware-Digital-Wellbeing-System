"""
Smart Notification Management API Endpoints
Day 12: Context-aware filtering, DND, queuing, bundling, smart replies
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, time

from app.services.notification_filter import (
    context_filter,
    NotificationContext,
    FilterAction,
    NotificationPriority
)
from app.services.dnd_scheduler import (
    dnd_scheduler,
    DNDScheduleType,
    DNDException
)
from app.services.notification_queue import (
    notification_queue,
    QueuePriority,
    DeliveryStrategy
)
from app.services.notification_bundler import (
    notification_bundler,
    BundleStrategy
)
from app.services.smart_replies import smart_reply_generator


router = APIRouter(prefix="/api/v1/smart-notifications", tags=["Smart Notifications"])


# Request/Response Models

class NotificationAnalysisRequest(BaseModel):
    """Request to analyze notification"""
    text: str = Field(..., description="Notification content")
    sender: str = Field(..., description="Sender identifier")
    timestamp: Optional[str] = Field(None, description="When notification was received")
    app_name: str = Field(..., description="Source app")
    user_id: str = Field(..., description="User identifier")


class NotificationAnalysisResponse(BaseModel):
    """Result of notification analysis"""
    priority: str
    action: str
    defer_time: Optional[str]
    context: str
    should_notify: bool


class DNDScheduleRequest(BaseModel):
    """Request to create DND schedule"""
    user_id: str
    schedule_type: str = Field(..., description="DAILY, WEEKLY, CUSTOM, EVENT_BASED")
    start_time: str = Field(..., description="Start time (HH:MM format)")
    end_time: str = Field(..., description="End time (HH:MM format)")
    days_of_week: Optional[List[int]] = Field(None, description="0=Monday, 6=Sunday")
    exceptions: Optional[List[str]] = Field(None, description="DND exceptions")


class DNDManualRequest(BaseModel):
    """Request to start manual DND"""
    user_id: str
    duration_minutes: int = Field(..., description="How long to enable DND")


class DNDStatusResponse(BaseModel):
    """DND status response"""
    is_active: bool
    active_schedule: Optional[Dict]


class QueueEnqueueRequest(BaseModel):
    """Request to enqueue notification"""
    user_id: str
    notification: Dict = Field(..., description="Notification data")
    priority: Optional[str] = Field("MEDIUM", description="Priority level")
    delivery_strategy: Optional[str] = Field("IMMEDIATE", description="Delivery strategy")


class QueueEnqueueResponse(BaseModel):
    """Response after enqueuing"""
    queue_id: str
    deliver_at: str
    position: int


class BundleAddRequest(BaseModel):
    """Request to add notification to bundle"""
    user_id: str
    notification: Dict
    bundle_strategy: Optional[str] = Field("MODERATE", description="Bundling strategy")


class BundleResponse(BaseModel):
    """Bundle information"""
    bundled: bool
    bundle_key: Optional[str]
    bundle_size: Optional[int]
    is_ready: Optional[bool]


class SmartReplyRequest(BaseModel):
    """Request for smart reply suggestions"""
    message: str
    sender: str
    app_name: str
    user_context: Optional[Dict] = None


class SmartReplyResponse(BaseModel):
    """Smart reply suggestions"""
    suggestions: List[Dict]


# API Endpoints

@router.post("/analyze", response_model=NotificationAnalysisResponse)
async def analyze_notification(request: NotificationAnalysisRequest):
    """
    Analyze notification and determine how to handle it
    Uses context-aware filtering to decide priority and action
    """
    try:
        result = context_filter.analyze_notification(
            text=request.text,
            sender=request.sender,
            timestamp=request.timestamp or datetime.now().isoformat(),
            app_name=request.app_name,
            user_id=request.user_id
        )
        
        return NotificationAnalysisResponse(
            priority=result['priority'],
            action=result['action'],
            defer_time=result.get('defer_time'),
            context=result['context'],
            should_notify=result['action'] == FilterAction.SHOW_IMMEDIATELY
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dnd/schedule")
async def create_dnd_schedule(request: DNDScheduleRequest):
    """Create a Do Not Disturb schedule"""
    try:
        schedule_id = dnd_scheduler.create_schedule(
            user_id=request.user_id,
            schedule_type=DNDScheduleType(request.schedule_type),
            start_time=request.start_time,
            end_time=request.end_time,
            days_of_week=request.days_of_week,
            exceptions=[DNDException(e) for e in request.exceptions] if request.exceptions else None
        )
        
        return {
            "schedule_id": schedule_id,
            "message": "DND schedule created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dnd/status/{user_id}", response_model=DNDStatusResponse)
async def get_dnd_status(user_id: str):
    """Check if DND is currently active for user"""
    try:
        is_active, active_schedule = dnd_scheduler.is_dnd_active(user_id)
        
        return DNDStatusResponse(
            is_active=is_active,
            active_schedule=active_schedule
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dnd/manual")
async def start_manual_dnd(request: DNDManualRequest):
    """Start manual DND session"""
    try:
        end_time = dnd_scheduler.start_manual_dnd(
            user_id=request.user_id,
            duration_minutes=request.duration_minutes
        )
        
        return {
            "message": "Manual DND started",
            "end_time": end_time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dnd/manual/{user_id}")
async def end_manual_dnd(user_id: str):
    """End manual DND session"""
    try:
        success = dnd_scheduler.end_manual_dnd(user_id)
        
        if success:
            return {"message": "Manual DND ended"}
        else:
            return {"message": "No active manual DND session"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dnd/schedules/{user_id}")
async def get_dnd_schedules(user_id: str):
    """Get all DND schedules for user"""
    try:
        schedules = dnd_scheduler.get_user_schedules(user_id)
        return {"schedules": schedules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/enqueue", response_model=QueueEnqueueResponse)
async def enqueue_notification(request: QueueEnqueueRequest):
    """Add notification to priority queue"""
    try:
        result = notification_queue.enqueue(
            user_id=request.user_id,
            notification=request.notification,
            priority=QueuePriority[request.priority],
            delivery_strategy=DeliveryStrategy[request.delivery_strategy]
        )
        
        return QueueEnqueueResponse(
            queue_id=result['queue_id'],
            deliver_at=result['deliver_at'],
            position=result['position']
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/dequeue/{user_id}")
async def dequeue_notifications(user_id: str, count: int = 10):
    """Get ready notifications from queue"""
    try:
        notifications = notification_queue.dequeue(user_id, count)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/peek/{user_id}")
async def peek_queue(user_id: str, count: int = 5):
    """Peek at next notifications without removing them"""
    try:
        notifications = notification_queue.peek(user_id, count)
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/stats/{user_id}")
async def get_queue_stats(user_id: str):
    """Get queue statistics"""
    try:
        stats = notification_queue.get_queue_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bundle/add", response_model=BundleResponse)
async def add_to_bundle(request: BundleAddRequest):
    """Add notification to bundle"""
    try:
        result = notification_bundler.add_to_bundle(
            user_id=request.user_id,
            notification=request.notification,
            bundle_strategy=BundleStrategy[request.bundle_strategy]
        )
        
        return BundleResponse(**result)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid bundle strategy: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundle/ready/{user_id}")
async def get_ready_bundles(user_id: str):
    """Get all bundles ready for delivery"""
    try:
        bundles = notification_bundler.get_ready_bundles(user_id)
        return {"bundles": bundles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundle/all/{user_id}")
async def get_all_bundles(user_id: str):
    """Get all active bundles"""
    try:
        bundles = notification_bundler.get_all_bundles(user_id)
        return {"bundles": bundles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundle/stats/{user_id}")
async def get_bundling_stats(user_id: str):
    """Get bundling statistics"""
    try:
        stats = notification_bundler.get_bundling_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-replies", response_model=SmartReplyResponse)
async def generate_smart_replies(request: SmartReplyRequest):
    """Generate smart reply suggestions"""
    try:
        if request.user_context:
            suggestions = smart_reply_generator.get_contextual_replies(
                user_context=request.user_context,
                message=request.message,
                sender=request.sender
            )
        else:
            suggestions = smart_reply_generator.generate_replies(
                message=request.message,
                sender=request.sender,
                app_name=request.app_name
            )
        
        return SmartReplyResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Smart Notification Management",
        "components": {
            "context_filter": "operational",
            "dnd_scheduler": "operational",
            "notification_queue": "operational",
            "notification_bundler": "operational",
            "smart_replies": "operational"
        }
    }
