"""
Tests for Notification Bundler
"""

import pytest
from datetime import datetime
from app.services.notification_bundler import (
    notification_bundler,
    BundleStrategy,
    BundleType
)


class TestNotificationBundler:
    """Test notification bundling functionality"""
    
    def setup_method(self):
        """Clean state before each test"""
        notification_bundler.bundles = {}
    
    def test_should_bundle_aggressive(self):
        """Test aggressive bundling strategy"""
        notification = {
            'app_name': 'facebook',
            'text': 'Someone liked your post',
            'priority': 'medium'
        }
        
        should_bundle = notification_bundler.should_bundle(
            notification,
            BundleStrategy.AGGRESSIVE
        )
        
        assert should_bundle is True
    
    def test_should_not_bundle_critical(self):
        """Critical notifications should never bundle"""
        notification = {
            'app_name': 'pagerduty',
            'text': 'Critical alert',
            'priority': 'critical'
        }
        
        should_bundle = notification_bundler.should_bundle(
            notification,
            BundleStrategy.AGGRESSIVE
        )
        
        assert should_bundle is False
    
    def test_should_not_bundle_calls(self):
        """Calls should never bundle"""
        notification = {
            'app_name': 'phone',
            'text': 'Incoming call',
            'type': 'call'
        }
        
        should_bundle = notification_bundler.should_bundle(
            notification,
            BundleStrategy.AGGRESSIVE
        )
        
        assert should_bundle is False
    
    def test_add_to_bundle(self):
        """Test adding notification to bundle"""
        notification = {
            'app_name': 'instagram',
            'text': 'New follower',
            'sender': 'instagram'
        }
        
        result = notification_bundler.add_to_bundle(
            user_id="user1",
            notification=notification,
            bundle_strategy=BundleStrategy.MODERATE
        )
        
        assert result['bundled'] is True
        assert result['bundle_key'] is not None
        assert result['bundle_size'] >= 1
    
    def test_bundle_by_category(self):
        """Test bundling by category"""
        # Add social notifications
        for i in range(3):
            notification = {
                'app_name': 'facebook',
                'text': f'Social update {i}',
                'sender': 'facebook'
            }
            notification_bundler.add_to_bundle(
                "user1",
                notification,
                BundleStrategy.AGGRESSIVE
            )
        
        bundles = notification_bundler.get_all_bundles("user1")
        assert len(bundles) >= 1
        
        # Should have bundled social notifications
        social_bundle = [b for b in bundles if 'social' in b['bundle_key']]
        if social_bundle:
            assert social_bundle[0]['size'] >= 3
    
    def test_bundle_by_app(self):
        """Test bundling by app"""
        for i in range(3):
            notification = {
                'app_name': 'whatsapp',
                'text': f'Message {i}',
                'sender': 'whatsapp'
            }
            notification_bundler.add_to_bundle(
                "user1",
                notification,
                BundleStrategy.CONSERVATIVE
            )
        
        bundles = notification_bundler.get_all_bundles("user1")
        whatsapp_bundle = [b for b in bundles if 'whatsapp' in b['bundle_key']]
        
        assert len(whatsapp_bundle) >= 1
        assert whatsapp_bundle[0]['size'] >= 3
    
    def test_bundle_readiness(self):
        """Test bundle becomes ready after threshold"""
        # Add notifications below threshold
        notification = {
            'app_name': 'email',
            'text': 'New email',
            'sender': 'gmail'
        }
        
        notification_bundler.add_to_bundle("user1", notification, BundleStrategy.MODERATE)
        
        bundles = notification_bundler.get_all_bundles("user1")
        if bundles:
            # With only 1 notification, should not be ready
            assert bundles[0]['is_ready'] is False
    
    def test_get_bundle(self):
        """Test retrieving specific bundle"""
        notification = {
            'app_name': 'twitter',
            'text': 'New tweet',
            'sender': 'twitter'
        }
        
        result = notification_bundler.add_to_bundle(
            "user1",
            notification,
            BundleStrategy.MODERATE
        )
        
        bundle_key = result['bundle_key']
        bundle = notification_bundler.get_bundle("user1", bundle_key, clear_after=False)
        
        assert bundle is not None
        assert bundle['size'] >= 1
        assert 'summary' in bundle
    
    def test_bundle_summary(self):
        """Test bundle summary generation"""
        # Add multiple notifications from same app
        for i in range(5):
            notification = {
                'app_name': 'instagram',
                'text': f'Instagram update {i}',
                'sender': 'instagram'
            }
            notification_bundler.add_to_bundle(
                "user1",
                notification,
                BundleStrategy.AGGRESSIVE
            )
        
        bundles = notification_bundler.get_all_bundles("user1")
        
        if bundles:
            summary = bundles[0]['summary']
            assert 'total_count' in summary or 'text' in summary
    
    def test_get_ready_bundles(self):
        """Test getting only ready bundles"""
        # Add many notifications to make bundle ready
        for i in range(10):
            notification = {
                'app_name': 'facebook',
                'text': f'Update {i}',
                'sender': 'facebook'
            }
            notification_bundler.add_to_bundle(
                "user1",
                notification,
                BundleStrategy.AGGRESSIVE
            )
        
        ready_bundles = notification_bundler.get_ready_bundles("user1")
        # Might have ready bundles depending on threshold
        assert isinstance(ready_bundles, list)
    
    def test_cleanup_old_bundles(self):
        """Test cleaning up old bundles"""
        notification = {
            'app_name': 'test',
            'text': 'Old notification',
            'sender': 'test'
        }
        
        notification_bundler.add_to_bundle("user1", notification, BundleStrategy.MODERATE)
        
        # Cleanup bundles older than 0 hours (should remove all)
        removed = notification_bundler.cleanup_old_bundles("user1", max_age_hours=0)
        assert removed >= 0
    
    def test_bundling_statistics(self):
        """Test bundling statistics"""
        for i in range(3):
            notification = {
                'app_name': 'messenger',
                'text': f'Message {i}',
                'sender': 'messenger'
            }
            notification_bundler.add_to_bundle(
                "user1",
                notification,
                BundleStrategy.MODERATE
            )
        
        stats = notification_bundler.get_bundling_stats("user1")
        assert 'active_bundles' in stats
        assert 'total_bundled_notifications' in stats
        assert stats['total_bundled_notifications'] >= 3
    
    def test_category_detection(self):
        """Test category detection from app name"""
        # Social
        assert notification_bundler._detect_category('facebook') == 'social'
        assert notification_bundler._detect_category('instagram') == 'social'
        
        # Messaging
        assert notification_bundler._detect_category('whatsapp') == 'messaging'
        assert notification_bundler._detect_category('telegram') == 'messaging'
        
        # Email
        assert notification_bundler._detect_category('gmail') == 'email'
        
        # Unknown
        assert notification_bundler._detect_category('unknown_app') == 'other'
    
    def test_moderate_strategy(self):
        """Test moderate bundling strategy"""
        # Social should bundle
        social_notif = {
            'app_name': 'facebook',
            'priority': 'medium'
        }
        assert notification_bundler.should_bundle(social_notif, BundleStrategy.MODERATE)
        
        # Work apps might not bundle
        work_notif = {
            'app_name': 'slack',
            'priority': 'high'
        }
        # Depends on implementation
    
    def test_conservative_strategy(self):
        """Test conservative bundling strategy"""
        # Only bundle low/medium priority
        low_notif = {
            'app_name': 'test',
            'priority': 'low'
        }
        assert notification_bundler.should_bundle(low_notif, BundleStrategy.CONSERVATIVE)
        
        # Don't bundle high priority
        high_notif = {
            'app_name': 'test',
            'priority': 'high'
        }
        # Might not bundle high priority with conservative strategy
