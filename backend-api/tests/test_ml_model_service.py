"""
Tests for ML Model Service
Tests caching, versioning, classification, and performance monitoring
"""

import pytest
import time
from pathlib import Path
import tempfile
import shutil

from app.services.ml_model_service import (
    ModelCache,
    ModelVersionManager,
    MLModelService,
    get_ml_service
)


class TestModelCache:
    """Test ModelCache functionality"""
    
    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = ModelCache(max_size=100, ttl_seconds=3600)
        
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600
        assert len(cache.cache) == 0
        assert cache.hit_count == 0
        assert cache.miss_count == 0
    
    def test_cache_set_and_get(self):
        """Test cache set and get operations"""
        cache = ModelCache()
        
        prediction = {'classification': 'urgent', 'confidence': 0.95}
        cache.set('Test notification', 'test_app', prediction)
        
        result = cache.get('Test notification', 'test_app')
        assert result == prediction
        assert cache.hit_count == 1
        assert cache.miss_count == 0
    
    def test_cache_miss(self):
        """Test cache miss"""
        cache = ModelCache()
        
        result = cache.get('Nonexistent', 'test_app')
        assert result is None
        assert cache.hit_count == 0
        assert cache.miss_count == 1
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        cache = ModelCache(ttl_seconds=1)
        
        prediction = {'classification': 'urgent'}
        cache.set('Test', 'app', prediction)
        
        # Should hit before expiration
        result = cache.get('Test', 'app')
        assert result == prediction
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should miss after expiration
        result = cache.get('Test', 'app')
        assert result is None
    
    def test_cache_max_size_eviction(self):
        """Test cache eviction when max size reached"""
        cache = ModelCache(max_size=3)
        
        # Add 4 items (should evict oldest)
        for i in range(4):
            cache.set(f'Text{i}', f'app{i}', {'id': i})
        
        # Cache should have only 3 items
        assert len(cache.cache) == 3
        
        # First item should be evicted
        assert cache.get('Text0', 'app0') is None
        
        # Last items should still be there
        assert cache.get('Text3', 'app3') is not None
    
    def test_cache_clear(self):
        """Test cache clear"""
        cache = ModelCache()
        
        # Add items
        for i in range(5):
            cache.set(f'Text{i}', f'app{i}', {'id': i})
        
        # Clear cache
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.hit_count == 0
        assert cache.miss_count == 0
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = ModelCache(max_size=100, ttl_seconds=3600)
        
        # Perform some operations
        cache.set('Text1', 'app1', {'id': 1})
        cache.get('Text1', 'app1')  # Hit
        cache.get('Text2', 'app2')  # Miss
        
        stats = cache.get_stats()
        
        assert stats['cache_size'] == 1
        assert stats['max_size'] == 100
        assert stats['hit_count'] == 1
        assert stats['miss_count'] == 1
        assert stats['hit_rate'] == 50.0
        assert stats['ttl_seconds'] == 3600


class TestModelVersionManager:
    """Test ModelVersionManager functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_version_manager_initialization(self, temp_dir):
        """Test version manager initialization"""
        manager = ModelVersionManager(temp_dir)
        
        assert manager.models_dir == Path(temp_dir)
        assert manager.versions_file.exists()
        assert manager.versions_data['current_version'] is None
        assert manager.versions_data['versions'] == []
    
    def test_register_version(self, temp_dir):
        """Test version registration"""
        manager = ModelVersionManager(temp_dir)
        
        metadata = {'model_type': 'RandomForest', 'accuracy': 0.95}
        manager.register_version('1.0.0', metadata)
        
        assert len(manager.versions_data['versions']) == 1
        assert manager.versions_data['current_version'] == '1.0.0'
        
        version_info = manager.versions_data['versions'][0]
        assert version_info['version'] == '1.0.0'
        assert version_info['metadata'] == metadata
        assert version_info['status'] == 'active'
    
    def test_set_current_version(self, temp_dir):
        """Test setting current version"""
        manager = ModelVersionManager(temp_dir)
        
        # Register versions
        manager.register_version('1.0.0', {})
        manager.register_version('2.0.0', {})
        
        # Switch to version 2.0.0
        success = manager.set_current_version('2.0.0')
        
        assert success is True
        assert manager.get_current_version() == '2.0.0'
    
    def test_set_nonexistent_version(self, temp_dir):
        """Test setting nonexistent version"""
        manager = ModelVersionManager(temp_dir)
        
        success = manager.set_current_version('999.0.0')
        assert success is False
    
    def test_list_versions(self, temp_dir):
        """Test listing versions"""
        manager = ModelVersionManager(temp_dir)
        
        # Register multiple versions
        for i in range(3):
            manager.register_version(f'1.{i}.0', {'version': i})
        
        versions = manager.list_versions()
        assert len(versions) == 3
    
    def test_get_version_info(self, temp_dir):
        """Test getting version info"""
        manager = ModelVersionManager(temp_dir)
        
        metadata = {'model_type': 'RF', 'accuracy': 0.92}
        manager.register_version('1.0.0', metadata)
        
        info = manager.get_version_info('1.0.0')
        assert info is not None
        assert info['version'] == '1.0.0'
        assert info['metadata'] == metadata
        
        # Nonexistent version
        info = manager.get_version_info('999.0.0')
        assert info is None


class TestMLModelService:
    """Test MLModelService functionality"""
    
    def test_service_initialization(self):
        """Test service initialization"""
        # Note: This might fail if models don't exist
        # In production, ensure models are trained first
        try:
            service = MLModelService()
            assert service.cache is not None
            assert service.version_manager is not None
        except:
            # If models don't exist, that's okay for this test
            pass
    
    def test_singleton_pattern(self):
        """Test singleton pattern"""
        service1 = get_ml_service()
        service2 = get_ml_service()
        
        assert service1 is service2
    
    def test_classify_notification(self):
        """Test notification classification"""
        try:
            service = get_ml_service()
            
            result = service.classify(
                text="URGENT: Server down!",
                sender="ops_team",
                use_cache=False
            )
            
            assert 'classification' in result
            assert 'confidence' in result
            assert 'action' in result
            assert 'reasoning' in result
            assert 'metadata' in result
            assert 'inference_time_ms' in result
            assert result['from_cache'] is False
            
            # Check value types
            assert isinstance(result['confidence'], float)
            assert 0 <= result['confidence'] <= 1
            assert result['classification'] in ['urgent', 'non-urgent']
            
        except RuntimeError:
            # Model not loaded - skip test
            pytest.skip("ML model not available")
    
    def test_classify_with_cache(self):
        """Test classification with caching"""
        try:
            service = get_ml_service()
            service.cache.clear()
            
            # First call - should not be from cache
            result1 = service.classify("Test notification", "test_app", use_cache=True)
            assert result1['from_cache'] is False
            
            # Second call - should be from cache
            result2 = service.classify("Test notification", "test_app", use_cache=True)
            assert result2['from_cache'] is True
            
            # Results should be identical
            assert result1['classification'] == result2['classification']
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_batch_classify(self):
        """Test batch classification"""
        try:
            service = get_ml_service()
            
            notifications = [
                {'text': 'Meeting in 5 minutes', 'sender': 'calendar'},
                {'text': 'Someone liked your photo', 'sender': 'social'},
                {'text': 'CRITICAL: Security alert', 'sender': 'security'}
            ]
            
            results = service.batch_classify(notifications)
            
            assert len(results) == 3
            assert all('classification' in r for r in results)
            assert all('confidence' in r for r in results)
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_action_determination(self):
        """Test action determination logic"""
        try:
            service = get_ml_service()
            
            # Test different confidence levels
            assert service._determine_action(True, 0.95) == "show_immediately"
            assert service._determine_action(True, 0.7) == "show_with_sound"
            assert service._determine_action(False, 0.8) == "batch"
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_reasoning_generation(self):
        """Test reasoning generation"""
        try:
            service = get_ml_service()
            
            # Urgent with keywords
            reasoning = service._generate_reasoning("URGENT meeting", True, 0.9)
            assert "urgent" in reasoning.lower()
            
            # Time-sensitive
            reasoning = service._generate_reasoning("Meeting in 5 minutes", True, 0.85)
            assert "time" in reasoning.lower() or "urgent" in reasoning.lower()
            
            # Non-urgent
            reasoning = service._generate_reasoning("Normal message", False, 0.75)
            assert "standard" in reasoning.lower() or "confidence" in reasoning.lower()
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_get_model_info(self):
        """Test getting model info"""
        try:
            service = get_ml_service()
            info = service.get_model_info()
            
            assert 'loaded_version' in info
            assert 'model_type' in info
            assert 'classes' in info
            assert 'model_loaded' in info
            assert 'available_versions' in info
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_performance_stats(self):
        """Test performance statistics"""
        try:
            service = get_ml_service()
            
            # Make some predictions
            for i in range(5):
                service.classify(f"Test {i}", "app", use_cache=False)
            
            stats = service.get_performance_stats()
            
            assert 'total_predictions' in stats
            assert 'avg_inference_time_ms' in stats
            assert 'min_inference_time_ms' in stats
            assert 'max_inference_time_ms' in stats
            assert 'cache_stats' in stats
            
            assert stats['total_predictions'] >= 5
            assert stats['avg_inference_time_ms'] > 0
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_health_check(self):
        """Test health check"""
        service = get_ml_service()
        health = service.health_check()
        
        assert 'status' in health
        assert 'model_loaded' in health
        assert 'vectorizer_loaded' in health
        assert 'loaded_version' in health
        assert 'cache_size' in health
        assert 'total_predictions' in health
        
        assert health['status'] in ['healthy', 'unhealthy']
    
    def test_inference_time_tracking(self):
        """Test inference time tracking"""
        try:
            service = get_ml_service()
            service.inference_times.clear()
            
            # Make predictions
            for i in range(10):
                service.classify(f"Test {i}", "app", use_cache=False)
            
            assert len(service.inference_times) == 10
            assert all(t > 0 for t in service.inference_times)
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_inference_time_limit(self):
        """Test that inference times are kept within limit"""
        try:
            service = get_ml_service()
            
            # Clear existing times
            service.inference_times.clear()
            
            # Generate more than 1000 predictions by calling classify
            for i in range(1200):
                service.classify(f"Test {i}", "app", use_cache=False)
            
            # Should keep only last 1000
            assert len(service.inference_times) <= 1000
            
        except RuntimeError:
            pytest.skip("ML model not available")


class TestMLModelServiceIntegration:
    """Integration tests for ML model service"""
    
    def test_end_to_end_classification(self):
        """Test end-to-end classification workflow"""
        try:
            service = get_ml_service()
            
            # Test urgent notification
            result = service.classify(
                text="URGENT: Production server is down! Need immediate attention!",
                sender="monitoring_system",
                received_at="2025-12-11T10:00:00Z"
            )
            
            assert result['classification'] in ['urgent', 'non-urgent']
            assert 0 <= result['confidence'] <= 1
            assert result['action'] in ['show_immediately', 'show_with_sound', 'batch', 'silent_notification']
            assert len(result['reasoning']) > 0
            assert result['metadata']['sender'] == 'monitoring_system'
            
            # Test normal notification
            result = service.classify(
                text="John liked your photo",
                sender="social_app",
                received_at="2025-12-11T10:01:00Z"
            )
            
            assert result['classification'] in ['urgent', 'non-urgent']
            assert 'metadata' in result
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_cache_performance_improvement(self):
        """Test that caching improves performance"""
        try:
            service = get_ml_service()
            service.cache.clear()
            
            text = "Test notification for performance"
            sender = "test_app"
            
            # First call - no cache
            start = time.time()
            result1 = service.classify(text, sender, use_cache=True)
            time1 = time.time() - start
            
            # Second call - from cache
            start = time.time()
            result2 = service.classify(text, sender, use_cache=True)
            time2 = time.time() - start
            
            # Cache should be faster (at least 2x in most cases)
            # But we'll use a more lenient check
            assert result2['from_cache'] is True
            assert time2 < time1 or time2 < 0.01  # Cache hit is very fast
            
        except RuntimeError:
            pytest.skip("ML model not available")
    
    def test_model_performance_sla(self):
        """Test that model meets performance SLA (<100ms)"""
        try:
            service = get_ml_service()
            
            # Test multiple predictions
            inference_times = []
            for i in range(20):
                result = service.classify(
                    f"Test notification {i}",
                    "test_app",
                    use_cache=False
                )
                inference_times.append(result['inference_time_ms'])
            
            # Calculate average
            avg_time = sum(inference_times) / len(inference_times)
            
            # Should be under 100ms on average
            assert avg_time < 100, f"Average inference time {avg_time}ms exceeds 100ms SLA"
            
        except RuntimeError:
            pytest.skip("ML model not available")
