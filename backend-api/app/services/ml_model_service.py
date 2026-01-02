"""
ML Model Service - Production ML Model Integration
Handles loading, versioning, caching, and inference for notification classification
"""

import pickle
import json
import os
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelCache:
    """LRU cache for model predictions to reduce inference time"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def _generate_key(self, text: str, sender: str) -> str:
        """Generate cache key from input"""
        input_str = f"{text}|{sender}".lower()
        return hashlib.md5(input_str.encode()).hexdigest()
    
    def get(self, text: str, sender: str) -> Optional[Dict[str, Any]]:
        """Get cached prediction if available and not expired"""
        key = self._generate_key(text, sender)
        
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        # Check if expired
        if time.time() - self.access_times[key] > self.ttl_seconds:
            del self.cache[key]
            del self.access_times[key]
            self.miss_count += 1
            return None
        
        self.hit_count += 1
        self.access_times[key] = time.time()
        return self.cache[key]
    
    def set(self, text: str, sender: str, prediction: Dict[str, Any]):
        """Cache a prediction"""
        key = self._generate_key(text, sender)
        
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = prediction
        self.access_times[key] = time.time()
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'ttl_seconds': self.ttl_seconds
        }


class ModelVersionManager:
    """Manages multiple model versions with rollback capability"""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.versions_file = self.models_dir / 'versions.json'
        self.versions_data = self._load_versions()
    
    def _load_versions(self) -> Dict[str, Any]:
        """Load version metadata"""
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                return json.load(f)
        
        # Initialize default structure
        default_data = {
            'current_version': None,
            'versions': []
        }
        
        # Save default structure
        with open(self.versions_file, 'w') as f:
            json.dump(default_data, f, indent=2)
        
        return default_data
    
    def _save_versions(self):
        """Save version metadata"""
        with open(self.versions_file, 'w') as f:
            json.dump(self.versions_data, f, indent=2)
    
    def register_version(self, version: str, metadata: Dict[str, Any]):
        """Register a new model version"""
        version_info = {
            'version': version,
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata,
            'status': 'active'
        }
        
        # Add to versions list
        self.versions_data['versions'].append(version_info)
        
        # Set as current if it's the first version
        if self.versions_data['current_version'] is None:
            self.versions_data['current_version'] = version
        
        self._save_versions()
        logger.info(f"Registered model version: {version}")
    
    def set_current_version(self, version: str) -> bool:
        """Set the active model version"""
        version_exists = any(v['version'] == version for v in self.versions_data['versions'])
        
        if not version_exists:
            logger.error(f"Version {version} not found")
            return False
        
        old_version = self.versions_data['current_version']
        self.versions_data['current_version'] = version
        self._save_versions()
        
        logger.info(f"Switched model version: {old_version} -> {version}")
        return True
    
    def get_current_version(self) -> Optional[str]:
        """Get the current active version"""
        return self.versions_data['current_version']
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all registered versions"""
        return self.versions_data['versions']
    
    def get_version_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific version"""
        for v in self.versions_data['versions']:
            if v['version'] == version:
                return v
        return None


class MLModelService:
    """Production ML Model Service with versioning, caching, and monitoring"""
    
    def __init__(self, models_dir: str = None):
        # Set models directory
        if models_dir is None:
            # Get absolute path to project root
            project_root = Path(__file__).parent.parent.parent.parent
            models_dir = project_root / 'ai-models' / 'models'
        
        self.models_dir = Path(models_dir)
        
        # Ensure models directory exists
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.cache = ModelCache(max_size=1000, ttl_seconds=3600)
        self.version_manager = ModelVersionManager(str(self.models_dir))
        
        # Model state
        self.classifier = None
        self.vectorizer = None
        self.metadata = None
        self.loaded_version = None
        self.inference_times: List[float] = []
        
        # Load default model
        self._load_model()
    
    def _load_model(self, version: str = None):
        """Load ML model from disk"""
        try:
            # Determine version to load
            if version is None:
                version = self.version_manager.get_current_version()
                if version is None:
                    version = "0.1.0"  # Default version
            
            # Load classifier
            classifier_path = self.models_dir / 'notification_classifier.pkl'
            if not classifier_path.exists():
                logger.warning(f"Classifier not found at {classifier_path}")
                return
            
            with open(classifier_path, 'rb') as f:
                self.classifier = pickle.load(f)
            
            # Load vectorizer
            vectorizer_path = self.models_dir / 'vectorizer.pkl'
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # Load metadata
            metadata_path = self.models_dir / 'model_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    'version': version,
                    'model_type': 'RandomForestClassifier',
                    'classes': ['normal', 'urgent']
                }
            
            self.loaded_version = version
            
            # Register version if not already registered
            if self.version_manager.get_version_info(version) is None:
                self.version_manager.register_version(version, self.metadata)
            
            logger.info(f"Loaded model version {version} successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def classify(
        self,
        text: str,
        sender: str,
        received_at: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Classify notification with caching and performance monitoring
        
        Args:
            text: Notification text
            sender: Sender/app name
            received_at: Timestamp (ISO format)
            use_cache: Whether to use cache
        
        Returns:
            Classification result with confidence and metadata
        """
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(text, sender)
            if cached_result is not None:
                cached_result['from_cache'] = True
                return cached_result
        
        # Ensure model is loaded
        if self.classifier is None or self.vectorizer is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        # Start timing
        start_time = time.time()
        
        try:
            # Feature extraction
            X = self.vectorizer.transform([text])
            
            # Prediction
            prediction = self.classifier.predict(X)[0]
            probabilities = self.classifier.predict_proba(X)[0]
            
            # Build result
            is_urgent = bool(prediction)
            confidence = float(max(probabilities))
            
            result = {
                'classification': 'urgent' if is_urgent else 'normal',
                'is_urgent': is_urgent,
                'confidence': confidence,
                'probabilities': {
                    'normal': float(probabilities[0]),
                    'urgent': float(probabilities[1])
                },
                'action': self._determine_action(is_urgent, confidence),
                'reasoning': self._generate_reasoning(text, is_urgent, confidence),
                'metadata': {
                    'model_version': self.loaded_version,
                    'timestamp': received_at or datetime.now().isoformat(),
                    'sender': sender
                },
                'from_cache': False
            }
            
            # Record inference time
            inference_time = (time.time() - start_time) * 1000  # ms
            self.inference_times.append(inference_time)
            if len(self.inference_times) > 1000:
                self.inference_times = self.inference_times[-1000:]
            
            result['inference_time_ms'] = round(inference_time, 2)
            
            # Cache result
            if use_cache:
                self.cache.set(text, sender, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            raise
    
    def _determine_action(self, is_urgent: bool, confidence: float) -> str:
        """Determine notification action based on classification"""
        if is_urgent and confidence > 0.8:
            return "show_immediately"
        elif is_urgent and confidence > 0.6:
            return "show_with_sound"
        elif not is_urgent and confidence > 0.7:
            return "batch"
        else:
            return "silent_notification"
    
    def _generate_reasoning(self, text: str, is_urgent: bool, confidence: float) -> str:
        """Generate human-readable reasoning"""
        text_lower = text.lower()
        
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "alert", "deadline", "important"]
        time_phrases = ["starts in", "due in", "expires in", "meeting in", "minutes", "hours"]
        
        has_urgent_keywords = any(kw in text_lower for kw in urgent_keywords)
        has_time_phrases = any(phrase in text_lower for phrase in time_phrases)
        
        if is_urgent:
            reasons = []
            if has_urgent_keywords:
                reasons.append("contains urgent keywords")
            if has_time_phrases:
                reasons.append("time-sensitive content")
            if confidence > 0.9:
                reasons.append("high confidence classification")
            
            if reasons:
                return f"Classified as urgent: {', '.join(reasons)}"
            else:
                return "Classified as urgent based on content analysis"
        else:
            return f"Standard notification without urgency indicators (confidence: {confidence:.0%})"
    
    def batch_classify(self, notifications: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Classify multiple notifications efficiently"""
        results = []
        
        for notif in notifications:
            result = self.classify(
                text=notif.get('text', ''),
                sender=notif.get('sender', ''),
                received_at=notif.get('received_at')
            )
            results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return {
            'loaded_version': self.loaded_version,
            'model_type': self.metadata.get('model_type') if self.metadata else None,
            'classes': self.metadata.get('classes') if self.metadata else None,
            'model_loaded': self.classifier is not None,
            'available_versions': self.version_manager.list_versions()
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.inference_times:
            return {
                'total_predictions': 0,
                'avg_inference_time_ms': 0,
                'min_inference_time_ms': 0,
                'max_inference_time_ms': 0,
                'cache_stats': self.cache.get_stats()
            }
        
        return {
            'total_predictions': len(self.inference_times),
            'avg_inference_time_ms': round(sum(self.inference_times) / len(self.inference_times), 2),
            'min_inference_time_ms': round(min(self.inference_times), 2),
            'max_inference_time_ms': round(max(self.inference_times), 2),
            'p95_inference_time_ms': round(sorted(self.inference_times)[int(len(self.inference_times) * 0.95)], 2),
            'cache_stats': self.cache.get_stats()
        }
    
    def reload_model(self, version: str = None) -> bool:
        """Reload model (useful for hot-swapping)"""
        try:
            self._load_model(version)
            self.cache.clear()  # Clear cache after model reload
            return True
        except Exception as e:
            logger.error(f"Failed to reload model: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        is_healthy = self.classifier is not None and self.vectorizer is not None
        
        # Test prediction
        test_result = None
        test_time = None
        
        if is_healthy:
            try:
                start = time.time()
                test_result = self.classify("Test notification", "test_app", use_cache=False)
                test_time = (time.time() - start) * 1000
            except Exception as e:
                is_healthy = False
                test_result = str(e)
        
        return {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'model_loaded': self.classifier is not None,
            'vectorizer_loaded': self.vectorizer is not None,
            'loaded_version': self.loaded_version,
            'test_inference_time_ms': round(test_time, 2) if test_time else None,
            'cache_size': len(self.cache.cache),
            'total_predictions': len(self.inference_times)
        }


# Singleton instance
_ml_service_instance = None


def get_ml_service() -> MLModelService:
    """Get singleton ML service instance"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLModelService()
    return _ml_service_instance
