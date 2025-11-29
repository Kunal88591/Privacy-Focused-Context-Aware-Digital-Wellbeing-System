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

# API Routes will be imported here
# from app.api import notifications, privacy, wellbeing, devices

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
