"""
Priority-Based Notification Queue
Manages intelligent queuing and batching of notifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, deque
from enum import Enum
import heapq


class QueuePriority(int, Enum):
    """Priority levels for queue (lower number = higher priority)"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    DEFERRED = 4


class DeliveryStrategy(str, Enum):
    """How to deliver queued notifications"""
    IMMEDIATE = "immediate"
    BATCH_HOURLY = "batch_hourly"
    BATCH_DAILY = "batch_daily"
    SMART_TIMING = "smart_timing"


class NotificationQueue:
    """
    Priority queue for notifications with intelligent batching
    """
    
    def __init__(self):
        # Priority queues per user (min-heap based on priority)
        self.queues = defaultdict(list)
        
        # Batch storage for bundled notifications
        self.batches = defaultdict(lambda: defaultdict(list))
        
        # Delivery schedules
        self.delivery_schedules = {}
        
        # Queue statistics
        self.stats = defaultdict(lambda: {
            'total_queued': 0,
            'delivered': 0,
            'batched': 0,
            'dropped': 0
        })
    
    def enqueue(
        self,
        user_id: str,
        notification: Dict,
        priority: QueuePriority,
        delivery_strategy: DeliveryStrategy = DeliveryStrategy.IMMEDIATE
    ) -> Dict:
        """
        Add notification to queue
        
        Args:
            user_id: User identifier
            notification: Notification data
            priority: Queue priority
            delivery_strategy: How to deliver
            
        Returns:
            Dict with queue status and delivery info
        """
        timestamp = datetime.now()
        
        # Create queue item
        queue_item = {
            'id': f"notif_{user_id}_{int(timestamp.timestamp()*1000)}",
            'user_id': user_id,
            'notification': notification,
            'priority': priority.value,
            'delivery_strategy': delivery_strategy,
            'queued_at': timestamp.isoformat(),
            'deliver_at': None,
            'attempts': 0,
            'status': 'queued'
        }
        
        # Determine delivery time based on strategy
        if delivery_strategy == DeliveryStrategy.IMMEDIATE:
            queue_item['deliver_at'] = timestamp.isoformat()
            queue_item['status'] = 'ready'
        elif delivery_strategy == DeliveryStrategy.BATCH_HOURLY:
            queue_item['deliver_at'] = self._next_hour_mark(timestamp).isoformat()
        elif delivery_strategy == DeliveryStrategy.BATCH_DAILY:
            queue_item['deliver_at'] = self._next_daily_batch(timestamp).isoformat()
        elif delivery_strategy == DeliveryStrategy.SMART_TIMING:
            queue_item['deliver_at'] = self._calculate_smart_time(user_id, timestamp).isoformat()
        
        # Initialize user queue if needed
        if user_id not in self.queues:
            self.queues[user_id] = []
        
        # Add to priority queue (heapq uses first element for comparison)
        heapq.heappush(
            self.queues[user_id],
            (priority.value, timestamp.timestamp(), queue_item)
        )
        
        self.stats[user_id]['total_queued'] += 1
        
        return {
            'queue_id': queue_item['id'],
            'position': len(self.queues[user_id]),
            'deliver_at': queue_item['deliver_at'],
            'strategy': delivery_strategy
        }
    
    def dequeue(self, user_id: str, count: int = 1) -> List[Dict]:
        """
        Get next notifications from queue
        
        Args:
            user_id: User identifier
            count: Number of notifications to dequeue
            
        Returns:
            List of notification items
        """
        if user_id not in self.queues or not self.queues[user_id]:
            return []
        
        results = []
        current_time = datetime.now()
        
        while len(results) < count and self.queues[user_id]:
            # Peek at highest priority item
            priority, _, item = self.queues[user_id][0]
            
            # Check if it's time to deliver
            deliver_at = datetime.fromisoformat(item['deliver_at'])
            if deliver_at <= current_time or item['status'] == 'ready':
                # Remove from queue
                heapq.heappop(self.queues[user_id])
                item['status'] = 'delivered'
                item['delivered_at'] = current_time.isoformat()
                results.append(item)
                self.stats[user_id]['delivered'] += 1
            else:
                # Not ready yet
                break
        
        return results
    
    def peek(self, user_id: str, count: int = 10) -> List[Dict]:
        """View queued notifications without removing them"""
        if user_id not in self.queues:
            return []
        
        # Get sorted copy of queue
        sorted_queue = sorted(self.queues[user_id], key=lambda x: (x[0], x[1]))
        return [item[2] for item in sorted_queue[:count]]
    
    def cancel(self, user_id: str, queue_id: str) -> bool:
        """Cancel a queued notification"""
        if user_id not in self.queues:
            return False
        
        # Find and remove item
        original_queue = self.queues[user_id]
        self.queues[user_id] = [
            item for item in original_queue
            if item[2]['id'] != queue_id
        ]
        
        # Re-heapify
        heapq.heapify(self.queues[user_id])
        
        return len(self.queues[user_id]) < len(original_queue)
    
    def add_to_batch(
        self,
        user_id: str,
        batch_key: str,
        notification: Dict
    ) -> Dict:
        """
        Add notification to a batch bundle
        
        Args:
            user_id: User identifier
            batch_key: Batch identifier (e.g., 'social', 'email')
            notification: Notification data
        """
        if user_id not in self.batches:
            self.batches[user_id] = defaultdict(list)
        
        self.batches[user_id][batch_key].append({
            'notification': notification,
            'added_at': datetime.now().isoformat()
        })
        
        self.stats[user_id]['batched'] += 1
        
        return {
            'batch_key': batch_key,
            'batch_size': len(self.batches[user_id][batch_key]),
            'estimated_delivery': self._get_batch_delivery_time(batch_key)
        }
    
    def get_batch(self, user_id: str, batch_key: str) -> List[Dict]:
        """Get and clear a batch of notifications"""
        if user_id not in self.batches or batch_key not in self.batches[user_id]:
            return []
        
        batch = self.batches[user_id][batch_key]
        self.batches[user_id][batch_key] = []
        
        return batch
    
    def get_all_batches(self, user_id: str) -> Dict[str, List[Dict]]:
        """Get all batches for a user"""
        if user_id not in self.batches:
            return {}
        
        return dict(self.batches[user_id])
    
    def flush_ready_notifications(self, user_id: str) -> List[Dict]:
        """Get all notifications that are ready to be delivered"""
        ready = []
        current_time = datetime.now()
        
        if user_id not in self.queues:
            return ready
        
        # Create new queue without ready items
        new_queue = []
        
        for priority, timestamp, item in self.queues[user_id]:
            deliver_at = datetime.fromisoformat(item['deliver_at'])
            
            if deliver_at <= current_time or item['status'] == 'ready':
                item['status'] = 'delivered'
                item['delivered_at'] = current_time.isoformat()
                ready.append(item)
                self.stats[user_id]['delivered'] += 1
            else:
                new_queue.append((priority, timestamp, item))
        
        self.queues[user_id] = new_queue
        heapq.heapify(self.queues[user_id])
        
        return ready
    
    def update_priority(
        self,
        user_id: str,
        queue_id: str,
        new_priority: QueuePriority
    ) -> bool:
        """Update priority of a queued notification"""
        if user_id not in self.queues:
            return False
        
        # Find item and update priority
        updated = False
        new_queue = []
        
        for priority, timestamp, item in self.queues[user_id]:
            if item['id'] == queue_id:
                item['priority'] = new_priority.value
                new_queue.append((new_priority.value, timestamp, item))
                updated = True
            else:
                new_queue.append((priority, timestamp, item))
        
        if updated:
            self.queues[user_id] = new_queue
            heapq.heapify(self.queues[user_id])
        
        return updated
    
    def get_queue_stats(self, user_id: str) -> Dict:
        """Get queue statistics for user"""
        queue_size = len(self.queues.get(user_id, []))
        batch_count = sum(
            len(batch) for batch in self.batches.get(user_id, {}).values()
        )
        
        return {
            'queue_size': queue_size,
            'batched_count': batch_count,
            'total_queued': self.stats[user_id]['total_queued'],
            'total_delivered': self.stats[user_id]['delivered'],
            'total_batched': self.stats[user_id]['batched'],
            'total_dropped': self.stats[user_id]['dropped']
        }
    
    def clear_queue(self, user_id: str) -> int:
        """Clear all queued notifications for user"""
        if user_id not in self.queues:
            return 0
        
        count = len(self.queues[user_id])
        self.queues[user_id] = []
        self.batches[user_id] = defaultdict(list)
        
        return count
    
    def _next_hour_mark(self, current_time: datetime) -> datetime:
        """Calculate next hour mark (e.g., 2:00 PM, 3:00 PM)"""
        next_hour = current_time.replace(minute=0, second=0, microsecond=0)
        next_hour += timedelta(hours=1)
        return next_hour
    
    def _next_daily_batch(self, current_time: datetime) -> datetime:
        """Calculate next daily batch time (e.g., 6:00 PM)"""
        batch_hour = 18  # 6 PM
        batch_time = current_time.replace(hour=batch_hour, minute=0, second=0, microsecond=0)
        
        if current_time >= batch_time:
            batch_time += timedelta(days=1)
        
        return batch_time
    
    def _calculate_smart_time(self, user_id: str, current_time: datetime) -> datetime:
        """
        Calculate smart delivery time based on user behavior patterns
        Delivers during known active/leisure times
        """
        hour = current_time.hour
        
        # Deliver during next break window
        if hour < 12:
            # Deliver at lunch (12:00 PM)
            return current_time.replace(hour=12, minute=0, second=0)
        elif hour < 15:
            # Deliver at afternoon break (3:00 PM)
            return current_time.replace(hour=15, minute=0, second=0)
        elif hour < 18:
            # Deliver after work (6:00 PM)
            return current_time.replace(hour=18, minute=0, second=0)
        else:
            # Deliver in evening (8:00 PM)
            deliver_time = current_time.replace(hour=20, minute=0, second=0)
            if current_time >= deliver_time:
                deliver_time += timedelta(days=1)
            return deliver_time
    
    def _get_batch_delivery_time(self, batch_key: str) -> str:
        """Get estimated delivery time for a batch"""
        # Default batches delivered hourly
        next_delivery = self._next_hour_mark(datetime.now())
        return next_delivery.isoformat()
    
    def get_queue_stats(self, user_id: str) -> Dict:
        """Get queue statistics for user"""
        if user_id not in self.queues:
            return {
                'total_queued': 0,
                'ready_count': 0,
                'deferred_count': 0,
                'by_priority': {}
            }
        
        queue = self.queues[user_id]
        by_priority = defaultdict(int)
        ready_count = 0
        now = datetime.now().timestamp()
        
        for priority, timestamp, item in queue:
            by_priority[priority] += 1
            deliver_at = datetime.fromisoformat(item['deliver_at']).timestamp()
            if deliver_at <= now:
                ready_count += 1
        
        return {
            'total_queued': len(queue),
            'ready_count': ready_count,
            'deferred_count': len(queue) - ready_count,
            'by_priority': dict(by_priority),
            **self.stats[user_id]
        }


# Singleton instance
notification_queue = NotificationQueue()
