"""
Context-Aware Notification Filter
Intelligently filters notifications based on user context, time, and behavior patterns
"""

from datetime import datetime, time as datetime_time
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class NotificationContext(str, Enum):
    """User context states"""
    FOCUS_MODE = "focus_mode"
    MEETING = "meeting"
    SLEEPING = "sleeping"
    COMMUTING = "commuting"
    WORKING = "working"
    LEISURE = "leisure"
    EXERCISING = "exercising"


class FilterAction(str, Enum):
    """Actions to take on notifications"""
    SHOW_IMMEDIATELY = "show_immediately"
    DEFER = "defer"
    BUNDLE = "bundle"
    SILENCE = "silence"
    BLOCK = "block"


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    SPAM = 4


class ContextAwareFilter:
    """Filter notifications based on user context and intelligent rules"""
    
    def __init__(self):
        # Critical keywords that always pass through
        self.critical_keywords = [
            'emergency', 'urgent', 'critical', 'alarm', 'security',
            'breach', 'alert', 'warning', 'deadline', '911'
        ]
        
        # Keywords for different priority levels
        self.high_priority_keywords = [
            'meeting', 'appointment', 'call', 'video', 'interview',
            'important', 'asap', 'now', 'immediately'
        ]
        
        self.low_priority_keywords = [
            'newsletter', 'promotion', 'sale', 'discount', 'offer',
            'subscribe', 'unsubscribe', 'marketing'
        ]
        
        # App categories
        self.work_apps = [
            'slack', 'teams', 'outlook', 'gmail', 'calendar',
            'zoom', 'meet', 'webex', 'jira', 'trello'
        ]
        
        self.social_apps = [
            'facebook', 'instagram', 'twitter', 'tiktok', 'snapchat',
            'whatsapp', 'telegram', 'discord', 'reddit'
        ]
        
        self.entertainment_apps = [
            'youtube', 'netflix', 'spotify', 'twitch', 'prime',
            'hulu', 'disney', 'hbo'
        ]
        
        # User preferences (loaded from database)
        self.user_preferences = {}
    
    def analyze_notification(
        self,
        notification_text: str,
        sender: str,
        timestamp: str,
        app_name: str,
        user_id: str
    ) -> Dict:
        """
        Analyze notification and determine how to handle it
        
        Returns:
            Dict with priority, action, reasoning, and metadata
        """
        # Convert timestamp if string
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # Determine priority
        priority = self._determine_priority(notification_text, sender, app_name)
        
        # Get current user context
        context = self._get_user_context(user_id, timestamp)
        
        # Decide action based on context and priority
        action = self._decide_action(priority, context, timestamp, app_name, user_id)
        
        # Calculate defer time if applicable
        defer_until = self._calculate_defer_time(action, context, timestamp)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(priority, context, action)
        
        return {
            'priority': priority.name.lower() if isinstance(priority, NotificationPriority) else priority,
            'action': action.name.lower() if isinstance(action, FilterAction) else action,
            'context': context.name.lower() if isinstance(context, NotificationContext) else context,
            'defer_until': defer_until,
            'reasoning': reasoning,
            'analyzed_at': timestamp.isoformat(),
            'metadata': {
                'is_work_related': self._is_work_app(app_name),
                'is_social': self._is_social_app(app_name),
                'is_entertainment': self._is_entertainment_app(app_name),
                'time_appropriate': self._is_time_appropriate(timestamp, app_name)
            }
        }
    
    def _determine_priority(
        self,
        text: str,
        sender: str,
        app_name: str
    ) -> NotificationPriority:
        """Determine notification priority based on content"""
        text_lower = text.lower()
        
        # Check for critical keywords
        if any(keyword in text_lower for keyword in self.critical_keywords):
            return NotificationPriority.CRITICAL
        
        # Check for high priority
        if any(keyword in text_lower for keyword in self.high_priority_keywords):
            return NotificationPriority.HIGH
        
        # Check for low priority/spam
        if any(keyword in text_lower for keyword in self.low_priority_keywords):
            return NotificationPriority.LOW
        
        # Work apps during work hours
        if self._is_work_app(app_name):
            return NotificationPriority.HIGH
        
        # Social apps
        if self._is_social_app(app_name):
            return NotificationPriority.MEDIUM
        
        # Entertainment
        if self._is_entertainment_app(app_name):
            return NotificationPriority.LOW
        
        return NotificationPriority.MEDIUM
    
    def _get_user_context(self, user_id: str, timestamp: datetime) -> NotificationContext:
        """Determine current user context"""
        hour = timestamp.hour
        
        # Check if user is in focus mode (from database)
        # This would normally query the database
        if self._is_focus_mode_active(user_id):
            return NotificationContext.FOCUS_MODE
        
        # Sleep hours (11 PM - 7 AM)
        if hour >= 23 or hour < 7:
            return NotificationContext.SLEEPING
        
        # Work hours (9 AM - 6 PM on weekdays)
        if timestamp.weekday() < 5 and 9 <= hour < 18:
            return NotificationContext.WORKING
        
        # Commute hours (7-9 AM, 5-7 PM)
        if (7 <= hour < 9) or (17 <= hour < 19):
            return NotificationContext.COMMUTING
        
        # Evening/leisure
        if 18 <= hour < 23:
            return NotificationContext.LEISURE
        
        return NotificationContext.LEISURE
    
    def _decide_action(
        self,
        priority: NotificationPriority,
        context: NotificationContext,
        timestamp: datetime,
        app_name: str,
        user_id: str
    ) -> FilterAction:
        """Decide what action to take based on priority and context"""
        
        # Critical notifications always show immediately
        if priority == NotificationPriority.CRITICAL:
            return FilterAction.SHOW_IMMEDIATELY
        
        # Focus mode: only critical or high priority work apps
        if context == NotificationContext.FOCUS_MODE:
            if priority == NotificationPriority.HIGH and self._is_work_app(app_name):
                return FilterAction.SHOW_IMMEDIATELY
            return FilterAction.DEFER
        
        # Sleeping: only critical
        if context == NotificationContext.SLEEPING:
            return FilterAction.SILENCE
        
        # Meeting: defer non-critical
        if context == NotificationContext.MEETING:
            if priority == NotificationPriority.HIGH:
                return FilterAction.BUNDLE
            return FilterAction.DEFER
        
        # Working: allow work apps, bundle social
        if context == NotificationContext.WORKING:
            if self._is_work_app(app_name):
                return FilterAction.SHOW_IMMEDIATELY
            if self._is_social_app(app_name):
                return FilterAction.BUNDLE
            return FilterAction.DEFER
        
        # Commuting: bundle most notifications
        if context == NotificationContext.COMMUTING:
            if priority == NotificationPriority.HIGH:
                return FilterAction.SHOW_IMMEDIATELY
            return FilterAction.BUNDLE
        
        # Leisure: more permissive
        if context == NotificationContext.LEISURE:
            if priority in [NotificationPriority.HIGH, NotificationPriority.MEDIUM]:
                return FilterAction.SHOW_IMMEDIATELY
            return FilterAction.BUNDLE
        
        return FilterAction.SHOW_IMMEDIATELY
    
    def _calculate_defer_time(
        self,
        action: FilterAction,
        context: NotificationContext,
        current_time: datetime
    ) -> Optional[str]:
        """Calculate when to show deferred notification"""
        if action != FilterAction.DEFER:
            return None
        
        hour = current_time.hour
        
        # If sleeping, defer until 8 AM
        if context == NotificationContext.SLEEPING:
            next_morning = current_time.replace(hour=8, minute=0, second=0)
            if hour >= 23:
                next_morning = next_morning.replace(day=current_time.day + 1)
            return next_morning.isoformat()
        
        # If focus mode, defer 1 hour
        if context == NotificationContext.FOCUS_MODE:
            from datetime import timedelta
            return (current_time + timedelta(hours=1)).isoformat()
        
        # If working, defer to lunch (12 PM) or end of day (6 PM)
        if context == NotificationContext.WORKING:
            if hour < 12:
                defer_time = current_time.replace(hour=12, minute=0)
            else:
                defer_time = current_time.replace(hour=18, minute=0)
            return defer_time.isoformat()
        
        # Default: defer 30 minutes
        from datetime import timedelta
        return (current_time + timedelta(minutes=30)).isoformat()
    
    def _generate_reasoning(
        self,
        priority: NotificationPriority,
        context: NotificationContext,
        action: FilterAction
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        reasons = []
        
        # Priority reasoning
        if priority == NotificationPriority.CRITICAL:
            reasons.append("Critical notification detected")
        elif priority == NotificationPriority.HIGH:
            reasons.append("High priority content")
        elif priority == NotificationPriority.LOW:
            reasons.append("Low priority content")
        
        # Context reasoning
        if context == NotificationContext.FOCUS_MODE:
            reasons.append("User in focus mode")
        elif context == NotificationContext.SLEEPING:
            reasons.append("User sleeping hours")
        elif context == NotificationContext.WORKING:
            reasons.append("User in work hours")
        elif context == NotificationContext.MEETING:
            reasons.append("User in meeting")
        
        # Action reasoning
        if action == FilterAction.DEFER:
            reasons.append("Deferred to avoid distraction")
        elif action == FilterAction.BUNDLE:
            reasons.append("Bundled with similar notifications")
        elif action == FilterAction.SILENCE:
            reasons.append("Silenced during quiet hours")
        
        return "; ".join(reasons) if reasons else "Standard notification processing"
    
    def _is_focus_mode_active(self, user_id: str) -> bool:
        """Check if user has focus mode active (mock)"""
        # This would query the database in production
        return False
    
    def _is_work_app(self, app_name: str) -> bool:
        """Check if app is work-related"""
        return any(work_app in app_name.lower() for work_app in self.work_apps)
    
    def _is_social_app(self, app_name: str) -> bool:
        """Check if app is social media"""
        return any(social_app in app_name.lower() for social_app in self.social_apps)
    
    def _is_entertainment_app(self, app_name: str) -> bool:
        """Check if app is entertainment"""
        return any(ent_app in app_name.lower() for ent_app in self.entertainment_apps)
    
    def _is_time_appropriate(self, timestamp: datetime, app_name: str) -> bool:
        """Check if notification is appropriate for current time"""
        hour = timestamp.hour
        
        # Work apps appropriate during work hours
        if self._is_work_app(app_name):
            return 9 <= hour < 18
        
        # Social apps appropriate during leisure
        if self._is_social_app(app_name):
            return 10 <= hour < 23
        
        # Entertainment appropriate in evening
        if self._is_entertainment_app(app_name):
            return 18 <= hour < 24
        
        return True
    
    def set_user_preferences(self, user_id: str, preferences: Dict):
        """Set user-specific filtering preferences"""
        self.user_preferences[user_id] = preferences
    
    def get_filter_stats(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get filtering statistics for analysis"""
        # This would query database for actual stats
        return {
            'total_notifications': 0,
            'filtered_count': 0,
            'deferred_count': 0,
            'bundled_count': 0,
            'blocked_count': 0,
            'filter_rate': 0.0
        }


# Singleton instance
context_filter = ContextAwareFilter()
