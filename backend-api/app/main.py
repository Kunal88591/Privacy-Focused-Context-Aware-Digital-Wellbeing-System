"""
Privacy-Focused Digital Wellbeing System - Backend API
Main application entry point with performance optimizations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from contextlib import asynccontextmanager

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Global Redis client for caching
redis_client = None

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global redis_client
    
    logger.info("🚀 Starting Privacy-Focused Digital Wellbeing System API...")
    logger.info("📡 Initializing MQTT connections...")
    logger.info("🤖 Loading AI models...")
    logger.info("⚡ Initializing Redis cache...")
    
    # Initialize Redis for caching
    try:
        if aioredis:
            redis_client = await aioredis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("✅ Redis cache initialized")
            
            # Initialize cache manager
            from app.core.cache import cache_manager
            cache_manager.redis_client = redis_client
            cache_manager.enabled = True
        else:
            logger.warning("⚠️ Redis library not available, caching disabled")
        
    except Exception as e:
        logger.warning(f"⚠️ Redis not available, caching disabled: {e}")
    
    # TODO: Initialize MQTT client
    # TODO: Load ML models
    
    yield
    
    logger.info("🛑 Shutting down API server...")
    
    # Cleanup Redis connection
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis connection closed")
    
    # TODO: Cleanup MQTT connections
    # TODO: Close database connections

# Initialize FastAPI application
app = FastAPI(
    title="Privacy-Focused Digital Wellbeing API",
    description="Backend API for context-aware digital wellbeing and privacy management",
    version="0.1.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add performance monitoring middleware
from app.middleware.performance import PerformanceMiddleware
app.add_middleware(PerformanceMiddleware, slow_threshold_ms=500)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "message": "Privacy-Focused Digital Wellbeing API",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    from app.core.cache import cache_manager
    
    # Check database if configured
    db_status = "online"
    try:
        from app.core.database import check_database_connection
        db_status = "online" if check_database_connection() else "offline"
    except:
        db_status = "not_configured"
    
    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": db_status,
            "cache": "online" if cache_manager.enabled else "disabled",
            "mqtt": "online",      # TODO: Check actual MQTT connection
            "ml_models": "loaded"  # TODO: Check actual model status
        }
    }

@app.get("/metrics")
async def get_metrics():
    """Get API performance metrics"""
    from app.core.cache import cache_manager
    
    # Get performance stats from middleware
    perf_middleware = None
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls.__name__ == 'PerformanceMiddleware':
            perf_middleware = middleware
            break
    
    metrics = {
        "cache": cache_manager.get_stats(),
    }
    
    # Add database pool stats if configured
    try:
        from app.core.database import get_pool_stats
        metrics["database_pool"] = get_pool_stats()
    except:
        metrics["database_pool"] = "not_configured"
    
    return metrics

# Import API routers
from app.api import auth, notifications, privacy, wellbeing, devices, ai_advanced, privacy_advanced, analytics, iot_automation
from app.routes import smart_notifications, ml_model, recommendations

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(privacy.router, prefix="/api/v1/privacy", tags=["privacy"])
app.include_router(wellbeing.router, prefix="/api/v1/wellbeing", tags=["wellbeing"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["devices"])
app.include_router(ai_advanced.router, tags=["Advanced AI"])
app.include_router(privacy_advanced.router, tags=["Advanced Privacy"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(smart_notifications.router, tags=["Smart Notifications"])
app.include_router(ml_model.router, tags=["Machine Learning"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(iot_automation.router, tags=["IoT Automation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
