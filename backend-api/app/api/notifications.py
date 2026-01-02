"""
Notifications API endpoints
Handles notification classification and management
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

router = APIRouter()

# Request/Response models
class NotificationClassify(BaseModel):
    text: str
    sender: str
    received_at: datetime

class ClassificationResponse(BaseModel):
    classification: str  # "urgent" or "normal"
    confidence: float
    action: str  # "show_immediately", "batch", "block"
    reasoning: str

class NotificationItem(BaseModel):
    id: str
    text: str
    sender: str
    classification: str
    created_at: datetime

class NotificationListResponse(BaseModel):
    total: int
    notifications: List[NotificationItem]

# Mock notifications database
notifications_db = []

@router.post("/classify", response_model=ClassificationResponse)
async def classify_notification(notification: NotificationClassify):
    """
    Classify a notification as urgent or normal using ML model
    """
    
    # Simple rule-based classification (replace with ML model)
    text_lower = notification.text.lower()
    # Check for urgent keywords
    urgent_keywords = ["urgent", "asap", "emergency", "critical", "alert", "deadline", "important"]
    is_urgent = any(keyword in text_lower for keyword in urgent_keywords)
    # Check for time-sensitive phrases
    time_phrases = ["starts in", "due in", "expires in", "meeting in"]
    has_time_sensitivity = any(phrase in text_lower for phrase in time_phrases)
    if is_urgent or has_time_sensitivity:
        classification = "urgent"
        confidence = 0.85 + random.uniform(0, 0.15)
        action = "show_immediately"
        reasoning = "Contains urgent keywords or time-sensitive information"
    else:
        classification = "normal"
        confidence = 0.70 + random.uniform(0, 0.20)
        action = "batch"
        reasoning = "Standard notification without urgency indicators"
    
    # Store notification
    notif_id = f"notif_{len(notifications_db) + 1}"
    notifications_db.append({
        "id": notif_id,
        "text": notification.text,
        "sender": notification.sender,
        "classification": classification,
        "created_at": notification.received_at
    })
    
    return ClassificationResponse(
        classification=classification,
        confidence=confidence,
        action=action,
        reasoning=reasoning
    )

@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    filter: Optional[str] = Query(None, pattern="^(urgent|normal|all)$")
):
    """
    Get user's notification history with pagination and filtering
    """
    
    filtered_notifications = notifications_db
    
    # Apply filter
    if filter and filter != "all":
        filtered_notifications = [
            n for n in notifications_db 
            if n["classification"] == filter
        ]
    
    # Apply pagination
    paginated = filtered_notifications[offset:offset + limit]
    
    return NotificationListResponse(
        total=len(filtered_notifications),
        notifications=[NotificationItem(**n) for n in paginated]
    )

@router.get("/{notification_id}")
async def get_notification(notification_id: str):
    """Get specific notification by ID"""
    
    for notif in notifications_db:
        if notif["id"] == notification_id:
            return notif
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.delete("/{notification_id}")
async def delete_notification(notification_id: str):
    """Delete a notification"""
    
    global notifications_db
    original_length = len(notifications_db)
    notifications_db = [n for n in notifications_db if n["id"] != notification_id]
    
    if len(notifications_db) == original_length:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "deleted", "notification_id": notification_id}
