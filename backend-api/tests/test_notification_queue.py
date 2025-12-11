"""
Tests for Notification Queue
"""

import pytest
from datetime import datetime, timedelta
from app.services.notification_queue import (
    notification_queue,
    QueuePriority,
    DeliveryStrategy
)


class TestNotificationQueue:
    """Test notification queuing functionality"""
    
    def setup_method(self):
        """Clean state before each test"""
        notification_queue.queues = {}
        notification_queue.batches = {}
    
    def test_enqueue_immediate(self):
        """Test enqueuing with immediate delivery"""
        notification = {
            'text': 'Test notification',
            'sender': 'test'
        }
        
        result = notification_queue.enqueue(
            user_id="user1",
            notification=notification,
            priority=QueuePriority.HIGH,
            delivery_strategy=DeliveryStrategy.IMMEDIATE
        )
        
        assert result['queue_id'] is not None
        assert result['position'] >= 0
    
    def test_enqueue_priority_ordering(self):
        """Test notifications are ordered by priority"""
        # Add low priority
        notification_queue.enqueue(
            "user1",
            {'text': 'Low', 'id': 'low'},
            QueuePriority.LOW,
            DeliveryStrategy.IMMEDIATE
        )
        
        # Add critical priority
        notification_queue.enqueue(
            "user1",
            {'text': 'Critical', 'id': 'critical'},
            QueuePriority.CRITICAL,
            DeliveryStrategy.IMMEDIATE
        )
        
        # Add medium priority
        notification_queue.enqueue(
            "user1",
            {'text': 'Medium', 'id': 'medium'},
            QueuePriority.MEDIUM,
            DeliveryStrategy.IMMEDIATE
        )
        
        # Dequeue - should get critical first
        notifications = notification_queue.dequeue("user1", count=1)
        assert len(notifications) == 1
        assert notifications[0]['notification']['id'] == 'critical'
    
    def test_dequeue_multiple(self):
        """Test dequeuing multiple notifications"""
        for i in range(5):
            notification_queue.enqueue(
                "user1",
                {'text': f'Notification {i}'},
                QueuePriority.MEDIUM,
                DeliveryStrategy.IMMEDIATE
            )
        
        notifications = notification_queue.dequeue("user1", count=3)
        assert len(notifications) == 3
    
    def test_peek_without_removing(self):
        """Test peeking at queue without dequeuing"""
        notification_queue.enqueue(
            "user1",
            {'text': 'Test'},
            QueuePriority.HIGH,
            DeliveryStrategy.IMMEDIATE
        )
        
        # Peek
        peeked = notification_queue.peek("user1", count=1)
        assert len(peeked) == 1
        
        # Verify still in queue
        dequeued = notification_queue.dequeue("user1", count=1)
        assert len(dequeued) == 1
    
    def test_batch_delivery(self):
        """Test batch delivery strategy"""
        result = notification_queue.enqueue(
            "user1",
            {'text': 'Batched notification'},
            QueuePriority.LOW,
            DeliveryStrategy.BATCH_HOURLY
        )
        
        # Should have future delivery time
        deliver_at = datetime.fromisoformat(result['deliver_at'])
        assert deliver_at > datetime.now()
    
    def test_smart_timing(self):
        """Test smart timing delivery"""
        result = notification_queue.enqueue(
            "user1",
            {'text': 'Smart timed notification'},
            QueuePriority.MEDIUM,
            DeliveryStrategy.SMART_TIMING
        )
        
        # Should schedule for optimal time
        assert result['deliver_at'] is not None
    
    def test_add_to_batch(self):
        """Test adding notifications to batch"""
        notification_queue.add_to_batch(
            user_id="user1",
            batch_key="social_updates",
            notification={'text': 'Update 1'}
        )
        
        notification_queue.add_to_batch(
            user_id="user1",
            batch_key="social_updates",
            notification={'text': 'Update 2'}
        )
        
        batch = notification_queue.get_batch("user1", "social_updates")
        assert batch is not None
        assert len(batch) == 2
    
    def test_flush_ready_notifications(self):
        """Test flushing ready notifications"""
        # Add immediate notification
        notification_queue.enqueue(
            "user1",
            {'text': 'Ready now'},
            QueuePriority.HIGH,
            DeliveryStrategy.IMMEDIATE
        )
        
        # Add future notification
        notification_queue.enqueue(
            "user1",
            {'text': 'Future'},
            QueuePriority.LOW,
            DeliveryStrategy.BATCH_DAILY
        )
        
        ready = notification_queue.flush_ready_notifications("user1")
        # Should only get immediate one
        assert len(ready) >= 1
    
    def test_cancel_notification(self):
        """Test canceling queued notification"""
        result = notification_queue.enqueue(
            "user1",
            {'text': 'To be canceled'},
            QueuePriority.MEDIUM,
            DeliveryStrategy.IMMEDIATE
        )
        
        queue_id = result['queue_id']
        success = notification_queue.cancel("user1", queue_id)
        assert success is True
    
    def test_update_priority(self):
        """Test updating notification priority"""
        result = notification_queue.enqueue(
            "user1",
            {'text': 'Priority update test'},
            QueuePriority.LOW,
            DeliveryStrategy.IMMEDIATE
        )
        
        queue_id = result['queue_id']
        success = notification_queue.update_priority(
            "user1",
            queue_id,
            QueuePriority.CRITICAL
        )
        
        assert success is True
    
    def test_queue_statistics(self):
        """Test queue statistics"""
        notification_queue.enqueue(
            "user1",
            {'text': 'Test 1'},
            QueuePriority.HIGH,
            DeliveryStrategy.IMMEDIATE
        )
        
        notification_queue.enqueue(
            "user1",
            {'text': 'Test 2'},
            QueuePriority.LOW,
            DeliveryStrategy.BATCH_HOURLY
        )
        
        stats = notification_queue.get_queue_stats("user1")
        assert stats['total_queued'] >= 2
        assert stats['by_priority'] is not None
    
    def test_empty_queue(self):
        """Test operations on empty queue"""
        notifications = notification_queue.dequeue("user2", count=5)
        assert len(notifications) == 0
        
        peeked = notification_queue.peek("user2", count=5)
        assert len(peeked) == 0
    
    def test_get_all_batches(self):
        """Test getting all batches"""
        notification_queue.add_to_batch(
            "user1",
            "batch1",
            {'text': 'Batch 1 item'}
        )
        
        notification_queue.add_to_batch(
            "user1",
            "batch2",
            {'text': 'Batch 2 item'}
        )
        
        batches = notification_queue.get_all_batches("user1")
        assert len(batches) == 2
    
    def test_priority_values(self):
        """Test priority enum values are correctly ordered"""
        assert QueuePriority.CRITICAL.value < QueuePriority.HIGH.value
        assert QueuePriority.HIGH.value < QueuePriority.MEDIUM.value
        assert QueuePriority.MEDIUM.value < QueuePriority.LOW.value
        assert QueuePriority.LOW.value < QueuePriority.DEFERRED.value
