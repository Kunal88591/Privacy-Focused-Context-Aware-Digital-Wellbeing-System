"""
TensorFlow Lite Model Converter
Converts sklearn Random Forest model to TensorFlow Lite format for mobile deployment
"""

import numpy as np
import tensorflow as tf
import pickle
import json
import os
from pathlib import Path


class TFLiteConverter:
    """Convert sklearn model to TensorFlow Lite format"""
    
    def __init__(self, models_dir='../models'):
        self.models_dir = Path(models_dir)
        self.classifier = None
        self.vectorizer = None
        self.metadata = None
    
    def load_sklearn_model(self):
        """Load the sklearn model and vectorizer"""
        print("Loading sklearn model...")
        
        # Load classifier
        classifier_path = self.models_dir / 'notification_classifier.pkl'
        with open(classifier_path, 'rb') as f:
            self.classifier = pickle.load(f)
        print(f"Loaded classifier from {classifier_path}")
        
        # Load vectorizer
        vectorizer_path = self.models_dir / 'vectorizer.pkl'
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        print(f"Loaded vectorizer from {vectorizer_path}")
        
        # Load metadata
        metadata_path = self.models_dir / 'model_metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
        
        return True
    
    def create_tensorflow_model(self):
        """Create TensorFlow model that mimics sklearn behavior"""
        print("\nCreating TensorFlow model...")
        
        # Get model parameters
        n_features = self.vectorizer.max_features
        n_estimators = self.classifier.n_estimators
        
        print(f"Model parameters:")
        print(f"  - Features: {n_features}")
        print(f"  - Estimators: {n_estimators}")
        
        # Create a simple neural network that approximates Random Forest
        # Note: Direct conversion of Random Forest to TF is complex,
        # so we'll create a neural network trained to mimic it
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(n_features,), name='input'),
            tf.keras.layers.Dense(128, activation='relu', name='dense1'),
            tf.keras.layers.Dropout(0.3, name='dropout1'),
            tf.keras.layers.Dense(64, activation='relu', name='dense2'),
            tf.keras.layers.Dropout(0.2, name='dropout2'),
            tf.keras.layers.Dense(32, activation='relu', name='dense3'),
            tf.keras.layers.Dense(2, activation='softmax', name='output')
        ])
        
        print("\nModel architecture:")
        model.summary()
        
        return model
    
    def train_tensorflow_model(self, model, num_samples=10000):
        """Train TensorFlow model to mimic sklearn model"""
        print(f"\nGenerating {num_samples} training samples...")
        
        # Generate synthetic data
        from train_notification_classifier import NotificationClassifier
        nc = NotificationClassifier(model_path=str(self.models_dir))
        df = nc.generate_training_data(num_samples=num_samples)
        
        # Prepare features
        print("Preparing features...")
        X_text = self.vectorizer.transform(df['text']).toarray()
        
        # Get sklearn predictions as labels
        print("Getting sklearn predictions as training labels...")
        y_sklearn = self.classifier.predict(X_text)
        y_proba = self.classifier.predict_proba(X_text)
        
        # Compile model
        print("\nCompiling model...")
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        print("\nTraining TensorFlow model...")
        history = model.fit(
            X_text,
            y_sklearn,
            epochs=20,
            batch_size=32,
            validation_split=0.2,
            verbose=1
        )
        
        # Evaluate
        final_acc = history.history['accuracy'][-1]
        val_acc = history.history['val_accuracy'][-1]
        
        print(f"\nTraining accuracy: {final_acc:.4f}")
        print(f"Validation accuracy: {val_acc:.4f}")
        
        return model, history
    
    def convert_to_tflite(self, model, optimize=True):
        """Convert TensorFlow model to TFLite format"""
        print("\nConverting to TensorFlow Lite...")
        
        # Create converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        if optimize:
            print("Applying optimizations...")
            # Dynamic range quantization
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            # Set supported types for quantization
            converter.target_spec.supported_types = [tf.float16]
        
        # Convert
        tflite_model = converter.convert()
        
        # Get model size
        size_kb = len(tflite_model) / 1024
        print(f"TFLite model size: {size_kb:.2f} KB")
        
        return tflite_model
    
    def save_tflite_model(self, tflite_model, filename='notification_classifier.tflite'):
        """Save TFLite model to disk"""
        tflite_path = self.models_dir / filename
        
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"\nSaved TFLite model to {tflite_path}")
        
        # Save metadata
        metadata = {
            'model_type': 'TensorFlow Lite',
            'source': 'sklearn RandomForest',
            'input_shape': [1, self.vectorizer.max_features],
            'output_shape': [1, 2],
            'classes': ['non-urgent', 'urgent'],
            'version': '1.0.0',
            'quantized': True
        }
        
        metadata_path = self.models_dir / 'tflite_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Saved metadata to {metadata_path}")
        
        return tflite_path
    
    def test_tflite_model(self, tflite_path):
        """Test TFLite model inference"""
        print("\nTesting TFLite model...")
        
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        # Get input/output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"Input shape: {input_details[0]['shape']}")
        print(f"Output shape: {output_details[0]['shape']}")
        
        # Test predictions
        test_texts = [
            "URGENT: Server down!",
            "New message from John",
            "Meeting starts in 5 minutes",
            "Someone liked your photo"
        ]
        
        print("\nTest predictions:")
        for text in test_texts:
            # Transform text
            X = self.vectorizer.transform([text]).toarray().astype(np.float32)
            
            # Set input tensor
            interpreter.set_tensor(input_details[0]['index'], X)
            
            # Run inference
            interpreter.invoke()
            
            # Get output
            output = interpreter.get_tensor(output_details[0]['index'])
            prediction = np.argmax(output[0])
            confidence = output[0][prediction]
            
            label = "URGENT" if prediction == 1 else "Normal"
            print(f"  {label} ({confidence:.2%}): {text}")
        
        return True
    
    def compare_models(self, tf_model, tflite_path, num_samples=100):
        """Compare sklearn, TensorFlow, and TFLite predictions"""
        print(f"\nComparing models on {num_samples} samples...")
        
        # Generate test data
        from train_notification_classifier import NotificationClassifier
        nc = NotificationClassifier(model_path=str(self.models_dir))
        df = nc.generate_training_data(num_samples=num_samples)
        
        # Prepare features
        X_text = self.vectorizer.transform(df['text']).toarray()
        
        # Sklearn predictions
        sklearn_pred = self.classifier.predict(X_text)
        
        # TensorFlow predictions
        tf_pred = np.argmax(tf_model.predict(X_text, verbose=0), axis=1)
        
        # TFLite predictions
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        tflite_pred = []
        for i in range(len(X_text)):
            X = X_text[i:i+1].astype(np.float32)
            interpreter.set_tensor(input_details[0]['index'], X)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            tflite_pred.append(np.argmax(output[0]))
        
        tflite_pred = np.array(tflite_pred)
        
        # Calculate agreement
        tf_sklearn_agreement = np.mean(tf_pred == sklearn_pred)
        tflite_sklearn_agreement = np.mean(tflite_pred == sklearn_pred)
        tflite_tf_agreement = np.mean(tflite_pred == tf_pred)
        
        print(f"\nModel Agreement:")
        print(f"  TF vs sklearn: {tf_sklearn_agreement:.2%}")
        print(f"  TFLite vs sklearn: {tflite_sklearn_agreement:.2%}")
        print(f"  TFLite vs TF: {tflite_tf_agreement:.2%}")
        
        return {
            'tf_sklearn_agreement': tf_sklearn_agreement,
            'tflite_sklearn_agreement': tflite_sklearn_agreement,
            'tflite_tf_agreement': tflite_tf_agreement
        }


def main():
    """Main conversion script"""
    print("=" * 60)
    print("TensorFlow Lite Model Conversion")
    print("=" * 60)
    
    # Initialize converter
    converter = TFLiteConverter()
    
    # Step 1: Load sklearn model
    converter.load_sklearn_model()
    
    # Step 2: Create TensorFlow model
    tf_model = converter.create_tensorflow_model()
    
    # Step 3: Train TensorFlow model to mimic sklearn
    tf_model, history = converter.train_tensorflow_model(tf_model, num_samples=10000)
    
    # Step 4: Convert to TFLite
    tflite_model = converter.convert_to_tflite(tf_model, optimize=True)
    
    # Step 5: Save TFLite model
    tflite_path = converter.save_tflite_model(tflite_model)
    
    # Step 6: Test TFLite model
    converter.test_tflite_model(tflite_path)
    
    # Step 7: Compare models
    metrics = converter.compare_models(tf_model, tflite_path, num_samples=500)
    
    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"\nTFLite model saved to: {tflite_path}")
    print(f"Model agreement with sklearn: {metrics['tflite_sklearn_agreement']:.2%}")
    print("\nThe model is ready for mobile deployment!")


if __name__ == "__main__":
    main()
