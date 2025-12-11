"""
TFLite Mobile Inference Wrapper
Provides inference interface for TensorFlow Lite models on mobile devices
"""

import numpy as np
import tensorflow as tf
import pickle
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TFLiteMobileInference:
    """Mobile-optimized inference wrapper for TFLite models"""
    
    def __init__(self, models_dir: str = '../models'):
        """
        Initialize mobile inference wrapper
        
        Args:
            models_dir: Directory containing TFLite model and vectorizer
        """
        self.models_dir = Path(models_dir)
        self.interpreter = None
        self.vectorizer = None
        self.metadata = None
        self.input_details = None
        self.output_details = None
    
    def load_model(self, model_name: str = 'notification_classifier.tflite'):
        """
        Load TFLite model and vectorizer
        
        Args:
            model_name: Name of TFLite model file
        """
        # Load TFLite model
        model_path = self.models_dir / model_name
        if not model_path.exists():
            raise FileNotFoundError(f"TFLite model not found: {model_path}")
        
        self.interpreter = tf.lite.Interpreter(model_path=str(model_path))
        self.interpreter.allocate_tensors()
        
        # Get input/output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load vectorizer
        vectorizer_path = self.models_dir / 'vectorizer.pkl'
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        # Load metadata
        metadata_path = self.models_dir / 'tflite_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
        
        return True
    
    def preprocess_text(self, text: str) -> np.ndarray:
        """
        Preprocess text for model inference
        
        Args:
            text: Input notification text
            
        Returns:
            Feature vector as numpy array
        """
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not loaded. Call load_model() first.")
        
        # Transform text using TF-IDF vectorizer
        features = self.vectorizer.transform([text]).toarray().astype(np.float32)
        return features
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Predict notification urgency
        
        Args:
            text: Notification text
            
        Returns:
            Dictionary with prediction results
        """
        if self.interpreter is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Preprocess
        features = self.preprocess_text(text)
        
        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], features)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Parse results
        probabilities = output[0]
        prediction = int(np.argmax(probabilities))
        confidence = float(probabilities[prediction])
        
        result = {
            'prediction': prediction,
            'is_urgent': bool(prediction == 1),
            'classification': 'urgent' if prediction == 1 else 'non-urgent',
            'confidence': confidence,
            'probabilities': {
                'non_urgent': float(probabilities[0]),
                'urgent': float(probabilities[1])
            }
        }
        
        return result
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Predict multiple notifications
        
        Args:
            texts: List of notification texts
            
        Returns:
            List of prediction results
        """
        return [self.predict(text) for text in texts]
    
    def get_model_info(self) -> Dict[str, any]:
        """Get model information"""
        if self.metadata is None:
            return {'status': 'Model not loaded'}
        
        info = {
            'model_type': self.metadata.get('model_type'),
            'version': self.metadata.get('version'),
            'input_shape': self.metadata.get('input_shape'),
            'output_shape': self.metadata.get('output_shape'),
            'classes': self.metadata.get('classes'),
            'quantized': self.metadata.get('quantized', False)
        }
        
        if self.input_details and self.output_details:
            info['input_dtype'] = str(self.input_details[0]['dtype'])
            info['output_dtype'] = str(self.output_details[0]['dtype'])
        
        return info
    
    def benchmark_inference(self, num_iterations: int = 100) -> Dict[str, float]:
        """
        Benchmark inference performance
        
        Args:
            num_iterations: Number of inference iterations
            
        Returns:
            Performance metrics
        """
        import time
        
        # Test text
        test_text = "URGENT: Server down! Need immediate attention!"
        
        # Warmup
        for _ in range(5):
            self.predict(test_text)
        
        # Benchmark
        times = []
        for _ in range(num_iterations):
            start = time.time()
            self.predict(test_text)
            times.append((time.time() - start) * 1000)  # Convert to ms
        
        return {
            'iterations': num_iterations,
            'avg_time_ms': np.mean(times),
            'min_time_ms': np.min(times),
            'max_time_ms': np.max(times),
            'std_time_ms': np.std(times),
            'p50_time_ms': np.percentile(times, 50),
            'p95_time_ms': np.percentile(times, 95),
            'p99_time_ms': np.percentile(times, 99)
        }
    
    def get_model_size(self) -> Dict[str, any]:
        """Get model file sizes"""
        model_path = self.models_dir / 'notification_classifier.tflite'
        vectorizer_path = self.models_dir / 'vectorizer.pkl'
        
        sizes = {}
        
        if model_path.exists():
            sizes['tflite_model_kb'] = model_path.stat().st_size / 1024
        
        if vectorizer_path.exists():
            sizes['vectorizer_kb'] = vectorizer_path.stat().st_size / 1024
        
        sizes['total_kb'] = sum(sizes.values())
        
        return sizes


class TFLiteValidator:
    """Validate TFLite model against sklearn model"""
    
    def __init__(self, models_dir: str = '../models'):
        self.models_dir = Path(models_dir)
        self.sklearn_model = None
        self.tflite_inference = None
    
    def load_models(self):
        """Load both sklearn and TFLite models"""
        # Load sklearn model
        sklearn_path = self.models_dir / 'notification_classifier.pkl'
        with open(sklearn_path, 'rb') as f:
            self.sklearn_model = pickle.load(f)
        
        # Load TFLite model
        self.tflite_inference = TFLiteMobileInference(str(self.models_dir))
        self.tflite_inference.load_model()
        
        return True
    
    def validate_predictions(self, test_texts: List[str]) -> Dict[str, any]:
        """
        Validate TFLite predictions against sklearn
        
        Args:
            test_texts: List of test notification texts
            
        Returns:
            Validation metrics
        """
        if self.sklearn_model is None or self.tflite_inference is None:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        sklearn_predictions = []
        tflite_predictions = []
        
        for text in test_texts:
            # Sklearn prediction
            features = self.tflite_inference.vectorizer.transform([text]).toarray()
            sklearn_pred = self.sklearn_model.predict(features)[0]
            sklearn_predictions.append(sklearn_pred)
            
            # TFLite prediction
            tflite_result = self.tflite_inference.predict(text)
            tflite_predictions.append(tflite_result['prediction'])
        
        # Calculate metrics
        sklearn_predictions = np.array(sklearn_predictions)
        tflite_predictions = np.array(tflite_predictions)
        
        agreement = np.mean(sklearn_predictions == tflite_predictions)
        matches = np.sum(sklearn_predictions == tflite_predictions)
        total = len(test_texts)
        
        return {
            'total_samples': total,
            'matches': int(matches),
            'mismatches': int(total - matches),
            'agreement_rate': float(agreement),
            'agreement_percentage': float(agreement * 100)
        }


def main():
    """Test TFLite mobile inference"""
    print("=" * 60)
    print("TFLite Mobile Inference Test")
    print("=" * 60)
    
    # Initialize inference
    inference = TFLiteMobileInference()
    
    # Load model
    print("\nLoading TFLite model...")
    inference.load_model()
    print("Model loaded successfully!")
    
    # Get model info
    print("\nModel Information:")
    info = inference.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Get model sizes
    print("\nModel Sizes:")
    sizes = inference.get_model_size()
    for key, value in sizes.items():
        print(f"  {key}: {value:.2f} KB")
    
    # Test predictions
    print("\nTest Predictions:")
    test_texts = [
        "URGENT: Server down! Production impacted!",
        "New message from John",
        "Meeting starts in 5 minutes",
        "Someone liked your photo",
        "CRITICAL: Security breach detected",
        "Weekly newsletter"
    ]
    
    for text in test_texts:
        result = inference.predict(text)
        label = "URGENT" if result['is_urgent'] else "Normal"
        print(f"  {label} ({result['confidence']:.2%}): {text}")
    
    # Benchmark
    print("\nBenchmarking inference performance...")
    benchmark = inference.benchmark_inference(num_iterations=100)
    print(f"  Iterations: {benchmark['iterations']}")
    print(f"  Average: {benchmark['avg_time_ms']:.2f} ms")
    print(f"  Min: {benchmark['min_time_ms']:.2f} ms")
    print(f"  Max: {benchmark['max_time_ms']:.2f} ms")
    print(f"  P95: {benchmark['p95_time_ms']:.2f} ms")
    print(f"  P99: {benchmark['p99_time_ms']:.2f} ms")
    
    # Validate against sklearn
    print("\nValidating against sklearn model...")
    validator = TFLiteValidator()
    validator.load_models()
    
    validation = validator.validate_predictions(test_texts)
    print(f"  Total samples: {validation['total_samples']}")
    print(f"  Matches: {validation['matches']}")
    print(f"  Mismatches: {validation['mismatches']}")
    print(f"  Agreement: {validation['agreement_percentage']:.2f}%")
    
    print("\n" + "=" * 60)
    print("TFLite model is ready for mobile deployment!")
    print("=" * 60)


if __name__ == "__main__":
    main()
