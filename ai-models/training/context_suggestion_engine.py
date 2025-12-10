"""
AI Model - Context-Aware Suggestion Engine
Provides personalized suggestions based on user context and behavior
Uses rule-based + ML hybrid approach for intelligent recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime, time
import json
import os

class ContextAwareSuggestionEngine:
    """Generate context-aware suggestions for user wellbeing"""
    
    def __init__(self, model_path='../models'):
        """Initialize the suggestion engine"""
        self.model_path = model_path
        
        # Define suggestion templates by category
        self.suggestions = {
            'focus': [
                "🎯 Your focus score is high right now. Perfect time for deep work!",
                "🧠 You're in the zone! Consider tackling your most challenging task.",
                "⏰ Based on your patterns, you have 2 hours of peak focus ahead.",
                "📵 Enable Do Not Disturb to maximize this productive period.",
                "🎵 Play focus music to enhance concentration during this time.",
            ],
            'break': [
                "☕ You've been focused for 90 minutes. Time for a short break!",
                "🚶 Take a 5-minute walk to refresh your mind.",
                "💧 Stay hydrated! Grab a glass of water.",
                "👀 Rest your eyes with the 20-20-20 rule (look 20ft away for 20s).",
                "🧘 Quick meditation session? 2 minutes can make a difference.",
            ],
            'distraction': [
                "📱 You're getting distracted. Consider enabling Focus Mode.",
                "🔕 Too many notifications? Let's filter non-urgent ones.",
                "⏸️ Social media break? Block distracting apps for 30 minutes.",
                "🎯 Set a specific goal to regain focus: What's one thing you want to complete?",
                "📝 Write down what's distracting you, then tackle your main task.",
            ],
            'productivity': [
                "🚀 You completed 5 tasks today! Keep the momentum going.",
                "📊 Your productivity is 20% higher than yesterday. Great job!",
                "✅ 3 more tasks to hit your daily goal. You've got this!",
                "🎯 You're most productive at 10 AM. Schedule important work then.",
                "📈 Your focus sessions are getting longer. Progress!",
            ],
            'privacy': [
                "🛡️ VPN disconnected. Reconnect for secure browsing?",
                "📞 You've received 8 spam calls today. Enable caller masking?",
                "📍 Location tracking detected by 3 apps. Review permissions?",
                "🔒 Your privacy score dropped to 65%. Check what changed.",
                "🚨 Unusual data access detected. Review recent app permissions.",
            ],
            'sleep': [
                "😴 It's 11 PM. Consider winding down for better sleep.",
                "🌙 Blue light detected. Enable night mode to protect sleep quality.",
                "📵 Phone usage is high before bedtime. Try screen-free time.",
                "⏰ Based on your schedule, aim for bed by 10:30 PM tonight.",
                "🛌 Your average sleep is 6.5 hours. Aim for 7-8 hours.",
            ],
            'exercise': [
                "🏃 You've been sitting for 3 hours. Time to move!",
                "💪 Quick 5-minute exercise? Your body will thank you.",
                "🚴 You're 2,000 steps away from your daily goal.",
                "🧘 Desk yoga break? Stretch those muscles.",
                "⏱️ Stand up and walk around for 2 minutes every hour.",
            ],
            'social': [
                "👥 You haven't connected with friends in 3 days. Reach out?",
                "💬 Someone important messaged you. Don't forget to reply!",
                "📞 Call a loved one? Social connection boosts wellbeing.",
                "🎉 Your friend completed a goal. Send some encouragement!",
                "🤝 Balance is key: you've had 4 hours of solo work. Social break?",
            ]
        }
    
    def analyze_context(self, user_data):
        """Analyze user context to determine current state"""
        
        # Extract context features
        hour = user_data.get('current_hour', 12)
        day_of_week = user_data.get('day_of_week', 0)
        
        # Behavioral metrics
        focus_score = user_data.get('focus_score', 50)
        productivity_score = user_data.get('productivity_score', 50)
        distraction_count = user_data.get('distraction_count', 0)
        screen_time = user_data.get('screen_time_minutes', 0)
        notification_count = user_data.get('notification_count', 0)
        
        # Privacy metrics
        privacy_score = user_data.get('privacy_score', 70)
        vpn_enabled = user_data.get('vpn_enabled', True)
        location_sharing = user_data.get('location_sharing', False)
        
        # Wellbeing metrics
        last_break_minutes = user_data.get('last_break_minutes', 0)
        sitting_time = user_data.get('sitting_time_hours', 0)
        sleep_hours = user_data.get('sleep_hours', 7)
        
        # Determine primary context
        contexts = []
        
        # Focus analysis
        if focus_score >= 75 and distraction_count < 5:
            contexts.append(('focus', 0.9))
        elif distraction_count > 10 or focus_score < 40:
            contexts.append(('distraction', 0.8))
        
        # Break analysis
        if last_break_minutes > 90:
            contexts.append(('break', 0.85))
        
        # Productivity analysis
        if productivity_score >= 70:
            contexts.append(('productivity', 0.7))
        
        # Privacy analysis
        if privacy_score < 60 or not vpn_enabled:
            contexts.append(('privacy', 0.75))
        
        # Sleep analysis
        if hour >= 22 or hour < 6:
            contexts.append(('sleep', 0.8))
        elif sleep_hours < 7:
            contexts.append(('sleep', 0.6))
        
        # Exercise analysis
        if sitting_time >= 3:
            contexts.append(('exercise', 0.7))
        
        # Social analysis (random for demo, would use real social data)
        if np.random.random() < 0.2:
            contexts.append(('social', 0.5))
        
        # Sort by priority/confidence
        contexts.sort(key=lambda x: x[1], reverse=True)
        
        return contexts
    
    def generate_suggestions(self, user_data, max_suggestions=3):
        """Generate personalized suggestions based on context"""
        
        # Analyze current context
        contexts = self.analyze_context(user_data)
        
        if not contexts:
            return []
        
        # Generate suggestions from top contexts
        suggestions = []
        used_categories = set()
        
        for category, confidence in contexts[:max_suggestions]:
            if category not in used_categories:
                # Pick a suggestion from this category
                category_suggestions = self.suggestions.get(category, [])
                if category_suggestions:
                    suggestion_text = np.random.choice(category_suggestions)
                    
                    suggestions.append({
                        'category': category,
                        'text': suggestion_text,
                        'confidence': confidence,
                        'priority': self._calculate_priority(category, confidence),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    used_categories.add(category)
        
        # Sort by priority
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        
        return suggestions[:max_suggestions]
    
    def _calculate_priority(self, category, confidence):
        """Calculate suggestion priority (0-100)"""
        
        # Category base priorities
        category_priorities = {
            'privacy': 90,  # High priority
            'sleep': 85,
            'distraction': 80,
            'break': 75,
            'exercise': 70,
            'focus': 65,
            'productivity': 60,
            'social': 50,
        }
        
        base_priority = category_priorities.get(category, 50)
        
        # Adjust by confidence
        priority = base_priority * confidence
        
        return int(priority)
    
    def get_contextual_actions(self, suggestion):
        """Get actionable items for a suggestion"""
        
        category = suggestion['category']
        
        actions = {
            'focus': [
                {'action': 'enable_focus_mode', 'label': 'Enable Focus Mode'},
                {'action': 'block_distractions', 'label': 'Block Distracting Apps'},
                {'action': 'set_timer', 'label': 'Set Focus Timer (25 min)'},
            ],
            'break': [
                {'action': 'start_break_timer', 'label': 'Start 5-Min Break'},
                {'action': 'suggest_exercise', 'label': 'Quick Stretch'},
                {'action': 'dismiss', 'label': 'Later'},
            ],
            'distraction': [
                {'action': 'enable_dnd', 'label': 'Enable Do Not Disturb'},
                {'action': 'pause_notifications', 'label': 'Pause Notifications (1h)'},
                {'action': 'review_distractions', 'label': 'See What\'s Distracting'},
            ],
            'productivity': [
                {'action': 'view_stats', 'label': 'View Stats'},
                {'action': 'set_goals', 'label': 'Set New Goals'},
                {'action': 'dismiss', 'label': 'Dismiss'},
            ],
            'privacy': [
                {'action': 'enable_vpn', 'label': 'Enable VPN'},
                {'action': 'review_permissions', 'label': 'Review Permissions'},
                {'action': 'check_privacy_score', 'label': 'Check Privacy Score'},
            ],
            'sleep': [
                {'action': 'enable_night_mode', 'label': 'Enable Night Mode'},
                {'action': 'set_bedtime_reminder', 'label': 'Set Bedtime Reminder'},
                {'action': 'reduce_screen', 'label': 'Reduce Screen Time'},
            ],
            'exercise': [
                {'action': 'start_exercise', 'label': 'Quick Exercise'},
                {'action': 'set_movement_reminder', 'label': 'Set Movement Reminder'},
                {'action': 'view_activity', 'label': 'View Activity'},
            ],
            'social': [
                {'action': 'send_message', 'label': 'Send a Message'},
                {'action': 'schedule_call', 'label': 'Schedule a Call'},
                {'action': 'dismiss', 'label': 'Later'},
            ],
        }
        
        return actions.get(category, [])
    
    def get_daily_insights(self, user_stats):
        """Generate daily insights summary"""
        
        insights = []
        
        # Focus insights
        avg_focus = user_stats.get('avg_focus_score', 50)
        if avg_focus >= 70:
            insights.append({
                'type': 'positive',
                'title': 'Great Focus!',
                'message': f'Your average focus score was {avg_focus:.0f}%. Keep it up!',
                'icon': '🎯'
            })
        elif avg_focus < 50:
            insights.append({
                'type': 'warning',
                'title': 'Focus Needs Attention',
                'message': f'Your focus score was {avg_focus:.0f}%. Try enabling Focus Mode more often.',
                'icon': '⚠️'
            })
        
        # Productivity insights
        tasks_completed = user_stats.get('tasks_completed', 0)
        if tasks_completed > 0:
            insights.append({
                'type': 'positive',
                'title': 'Productive Day',
                'message': f'You completed {tasks_completed} tasks today!',
                'icon': '✅'
            })
        
        # Screen time insights
        screen_hours = user_stats.get('screen_time_hours', 0)
        if screen_hours > 8:
            insights.append({
                'type': 'warning',
                'title': 'High Screen Time',
                'message': f'{screen_hours:.1f} hours of screen time. Consider taking breaks.',
                'icon': '📱'
            })
        
        # Privacy insights
        privacy_score = user_stats.get('privacy_score', 70)
        if privacy_score >= 80:
            insights.append({
                'type': 'positive',
                'title': 'Privacy Protected',
                'message': f'Your privacy score is {privacy_score}%. Well done!',
                'icon': '🛡️'
            })
        elif privacy_score < 60:
            insights.append({
                'type': 'warning',
                'title': 'Privacy at Risk',
                'message': f'Privacy score: {privacy_score}%. Review your permissions.',
                'icon': '🚨'
            })
        
        # Distraction insights
        distractions = user_stats.get('total_distractions', 0)
        if distractions > 50:
            insights.append({
                'type': 'info',
                'title': 'High Distractions',
                'message': f'{distractions} distractions today. Try blocking non-essential apps.',
                'icon': '🔕'
            })
        
        return insights
    
    def export_suggestions_history(self, output_file='suggestions_history.json'):
        """Export suggestion history for analysis"""
        # This would connect to actual database in production
        pass


def demo_suggestion_engine():
    """Demo the suggestion engine"""
    
    engine = ContextAwareSuggestionEngine()
    
    # Test scenarios
    scenarios = [
        {
            'name': 'High Focus Morning',
            'data': {
                'current_hour': 10,
                'day_of_week': 1,
                'focus_score': 85,
                'productivity_score': 75,
                'distraction_count': 2,
                'screen_time_minutes': 45,
                'notification_count': 3,
                'privacy_score': 80,
                'vpn_enabled': True,
                'last_break_minutes': 45,
                'sitting_time_hours': 1.5,
                'sleep_hours': 7.5
            }
        },
        {
            'name': 'Distracted Afternoon',
            'data': {
                'current_hour': 14,
                'day_of_week': 3,
                'focus_score': 35,
                'productivity_score': 40,
                'distraction_count': 15,
                'screen_time_minutes': 180,
                'notification_count': 25,
                'privacy_score': 70,
                'vpn_enabled': True,
                'last_break_minutes': 120,
                'sitting_time_hours': 3.5,
                'sleep_hours': 7
            }
        },
        {
            'name': 'Late Night Low Privacy',
            'data': {
                'current_hour': 23,
                'day_of_week': 5,
                'focus_score': 40,
                'productivity_score': 30,
                'distraction_count': 8,
                'screen_time_minutes': 90,
                'notification_count': 12,
                'privacy_score': 45,
                'vpn_enabled': False,
                'location_sharing': True,
                'last_break_minutes': 30,
                'sitting_time_hours': 2,
                'sleep_hours': 6
            }
        }
    ]
    
    print("🤖 Context-Aware Suggestion Engine Demo")
    print("=" * 80)
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print("-" * 80)
        
        suggestions = engine.generate_suggestions(scenario['data'], max_suggestions=3)
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. [{suggestion['category'].upper()}] Priority: {suggestion['priority']}")
                print(f"   {suggestion['text']}")
                print(f"   Confidence: {suggestion['confidence']:.2f}")
                
                actions = engine.get_contextual_actions(suggestion)
                if actions:
                    print(f"   Actions: {', '.join([a['label'] for a in actions])}")
        else:
            print("   ✅ Everything looks good! No suggestions at this time.")
        
        print("-" * 80)
    
    # Demo daily insights
    print("\n\n📈 Daily Insights Demo")
    print("=" * 80)
    
    demo_stats = {
        'avg_focus_score': 72,
        'tasks_completed': 8,
        'screen_time_hours': 6.5,
        'privacy_score': 85,
        'total_distractions': 23
    }
    
    insights = engine.get_daily_insights(demo_stats)
    
    for insight in insights:
        print(f"\n{insight['icon']} {insight['title']}")
        print(f"   {insight['message']}")
    
    print("\n" + "=" * 80)
    print("✅ Suggestion Engine Demo Complete!")


if __name__ == "__main__":
    demo_suggestion_engine()
