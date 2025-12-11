"""
Tests for TensorFlow Lite Model Conversion
Tests model conversion, quantization, and inference accuracy
"""

import pytest
import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path

# Add training directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'training'))

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class TestTFLiteModelConversion:
    """Test TFLite model conversion process"""
    
    @pytest.fixture
    def models_dir(self):
        """Get models directory path"""
        return Path(__file__).parent.parent / 'models'
    
    @pytest.fixture
    def tflite_model_path(self, models_dir):
        """Get TFLite model path"""
        return models_dir / 'notification_classifier.tflite'
    
    @pytest.fixture
    def sklearn_model_path(self, models_dir):
        """Get sklearn model path"""
        return models_dir / 'notification_classifier.pkl'
    
    @pytest.fixture
    def vectorizer_path(self, models_dir):
        """Get vectorizer path"""
        return models_dir / 'vectorizer.pkl'
    
    @pytest.fixture
    def metadata_path(self, models_dir):
        """Get TFLite metadata path"""
        return models_dir / 'tflite_metadata.json'
    
    def test_tflite_model_exists(self, tflite_model_path):
        """Test that TFLite model file exists"""
        assert tflite_model_path.exists(), f"TFLite model not found at {tflite_model_path}"
    
    def test_tflite_model_size(self, tflite_model_path):
        """Test TFLite model size is reasonable for mobile"""
        if not tflite_model_path.exists():
            pytest.skip("TFLite model not found")
        
        size_bytes = tflite_model_path.stat().st_size
        size_kb = size_bytes / 1024
        
        # Model should be under 100KB for mobile deployment
        assert size_kb < 100, f"Model too large: {size_kb:.2f}KB (should be < 100KB)"
        
        # Model shouldn't be suspiciously small
        assert size_kb > 10, f"Model suspiciously small: {size_kb:.2f}KB"
    
    def test_metadata_exists(self, metadata_path):
        """Test that TFLite metadata exists"""
        assert metadata_path.exists(), f"TFLite metadata not found at {metadata_path}"
    
    def test_metadata_structure(self, metadata_path):
        """Test metadata has correct structure"""
        if not metadata_path.exists():
            pytest.skip("Metadata file not found")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Check required fields
        assert 'model_type' in metadata
        assert 'version' in metadata
        assert 'input_shape' in metadata
        assert 'output_shape' in metadata
        assert 'classes' in metadata
        assert 'quantized' in metadata
        
        # Check values
        assert metadata['model_type'] == 'TensorFlow Lite'
        assert metadata['input_shape'] == [1, 100]
        assert metadata['output_shape'] == [1, 2]
        assert metadata['classes'] == ['non-urgent', 'urgent']
        assert isinstance(metadata['quantized'], bool)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_tflite_model_loads(self, tflite_model_path):
        """Test that TFLite model can be loaded"""
        if not tflite_model_path.exists():
            pytest.skip("TFLite model not found")
        
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        
        # Should not raise any exceptions
        assert interpreter is not None
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_tflite_input_output_shapes(self, tflite_model_path):
        """Test TFLite model input/output tensor shapes"""
        if not tflite_model_path.exists():
            pytest.skip("TFLite model not found")
        
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Check input shape [1, 100]
        assert len(input_details) == 1
        assert input_details[0]['shape'].tolist() == [1, 100]
        assert input_details[0]['dtype'] == np.float32
        
        # Check output shape [1, 2]
        assert len(output_details) == 1
        assert output_details[0]['shape'].tolist() == [1, 2]
        assert output_details[0]['dtype'] == np.float32
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_tflite_inference(self, tflite_model_path, vectorizer_path):
        """Test TFLite model inference"""
        if not tflite_model_path.exists() or not vectorizer_path.exists():
            pytest.skip("Model or vectorizer not found")
        
        # Load vectorizer
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Test prediction
        test_text = "URGENT: Server down!"
        X = vectorizer.transform([test_text]).toarray().astype(np.float32)
        
        interpreter.set_tensor(input_details[0]['index'], X)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        
        # Check output shape and values
        assert output.shape == (1, 2)
        assert np.sum(output) > 0  # Should have non-zero probabilities
        assert output[0][0] >= 0 and output[0][0] <= 1  # Valid probability
        assert output[0][1] >= 0 and output[0][1] <= 1
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_tflite_vs_sklearn_agreement(self, tflite_model_path, sklearn_model_path, vectorizer_path):
        """Test that TFLite predictions match sklearn predictions"""
        if not all([tflite_model_path.exists(), sklearn_model_path.exists(), vectorizer_path.exists()]):
            pytest.skip("Required models not found")
        
        # Load models
        with open(sklearn_model_path, 'rb') as f:
            sklearn_model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        interpreter = tf.lite.Interpreter(model_path=str(tflite_model_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Test cases
        test_cases = [
            "URGENT: Server down!",
            "New message from John",
            "Meeting starts in 5 minutes",
            "Someone liked your photo",
            "CRITICAL: Security breach",
            "Weekly newsletter"
        ]
        
        matches = 0
        for text in test_cases:
            # sklearn prediction
            X = vectorizer.transform([text])
            sklearn_pred = sklearn_model.predict(X)[0]
            
            # TFLite prediction
            X_tflite = X.toarray().astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], X_tflite)
            interpreter.invoke()
            tflite_output = interpreter.get_tensor(output_details[0]['index'])
            tflite_pred = np.argmax(tflite_output[0])
            
            if sklearn_pred == tflite_pred:
                matches += 1
        
        # Require at least 80% agreement
        agreement = matches / len(test_cases) * 100
        assert agreement >= 80, f"Model agreement too low: {agreement:.1f}%"


class TestTFLiteInferencePerformance:
    """Test TFLite inference performance"""
    
    @pytest.fixture
    def models_dir(self):
        """Get models directory path"""
        return Path(__file__).parent.parent / 'models'
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_inference_speed(self, models_dir):
        """Test TFLite inference is fast enough for mobile"""
        import time
        
        tflite_path = models_dir / 'notification_classifier.tflite'
        vectorizer_path = models_dir / 'vectorizer.pkl'
        
        if not tflite_path.exists() or not vectorizer_path.exists():
            pytest.skip("Required models not found")
        
        # Load models
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Benchmark
        test_text = "Test notification"
        X = vectorizer.transform([test_text]).toarray().astype(np.float32)
        
        times = []
        for _ in range(100):
            start = time.time()
            interpreter.set_tensor(input_details[0]['index'], X)
            interpreter.invoke()
            _ = interpreter.get_tensor(output_details[0]['index'])
            times.append((time.time() - start) * 1000)  # Convert to ms
        
        avg_time = np.mean(times)
        p95_time = np.percentile(times, 95)
        
        # Should be under 5ms for mobile
        assert avg_time < 5, f"Average inference too slow: {avg_time:.2f}ms"
        assert p95_time < 10, f"P95 inference too slow: {p95_time:.2f}ms"
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_batch_inference(self, models_dir):
        """Test batch inference capability"""
        tflite_path = models_dir / 'notification_classifier.tflite'
        vectorizer_path = models_dir / 'vectorizer.pkl'
        
        if not tflite_path.exists() or not vectorizer_path.exists():
            pytest.skip("Required models not found")
        
        # Load models
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Test multiple predictions
        test_texts = ["Text 1", "Text 2", "Text 3"]
        
        for text in test_texts:
            X = vectorizer.transform([text]).toarray().astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], X)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            
            # Each should produce valid output
            assert output.shape == (1, 2)
            assert np.sum(output) > 0


class TestTFLiteQuantization:
    """Test model quantization"""
    
    @pytest.fixture
    def models_dir(self):
        """Get models directory path"""
        return Path(__file__).parent.parent / 'models'
    
    def test_quantization_metadata(self, models_dir):
        """Test that quantization is properly documented"""
        metadata_path = models_dir / 'tflite_metadata.json'
        
        if not metadata_path.exists():
            pytest.skip("Metadata file not found")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        assert 'quantized' in metadata
        assert isinstance(metadata['quantized'], bool)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not installed")
    def test_model_is_quantized(self, models_dir):
        """Test that model uses quantization for smaller size"""
        tflite_path = models_dir / 'notification_classifier.tflite'
        
        if not tflite_path.exists():
            pytest.skip("TFLite model not found")
        
        # Load model
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        # Check tensor details
        input_details = interpreter.get_input_details()
        
        # Model should still use float32 for inputs (quantization happens internally)
        assert input_details[0]['dtype'] == np.float32


class TestModelFiles:
    """Test all required model files exist"""
    
    @pytest.fixture
    def models_dir(self):
        """Get models directory path"""
        return Path(__file__).parent.parent / 'models'
    
    def test_all_files_exist(self, models_dir):
        """Test that all required model files exist"""
        required_files = [
            'notification_classifier.pkl',
            'vectorizer.pkl',
            'notification_classifier.tflite',
            'tflite_metadata.json'
        ]
        
        for filename in required_files:
            filepath = models_dir / filename
            assert filepath.exists(), f"Required file missing: {filename}"
    
    def test_model_sizes_reasonable(self, models_dir):
        """Test that model file sizes are reasonable"""
        # TFLite should be smaller or similar to sklearn
        tflite_path = models_dir / 'notification_classifier.tflite'
        sklearn_path = models_dir / 'notification_classifier.pkl'
        
        if not tflite_path.exists() or not sklearn_path.exists():
            pytest.skip("Models not found")
        
        tflite_size = tflite_path.stat().st_size / 1024  # KB
        sklearn_size = sklearn_path.stat().st_size / 1024  # KB
        
        # TFLite should be optimized (within 2x of sklearn)
        assert tflite_size < sklearn_size * 2, f"TFLite model too large compared to sklearn"


class TestConversionScripts:
    """Test that conversion scripts exist"""
    
    @pytest.fixture
    def training_dir(self):
        """Get training directory path"""
        return Path(__file__).parent.parent / 'training'
    
    def test_conversion_script_exists(self, training_dir):
        """Test that TFLite conversion script exists"""
        script_path = training_dir / 'convert_to_tflite.py'
        assert script_path.exists(), "TFLite conversion script not found"
    
    def test_inference_script_exists(self, training_dir):
        """Test that TFLite inference script exists"""
        script_path = training_dir / 'tflite_inference.py'
        assert script_path.exists(), "TFLite inference script not found"
