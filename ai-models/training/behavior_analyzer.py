"""
AI Model - User Behavior Analysis
Tracks and analyzes user behavior patterns for personalization
Provides insights into productivity, focus, and wellbeing trends
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os

class UserBehaviorAnalyzer:
    """Analyze user behavior patterns and trends"""
    
    def __init__(self, data_path='../data'):
        """Initialize the behavior analyzer"""
        self.data_path = data_path
        os.makedirs(data_path, exist_ok=True)
        
        # Initialize tracking data structures
        self.behavior_data = {
            'focus_sessions': [],
            'distractions': [],
            'notifications': [],
            'app_usage': defaultdict(int),
            'productivity_scores': [],
            'privacy_events': [],
            'breaks': [],
        }
    
    def track_focus_session(self, start_time, end_time, quality_score):
        """Track a focus session"""
        
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        session = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration_minutes,
            'quality_score': quality_score,
            'hour': start_time.hour,
            'day_of_week': start_time.weekday()
        }
        
        self.behavior_data['focus_sessions'].append(session)
        return session
    
    def track_distraction(self, timestamp, source, severity):
        """Track a distraction event"""
        
        distraction = {
            'timestamp': timestamp.isoformat(),
            'source': source,
            'severity': severity,  # 1-5
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        }
        
        self.behavior_data['distractions'].append(distraction)
        return distraction
    
    def track_notification(self, timestamp, app_name, priority_score, was_handled):
        """Track notification handling"""
        
        notification = {
            'timestamp': timestamp.isoformat(),
            'app_name': app_name,
            'priority_score': priority_score,
            'was_handled': was_handled,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday()
        }
        
        self.behavior_data['notifications'].append(notification)
        return notification
    
    def track_app_usage(self, app_name, duration_minutes, timestamp):
        """Track app usage time"""
        
        self.behavior_data['app_usage'][app_name] += duration_minutes
        
        return {
            'app_name': app_name,
            'duration_minutes': duration_minutes,
            'timestamp': timestamp.isoformat()
        }
    
    def analyze_focus_patterns(self, days=7):
        """Analyze focus patterns over time"""
        
        if not self.behavior_data['focus_sessions']:
            return self._generate_sample_focus_analysis()
        
        sessions = self.behavior_data['focus_sessions']
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(sessions)
        
        analysis = {
            'total_sessions': len(sessions),
            'total_focus_time': df['duration_minutes'].sum(),
            'avg_session_duration': df['duration_minutes'].mean(),
            'avg_quality_score': df['quality_score'].mean(),
            'best_hours': self._find_best_hours(df),
            'best_days': self._find_best_days(df),
            'focus_trend': self._calculate_trend(df['quality_score'].tolist()),
        }
        
        return analysis
    
    def _find_best_hours(self, df):
        """Find best hours for focus"""
        
        if df.empty:
            return []
        
        hourly_quality = df.groupby('hour')['quality_score'].agg(['mean', 'count'])
        hourly_quality = hourly_quality[hourly_quality['count'] >= 2]  # At least 2 sessions
        hourly_quality = hourly_quality.sort_values('mean', ascending=False)
        
        return [
            {'hour': hour, 'avg_quality': score}
            for hour, score in hourly_quality['mean'].head(3).items()
        ]
    
    def _find_best_days(self, df):
        """Find best days for focus"""
        
        if df.empty:
            return []
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_quality = df.groupby('day_of_week')['quality_score'].agg(['mean', 'count'])
        daily_quality = daily_quality.sort_values('mean', ascending=False)
        
        return [
            {'day': day_names[day], 'avg_quality': score}
            for day, score in daily_quality['mean'].head(3).items()
        ]
    
    def _calculate_trend(self, scores):
        """Calculate trend direction (improving/declining/stable)"""
        
        if len(scores) < 3:
            return 'insufficient_data'
        
        # Simple trend: compare first half to second half
        mid = len(scores) // 2
        first_half = np.mean(scores[:mid])
        second_half = np.mean(scores[mid:])
        
        diff = second_half - first_half
        
        if diff > 5:
            return 'improving'
        elif diff < -5:
            return 'declining'
        else:
            return 'stable'
    
    def analyze_distraction_patterns(self):
        """Analyze distraction patterns"""
        
        if not self.behavior_data['distractions']:
            return self._generate_sample_distraction_analysis()
        
        distractions = self.behavior_data['distractions']
        df = pd.DataFrame(distractions)
        
        # Find most common distraction sources
        source_counts = df['source'].value_counts()
        
        # Find worst hours for distractions
        hourly_distractions = df.groupby('hour').size().sort_values(ascending=False)
        
        analysis = {
            'total_distractions': len(distractions),
            'avg_severity': df['severity'].mean(),
            'top_sources': [
                {'source': source, 'count': count}
                for source, count in source_counts.head(5).items()
            ],
            'worst_hours': [
                {'hour': hour, 'count': count}
                for hour, count in hourly_distractions.head(3).items()
            ],
        }
        
        return analysis
    
    def analyze_notification_behavior(self):
        """Analyze notification handling behavior"""
        
        if not self.behavior_data['notifications']:
            return self._generate_sample_notification_analysis()
        
        notifications = self.behavior_data['notifications']
        df = pd.DataFrame(notifications)
        
        analysis = {
            'total_notifications': len(notifications),
            'handle_rate': df['was_handled'].mean(),
            'avg_priority': df['priority_score'].mean(),
            'top_apps': df['app_name'].value_counts().head(5).to_dict(),
            'peak_hours': df.groupby('hour').size().sort_values(ascending=False).head(3).to_dict(),
        }
        
        return analysis
    
    def generate_productivity_insights(self):
        """Generate comprehensive productivity insights"""
        
        focus_analysis = self.analyze_focus_patterns()
        distraction_analysis = self.analyze_distraction_patterns()
        notification_analysis = self.analyze_notification_behavior()
        
        # Calculate overall productivity score
        focus_score = min(100, focus_analysis['avg_quality_score'] if 'avg_quality_score' in focus_analysis else 70)
        distraction_penalty = min(30, distraction_analysis['total_distractions'] / 2)
        notification_bonus = notification_analysis['handle_rate'] * 10
        
        productivity_score = max(0, min(100, focus_score - distraction_penalty + notification_bonus))
        
        insights = {
            'productivity_score': productivity_score,
            'focus_insights': focus_analysis,
            'distraction_insights': distraction_analysis,
            'notification_insights': notification_analysis,
            'recommendations': self._generate_recommendations(
                focus_analysis,
                distraction_analysis,
                notification_analysis
            )
        }
        
        return insights
    
    def _generate_recommendations(self, focus_analysis, distraction_analysis, notification_analysis):
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Focus recommendations
        if 'best_hours' in focus_analysis and focus_analysis['best_hours']:
            best_hour = focus_analysis['best_hours'][0]['hour']
            recommendations.append({
                'category': 'focus',
                'priority': 'high',
                'text': f"Schedule important tasks around {best_hour}:00 - your peak focus time"
            })
        
        if focus_analysis.get('focus_trend') == 'declining':
            recommendations.append({
                'category': 'focus',
                'priority': 'medium',
                'text': "Your focus quality is declining. Try shorter, more frequent sessions."
            })
        
        # Distraction recommendations
        if distraction_analysis['total_distractions'] > 20:
            recommendations.append({
                'category': 'distraction',
                'priority': 'high',
                'text': "High distraction count. Enable Focus Mode during important work."
            })
        
        if distraction_analysis.get('top_sources'):
            top_source = distraction_analysis['top_sources'][0]['source']
            recommendations.append({
                'category': 'distraction',
                'priority': 'medium',
                'text': f"'{top_source}' is your main distraction. Consider blocking it during focus time."
            })
        
        # Notification recommendations
        if notification_analysis['handle_rate'] < 0.5:
            recommendations.append({
                'category': 'notification',
                'priority': 'medium',
                'text': "You're ignoring most notifications. Adjust filters to see only important ones."
            })
        
        return recommendations
    
    def _generate_sample_focus_analysis(self):
        """Generate sample focus analysis for demo"""
        return {
            'total_sessions': 12,
            'total_focus_time': 480,
            'avg_session_duration': 40,
            'avg_quality_score': 75,
            'best_hours': [
                {'hour': 10, 'avg_quality': 85},
                {'hour': 14, 'avg_quality': 80},
                {'hour': 16, 'avg_quality': 75}
            ],
            'best_days': [
                {'day': 'Tuesday', 'avg_quality': 82},
                {'day': 'Wednesday', 'avg_quality': 79},
                {'day': 'Thursday', 'avg_quality': 76}
            ],
            'focus_trend': 'improving'
        }
    
    def _generate_sample_distraction_analysis(self):
        """Generate sample distraction analysis for demo"""
        return {
            'total_distractions': 28,
            'avg_severity': 2.5,
            'top_sources': [
                {'source': 'Social Media', 'count': 10},
                {'source': 'Messages', 'count': 8},
                {'source': 'News Apps', 'count': 6},
                {'source': 'Email', 'count': 4}
            ],
            'worst_hours': [
                {'hour': 15, 'count': 6},
                {'hour': 11, 'count': 5},
                {'hour': 14, 'count': 4}
            ]
        }
    
    def _generate_sample_notification_analysis(self):
        """Generate sample notification analysis for demo"""
        return {
            'total_notifications': 45,
            'handle_rate': 0.65,
            'avg_priority': 55,
            'top_apps': {
                'WhatsApp': 12,
                'Email': 10,
                'Slack': 8,
                'Instagram': 7,
                'Twitter': 5
            },
            'peak_hours': {
                14: 8,
                11: 7,
                16: 6
            }
        }
    
    def export_behavior_report(self, output_file='behavior_report.json'):
        """Export comprehensive behavior report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'productivity_insights': self.generate_productivity_insights(),
            'raw_data_summary': {
                'focus_sessions_count': len(self.behavior_data['focus_sessions']),
                'distractions_count': len(self.behavior_data['distractions']),
                'notifications_count': len(self.behavior_data['notifications']),
                'apps_tracked': len(self.behavior_data['app_usage'])
            }
        }
        
        filepath = os.path.join(self.data_path, output_file)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Behavior report exported to: {filepath}")
        return report


def demo_behavior_analyzer():
    """Demo the behavior analyzer"""
    
    analyzer = UserBehaviorAnalyzer()
    
    print("🤖 User Behavior Analyzer Demo")
    print("=" * 80)
    
    # Simulate some behavior data
    now = datetime.now()
    
    # Track focus sessions
    print("\n📊 Tracking Focus Sessions...")
    for i in range(5):
        start = now - timedelta(hours=i*2)
        end = start + timedelta(minutes=np.random.randint(25, 60))
        quality = np.random.randint(60, 95)
        analyzer.track_focus_session(start, end, quality)
    
    # Track distractions
    print("📊 Tracking Distractions...")
    sources = ['Social Media', 'Messages', 'News Apps', 'Email']
    for i in range(15):
        timestamp = now - timedelta(hours=np.random.randint(0, 24))
        source = np.random.choice(sources)
        severity = np.random.randint(1, 6)
        analyzer.track_distraction(timestamp, source, severity)
    
    # Track notifications
    print("📊 Tracking Notifications...")
    apps = ['WhatsApp', 'Email', 'Slack', 'Instagram', 'Twitter']
    for i in range(20):
        timestamp = now - timedelta(hours=np.random.randint(0, 24))
        app = np.random.choice(apps)
        priority = np.random.randint(30, 90)
        handled = np.random.random() > 0.3
        analyzer.track_notification(timestamp, app, priority, handled)
    
    # Generate insights
    print("\n📈 Generating Productivity Insights...")
    print("=" * 80)
    
    insights = analyzer.generate_productivity_insights()
    
    print(f"\n🎯 Overall Productivity Score: {insights['productivity_score']:.0f}/100")
    
    print("\n⏰ Best Focus Hours:")
    for hour_data in insights['focus_insights']['best_hours']:
        print(f"   • {hour_data['hour']:02d}:00 - Quality: {hour_data['avg_quality']:.1f}")
    
    print("\n📅 Best Focus Days:")
    for day_data in insights['focus_insights']['best_days']:
        print(f"   • {day_data['day']} - Quality: {day_data['avg_quality']:.1f}")
    
    print(f"\n📊 Focus Trend: {insights['focus_insights']['focus_trend'].upper()}")
    
    print(f"\n⚠️ Total Distractions: {insights['distraction_insights']['total_distractions']}")
    print("   Top Sources:")
    for source_data in insights['distraction_insights']['top_sources']:
        print(f"   • {source_data['source']}: {source_data['count']} times")
    
    print(f"\n🔔 Notification Handle Rate: {insights['notification_insights']['handle_rate']:.1%}")
    print("   Top Apps:")
    for app, count in list(insights['notification_insights']['top_apps'].items())[:5]:
        print(f"   • {app}: {count} notifications")
    
    print("\n💡 Recommendations:")
    for rec in insights['recommendations']:
        priority_emoji = '🔴' if rec['priority'] == 'high' else '🟡'
        print(f"   {priority_emoji} [{rec['category'].upper()}] {rec['text']}")
    
    # Export report
    print("\n" + "=" * 80)
    report = analyzer.export_behavior_report()
    
    print("\n✅ Behavior Analyzer Demo Complete!")


if __name__ == "__main__":
    demo_behavior_analyzer()
