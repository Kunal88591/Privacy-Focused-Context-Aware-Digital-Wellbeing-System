"""
Optimized Analytics Data Aggregation Service
Pre-computed metrics and efficient data queries
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class OptimizedAnalyticsService:
    """Provides pre-aggregated analytics data for fast retrieval"""
    
    def __init__(self):
        """Initialize with in-memory aggregation cache"""
        self.daily_cache = {}
        self.weekly_cache = {}
        self.last_aggregation = None
        self.cache_ttl = 300  # 5 minutes
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refresh"""
        if not self.last_aggregation:
            return True
        age = (datetime.now() - self.last_aggregation).total_seconds()
        return age > self.cache_ttl
    
    async def get_daily_summary(self, user_id: str, date: str = None) -> Dict:
        """
        Get pre-aggregated daily summary
        Much faster than querying individual records
        """
        cache_key = f"{user_id}:{date or 'today'}"
        
        # Check cache
        if cache_key in self.daily_cache and not self._should_refresh_cache():
            logger.debug(f"Returning cached daily summary for {user_id}")
            return self.daily_cache[cache_key]
        
        # Aggregate data (in production, this would query from database)
        summary = await self._aggregate_daily_data(user_id, date)
        
        # Cache result
        self.daily_cache[cache_key] = summary
        self.last_aggregation = datetime.now()
        
        return summary
    
    async def _aggregate_daily_data(self, user_id: str, date: str = None) -> Dict:
        """Aggregate daily data from raw events"""
        target_date = date or datetime.now().date().isoformat()
        
        # Simulated aggregation (in production, use database GROUP BY queries)
        return {
            "date": target_date,
            "user_id": user_id,
            "total_screen_time_minutes": 245,
            "focus_sessions_completed": 3,
            "focus_time_minutes": 135,
            "apps_used": 18,
            "top_apps": [
                {"name": "Chrome", "time_minutes": 85, "category": "productivity"},
                {"name": "Slack", "time_minutes": 42, "category": "communication"},
                {"name": "Spotify", "time_minutes": 38, "category": "entertainment"}
            ],
            "notifications_received": 87,
            "notifications_filtered": 23,
            "privacy_score": 78,
            "wellbeing_score": 72,
            "breaks_taken": 5,
            "goal_progress": {
                "daily_limit": {"target": 300, "current": 245, "percentage": 82},
                "focus_time": {"target": 120, "current": 135, "percentage": 113}
            }
        }
    
    async def get_weekly_trends(self, user_id: str) -> Dict:
        """Get pre-aggregated weekly trends"""
        cache_key = f"{user_id}:week"
        
        # Check cache
        if cache_key in self.weekly_cache and not self._should_refresh_cache():
            logger.debug(f"Returning cached weekly trends for {user_id}")
            return self.weekly_cache[cache_key]
        
        # Aggregate weekly data
        trends = await self._aggregate_weekly_data(user_id)
        
        # Cache result
        self.weekly_cache[cache_key] = trends
        self.last_aggregation = datetime.now()
        
        return trends
    
    async def _aggregate_weekly_data(self, user_id: str) -> Dict:
        """Aggregate weekly trends"""
        # Simulated weekly aggregation
        daily_values = [210, 245, 198, 267, 234, 189, 245]
        
        return {
            "user_id": user_id,
            "week_start": (datetime.now() - timedelta(days=7)).date().isoformat(),
            "week_end": datetime.now().date().isoformat(),
            "daily_screen_time": daily_values,
            "average_screen_time": statistics.mean(daily_values),
            "trend": "stable",  # increasing, decreasing, stable
            "week_over_week_change_percent": -3.2,
            "focus_sessions": {
                "total": 18,
                "completed": 16,
                "total_minutes": 890,
                "average_quality": 78
            },
            "privacy_scores": [75, 78, 76, 80, 78, 77, 78],
            "wellbeing_scores": [70, 72, 69, 74, 72, 71, 72],
            "most_productive_day": "Thursday",
            "most_productive_time": "10:00-12:00",
            "improvement_areas": [
                "Reduce evening screen time",
                "Take more breaks during work hours",
                "Complete more focus sessions"
            ]
        }
    
    async def get_insights(self, user_id: str) -> List[Dict]:
        """
        Get AI-generated insights based on aggregated data
        Returns pre-computed insights for fast loading
        """
        # In production, these would be generated by AI model and cached
        insights = [
            {
                "id": "insight_1",
                "type": "achievement",
                "title": "Great Focus Week!",
                "description": "You completed 16 focus sessions this week, your highest yet!",
                "icon": "trophy",
                "priority": "high",
                "action": None
            },
            {
                "id": "insight_2",
                "type": "warning",
                "title": "Evening Screen Time High",
                "description": "Your screen time after 9 PM increased by 25% this week.",
                "icon": "alert",
                "priority": "medium",
                "action": {
                    "label": "Set Evening Limit",
                    "type": "create_goal"
                }
            },
            {
                "id": "insight_3",
                "type": "suggestion",
                "title": "Optimal Work Time Detected",
                "description": "You're most productive between 10 AM - 12 PM. Schedule important tasks then.",
                "icon": "lightbulb",
                "priority": "low",
                "action": {
                    "label": "Create Schedule",
                    "type": "schedule_focus"
                }
            },
            {
                "id": "insight_4",
                "type": "milestone",
                "title": "30-Day Streak!",
                "description": "You've maintained your focus goals for 30 consecutive days.",
                "icon": "fire",
                "priority": "high",
                "action": None
            }
        ]
        
        return insights
    
    async def get_quick_stats(self, user_id: str) -> Dict:
        """
        Get minimal stats for dashboard - optimized for speed
        Returns only essential metrics
        """
        return {
            "today_screen_time": 245,
            "today_focus_time": 135,
            "privacy_score": 78,
            "wellbeing_score": 72,
            "active_streak": 12,
            "notifications_filtered": 23
        }
    
    def clear_cache(self, user_id: str = None):
        """Clear aggregation cache"""
        if user_id:
            # Clear specific user cache
            keys_to_remove = [k for k in self.daily_cache.keys() if k.startswith(user_id)]
            for key in keys_to_remove:
                del self.daily_cache[key]
            
            keys_to_remove = [k for k in self.weekly_cache.keys() if k.startswith(user_id)]
            for key in keys_to_remove:
                del self.weekly_cache[key]
        else:
            # Clear all cache
            self.daily_cache.clear()
            self.weekly_cache.clear()
        
        logger.info(f"Cleared analytics cache for {user_id or 'all users'}")


# Global optimized analytics instance
optimized_analytics = OptimizedAnalyticsService()
