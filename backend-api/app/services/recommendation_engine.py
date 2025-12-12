"""
Smart Recommendation Engine
AI-powered personalized recommendations based on user behavior patterns
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from collections import defaultdict


class RecommendationEngine:
    """
    Generates personalized recommendations using:
    - Usage patterns analysis
    - Time-based behavioral insights
    - Context-aware suggestions
    - Privacy-preserving algorithms
    """
    
    def __init__(self):
        self.recommendation_types = [
            "focus_time",
            "break_time",
            "app_limit",
            "bedtime",
            "morning_routine",
            "notification_control",
            "privacy_improvement",
            "wellbeing_boost"
        ]
    
    async def generate_recommendations(
        self,
        user_id: int,
        analytics_data: Dict,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate personalized recommendations based on user data
        
        Args:
            user_id: User identifier
            analytics_data: User analytics and behavior data
            context: Current context (time, location, activity)
        
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Analyze patterns
        patterns = self._analyze_patterns(analytics_data)
        
        # Generate recommendations by category
        recommendations.extend(self._focus_recommendations(patterns, context))
        recommendations.extend(self._break_recommendations(patterns, context))
        recommendations.extend(self._app_usage_recommendations(patterns))
        recommendations.extend(self._sleep_recommendations(patterns, context))
        recommendations.extend(self._notification_recommendations(patterns))
        recommendations.extend(self._privacy_recommendations(analytics_data))
        recommendations.extend(self._wellbeing_recommendations(patterns))
        
        # Score and rank recommendations
        scored_recommendations = self._score_recommendations(
            recommendations,
            patterns,
            context
        )
        
        # Return top recommendations
        return sorted(
            scored_recommendations,
            key=lambda x: x['priority'],
            reverse=True
        )[:10]
    
    def _analyze_patterns(self, analytics_data: Dict) -> Dict:
        """Analyze user behavior patterns"""
        patterns = {
            'peak_hours': self._identify_peak_hours(analytics_data),
            'app_categories': self._categorize_app_usage(analytics_data),
            'focus_duration': self._analyze_focus_sessions(analytics_data),
            'break_frequency': self._analyze_break_patterns(analytics_data),
            'sleep_schedule': self._analyze_sleep_patterns(analytics_data),
            'notification_load': self._analyze_notifications(analytics_data),
            'distractions': self._identify_distractions(analytics_data),
            'productivity_score': analytics_data.get('productivity_score', 50),
            'wellbeing_score': analytics_data.get('wellbeing_score', 50),
        }
        return patterns
    
    def _identify_peak_hours(self, analytics_data: Dict) -> List[int]:
        """Identify hours when user is most productive"""
        hourly_usage = analytics_data.get('hourly_usage', {})
        if not hourly_usage:
            return [9, 10, 11, 14, 15, 16]  # Default office hours
        
        # Find hours with highest productivity (lowest distraction apps)
        productive_hours = []
        for hour, data in hourly_usage.items():
            if data.get('focus_score', 0) > 70:
                productive_hours.append(int(hour))
        
        return productive_hours or [9, 10, 11, 14, 15, 16]
    
    def _categorize_app_usage(self, analytics_data: Dict) -> Dict:
        """Categorize apps by type and usage"""
        app_usage = analytics_data.get('app_usage', [])
        categories = defaultdict(lambda: {'time': 0, 'opens': 0, 'apps': []})
        
        for app in app_usage:
            category = app.get('category', 'Other')
            categories[category]['time'] += app.get('usage_time', 0)
            categories[category]['opens'] += app.get('open_count', 0)
            categories[category]['apps'].append(app.get('app_name'))
        
        return dict(categories)
    
    def _analyze_focus_sessions(self, analytics_data: Dict) -> Dict:
        """Analyze focus session patterns"""
        focus_data = analytics_data.get('focus_sessions', [])
        
        if not focus_data:
            return {'avg_duration': 25, 'completion_rate': 0, 'best_time': 10}
        
        durations = [s.get('duration', 0) for s in focus_data]
        completed = [s for s in focus_data if s.get('completed', False)]
        
        return {
            'avg_duration': np.mean(durations) if durations else 25,
            'completion_rate': len(completed) / len(focus_data) * 100,
            'total_sessions': len(focus_data),
            'best_time': self._find_best_focus_time(focus_data),
        }
    
    def _analyze_break_patterns(self, analytics_data: Dict) -> Dict:
        """Analyze break patterns"""
        sessions = analytics_data.get('sessions', [])
        
        if len(sessions) < 2:
            return {'avg_interval': 60, 'recommended': 50}
        
        intervals = []
        for i in range(1, len(sessions)):
            interval = sessions[i]['start'] - sessions[i-1]['end']
            intervals.append(interval)
        
        avg_interval = np.mean(intervals) if intervals else 60
        
        return {
            'avg_interval': avg_interval,
            'recommended': 50 if avg_interval > 90 else 30,
            'needs_more_breaks': avg_interval > 120,
        }
    
    def _analyze_sleep_patterns(self, analytics_data: Dict) -> Dict:
        """Analyze sleep schedule"""
        sleep_data = analytics_data.get('sleep_schedule', {})
        
        return {
            'avg_bedtime': sleep_data.get('avg_bedtime', 23),
            'avg_wake_time': sleep_data.get('avg_wake_time', 7),
            'sleep_duration': sleep_data.get('avg_duration', 7),
            'consistency': sleep_data.get('consistency_score', 50),
            'late_night_usage': analytics_data.get('usage_after_11pm', 0),
        }
    
    def _analyze_notifications(self, analytics_data: Dict) -> Dict:
        """Analyze notification patterns"""
        notifications = analytics_data.get('notifications', [])
        
        total = len(notifications)
        urgent = len([n for n in notifications if n.get('priority') == 'URGENT'])
        dismissed = len([n for n in notifications if n.get('action') == 'dismissed'])
        
        return {
            'total_count': total,
            'urgent_count': urgent,
            'dismissal_rate': dismissed / total * 100 if total > 0 else 0,
            'avg_per_hour': total / 24 if total > 0 else 0,
            'overwhelming': total > 100,
        }
    
    def _identify_distractions(self, analytics_data: Dict) -> List[Dict]:
        """Identify top distraction sources"""
        app_usage = analytics_data.get('app_usage', [])
        
        # Filter for social media, games, entertainment
        distraction_categories = ['Social', 'Games', 'Entertainment', 'News']
        distractions = []
        
        for app in app_usage:
            if app.get('category') in distraction_categories:
                distractions.append({
                    'app': app.get('app_name'),
                    'category': app.get('category'),
                    'time': app.get('usage_time', 0),
                    'opens': app.get('open_count', 0),
                })
        
        return sorted(distractions, key=lambda x: x['time'], reverse=True)[:5]
    
    def _find_best_focus_time(self, focus_sessions: List[Dict]) -> int:
        """Find the hour when focus sessions are most successful"""
        hourly_success = defaultdict(list)
        
        for session in focus_sessions:
            if session.get('completed'):
                hour = datetime.fromisoformat(session['start_time']).hour
                hourly_success[hour].append(session.get('duration', 0))
        
        if not hourly_success:
            return 10  # Default to 10 AM
        
        # Return hour with most successful sessions
        best_hour = max(hourly_success.items(), key=lambda x: len(x[1]))[0]
        return best_hour
    
    # ==================== RECOMMENDATION GENERATORS ====================
    
    def _focus_recommendations(
        self,
        patterns: Dict,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Generate focus-related recommendations"""
        recommendations = []
        current_hour = context.get('hour', datetime.now().hour) if context else datetime.now().hour
        
        focus_data = patterns.get('focus_duration', {})
        
        # Low completion rate
        if focus_data.get('completion_rate', 0) < 50:
            recommendations.append({
                'type': 'focus_time',
                'title': 'Try Shorter Focus Sessions',
                'description': f"Your focus session completion rate is {focus_data.get('completion_rate', 0):.0f}%. Try 25-minute sessions instead.",
                'action': 'adjust_focus_duration',
                'action_data': {'duration': 25},
                'priority': 80,
                'category': 'productivity',
                'impact': 'high',
            })
        
        # Schedule focus during peak hours
        peak_hours = patterns.get('peak_hours', [])
        if current_hour in peak_hours:
            recommendations.append({
                'type': 'focus_time',
                'title': 'Perfect Time for Deep Work',
                'description': f"You're most productive around {current_hour}:00. Start a focus session now!",
                'action': 'start_focus_session',
                'action_data': {'duration': 50},
                'priority': 90,
                'category': 'productivity',
                'impact': 'high',
            })
        
        return recommendations
    
    def _break_recommendations(
        self,
        patterns: Dict,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Generate break-related recommendations"""
        recommendations = []
        
        break_data = patterns.get('break_frequency', {})
        
        if break_data.get('needs_more_breaks', False):
            recommendations.append({
                'type': 'break_time',
                'title': 'Take More Breaks',
                'description': f"You're working {break_data.get('avg_interval', 0):.0f} minutes between breaks. Try taking a 5-minute break every 50 minutes.",
                'action': 'schedule_breaks',
                'action_data': {'interval': 50, 'duration': 5},
                'priority': 75,
                'category': 'wellbeing',
                'impact': 'medium',
            })
        
        return recommendations
    
    def _app_usage_recommendations(self, patterns: Dict) -> List[Dict]:
        """Generate app usage recommendations"""
        recommendations = []
        
        distractions = patterns.get('distractions', [])
        
        if distractions:
            top_distraction = distractions[0]
            recommendations.append({
                'type': 'app_limit',
                'title': f"Limit {top_distraction['app']}",
                'description': f"You spent {top_distraction['time']:.0f} minutes on {top_distraction['app']} today. Set a daily limit?",
                'action': 'set_app_limit',
                'action_data': {
                    'app': top_distraction['app'],
                    'limit': int(top_distraction['time'] * 0.7)  # 30% reduction
                },
                'priority': 85,
                'category': 'productivity',
                'impact': 'high',
            })
        
        return recommendations
    
    def _sleep_recommendations(
        self,
        patterns: Dict,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Generate sleep-related recommendations"""
        recommendations = []
        current_hour = context.get('hour', datetime.now().hour) if context else datetime.now().hour
        
        sleep_data = patterns.get('sleep_schedule', {})
        
        # Late bedtime
        if sleep_data.get('avg_bedtime', 23) > 23:
            recommendations.append({
                'type': 'bedtime',
                'title': 'Earlier Bedtime Recommended',
                'description': f"Your average bedtime is {sleep_data['avg_bedtime']}:00. Try going to bed at 23:00 for better sleep quality.",
                'action': 'set_bedtime_reminder',
                'action_data': {'time': '23:00'},
                'priority': 70,
                'category': 'wellbeing',
                'impact': 'high',
            })
        
        # Late night usage
        if sleep_data.get('late_night_usage', 0) > 30:
            recommendations.append({
                'type': 'bedtime',
                'title': 'Reduce Late Night Screen Time',
                'description': f"You use your phone {sleep_data['late_night_usage']:.0f} minutes after 11 PM. Enable bedtime mode?",
                'action': 'enable_bedtime_mode',
                'action_data': {'start_time': '22:00', 'end_time': '07:00'},
                'priority': 75,
                'category': 'wellbeing',
                'impact': 'high',
            })
        
        # Morning reminder for late wakers
        if current_hour >= 7 and current_hour <= 9:
            if sleep_data.get('avg_wake_time', 7) > 8:
                recommendations.append({
                    'type': 'morning_routine',
                    'title': 'Start Your Day Earlier',
                    'description': "Early risers report higher productivity. Try waking up at 7:00.",
                    'action': 'set_wake_alarm',
                    'action_data': {'time': '07:00'},
                    'priority': 60,
                    'category': 'wellbeing',
                    'impact': 'medium',
                })
        
        return recommendations
    
    def _notification_recommendations(self, patterns: Dict) -> List[Dict]:
        """Generate notification management recommendations"""
        recommendations = []
        
        notif_data = patterns.get('notification_load', {})
        
        if notif_data.get('overwhelming', False):
            recommendations.append({
                'type': 'notification_control',
                'title': 'Too Many Notifications',
                'description': f"You received {notif_data['total_count']} notifications today. Mute non-urgent apps?",
                'action': 'review_notification_settings',
                'action_data': {},
                'priority': 80,
                'category': 'focus',
                'impact': 'high',
            })
        
        # High dismissal rate
        if notif_data.get('dismissal_rate', 0) > 70:
            recommendations.append({
                'type': 'notification_control',
                'title': 'Filter Unimportant Notifications',
                'description': f"You dismiss {notif_data['dismissal_rate']:.0f}% of notifications. Let our AI filter them?",
                'action': 'enable_smart_filtering',
                'action_data': {},
                'priority': 75,
                'category': 'focus',
                'impact': 'medium',
            })
        
        return recommendations
    
    def _privacy_recommendations(self, analytics_data: Dict) -> List[Dict]:
        """Generate privacy improvement recommendations"""
        recommendations = []
        
        privacy_score = analytics_data.get('privacy_score', {}).get('overall', 50)
        
        if privacy_score < 70:
            recommendations.append({
                'type': 'privacy_improvement',
                'title': 'Boost Your Privacy Score',
                'description': f"Your privacy score is {privacy_score}. Enable VPN and review app permissions?",
                'action': 'improve_privacy',
                'action_data': {},
                'priority': 85,
                'category': 'privacy',
                'impact': 'high',
            })
        
        # Check if VPN is off
        vpn_active = analytics_data.get('vpn_active', False)
        if not vpn_active:
            recommendations.append({
                'type': 'privacy_improvement',
                'title': 'Enable Privacy Shield',
                'description': "Activate VPN to block trackers and ads while browsing.",
                'action': 'enable_vpn',
                'action_data': {},
                'priority': 80,
                'category': 'privacy',
                'impact': 'high',
            })
        
        return recommendations
    
    def _wellbeing_recommendations(self, patterns: Dict) -> List[Dict]:
        """Generate overall wellbeing recommendations"""
        recommendations = []
        
        wellbeing_score = patterns.get('wellbeing_score', 50)
        
        if wellbeing_score < 60:
            recommendations.append({
                'type': 'wellbeing_boost',
                'title': 'Improve Your Wellbeing',
                'description': f"Your wellbeing score is {wellbeing_score}. Take regular breaks, limit screen time, and maintain a healthy sleep schedule.",
                'action': 'view_wellbeing_tips',
                'action_data': {},
                'priority': 70,
                'category': 'wellbeing',
                'impact': 'medium',
            })
        
        return recommendations
    
    def _score_recommendations(
        self,
        recommendations: List[Dict],
        patterns: Dict,
        context: Optional[Dict]
    ) -> List[Dict]:
        """Score and adjust recommendation priorities based on context"""
        for rec in recommendations:
            # Adjust priority based on current context
            if context:
                hour = context.get('hour', datetime.now().hour)
                
                # Boost focus recommendations during work hours
                if rec['type'] == 'focus_time' and 9 <= hour <= 17:
                    rec['priority'] += 10
                
                # Boost sleep recommendations in evening
                if rec['type'] == 'bedtime' and 21 <= hour <= 23:
                    rec['priority'] += 15
                
                # Boost break recommendations after long work
                if rec['type'] == 'break_time' and context.get('continuous_work_time', 0) > 90:
                    rec['priority'] += 20
            
            # Add metadata
            rec['id'] = hash(rec['title']) % 10000
            rec['generated_at'] = datetime.now().isoformat()
            rec['expires_at'] = (datetime.now() + timedelta(hours=6)).isoformat()
        
        return recommendations


# Singleton instance
recommendation_engine = RecommendationEngine()
