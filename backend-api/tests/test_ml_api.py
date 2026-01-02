"""
Tests for ML Model API Endpoints
Tests all production ML endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestMLClassifyEndpoint:
    """Test /api/v1/ml/classify endpoint"""
    
    def test_classify_urgent_notification(self):
        """Test classifying urgent notification"""
        response = client.post(
            "/api/v1/ml/classify",
            json={
                "text": "URGENT: Server down! Production impacted!",
                "sender": "monitoring",
                "use_cache": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'classification' in data
        assert 'is_urgent' in data
        assert 'confidence' in data
        assert 'probabilities' in data
        assert 'action' in data
        assert 'reasoning' in data
        assert 'metadata' in data
        assert 'inference_time_ms' in data
        assert 'from_cache' in data
        
        assert data['classification'] in ['urgent', 'normal']
        assert isinstance(data['is_urgent'], bool)
        assert 0 <= data['confidence'] <= 1
    
    def test_classify_normal_notification(self):
        """Test classifying normal notification"""
        response = client.post(
            "/api/v1/ml/classify",
            json={
                "text": "Someone commented on your post",
                "sender": "social_app",
                "use_cache": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'classification' in data
        assert data['classification'] in ['urgent', 'normal']
    
    def test_classify_with_timestamp(self):
        """Test classification with timestamp"""
        response = client.post(
            "/api/v1/ml/classify",
            json={
                "text": "Meeting starts in 5 minutes",
                "sender": "calendar",
                "received_at": "2025-12-11T10:00:00Z",
                "use_cache": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['metadata']['timestamp'] == "2025-12-11T10:00:00Z"
    
    def test_classify_with_cache_enabled(self):
        """Test classification with caching"""
        payload = {
            "text": "Test notification for caching",
            "sender": "test_app",
            "use_cache": True
        }
        
        # First call
        response1 = client.post("/api/v1/ml/classify", json=payload)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1['from_cache'] is False
        
        # Second call - should be from cache
        response2 = client.post("/api/v1/ml/classify", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2['from_cache'] is True
        
        # Classifications should match
        assert data1['classification'] == data2['classification']
    
    def test_classify_missing_fields(self):
        """Test classification with missing required fields"""
        response = client.post(
            "/api/v1/ml/classify",
            json={"text": "Only text provided"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_classify_empty_text(self):
        """Test classification with empty text"""
        response = client.post(
            "/api/v1/ml/classify",
            json={
                "text": "",
                "sender": "test_app"
            }
        )
        
        # Should still process (might classify as normal)
        assert response.status_code in [200, 422, 500]


class TestMLBatchClassifyEndpoint:
    """Test /api/v1/ml/classify/batch endpoint"""
    
    def test_batch_classify_multiple_notifications(self):
        """Test batch classification"""
        response = client.post(
            "/api/v1/ml/classify/batch",
            json={
                "notifications": [
                    {"text": "URGENT: Server down", "sender": "ops"},
                    {"text": "Meeting reminder", "sender": "calendar"},
                    {"text": "New message", "sender": "chat"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'total' in data
        assert 'results' in data
        assert 'batch_size' in data
        
        assert data['total'] == 3
        assert len(data['results']) == 3
        
        # Check each result has required fields
        for result in data['results']:
            assert 'classification' in result
            assert 'confidence' in result
            assert 'action' in result
    
    def test_batch_classify_with_timestamps(self):
        """Test batch classification with timestamps"""
        response = client.post(
            "/api/v1/ml/classify/batch",
            json={
                "notifications": [
                    {
                        "text": "Test 1",
                        "sender": "app1",
                        "received_at": "2025-12-11T10:00:00Z"
                    },
                    {
                        "text": "Test 2",
                        "sender": "app2",
                        "received_at": "2025-12-11T10:01:00Z"
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 2
    
    def test_batch_classify_empty_list(self):
        """Test batch classification with empty list"""
        response = client.post(
            "/api/v1/ml/classify/batch",
            json={"notifications": []}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 0
    
    def test_batch_classify_large_batch(self):
        """Test batch classification with many notifications"""
        notifications = [
            {"text": f"Test notification {i}", "sender": f"app{i}"}
            for i in range(50)
        ]
        
        response = client.post(
            "/api/v1/ml/classify/batch",
            json={"notifications": notifications}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 50


class TestMLModelInfoEndpoint:
    """Test /api/v1/ml/model/info endpoint"""
    
    def test_get_model_info(self):
        """Test getting model information"""
        response = client.get("/api/v1/ml/model/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'loaded_version' in data
        assert 'model_type' in data
        assert 'classes' in data
        assert 'model_loaded' in data
        assert 'available_versions' in data
        
        assert isinstance(data['model_loaded'], bool)
        assert isinstance(data['available_versions'], list)


class TestMLPerformanceEndpoint:
    """Test /api/v1/ml/model/performance endpoint"""
    
    def test_get_performance_stats(self):
        """Test getting performance statistics"""
        # Make some predictions first
        for i in range(5):
            client.post(
                "/api/v1/ml/classify",
                json={
                    "text": f"Test {i}",
                    "sender": "test_app",
                    "use_cache": False
                }
            )
        
        response = client.get("/api/v1/ml/model/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'total_predictions' in data
        assert 'avg_inference_time_ms' in data
        assert 'min_inference_time_ms' in data
        assert 'max_inference_time_ms' in data
        assert 'cache_stats' in data
        
        assert data['total_predictions'] >= 0
        if data['total_predictions'] > 0:
            assert data['avg_inference_time_ms'] > 0


class TestMLCacheEndpoints:
    """Test cache management endpoints"""
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        response = client.get("/api/v1/ml/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'cache_size' in data
        assert 'max_size' in data
        assert 'hit_count' in data
        assert 'miss_count' in data
        assert 'hit_rate' in data
        assert 'ttl_seconds' in data
    
    def test_clear_cache(self):
        """Test clearing cache"""
        # Add item to cache
        client.post(
            "/api/v1/ml/classify",
            json={
                "text": "Test for cache clear",
                "sender": "test_app",
                "use_cache": True
            }
        )
        
        # Clear cache
        response = client.delete("/api/v1/ml/cache")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'success'
        assert 'stats_before_clear' in data
        assert 'timestamp' in data
        
        # Verify cache is cleared
        stats_response = client.get("/api/v1/ml/cache/stats")
        stats = stats_response.json()
        assert stats['cache_size'] == 0


class TestMLVersionEndpoints:
    """Test version management endpoints"""
    
    def test_list_versions(self):
        """Test listing model versions"""
        response = client.get("/api/v1/ml/model/versions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'current_version' in data
        assert 'total_versions' in data
        assert 'versions' in data
        
        assert isinstance(data['versions'], list)
    
    def test_reload_model(self):
        """Test model reload"""
        response = client.post("/api/v1/ml/model/reload")
        
        # Should succeed or fail gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['status'] == 'success'
            assert 'loaded_version' in data


class TestMLHealthEndpoint:
    """Test /api/v1/ml/health endpoint"""
    
    def test_health_check(self):
        """Test ML service health check"""
        response = client.get("/api/v1/ml/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'status' in data
        assert 'model_loaded' in data
        assert 'vectorizer_loaded' in data
        assert 'loaded_version' in data
        assert 'cache_size' in data
        assert 'total_predictions' in data
        
        assert data['status'] in ['healthy', 'unhealthy']
        assert isinstance(data['model_loaded'], bool)
        assert isinstance(data['vectorizer_loaded'], bool)
        assert isinstance(data['cache_size'], int)


class TestMLAPIIntegration:
    """Integration tests for ML API"""
    
    def test_full_workflow(self):
        """Test complete ML workflow"""
        # 1. Check health
        health_response = client.get("/api/v1/ml/health")
        assert health_response.status_code == 200
        
        # 2. Get model info
        info_response = client.get("/api/v1/ml/model/info")
        assert info_response.status_code == 200
        
        # 3. Classify notification
        classify_response = client.post(
            "/api/v1/ml/classify",
            json={
                "text": "CRITICAL: System failure",
                "sender": "monitoring",
                "use_cache": False
            }
        )
        assert classify_response.status_code == 200
        
        # 4. Check performance stats
        perf_response = client.get("/api/v1/ml/model/performance")
        assert perf_response.status_code == 200
        perf_data = perf_response.json()
        assert perf_data['total_predictions'] > 0
        
        # 5. Check cache stats
        cache_response = client.get("/api/v1/ml/cache/stats")
        assert cache_response.status_code == 200
    
    def test_concurrent_predictions(self):
        """Test multiple concurrent predictions"""
        responses = []
        
        for i in range(10):
            response = client.post(
                "/api/v1/ml/classify",
                json={
                    "text": f"Test notification {i}",
                    "sender": f"app{i}",
                    "use_cache": False
                }
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Check performance
        perf_response = client.get("/api/v1/ml/model/performance")
        perf_data = perf_response.json()
        assert perf_data['total_predictions'] >= 10
    
    def test_cache_hit_rate_improvement(self):
        """Test that cache improves hit rate over time"""
        # Clear cache first
        client.delete("/api/v1/ml/cache")
        
        # Make same prediction multiple times
        for _ in range(5):
            client.post(
                "/api/v1/ml/classify",
                json={
                    "text": "Repeated notification",
                    "sender": "test_app",
                    "use_cache": True
                }
            )
        
        # Check cache stats
        cache_response = client.get("/api/v1/ml/cache/stats")
        cache_data = cache_response.json()
        
        # Should have good hit rate
        assert cache_data['hit_count'] > 0
        assert cache_data['hit_rate'] > 0
