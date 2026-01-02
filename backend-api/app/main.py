"""
Privacy-Focused Digital Wellbeing System - Backend API
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("🚀 Starting Privacy-Focused Digital Wellbeing System API...")
    logger.info("📡 Initializing MQTT connections...")
    logger.info("🤖 Loading AI models...")
    # TODO: Initialize MQTT client
    # TODO: Load ML models
    yield
    logger.info("🛑 Shutting down API server...")
    # TODO: Cleanup MQTT connections
    # TODO: Close database connections

# Initialize FastAPI application
app = FastAPI(
    title="Privacy-Focused Digital Wellbeing API",
    description="Backend API for context-aware digital wellbeing and privacy management",
    version="0.1.0",
    lifespan=lifespan
)

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
    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "online",  # TODO: Check actual DB connection
            "mqtt": "online",      # TODO: Check actual MQTT connection
            "ml_models": "loaded"  # TODO: Check actual model status
        }
    }

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
