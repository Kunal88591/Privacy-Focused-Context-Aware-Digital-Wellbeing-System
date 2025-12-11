"""
Do Not Disturb (DND) Scheduler
Manages automated DND schedules and rules
"""

from datetime import datetime, time as datetime_time, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json


class DNDScheduleType(str, Enum):
    """Types of DND schedules"""
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"
    EVENT_BASED = "event_based"


class DNDException(str, Enum):
    """Exceptions to DND rules"""
    ALLOW_CONTACTS = "allow_contacts"
    ALLOW_FAVORITES = "allow_favorites"
    ALLOW_REPEATED_CALLS = "allow_repeated_calls"
    ALLOW_ALARMS = "allow_alarms"
    ALLOW_CRITICAL = "allow_critical"


class DNDScheduler:
    """Manage Do Not Disturb schedules and automation"""
    
    def __init__(self):
        # In-memory storage (would be database in production)
        self.schedules = {}
        self.active_dnd_sessions = {}
        self.manual_sessions = self.active_dnd_sessions  # Alias for tests
        
        # Default DND exceptions
        self.default_exceptions = [
            DNDException.ALLOW_ALARMS,
            DNDException.ALLOW_CRITICAL,
            DNDException.ALLOW_REPEATED_CALLS
        ]
    
    def create_schedule(
        self,
        user_id: str,
        schedule_type: DNDScheduleType,
        start_time: str,  # HH:MM format
        end_time: str,    # HH:MM format
        days_of_week: Optional[List[int]] = None,  # 0=Monday, 6=Sunday
        enabled: bool = True,
        exceptions: Optional[List[DNDException]] = None
    ) -> Dict:
        """
        Create a new DND schedule
        
        Args:
            user_id: User identifier
            schedule_type: Type of schedule
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            days_of_week: List of days (0-6) for weekly schedules
            enabled: Whether schedule is active
            exceptions: List of exceptions to allow
        """
        schedule_id = f"dnd_{user_id}_{len(self.schedules.get(user_id, []))}"
        
        schedule = {
            'schedule_id': schedule_id,
            'user_id': user_id,
            'schedule_type': schedule_type,
            'type': schedule_type,  # Alias for tests
            'start_time': start_time,
            'end_time': end_time,
            'days_of_week': days_of_week or [],
            'enabled': enabled,
            'exceptions': exceptions or self.default_exceptions,
            'created_at': datetime.now().isoformat(),
            'last_triggered': None
        }
        
        if user_id not in self.schedules:
            self.schedules[user_id] = []
        
        self.schedules[user_id].append(schedule)
        
        return schedule_id  # Return ID instead of full schedule
    
    def get_user_schedules(self, user_id: str) -> List[Dict]:
        """Get all DND schedules for user"""
        return self.get_schedules(user_id)
    
    def get_schedules(self, user_id: str) -> List[Dict]:
        """Get all DND schedules for a user"""
        return self.schedules.get(user_id, [])
    
    def update_schedule(
        self,
        user_id: str,
        schedule_id: str,
        updates: Optional[Dict] = None,
        **kwargs
    ) -> bool:
        """Update an existing schedule"""
        if user_id not in self.schedules:
            return False
        
        # Merge updates dict and kwargs
        all_updates = updates or {}
        all_updates.update(kwargs)
        
        for schedule in self.schedules[user_id]:
            if schedule['schedule_id'] == schedule_id:
                schedule.update(all_updates)
                schedule['updated_at'] = datetime.now().isoformat()
                return True
        
        return False
    
    def delete_schedule(self, user_id: str, schedule_id: str) -> bool:
        """Delete a DND schedule"""
        if user_id not in self.schedules:
            return False
        
        original_count = len(self.schedules[user_id])
        self.schedules[user_id] = [
            s for s in self.schedules[user_id]
            if s['schedule_id'] != schedule_id
        ]
        
        return len(self.schedules[user_id]) < original_count
    
    def is_dnd_active(self, user_id: str, check_time: Optional[datetime] = None) -> Dict:
        """
        Check if DND is currently active for user
        
        Returns:
            Dict with is_active, active_schedule, and reason
        """
        if check_time is None:
            check_time = datetime.now()
        
        # Check manual DND session
        if user_id in self.active_dnd_sessions:
            session = self.active_dnd_sessions[user_id]
            if datetime.fromisoformat(session['end_time']) > check_time:
                return {
                    'is_active': True,
                    'active_schedule': session,
                    'reason': 'Manual DND session',
                    'ends_at': session['end_time']
                }
        
        # Check scheduled DND
        user_schedules = self.schedules.get(user_id, [])
        for schedule in user_schedules:
            if not schedule['enabled']:
                continue
            
            if self._is_schedule_active(schedule, check_time):
                return {
                    'is_active': True,
                    'active_schedule': schedule,
                    'reason': f"{schedule['schedule_type']} schedule",
                    'ends_at': self._calculate_end_time(schedule, check_time)
                }
        
        return {
            'is_active': False,
            'active_schedule': None,
            'reason': 'No active DND schedule',
            'ends_at': None
        }
    
    def start_manual_dnd(
        self,
        user_id: str,
        duration_minutes: int,
        exceptions: Optional[List[DNDException]] = None
    ) -> Dict:
        """Start a manual DND session"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        session = {
            'session_id': f"manual_{user_id}_{int(start_time.timestamp())}",
            'user_id': user_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'exceptions': exceptions or self.default_exceptions,
            'type': 'manual'
        }
        
        self.active_dnd_sessions[user_id] = session
        return session
    
    def end_manual_dnd(self, user_id: str) -> bool:
        """End manual DND session"""
        if user_id in self.active_dnd_sessions:
            del self.active_dnd_sessions[user_id]
            return True
        return False
    
    def should_allow_notification(
        self,
        user_id: str,
        notification_type: str,
        is_critical: bool = False,
        sender: Optional[str] = None
    ) -> Dict:
        """
        Check if notification should be allowed during DND
        
        Returns:
            Dict with allowed (bool) and reason (str)
        """
        dnd_status = self.is_dnd_active(user_id)
        
        if not dnd_status['is_active']:
            return {'allowed': True, 'reason': 'DND not active'}
        
        active_schedule = dnd_status['active_schedule']
        exceptions = active_schedule.get('exceptions', [])
        
        # Check for critical notifications
        if is_critical and DNDException.ALLOW_CRITICAL in exceptions:
            return {'allowed': True, 'reason': 'Critical notification exception'}
        
        # Check for alarms
        if notification_type == 'alarm' and DNDException.ALLOW_ALARMS in exceptions:
            return {'allowed': True, 'reason': 'Alarm exception'}
        
        # Check for repeated calls (3 calls within 15 minutes)
        if notification_type == 'call' and DNDException.ALLOW_REPEATED_CALLS in exceptions:
            if self._is_repeated_call(user_id, sender):
                return {'allowed': True, 'reason': 'Repeated call exception'}
        
        # Check for favorite contacts
        if DNDException.ALLOW_FAVORITES in exceptions:
            if self._is_favorite_contact(user_id, sender):
                return {'allowed': True, 'reason': 'Favorite contact exception'}
        
        # Check for allowed contacts
        if DNDException.ALLOW_CONTACTS in exceptions:
            if self._is_in_contacts(user_id, sender):
                return {'allowed': True, 'reason': 'Contact exception'}
        
        return {'allowed': False, 'reason': 'DND active, no exception applies'}
    
    def _is_schedule_active(self, schedule: Dict, check_time: datetime) -> bool:
        """Check if a schedule is active at given time"""
        return self._is_time_match(schedule, check_time)
    
    def _is_time_match(self, schedule: Dict, check_time: datetime) -> bool:
        """Check if a schedule matches the given time"""
        schedule_type = schedule['schedule_type']
        start_time_str = schedule['start_time']
        end_time_str = schedule['end_time']
        
        # Parse times
        start_hour, start_min = map(int, start_time_str.split(':'))
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        current_time = check_time.time()
        start_time = datetime_time(start_hour, start_min)
        end_time = datetime_time(end_hour, end_min)
        
        # Check time range
        if end_time > start_time:
            time_match = start_time <= current_time <= end_time
        else:
            # Handle overnight schedules (e.g., 22:00 to 07:00)
            time_match = current_time >= start_time or current_time <= end_time
        
        if not time_match:
            return False
        
        # Check day of week for weekly schedules
        if schedule_type == DNDScheduleType.WEEKLY:
            days_of_week = schedule.get('days_of_week', [])
            if days_of_week and check_time.weekday() not in days_of_week:
                return False
        
        return True
    

    def _calculate_end_time(self, schedule: Dict, current_time: datetime) -> str:
        """Calculate when DND will end"""
        end_time_str = schedule['end_time']
        end_hour, end_min = map(int, end_time_str.split(':'))
        
        end_time = current_time.replace(hour=end_hour, minute=end_min, second=0)
        
        # If end time is before current time, it's tomorrow
        if end_time < current_time:
            end_time += timedelta(days=1)
        
        return end_time.isoformat()
    
    def _is_repeated_call(self, user_id: str, sender: Optional[str]) -> bool:
        """Check if this is a repeated call (mock implementation)"""
        # In production, this would check call history from database
        # For now, return False
        return False
    
    def _is_favorite_contact(self, user_id: str, sender: Optional[str]) -> bool:
        """Check if sender is a favorite contact (mock)"""
        # Would query user's favorites from database
        return False
    
    def _is_in_contacts(self, user_id: str, sender: Optional[str]) -> bool:
        """Check if sender is in contacts (mock)"""
        # Would query user's contacts from database
        return False
    
    def get_smart_suggestions(self, user_id: str) -> List[Dict]:
        """Get smart DND schedule suggestions based on user behavior"""
        return self.suggest_schedules(user_id)
    
    def suggest_schedules(self, user_id: str) -> List[Dict]:
        """Suggest DND schedules based on user behavior"""
        suggestions = []
        
        # Suggest sleep schedule
        suggestions.append({
            'name': 'Sleep Schedule',
            'type': 'sleep',
            'schedule_type': DNDScheduleType.DAILY,
            'start_time': '23:00',
            'end_time': '07:00',
            'reason': 'Recommended sleep hours',
            'priority': 'high'
        })
        
        # Suggest work focus hours
        suggestions.append({
            'name': 'Work Focus',
            'type': 'work_focus',
            'schedule_type': DNDScheduleType.WEEKLY,
            'start_time': '09:00',
            'end_time': '12:00',
            'days_of_week': [0, 1, 2, 3, 4],  # Weekdays
            'reason': 'Morning focus time',
            'priority': 'medium'
        })
        
        # Suggest weekend mornings
        suggestions.append({            'name': 'Weekend Rest',            'type': 'weekend_rest',
            'schedule_type': DNDScheduleType.WEEKLY,
            'start_time': '08:00',
            'end_time': '10:00',
            'days_of_week': [5, 6],  # Weekend
            'reason': 'Weekend relaxation',
            'priority': 'low'
        })
        
        return suggestions
    
    def get_statistics(self, user_id: str, days: int = 7) -> Dict:
        """Get DND usage statistics"""
        schedules = self.get_schedules(user_id) if user_id in self.schedules else []
        check_time = datetime.now()
        active_count = sum(1 for s in schedules if self._is_time_match(s, check_time))
        
        # Mock statistics - would query database in production
        return {
            'total_schedules': len(schedules),
            'active_schedules': active_count,
            'total_dnd_hours': 45.5,
            'avg_dnd_hours_per_day': 6.5,
            'most_used_schedule': 'sleep',
            'notifications_blocked': 127,
            'notifications_allowed': 8,
            'effectiveness_score': 94  # Percentage
        }


# Singleton instance
dnd_scheduler = DNDScheduler()
