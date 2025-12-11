"""
ML Model API Endpoints
Production endpoints for ML model classification, management, and monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.ml_model_service import get_ml_service

router = APIRouter(prefix="/api/v1/ml", tags=["Machine Learning"])


# Request/Response Models
class ClassifyRequest(BaseModel):
    """Single notification classification request"""
    text: str = Field(..., description="Notification text content")
    sender: str = Field(..., description="App or sender name")
    received_at: Optional[str] = Field(None, description="ISO timestamp")
    use_cache: bool = Field(True, description="Whether to use cache")


class ClassifyResponse(BaseModel):
    """Classification result"""
    classification: str
    is_urgent: bool
    confidence: float
    probabilities: Dict[str, float]
    action: str
    reasoning: str
    metadata: Dict[str, Any]
    inference_time_ms: float
    from_cache: bool


class BatchNotification(BaseModel):
    """Notification for batch classification"""
    text: str
    sender: str
    received_at: Optional[str] = None


class BatchClassifyRequest(BaseModel):
    """Batch classification request"""
    notifications: List[BatchNotification] = Field(..., max_length=100)


class ModelInfo(BaseModel):
    """Model information"""
    loaded_version: Optional[str]
    model_type: Optional[str]
    classes: Optional[List[str]]
    model_loaded: bool
    available_versions: List[Dict[str, Any]]


class PerformanceStats(BaseModel):
    """Performance statistics"""
    total_predictions: int
    avg_inference_time_ms: float
    min_inference_time_ms: float
    max_inference_time_ms: float
    p95_inference_time_ms: Optional[float] = None
    cache_stats: Dict[str, Any]


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    vectorizer_loaded: bool
    loaded_version: Optional[str]
    test_inference_time_ms: Optional[float]
    cache_size: int
    total_predictions: int


class VersionSwitch(BaseModel):
    """Model version switch request"""
    version: str = Field(..., description="Version to switch to")


# API Endpoints

@router.post("/classify", response_model=ClassifyResponse)
async def classify_notification(request: ClassifyRequest):
    """
    Classify a single notification as urgent or non-urgent
    
    **Features:**
    - ML-powered classification
    - Confidence scoring
    - Action recommendations
    - Intelligent caching
    - Sub-100ms inference time
    
    **Returns:**
    - Classification (urgent/non-urgent)
    - Confidence score (0-1)
    - Recommended action
    - Human-readable reasoning
    """
    try:
        ml_service = get_ml_service()
        result = ml_service.classify(
            text=request.text,
            sender=request.sender,
            received_at=request.received_at,
            use_cache=request.use_cache
        )
        return ClassifyResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@router.post("/classify/batch")
async def batch_classify(request: BatchClassifyRequest):
    """
    Classify multiple notifications in a single request
    
    **Features:**
    - Batch processing for efficiency
    - Up to 100 notifications per request
    - Automatic caching
    - Parallel processing ready
    
    **Returns:**
    - List of classification results
    - Same format as single classification
    """
    try:
        ml_service = get_ml_service()
        
        # Convert to dict format
        notifications = [
            {
                'text': n.text,
                'sender': n.sender,
                'received_at': n.received_at
            }
            for n in request.notifications
        ]
        
        results = ml_service.batch_classify(notifications)
        
        return {
            'total': len(results),
            'results': results,
            'batch_size': len(request.notifications)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch classification failed: {str(e)}"
        )


@router.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """
    Get information about the loaded ML model
    
    **Returns:**
    - Current model version
    - Model type and architecture
    - Available classes
    - Version history
    """
    try:
        ml_service = get_ml_service()
        info = ml_service.get_model_info()
        return ModelInfo(**info)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model info: {str(e)}"
        )


@router.get("/model/performance", response_model=PerformanceStats)
async def get_performance_stats():
    """
    Get model performance statistics
    
    **Returns:**
    - Inference time metrics (avg, min, max, p95)
    - Cache hit rate
    - Total predictions count
    """
    try:
        ml_service = get_ml_service()
        stats = ml_service.get_performance_stats()
        return PerformanceStats(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance stats: {str(e)}"
        )


@router.post("/model/reload")
async def reload_model(version_request: Optional[VersionSwitch] = None):
    """
    Reload the ML model (hot-swap)
    
    **Features:**
    - Zero-downtime model updates
    - Version switching
    - Cache clearing
    
    **Args:**
    - version (optional): Specific version to load
    
    **Returns:**
    - Success status
    - New loaded version
    """
    try:
        ml_service = get_ml_service()
        version = version_request.version if version_request else None
        
        success = ml_service.reload_model(version)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Model reload failed"
            )
        
        return {
            'status': 'success',
            'message': f'Model reloaded successfully',
            'loaded_version': ml_service.loaded_version,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model reload failed: {str(e)}"
        )


@router.get("/model/versions")
async def list_model_versions():
    """
    List all available model versions
    
    **Returns:**
    - List of registered versions
    - Current active version
    - Version metadata
    """
    try:
        ml_service = get_ml_service()
        versions = ml_service.version_manager.list_versions()
        current = ml_service.version_manager.get_current_version()
        
        return {
            'current_version': current,
            'total_versions': len(versions),
            'versions': versions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list versions: {str(e)}"
        )


@router.post("/model/version/switch")
async def switch_model_version(request: VersionSwitch):
    """
    Switch to a different model version
    
    **Args:**
    - version: Version identifier to switch to
    
    **Returns:**
    - Success status
    - Old and new version
    """
    try:
        ml_service = get_ml_service()
        old_version = ml_service.loaded_version
        
        success = ml_service.version_manager.set_current_version(request.version)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Version {request.version} not found"
            )
        
        # Reload model with new version
        ml_service.reload_model(request.version)
        
        return {
            'status': 'success',
            'message': 'Model version switched successfully',
            'old_version': old_version,
            'new_version': request.version,
            'timestamp': datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Version switch failed: {str(e)}"
        )


@router.delete("/cache")
async def clear_cache():
    """
    Clear the prediction cache
    
    **Use cases:**
    - Force fresh predictions
    - Model updates
    - Testing
    
    **Returns:**
    - Cache statistics before clearing
    """
    try:
        ml_service = get_ml_service()
        stats_before = ml_service.cache.get_stats()
        
        ml_service.cache.clear()
        
        return {
            'status': 'success',
            'message': 'Cache cleared successfully',
            'stats_before_clear': stats_before,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cache clear failed: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics
    
    **Returns:**
    - Cache size
    - Hit/miss counts
    - Hit rate percentage
    - TTL settings
    """
    try:
        ml_service = get_ml_service()
        stats = ml_service.cache.get_stats()
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Perform ML service health check
    
    **Checks:**
    - Model loaded status
    - Vectorizer loaded status
    - Test inference execution
    - Cache functionality
    
    **Returns:**
    - Health status (healthy/unhealthy)
    - Component statuses
    - Test inference time
    """
    try:
        ml_service = get_ml_service()
        health = ml_service.health_check()
        return HealthCheck(**health)
    
    except Exception as e:
        return HealthCheck(
            status='unhealthy',
            model_loaded=False,
            vectorizer_loaded=False,
            loaded_version=None,
            test_inference_time_ms=None,
            cache_size=0,
            total_predictions=0
        )
