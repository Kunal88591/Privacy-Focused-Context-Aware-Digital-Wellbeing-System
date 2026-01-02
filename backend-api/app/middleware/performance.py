"""
Performance Monitoring Middleware
Tracks API response times and adds performance headers
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track and log API performance metrics"""
    
    def __init__(self, app, slow_threshold_ms: float = 500):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms
        self.request_count = 0
        self.total_time = 0
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Track request timing and add performance headers"""
        
        # Start timer
        start_time = time.time()
        
        # Increment request counter
        self.request_count += 1
        
        # Process request
        response = await call_next(request)
        
        # Calculate elapsed time
        elapsed_ms = (time.time() - start_time) * 1000
        self.total_time += elapsed_ms
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
        response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}"
        
        # Log slow requests
        if elapsed_ms > self.slow_threshold_ms:
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.url.path} "
                f"took {elapsed_ms:.2f}ms (threshold: {self.slow_threshold_ms}ms)"
            )
        
        # Log request details
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {elapsed_ms:.2f}ms"
        )
        
        return response
    
    def get_stats(self):
        """Get performance statistics"""
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "total_requests": self.request_count,
            "total_time_ms": round(self.total_time, 2),
            "average_time_ms": round(avg_time, 2)
        }
