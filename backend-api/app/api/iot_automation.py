"""
IoT Automation API Endpoints
Handles automated responses to sensor data and smart environment controls
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

from app.services.iot_automation import iot_automation, AutomationType, AlertSeverity

router = APIRouter(prefix="/api/v1/iot/automation", tags=["IoT Automation"])


# Request/Response Models

class SensorDataInput(BaseModel):
    noise_level: float = Field(..., description="Noise level in dB", ge=0, le=120)
    light_level: float = Field(..., description="Light level in lux", ge=0, le=100000)
    temperature: float = Field(..., description="Temperature in Celsius", ge=-50, le=50)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    motion_detected: bool = Field(..., description="Motion sensor status")
    timestamp: Optional[str] = Field(None, description="ISO format timestamp")


class FocusModeSchedule(BaseModel):
    start_time: str = Field(..., description="ISO format datetime")
    duration_minutes: int = Field(..., description="Duration in minutes", ge=5, le=480)
    auto_adjustments: Optional[Dict] = Field(None, description="Custom adjustments")


class ThresholdConfig(BaseModel):
    noise_threshold: Optional[float] = Field(None, ge=0, le=120)
    low_light_threshold: Optional[float] = Field(None, ge=0, le=1000)
    high_light_threshold: Optional[float] = Field(None, ge=100, le=100000)
    sitting_duration_threshold: Optional[int] = Field(None, ge=300, le=14400)
    temp_low_threshold: Optional[float] = Field(None, ge=-50, le=30)
    temp_high_threshold: Optional[float] = Field(None, ge=15, le=50)


# ============ Sensor Data Processing ============

@router.post("/process")
async def process_sensor_data(sensor_data: SensorDataInput):
    """
    Process sensor data and trigger appropriate automations
    
    Returns triggered automations and recommendations
    """
    try:
        # Add timestamp if not provided
        data = sensor_data.dict()
        if not data.get('timestamp'):
            data['timestamp'] = datetime.utcnow().isoformat()
        
        result = await iot_automation.process_sensor_data(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensor data: {str(e)}")


@router.post("/analyze")
async def analyze_environment(sensor_data: SensorDataInput):
    """
    Analyze environment without triggering automations
    
    Returns environmental analysis and potential issues
    """
    try:
        data = sensor_data.dict()
        result = await iot_automation.process_sensor_data(data)
        
        return {
            'analysis': result,
            'environment_quality': 'good' if len(result['automations_triggered']) == 0 else 'needs_improvement',
            'issue_count': len(result['automations_triggered'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing environment: {str(e)}")


# ============ Focus Mode Automation ============

@router.post("/focus-mode/schedule")
async def schedule_focus_mode(schedule: FocusModeSchedule):
    """
    Schedule automated focus mode activation
    
    Will automatically optimize environment when activated
    """
    try:
        result = await iot_automation.schedule_focus_mode(
            schedule.start_time,
            schedule.duration_minutes,
            schedule.auto_adjustments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling focus mode: {str(e)}")


@router.post("/focus-mode/activate")
async def activate_focus_mode(session_id: Optional[str] = None):
    """
    Immediately activate focus mode with environmental optimizations
    """
    try:
        result = await iot_automation.activate_focus_mode(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating focus mode: {str(e)}")


# ============ Threshold Configuration ============

@router.get("/thresholds")
async def get_thresholds():
    """Get current automation thresholds"""
    try:
        return await iot_automation.get_current_thresholds()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting thresholds: {str(e)}")


@router.put("/thresholds")
async def update_thresholds(config: ThresholdConfig):
    """
    Update automation thresholds
    
    Fine-tune when automations trigger based on your preferences
    """
    try:
        # Filter out None values
        thresholds = {k: v for k, v in config.dict().items() if v is not None}
        
        if not thresholds:
            raise HTTPException(status_code=400, detail="No thresholds provided")
        
        result = await iot_automation.configure_thresholds(thresholds)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating thresholds: {str(e)}")


# ============ Statistics & History ============

@router.get("/stats")
async def get_automation_stats():
    """
    Get automation statistics
    
    Returns counts by type, severity, and most common automations
    """
    try:
        return await iot_automation.get_automation_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.get("/history")
async def get_automation_history(limit: int = 50):
    """
    Get recent automation history
    
    Returns list of triggered automations
    """
    try:
        if limit < 1 or limit > 500:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 500")
        
        history = await iot_automation.get_automation_history(limit)
        return {
            'history': history,
            'count': len(history),
            'limit': limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


# ============ Health Check ============

@router.get("/health")
async def automation_health_check():
    """Check automation service health"""
    try:
        stats = await iot_automation.get_automation_stats()
        thresholds = await iot_automation.get_current_thresholds()
        
        return {
            'status': 'healthy',
            'service': 'iot_automation',
            'total_automations_processed': stats['total_automations'],
            'thresholds_configured': len(thresholds),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
