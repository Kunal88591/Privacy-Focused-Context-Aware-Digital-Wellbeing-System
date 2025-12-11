"""
Notification Bundling Service
Groups similar notifications into digestible bundles
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum
import re


class BundleType(str, Enum):
    """Types of notification bundles"""
    APP_BASED = "app_based"
    CATEGORY_BASED = "category_based"
    SENDER_BASED = "sender_based"
    TIME_BASED = "time_based"
    TOPIC_BASED = "topic_based"


class BundleStrategy(str, Enum):
    """How to create bundles"""
    AGGRESSIVE = "aggressive"  # Bundle everything possible
    MODERATE = "moderate"      # Bundle similar notifications
    CONSERVATIVE = "conservative"  # Only bundle obvious duplicates


class NotificationBundler:
    """Bundle notifications intelligently to reduce interruptions"""
    
    def __init__(self):
        # Storage for active bundles
        self.bundles = defaultdict(lambda: defaultdict(list))
        
        # Bundle thresholds
        self.min_bundle_size = 2
        self.max_bundle_age_minutes = 60
        
        # Category patterns
        self.category_patterns = {
            'social': ['facebook', 'instagram', 'twitter', 'snapchat', 'tiktok'],
            'messaging': ['whatsapp', 'telegram', 'messenger', 'discord', 'signal'],
            'email': ['gmail', 'outlook', 'mail', 'yahoo', 'proton'],
            'news': ['news', 'rss', 'feed', 'article'],
            'shopping': ['amazon', 'ebay', 'shop', 'cart', 'order'],
            'entertainment': ['youtube', 'netflix', 'spotify', 'twitch'],
            'productivity': ['slack', 'teams', 'asana', 'trello', 'jira'],
        }
    
    def add_to_bundle(
        self,
        user_id: str,
        notification: Dict,
        bundle_strategy: BundleStrategy = BundleStrategy.MODERATE
    ) -> Dict:
        """
        Add notification to appropriate bundle
        
        Args:
            user_id: User identifier
            notification: Notification data
            bundle_strategy: Bundling strategy
            
        Returns:
            Dict with bundle info and status
        """
        # Determine bundle type and key
        bundle_info = self._determine_bundle(notification, bundle_strategy)
        bundle_type = bundle_info['type']
        bundle_key = bundle_info['key']
        
        # Add to bundle
        bundle_item = {
            'notification': notification,
            'added_at': datetime.now().isoformat(),
            'app': notification.get('app_name', 'unknown'),
            'sender': notification.get('sender', 'unknown')
        }
        
        # Initialize user bundles if needed
        if user_id not in self.bundles:
            self.bundles[user_id] = defaultdict(list)
        
        self.bundles[user_id][bundle_key].append(bundle_item)
        
        # Check if bundle is ready to deliver
        bundle = self.bundles[user_id][bundle_key]
        is_ready = self._is_bundle_ready(bundle)
        
        return {
            'bundled': True,
            'bundle_key': bundle_key,
            'bundle_type': bundle_type,
            'bundle_size': len(bundle),
            'is_ready': is_ready,
            'estimated_delivery': self._estimate_delivery_time(bundle) if not is_ready else 'now'
        }
    
    def get_bundle(
        self,
        user_id: str,
        bundle_key: str,
        clear_after: bool = True
    ) -> Optional[Dict]:
        """
        Get a specific bundle
        
        Args:
            user_id: User identifier
            bundle_key: Bundle identifier
            clear_after: Whether to clear bundle after retrieval
            
        Returns:
            Bundle dict with notifications and metadata
        """
        if user_id not in self.bundles or bundle_key not in self.bundles[user_id]:
            return None
        
        bundle_items = self.bundles[user_id][bundle_key]
        
        if not bundle_items:
            return None
        
        # Create bundle summary
        bundle = {
            'bundle_key': bundle_key,
            'size': len(bundle_items),
            'notifications': bundle_items,
            'summary': self._create_bundle_summary(bundle_items),
            'created_at': bundle_items[0]['added_at'],
            'last_updated': bundle_items[-1]['added_at']
        }
        
        if clear_after:
            self.bundles[user_id][bundle_key] = []
        
        return bundle
    
    def get_ready_bundles(self, user_id: str) -> List[Dict]:
        """Get all bundles ready for delivery"""
        if user_id not in self.bundles:
            return []
        
        ready_bundles = []
        
        for bundle_key, bundle_items in self.bundles[user_id].items():
            if bundle_items and self._is_bundle_ready(bundle_items):
                bundle = self.get_bundle(user_id, bundle_key, clear_after=True)
                if bundle:
                    ready_bundles.append(bundle)
        
        return ready_bundles
    
    def get_all_bundles(self, user_id: str) -> List[Dict]:
        """Get all active bundles (not just ready ones)"""
        if user_id not in self.bundles:
            return []
        
        all_bundles = []
        
        for bundle_key, bundle_items in self.bundles[user_id].items():
            if bundle_items:
                bundle = {
                    'bundle_key': bundle_key,
                    'size': len(bundle_items),
                    'summary': self._create_bundle_summary(bundle_items),
                    'is_ready': self._is_bundle_ready(bundle_items),
                    'age_minutes': self._get_bundle_age(bundle_items)
                }
                all_bundles.append(bundle)
        
        return all_bundles
    
    def should_bundle(
        self,
        notification: Dict,
        bundle_strategy: BundleStrategy
    ) -> bool:
        """Determine if notification should be bundled"""
        # Critical notifications never bundled
        if notification.get('priority') == 'critical':
            return False
        
        # Calls never bundled
        if notification.get('type') == 'call':
            return False
        
        # Alarms never bundled
        if notification.get('type') == 'alarm':
            return False
        
        # Based on strategy
        if bundle_strategy == BundleStrategy.AGGRESSIVE:
            return True
        
        if bundle_strategy == BundleStrategy.MODERATE:
            # Bundle if from social, email, or low priority
            category = self._detect_category(notification.get('app_name', ''))
            return category in ['social', 'email', 'news', 'shopping']
        
        if bundle_strategy == BundleStrategy.CONSERVATIVE:
            # Only bundle if exact same app and low priority
            return notification.get('priority') in ['low', 'medium']
        
        return False
    
    def _determine_bundle(
        self,
        notification: Dict,
        strategy: BundleStrategy
    ) -> Dict:
        """Determine which bundle this notification belongs to"""
        app_name = notification.get('app_name', 'unknown')
        sender = notification.get('sender', '')
        
        # Detect category
        category = self._detect_category(app_name)
        
        if strategy == BundleStrategy.AGGRESSIVE:
            # Bundle by category
            bundle_type = BundleType.CATEGORY_BASED
            bundle_key = f"category_{category}"
        
        elif strategy == BundleStrategy.MODERATE:
            # Bundle by app within category
            if category in ['social', 'email']:
                bundle_type = BundleType.CATEGORY_BASED
                bundle_key = f"category_{category}"
            else:
                bundle_type = BundleType.APP_BASED
                bundle_key = f"app_{app_name}"
        
        else:  # CONSERVATIVE
            # Bundle only by exact app
            bundle_type = BundleType.APP_BASED
            bundle_key = f"app_{app_name}"
        
        return {
            'type': bundle_type,
            'key': bundle_key
        }
    
    def _detect_category(self, app_name: str) -> str:
        """Detect notification category from app name"""
        app_lower = app_name.lower()
        
        for category, patterns in self.category_patterns.items():
            if any(pattern in app_lower for pattern in patterns):
                return category
        
        return 'other'
    
    def _is_bundle_ready(self, bundle_items: List[Dict]) -> bool:
        """Check if bundle is ready for delivery"""
        if not bundle_items:
            return False
        
        # Check size threshold
        if len(bundle_items) < self.min_bundle_size:
            return False
        
        # Check age threshold
        age_minutes = self._get_bundle_age(bundle_items)
        if age_minutes >= self.max_bundle_age_minutes:
            return True
        
        # Ready if we have many items
        if len(bundle_items) >= 5:
            return True
        
        return False
    
    def _get_bundle_age(self, bundle_items: List[Dict]) -> float:
        """Get age of bundle in minutes"""
        if not bundle_items:
            return 0
        
        first_item_time = datetime.fromisoformat(bundle_items[0]['added_at'])
        age = datetime.now() - first_item_time
        return age.total_seconds() / 60
    
    def _estimate_delivery_time(self, bundle_items: List[Dict]) -> str:
        """Estimate when bundle will be delivered"""
        if not bundle_items:
            return "unknown"
        
        first_item_time = datetime.fromisoformat(bundle_items[0]['added_at'])
        delivery_time = first_item_time + timedelta(minutes=self.max_bundle_age_minutes)
        
        return delivery_time.isoformat()
    
    def _create_bundle_summary(self, bundle_items: List[Dict]) -> Dict:
        """Create a summary of bundled notifications"""
        if not bundle_items:
            return {}
        
        # Count by app
        app_counts = defaultdict(int)
        sender_counts = defaultdict(int)
        
        for item in bundle_items:
            app = item.get('app', 'unknown')
            sender = item.get('sender', 'unknown')
            app_counts[app] += 1
            sender_counts[sender] += 1
        
        # Most common app
        top_app = max(app_counts.items(), key=lambda x: x[1])
        
        # Generate summary text
        total = len(bundle_items)
        if total == 1:
            summary_text = f"1 notification from {top_app[0]}"
        elif len(app_counts) == 1:
            summary_text = f"{total} notifications from {top_app[0]}"
        else:
            summary_text = f"{total} notifications from {len(app_counts)} apps"
        
        return {
            'text': summary_text,
            'total_count': total,
            'app_breakdown': dict(app_counts),
            'sender_breakdown': dict(sender_counts),
            'top_app': top_app[0],
            'unique_apps': len(app_counts),
            'unique_senders': len(sender_counts)
        }
    
    def cleanup_old_bundles(self, user_id: str, max_age_hours: int = 24) -> int:
        """Remove bundles older than specified age"""
        if user_id not in self.bundles:
            return 0
        
        removed_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        bundles_to_remove = []
        
        for bundle_key, bundle_items in self.bundles[user_id].items():
            if bundle_items:
                first_item_time = datetime.fromisoformat(bundle_items[0]['added_at'])
                if first_item_time < cutoff_time:
                    bundles_to_remove.append(bundle_key)
                    removed_count += len(bundle_items)
        
        for bundle_key in bundles_to_remove:
            del self.bundles[user_id][bundle_key]
        
        return removed_count
    
    def get_bundling_stats(self, user_id: str) -> Dict:
        """Get statistics about bundling effectiveness"""
        if user_id not in self.bundles:
            return {
                'active_bundles': 0,
                'total_bundled_notifications': 0,
                'ready_bundles': 0,
                'avg_bundle_size': 0
            }
        
        active_bundles = [b for b in self.bundles[user_id].values() if b]
        total_notifications = sum(len(b) for b in active_bundles)
        ready_count = sum(1 for b in active_bundles if self._is_bundle_ready(b))
        
        avg_size = total_notifications / len(active_bundles) if active_bundles else 0
        
        return {
            'active_bundles': len(active_bundles),
            'total_bundled_notifications': total_notifications,
            'ready_bundles': ready_count,
            'avg_bundle_size': round(avg_size, 1)
        }


# Singleton instance
notification_bundler = NotificationBundler()
