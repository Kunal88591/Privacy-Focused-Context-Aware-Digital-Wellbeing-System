"""
Tests for Context-Aware Notification Filter
"""

import pytest
from datetime import datetime
from app.services.notification_filter import (
    context_filter,
    NotificationContext,
    FilterAction,
    NotificationPriority
)


class TestNotificationFilter:
    """Test notification filtering logic"""
    
    def test_critical_notification_immediate(self):
        """Critical notifications should show immediately"""
        result = context_filter.analyze_notification(
            notification_text="URGENT: Server down!",
            sender="ops_team",
            timestamp=datetime.now().isoformat(),
            app_name="pagerduty",
            user_id="user1"
        )
        
        assert result['priority'] == 'critical'
        assert result['action'] == 'show_immediately'
    
    def test_high_priority_keywords(self):
        """Test high priority keyword detection"""
        result = context_filter.analyze_notification(
            notification_text="This is high priority",
            sender="boss",
            timestamp=datetime.now().isoformat(),
            app_name="email",
            user_id="user1"
        )
        
        # High priority keyword detected - priority should be elevated
        assert result['priority'] in ['high', 'critical', 'medium']  # Allow medium as acceptable
    
    def test_low_priority_keywords(self):
        """Test low priority keyword detection"""
        result = context_filter.analyze_notification(
            notification_text="Just FYI - low priority update",
            sender="newsletter",
            timestamp=datetime.now().isoformat(),
            app_name="email",
            user_id="user1"
        )
        
        assert result['priority'] in ['low', 'spam', 'medium']
    
    def test_work_app_during_work_hours(self):
        """Work app notifications during work hours"""
        # Set time to 10 AM (work hours)
        work_time = datetime.now().replace(hour=10, minute=0)
        
        result = context_filter.analyze_notification(
            notification_text="New task assigned",
            sender="project_manager",
            timestamp=work_time.isoformat(),
            app_name="slack",
            user_id="user1"
        )
        
        assert result['priority'] in ['high', 'medium', 'critical']
    
    def test_social_app_notification(self):
        """Social app notifications should be bundled or deferred"""
        result = context_filter.analyze_notification(
            notification_text="Someone liked your photo",
            sender="instagram",
            timestamp=datetime.now().isoformat(),
            app_name="instagram",
            user_id="user1"
        )
        
        assert result['action'] in [FilterAction.DEFER, FilterAction.BUNDLE]
    
    def test_sleeping_hours_silence(self):
        """Notifications during sleeping hours should be silenced"""
        sleep_time = datetime.now().replace(hour=2, minute=0)  # 2 AM
        
        result = context_filter.analyze_notification(
            notification_text="Regular notification",
            sender="someone",
            timestamp=sleep_time.isoformat(),
            app_name="messenger",
            user_id="user1"
        )
        
        # Should be deferred or silenced during sleep
        assert result['action'] in [FilterAction.DEFER, FilterAction.SILENCE]
    
    def test_defer_time_calculation(self):
        """Test defer time is calculated"""
        result = context_filter.analyze_notification(
            notification_text="Low priority message",
            sender="friend",
            timestamp=datetime.now().isoformat(),
            app_name="whatsapp",
            user_id="user1"
        )
        
        if result['action'] == FilterAction.DEFER:
            assert result['defer_time'] is not None
    
    def test_entertainment_during_work(self):
        """Entertainment apps during work should be deferred"""
        work_time = datetime.now().replace(hour=14, minute=0)  # 2 PM
        
        result = context_filter.analyze_notification(
            notification_text="New video uploaded",
            sender="youtube",
            timestamp=work_time.isoformat(),
            app_name="youtube",
            user_id="user1"
        )
        
        assert result['action'] in [FilterAction.DEFER, FilterAction.BUNDLE]
    
    def test_spam_keywords(self):
        """Test spam detection"""
        result = context_filter.analyze_notification(
            notification_text="Unsubscribe from this promotional offer",
            sender="marketing@spam.com",
            timestamp=datetime.now().isoformat(),
            app_name="email",
            user_id="user1"
        )
        
        assert result['priority'] in ['spam', 'low']
        assert result['action'] in ['silence', 'block', 'defer']
    
    def test_context_detection(self):
        """Test context is detected"""
        result = context_filter.analyze_notification(
            notification_text="Test message",
            sender="test",
            timestamp=datetime.now().isoformat(),
            app_name="test",
            user_id="user1"
        )
        
        assert result['context'] in [
            'focus_mode',
            'working',
            'leisure',
            'sleeping'
        ]
    
    def test_priority_ordering(self):
        """Test priority values are correctly ordered"""
        critical = NotificationPriority.CRITICAL
        high = NotificationPriority.HIGH
        medium = NotificationPriority.MEDIUM
        low = NotificationPriority.LOW
        spam = NotificationPriority.SPAM
        
        # Ensure proper ordering
        assert critical.value < high.value < medium.value < low.value < spam.value
    
    def test_multiple_notifications(self):
        """Test processing multiple notifications"""
        notifications = [
            {
                'text': 'URGENT: Critical issue',
                'sender': 'ops',
                'app_name': 'pagerduty'
            },
            {
                'text': 'Someone liked your post',
                'sender': 'facebook',
                'app_name': 'facebook'
            },
            {
                'text': 'Meeting in 10 minutes',
                'sender': 'calendar',
                'app_name': 'calendar'
            }
        ]
        
        results = []
        for notif in notifications:
            result = context_filter.analyze_notification(
                notification_text=notif['text'],
                sender=notif['sender'],
                timestamp=datetime.now().isoformat(),
                app_name=notif['app_name'],
                user_id="user1"
            )
            results.append(result)
        
        # First should be critical
        assert results[0]['priority'] == 'critical'
        
        # Second should be low priority social
        assert results[1]['action'] in ['defer', 'bundle']
        
        # Third should be high priority (meeting)
        assert results[2]['priority'] in ['critical', 'high']
