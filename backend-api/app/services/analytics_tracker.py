"""
User Analytics Tracker
Comprehensive analytics service for tracking user behavior and generating insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics
import json


class AnalyticsTracker:
    """Track and analyze user behavior patterns for data-driven insights"""
    
    def __init__(self):
        """Initialize analytics tracker with in-memory storage"""
        self.data_store = {
            'sessions': [],  # User sessions with start/end times
            'screen_time': [],  # App screen time tracking
            'focus_sessions': [],  # Deep focus work sessions
            'breaks': [],  # Break tracking
            'notifications': [],  # Notification events
            'app_usage': defaultdict(lambda: {'total_time': 0, 'open_count': 0, 'last_used': None}),
            'productivity_scores': [],  # Daily productivity scores
            'wellbeing_scores': [],  # Daily wellbeing scores
            'goals': [],  # User-set goals and completion
            'distractions': [],  # Distraction events
        }
    
    # ==================== Session Tracking ====================
    
    def track_session(self, user_id: str, start_time: datetime, end_time: datetime, 
                     device_type: str = 'mobile') -> Dict:
        """Track a user session"""
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        session = {
            'user_id': user_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'device_type': device_type,
            'date': start_time.date().isoformat(),
            'hour': start_time.hour,
            'day_of_week': start_time.strftime('%A')
        }
        
        self.data_store['sessions'].append(session)
        return session
    
    # ==================== Screen Time Tracking ====================
    
    def track_screen_time(self, user_id: str, app_name: str, duration_minutes: float,
                         timestamp: datetime, category: str = 'other') -> Dict:
        """Track screen time for specific app"""
        screen_time = {
            'user_id': user_id,
            'app_name': app_name,
            'duration_minutes': duration_minutes,
            'category': category,
            'timestamp': timestamp.isoformat(),
            'date': timestamp.date().isoformat(),
            'hour': timestamp.hour
        }
        
        self.data_store['screen_time'].append(screen_time)
        
        # Update app usage stats
        self.data_store['app_usage'][app_name]['total_time'] += duration_minutes
        self.data_store['app_usage'][app_name]['open_count'] += 1
        self.data_store['app_usage'][app_name]['last_used'] = timestamp.isoformat()
        
        return screen_time
    
    # ==================== Focus Session Tracking ====================
    
    def track_focus_session(self, user_id: str, start_time: datetime, end_time: datetime,
                           quality_score: int, task_name: Optional[str] = None) -> Dict:
        """Track a deep focus work session"""
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        focus_session = {
            'user_id': user_id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'quality_score': quality_score,  # 0-100
            'task_name': task_name,
            'date': start_time.date().isoformat(),
            'hour': start_time.hour
        }
        
        self.data_store['focus_sessions'].append(focus_session)
        return focus_session
    
    # ==================== Break Tracking ====================
    
    def track_break(self, user_id: str, start_time: datetime, duration_minutes: int,
                   break_type: str = 'short') -> Dict:
        """Track a break"""
        break_event = {
            'user_id': user_id,
            'start_time': start_time.isoformat(),
            'duration_minutes': duration_minutes,
            'break_type': break_type,  # short, long, lunch
            'date': start_time.date().isoformat()
        }
        
        self.data_store['breaks'].append(break_event)
        return break_event
    
    # ==================== Notification Tracking ====================
    
    def track_notification(self, user_id: str, timestamp: datetime, app_name: str,
                          priority: int, was_interacted: bool = False) -> Dict:
        """Track notification events"""
        notification = {
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'app_name': app_name,
            'priority': priority,  # 0-100
            'was_interacted': was_interacted,
            'date': timestamp.date().isoformat(),
            'hour': timestamp.hour
        }
        
        self.data_store['notifications'].append(notification)
        return notification
    
    # ==================== Distraction Tracking ====================
    
    def track_distraction(self, user_id: str, timestamp: datetime, source: str,
                         severity: int, duration_seconds: int = 0) -> Dict:
        """Track distraction events"""
        distraction = {
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'source': source,
            'severity': severity,  # 1-5
            'duration_seconds': duration_seconds,
            'date': timestamp.date().isoformat(),
            'hour': timestamp.hour
        }
        
        self.data_store['distractions'].append(distraction)
        return distraction
    
    # ==================== Goal Tracking ====================
    
    def set_goal(self, user_id: str, goal_type: str, target_value: float,
                current_value: float = 0, deadline: Optional[datetime] = None) -> Dict:
        """Set a user goal"""
        goal = {
            'user_id': user_id,
            'goal_type': goal_type,  # e.g., 'daily_focus_time', 'screen_time_limit'
            'target_value': target_value,
            'current_value': current_value,
            'progress_percent': (current_value / target_value * 100) if target_value > 0 else 0,
            'deadline': deadline.isoformat() if deadline else None,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.data_store['goals'].append(goal)
        return goal
    
    def update_goal_progress(self, goal_index: int, new_value: float) -> Dict:
        """Update goal progress"""
        if goal_index < len(self.data_store['goals']):
            goal = self.data_store['goals'][goal_index]
            goal['current_value'] = new_value
            goal['progress_percent'] = (new_value / goal['target_value'] * 100) if goal['target_value'] > 0 else 0
            
            # Mark as completed if target reached
            if new_value >= goal['target_value']:
                goal['status'] = 'completed'
                goal['completed_at'] = datetime.now().isoformat()
            
            return goal
        return {}
    
    # ==================== Analytics Generation ====================
    
    def get_daily_summary(self, user_id: str, date: Optional[datetime] = None) -> Dict:
        """Generate comprehensive daily summary"""
        if date is None:
            date = datetime.now()
        
        date_str = date.date().isoformat()
        
        # Filter data for this date
        daily_sessions = [s for s in self.data_store['sessions'] 
                         if s['user_id'] == user_id and s['date'] == date_str]
        daily_screen_time = [s for s in self.data_store['screen_time'] 
                            if s['user_id'] == user_id and s['date'] == date_str]
        daily_focus = [f for f in self.data_store['focus_sessions'] 
                      if f['user_id'] == user_id and f['date'] == date_str]
        daily_breaks = [b for b in self.data_store['breaks'] 
                       if b['user_id'] == user_id and b['date'] == date_str]
        daily_notifications = [n for n in self.data_store['notifications'] 
                              if n['user_id'] == user_id and n['date'] == date_str]
        daily_distractions = [d for d in self.data_store['distractions'] 
                             if d['user_id'] == user_id and d['date'] == date_str]
        
        # Calculate metrics
        total_screen_time = sum(s['duration_minutes'] for s in daily_screen_time)
        total_focus_time = sum(f['duration_minutes'] for f in daily_focus)
        total_break_time = sum(b['duration_minutes'] for b in daily_breaks)
        
        avg_focus_quality = statistics.mean([f['quality_score'] for f in daily_focus]) if daily_focus else 0
        
        notification_interaction_rate = (
            sum(1 for n in daily_notifications if n['was_interacted']) / len(daily_notifications) * 100
            if daily_notifications else 0
        )
        
        # Calculate productivity score (0-100)
        productivity_score = self._calculate_productivity_score(
            focus_time=total_focus_time,
            focus_quality=avg_focus_quality,
            distractions=len(daily_distractions),
            breaks_taken=len(daily_breaks)
        )
        
        # Top apps by screen time
        app_times = defaultdict(float)
        for screen in daily_screen_time:
            app_times[screen['app_name']] += screen['duration_minutes']
        
        top_apps = sorted(app_times.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'date': date_str,
            'user_id': user_id,
            'total_screen_time_minutes': round(total_screen_time, 1),
            'total_focus_time_minutes': round(total_focus_time, 1),
            'total_break_time_minutes': round(total_break_time, 1),
            'average_focus_quality': round(avg_focus_quality, 1),
            'productivity_score': round(productivity_score, 1),
            'sessions_count': len(daily_sessions),
            'focus_sessions_count': len(daily_focus),
            'breaks_count': len(daily_breaks),
            'notifications_received': len(daily_notifications),
            'notifications_interacted': sum(1 for n in daily_notifications if n['was_interacted']),
            'notification_interaction_rate': round(notification_interaction_rate, 1),
            'distractions_count': len(daily_distractions),
            'top_apps': [{'app': app, 'minutes': round(mins, 1)} for app, mins in top_apps],
            'hourly_breakdown': self._get_hourly_breakdown(daily_screen_time),
        }
    
    def get_weekly_trends(self, user_id: str, end_date: Optional[datetime] = None) -> Dict:
        """Generate weekly trends analysis"""
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=7)
        
        daily_summaries = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            summary = self.get_daily_summary(user_id, current_date)
            daily_summaries.append(summary)
        
        # Calculate weekly averages
        avg_screen_time = statistics.mean([d['total_screen_time_minutes'] for d in daily_summaries])
        avg_focus_time = statistics.mean([d['total_focus_time_minutes'] for d in daily_summaries])
        avg_productivity = statistics.mean([d['productivity_score'] for d in daily_summaries])
        
        total_distractions = sum(d['distractions_count'] for d in daily_summaries)
        total_notifications = sum(d['notifications_received'] for d in daily_summaries)
        
        # Identify best and worst days
        best_day = max(daily_summaries, key=lambda x: x['productivity_score'])
        worst_day = min(daily_summaries, key=lambda x: x['productivity_score'])
        
        # Trend analysis
        productivity_trend = self._analyze_trend([d['productivity_score'] for d in daily_summaries])
        focus_trend = self._analyze_trend([d['total_focus_time_minutes'] for d in daily_summaries])
        
        return {
            'period': f"{start_date.date().isoformat()} to {end_date.date().isoformat()}",
            'user_id': user_id,
            'daily_summaries': daily_summaries,
            'weekly_averages': {
                'screen_time_minutes': round(avg_screen_time, 1),
                'focus_time_minutes': round(avg_focus_time, 1),
                'productivity_score': round(avg_productivity, 1),
                'distractions_per_day': round(total_distractions / 7, 1),
                'notifications_per_day': round(total_notifications / 7, 1),
            },
            'best_day': {
                'date': best_day['date'],
                'productivity_score': best_day['productivity_score'],
                'focus_time': best_day['total_focus_time_minutes']
            },
            'worst_day': {
                'date': worst_day['date'],
                'productivity_score': worst_day['productivity_score'],
                'focus_time': worst_day['total_focus_time_minutes']
            },
            'trends': {
                'productivity': productivity_trend,
                'focus_time': focus_trend
            }
        }
    
    def get_app_usage_breakdown(self, user_id: str, days: int = 7) -> Dict:
        """Get detailed app usage breakdown"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_str = start_date.date().isoformat()
        end_str = end_date.date().isoformat()
        
        # Filter screen time data
        relevant_screen_time = [
            s for s in self.data_store['screen_time']
            if s['user_id'] == user_id and start_str <= s['date'] <= end_str
        ]
        
        # Aggregate by app
        app_stats = defaultdict(lambda: {'total_time': 0, 'sessions': 0, 'categories': set()})
        
        for screen in relevant_screen_time:
            app = screen['app_name']
            app_stats[app]['total_time'] += screen['duration_minutes']
            app_stats[app]['sessions'] += 1
            app_stats[app]['categories'].add(screen['category'])
        
        # Convert to list and sort
        apps_list = []
        for app, stats in app_stats.items():
            apps_list.append({
                'app_name': app,
                'total_time_minutes': round(stats['total_time'], 1),
                'total_time_hours': round(stats['total_time'] / 60, 2),
                'sessions': stats['sessions'],
                'avg_session_minutes': round(stats['total_time'] / stats['sessions'], 1) if stats['sessions'] > 0 else 0,
                'categories': list(stats['categories']),
                'percentage': 0  # Will calculate after
            })
        
        # Sort by total time
        apps_list.sort(key=lambda x: x['total_time_minutes'], reverse=True)
        
        # Calculate percentages
        total_time = sum(app['total_time_minutes'] for app in apps_list)
        for app in apps_list:
            app['percentage'] = round((app['total_time_minutes'] / total_time * 100), 1) if total_time > 0 else 0
        
        return {
            'period_days': days,
            'start_date': start_str,
            'end_date': end_str,
            'total_apps': len(apps_list),
            'total_time_minutes': round(total_time, 1),
            'total_time_hours': round(total_time / 60, 2),
            'apps': apps_list[:20]  # Top 20 apps
        }
    
    def get_productivity_insights(self, user_id: str) -> Dict:
        """Generate AI-powered productivity insights"""
        # Get weekly data
        weekly_data = self.get_weekly_trends(user_id)
        
        insights = []
        recommendations = []
        
        # Focus time analysis
        avg_focus = weekly_data['weekly_averages']['focus_time_minutes']
        if avg_focus < 120:
            insights.append({
                'type': 'warning',
                'category': 'focus',
                'title': 'Low Focus Time',
                'message': f'Your average daily focus time is {avg_focus:.0f} minutes. Aim for at least 2 hours.',
                'icon': '⚠️'
            })
            recommendations.append({
                'category': 'focus',
                'priority': 'high',
                'text': 'Schedule dedicated focus blocks in your calendar',
                'action': 'enable_focus_mode'
            })
        elif avg_focus >= 180:
            insights.append({
                'type': 'positive',
                'category': 'focus',
                'title': 'Excellent Focus',
                'message': f'Great job! You averaged {avg_focus:.0f} minutes of focus time daily.',
                'icon': '🎯'
            })
        
        # Distraction analysis
        avg_distractions = weekly_data['weekly_averages']['distractions_per_day']
        if avg_distractions > 20:
            insights.append({
                'type': 'warning',
                'category': 'distractions',
                'title': 'High Distractions',
                'message': f'{avg_distractions:.0f} distractions per day detected.',
                'icon': '🚨'
            })
            recommendations.append({
                'category': 'distractions',
                'priority': 'high',
                'text': 'Enable Do Not Disturb mode during focus sessions',
                'action': 'configure_dnd'
            })
        
        # Productivity trend analysis
        if weekly_data['trends']['productivity'] == 'improving':
            insights.append({
                'type': 'positive',
                'category': 'trend',
                'title': 'Improving Productivity',
                'message': 'Your productivity is trending upward! Keep it up!',
                'icon': '📈'
            })
        elif weekly_data['trends']['productivity'] == 'declining':
            insights.append({
                'type': 'warning',
                'category': 'trend',
                'title': 'Declining Productivity',
                'message': 'Your productivity has been declining this week.',
                'icon': '📉'
            })
            recommendations.append({
                'category': 'recovery',
                'priority': 'medium',
                'text': 'Review your best day and replicate those conditions',
                'action': 'view_best_day'
            })
        
        # Screen time analysis
        avg_screen = weekly_data['weekly_averages']['screen_time_minutes']
        if avg_screen > 480:  # 8 hours
            insights.append({
                'type': 'info',
                'category': 'screen_time',
                'title': 'High Screen Time',
                'message': f'{avg_screen / 60:.1f} hours average daily screen time.',
                'icon': '📱'
            })
            recommendations.append({
                'category': 'wellbeing',
                'priority': 'medium',
                'text': 'Schedule regular breaks to reduce eye strain',
                'action': 'enable_break_reminders'
            })
        
        return {
            'generated_at': datetime.now().isoformat(),
            'user_id': user_id,
            'insights': insights,
            'recommendations': recommendations,
            'weekly_summary': weekly_data['weekly_averages']
        }
    
    # ==================== Helper Methods ====================
    
    def _calculate_productivity_score(self, focus_time: float, focus_quality: float,
                                      distractions: int, breaks_taken: int) -> float:
        """Calculate productivity score (0-100)"""
        # Weighted formula
        focus_score = min((focus_time / 240) * 100, 100)  # 240 min = 4 hours ideal
        quality_score = focus_quality
        distraction_penalty = max(0, 100 - (distractions * 2))
        break_bonus = min(breaks_taken * 5, 20)  # Up to 20 points for taking breaks
        
        score = (
            focus_score * 0.4 +
            quality_score * 0.3 +
            distraction_penalty * 0.2 +
            break_bonus * 0.1
        )
        
        return max(0, min(100, score))
    
    def _get_hourly_breakdown(self, screen_time_data: List[Dict]) -> List[Dict]:
        """Get hourly breakdown of screen time"""
        hourly = defaultdict(float)
        
        for screen in screen_time_data:
            hourly[screen['hour']] += screen['duration_minutes']
        
        breakdown = []
        for hour in range(24):
            breakdown.append({
                'hour': hour,
                'time_label': f"{hour:02d}:00",
                'minutes': round(hourly[hour], 1)
            })
        
        return breakdown
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend direction in time series data"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Threshold for significance
        if slope > 2:
            return 'improving'
        elif slope < -2:
            return 'declining'
        else:
            return 'stable'
    
    def export_data(self, user_id: str, format: str = 'json') -> str:
        """Export user analytics data"""
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'daily_summary': self.get_daily_summary(user_id),
            'weekly_trends': self.get_weekly_trends(user_id),
            'app_usage': self.get_app_usage_breakdown(user_id),
            'productivity_insights': self.get_productivity_insights(user_id)
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2)
        
        return str(export_data)


# Global analytics instance
analytics_tracker = AnalyticsTracker()
