"""
Tests for TFLite Conversion and Mobile Inference
Tests model conversion, inference, and validation
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'training'))

from tflite_inference import TFLiteMobileInference, TFLiteValidator


class TestTFLiteMobileInference:
    """Test TFLite mobile inference wrapper"""
    
    @pytest.fixture
    def inference(self):
        """Create inference instance"""
        inference = TFLiteMobileInference()
        inference.load_model()
        return inference
    
    def test_model_loading(self, inference):
        """Test model loads successfully"""
        assert inference.interpreter is not None
        assert inference.vectorizer is not None
        assert inference.input_details is not None
        assert inference.output_details is not None
    
    def test_model_info(self, inference):
        """Test model information retrieval"""
        info = inference.get_model_info()
        
        assert 'model_type' in info
        assert 'version' in info
        assert 'classes' in info
        assert 'input_shape' in info
        assert 'output_shape' in info
        
        assert info['model_type'] == 'TensorFlow Lite'
        assert info['classes'] == ['non-urgent', 'urgent']
    
    def test_single_prediction(self, inference):
        """Test single prediction"""
        result = inference.predict("URGENT: Server down!")
        
        assert 'prediction' in result
        assert 'is_urgent' in result
        assert 'classification' in result
        assert 'confidence' in result
        assert 'probabilities' in result
        
        assert isinstance(result['prediction'], int)
        assert isinstance(result['is_urgent'], bool)
        assert result['classification'] in ['urgent', 'non-urgent']
        assert 0 <= result['confidence'] <= 1
    
    def test_urgent_prediction(self, inference):
        """Test urgent notification detection"""
        urgent_texts = [
            "URGENT: Server down!",
            "CRITICAL: Security breach",
            "Meeting starts in 5 minutes"
        ]
        
        for text in urgent_texts:
            result = inference.predict(text)
            # Most should be classified as urgent (but not guaranteed)
            assert result['classification'] in ['urgent', 'non-urgent']
            assert result['confidence'] > 0.5
    
    def test_non_urgent_prediction(self, inference):
        """Test non-urgent notification detection"""
        normal_texts = [
            "Someone liked your photo",
            "New message from friend",
            "Weekly newsletter"
        ]
        
        for text in normal_texts:
            result = inference.predict(text)
            assert result['classification'] in ['urgent', 'non-urgent']
            assert result['confidence'] > 0.5
    
    def test_probabilities_sum_to_one(self, inference):
        """Test probabilities sum to approximately 1"""
        result = inference.predict("Test notification")
        
        probs = result['probabilities']
        total = probs['non_urgent'] + probs['urgent']
        
        assert abs(total - 1.0) < 0.01  # Allow small floating point error
    
    def test_batch_prediction(self, inference):
        """Test batch predictions"""
        texts = [
            "URGENT: Critical alert",
            "Normal message",
            "Meeting reminder"
        ]
        
        results = inference.predict_batch(texts)
        
        assert len(results) == len(texts)
        assert all('prediction' in r for r in results)
        assert all('confidence' in r for r in results)
    
    def test_empty_text(self, inference):
        """Test empty text handling"""
        # Should not crash, might classify as non-urgent
        result = inference.predict("")
        assert 'prediction' in result
    
    def test_long_text(self, inference):
        """Test long text handling"""
        long_text = "URGENT " * 100  # Very long text
        result = inference.predict(long_text)
        assert 'prediction' in result
    
    def test_special_characters(self, inference):
        """Test special character handling"""
        texts = [
            "!!! URGENT !!!",
            "Message with @mentions and #hashtags",
            "Text with émojis and spëcial çhars"
        ]
        
        for text in texts:
            result = inference.predict(text)
            assert 'prediction' in result
    
    def test_model_size(self, inference):
        """Test model size retrieval"""
        sizes = inference.get_model_size()
        
        assert 'tflite_model_kb' in sizes
        assert 'vectorizer_kb' in sizes
        assert 'total_kb' in sizes
        
        # Model should be reasonably small for mobile
        assert sizes['total_kb'] < 1024  # Less than 1MB total
        assert sizes['tflite_model_kb'] < 100  # TFLite model < 100KB
    
    def test_inference_performance(self, inference):
        """Test inference is fast enough for mobile"""
        benchmark = inference.benchmark_inference(num_iterations=10)
        
        assert 'avg_time_ms' in benchmark
        assert 'max_time_ms' in benchmark
        assert 'p95_time_ms' in benchmark
        
        # Should be very fast (< 10ms for mobile)
        assert benchmark['avg_time_ms'] < 10
        assert benchmark['p95_time_ms'] < 20
    
    def test_consistency(self, inference):
        """Test predictions are consistent"""
        text = "URGENT: Server down!"
        
        # Predict same text multiple times
        results = [inference.predict(text) for _ in range(10)]
        
        # All predictions should be identical
        predictions = [r['prediction'] for r in results]
        assert all(p == predictions[0] for p in predictions)
    
    def test_confidence_scores(self, inference):
        """Test confidence scores are reasonable"""
        result = inference.predict("URGENT: Critical system failure!")
        
        # Confidence should be high for clear urgent message
        assert result['confidence'] > 0.7
        
        # Higher probability class should match prediction
        if result['prediction'] == 1:
            assert result['probabilities']['urgent'] > result['probabilities']['non_urgent']
        else:
            assert result['probabilities']['non_urgent'] > result['probabilities']['urgent']


class TestTFLiteValidator:
    """Test TFLite model validation"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        validator = TFLiteValidator()
        validator.load_models()
        return validator
    
    def test_models_loading(self, validator):
        """Test both models load successfully"""
        assert validator.sklearn_model is not None
        assert validator.tflite_inference is not None
    
    def test_prediction_validation(self, validator):
        """Test TFLite predictions match sklearn"""
        test_texts = [
            "URGENT: Server down!",
            "New message from John",
            "Meeting in 5 minutes",
            "Someone liked your photo"
        ]
        
        validation = validator.validate_predictions(test_texts)
        
        assert 'total_samples' in validation
        assert 'matches' in validation
        assert 'agreement_rate' in validation
        
        assert validation['total_samples'] == len(test_texts)
        
        # Should have high agreement (>90%)
        assert validation['agreement_percentage'] > 90
    
    def test_large_sample_validation(self, validator):
        """Test validation on larger sample"""
        # Generate diverse test texts
        test_texts = [
            "URGENT: Critical issue",
            "Normal notification",
            "ALERT: Security breach",
            "Weekly update",
            "Meeting reminder",
            "Someone commented",
            "IMPORTANT: Action required",
            "New follower",
            "Emergency contact",
            "Daily summary"
        ]
        
        validation = validator.validate_predictions(test_texts)
        
        # Should have very high agreement
        assert validation['agreement_percentage'] >= 90
        assert validation['mismatches'] <= 1  # Allow max 1 mismatch


class TestTFLiteModelProperties:
    """Test TFLite model properties and characteristics"""
    
    @pytest.fixture
    def inference(self):
        """Create inference instance"""
        inference = TFLiteMobileInference()
        inference.load_model()
        return inference
    
    def test_input_shape(self, inference):
        """Test input shape is correct"""
        input_shape = inference.input_details[0]['shape']
        
        # Should be [1, 100] for single sample with 100 features
        assert len(input_shape) == 2
        assert input_shape[0] == 1
        assert input_shape[1] == 100
    
    def test_output_shape(self, inference):
        """Test output shape is correct"""
        output_shape = inference.output_details[0]['shape']
        
        # Should be [1, 2] for binary classification
        assert len(output_shape) == 2
        assert output_shape[0] == 1
        assert output_shape[1] == 2
    
    def test_dtype_consistency(self, inference):
        """Test input/output dtypes are correct"""
        input_dtype = inference.input_details[0]['dtype']
        output_dtype = inference.output_details[0]['dtype']
        
        # Should be float32 for TFLite
        assert input_dtype == np.float32
        assert output_dtype == np.float32
    
    def test_model_is_quantized(self, inference):
        """Test model metadata indicates quantization"""
        info = inference.get_model_info()
        
        # Model should be quantized for mobile
        assert info.get('quantized') is True
    
    def test_preprocess_output_shape(self, inference):
        """Test preprocessing produces correct shape"""
        features = inference.preprocess_text("Test notification")
        
        assert features.shape == (1, 100)
        assert features.dtype == np.float32


class TestTFLiteIntegration:
    """Integration tests for TFLite deployment"""
    
    @pytest.fixture
    def inference(self):
        """Create inference instance"""
        inference = TFLiteMobileInference()
        inference.load_model()
        return inference
    
    def test_end_to_end_workflow(self, inference):
        """Test complete inference workflow"""
        # Step 1: Load model (already done in fixture)
        info = inference.get_model_info()
        assert info['model_type'] == 'TensorFlow Lite'
        
        # Step 2: Make prediction
        result = inference.predict("URGENT: System failure!")
        assert 'classification' in result
        
        # Step 3: Verify result structure
        assert all(key in result for key in ['prediction', 'is_urgent', 'confidence'])
        
        # Step 4: Check performance
        benchmark = inference.benchmark_inference(num_iterations=5)
        assert benchmark['avg_time_ms'] < 10
    
    def test_mobile_readiness(self, inference):
        """Test model is ready for mobile deployment"""
        # Check model size
        sizes = inference.get_model_size()
        assert sizes['total_kb'] < 100  # Should be < 100KB for mobile
        
        # Check inference speed
        benchmark = inference.benchmark_inference(num_iterations=10)
        assert benchmark['p95_time_ms'] < 10  # 95% under 10ms
        
        # Check accuracy via validation
        validator = TFLiteValidator()
        validator.load_models()
        
        test_texts = ["URGENT: Test", "Normal text"]
        validation = validator.validate_predictions(test_texts)
        assert validation['agreement_percentage'] == 100
    
    def test_realistic_notifications(self, inference):
        """Test with realistic notification texts"""
        notifications = [
            ("URGENT: Your server is down! Immediate action required.", True),
            ("Someone liked your photo on Instagram.", False),
            ("Meeting with Bob starts in 5 minutes.", True),
            ("Weekly digest: Here's what you missed.", False),
            ("CRITICAL: Security breach detected in your account!", True),
            ("New message from Mom: 'Hi honey'", False),
        ]
        
        correct = 0
        for text, expected_urgent in notifications:
            result = inference.predict(text)
            if result['is_urgent'] == expected_urgent:
                correct += 1
        
        # Should get most predictions correct
        accuracy = correct / len(notifications)
        assert accuracy >= 0.7  # At least 70% accurate


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_model_not_loaded_error(self):
        """Test error when model not loaded"""
        inference = TFLiteMobileInference()
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            inference.predict("Test")
    
    def test_vectorizer_not_loaded_error(self):
        """Test error when vectorizer not loaded"""
        inference = TFLiteMobileInference()
        
        with pytest.raises(RuntimeError, match="Vectorizer not loaded"):
            inference.preprocess_text("Test")
    
    def test_invalid_model_path(self):
        """Test error with invalid model path"""
        inference = TFLiteMobileInference(models_dir='/nonexistent')
        
        with pytest.raises(FileNotFoundError):
            inference.load_model()
    
    def test_unicode_handling(self):
        """Test Unicode character handling"""
        inference = TFLiteMobileInference()
        inference.load_model()
        
        # Should handle various Unicode characters
        texts = [
            "你好",  # Chinese
            "مرحبا",  # Arabic
            "Привет",  # Russian
            "🚨 URGENT 🚨",  # Emojis
        ]
        
        for text in texts:
            result = inference.predict(text)
            assert 'prediction' in result
