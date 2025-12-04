"""
AI Model Training - Notification Classifier
Classifies notifications as urgent or non-urgent
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import json
import os

class NotificationClassifier:
    """Train a model to classify notifications as urgent or non-urgent"""
    
    def __init__(self, model_path='../models'):
        """Initialize the classifier"""
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    def generate_training_data(self, num_samples=1000):
        """Generate synthetic training data for demonstration"""
        
        # Urgent notification patterns
        urgent_templates = [
            "URGENT: {}",
            "Emergency: {}",
            "ASAP: {}",
            "Important: {}",
            "Alert: {}",
            "Critical: {}",
            "Your meeting starts in 5 minutes",
            "Security alert: {}",
            "Payment due today",
            "Deadline in 1 hour: {}",
        ]
        
        # Non-urgent notification patterns
        non_urgent_templates = [
            "You have a new message from {}",
            "New post from {}",
            "Check out this article: {}",
            "Daily digest: {}",
            "Someone liked your post",
            "Weekly summary",
            "Trending now: {}",
            "New follower: {}",
            "Reminder: {}",
            "Update available for {}",
        ]
        
        data = []
        
        # Generate urgent notifications
        for _ in range(num_samples // 2):
            template = np.random.choice(urgent_templates)
            text = template.format(f"task_{np.random.randint(1, 100)}")
            data.append({
                'text': text,
                'label': 1,  # Urgent
                'sender': f"sender_{np.random.randint(1, 50)}",
                'time': np.random.randint(0, 24)
            })
        
        # Generate non-urgent notifications
        for _ in range(num_samples // 2):
            template = np.random.choice(non_urgent_templates)
            text = template.format(f"item_{np.random.randint(1, 100)}")
            data.append({
                'text': text,
                'label': 0,  # Non-urgent
                'sender': f"sender_{np.random.randint(1, 50)}",
                'time': np.random.randint(0, 24)
            })
        
        return pd.DataFrame(data)
    
    def train(self, df=None):
        """Train the notification classifier"""
        
        # Generate data if not provided
        if df is None:
            print("📊 Generating synthetic training data...")
            df = self.generate_training_data(1000)
        
        print(f"Training with {len(df)} samples...")
        print(f"Urgent: {sum(df['label'] == 1)}, Non-urgent: {sum(df['label'] == 0)}")
        
        # Prepare features
        X_text = df['text'].values
        y = df['label'].values
        
        # Split data
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            X_text, y, test_size=0.2, random_state=42
        )
        
        # Vectorize text
        X_train = self.vectorizer.fit_transform(X_train_text)
        X_test = self.vectorizer.transform(X_test_text)
        
        # Train classifier
        print("🎯 Training model...")
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.classifier.score(X_train, y_train)
        test_score = self.classifier.score(X_test, y_test)
        
        print(f"✅ Training accuracy: {train_score:.3f}")
        print(f"✅ Testing accuracy: {test_score:.3f}")
        
        return train_score, test_score
    
    def save_model(self):
        """Save the trained model"""
        # Save sklearn model
        model_file = os.path.join(self.model_path, 'notification_classifier.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(self.classifier, f)
        print(f"💾 Saved classifier to {model_file}")
        
        # Save vectorizer
        vectorizer_file = os.path.join(self.model_path, 'vectorizer.pkl')
        with open(vectorizer_file, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        print(f"💾 Saved vectorizer to {vectorizer_file}")
        
        # Save metadata
        metadata = {
            'model_type': 'RandomForestClassifier',
            'features': self.vectorizer.max_features,
            'classes': ['non-urgent', 'urgent'],
            'version': '0.1.0'
        }
        
        metadata_file = os.path.join(self.model_path, 'model_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"💾 Saved metadata to {metadata_file}")
    
    def predict(self, notification_text):
        """Predict if a notification is urgent"""
        X = self.vectorizer.transform([notification_text])
        prediction = self.classifier.predict(X)[0]
        probability = self.classifier.predict_proba(X)[0]
        
        return {
            'is_urgent': bool(prediction),
            'confidence': float(max(probability)),
            'probabilities': {
                'non_urgent': float(probability[0]),
                'urgent': float(probability[1])
            }
        }

def main():
    """Main training script"""
    print("🤖 Starting Notification Classifier Training...")
    
    # Initialize classifier
    classifier = NotificationClassifier()
    
    # Train model
    train_acc, test_acc = classifier.train()
    
    # Save model
    classifier.save_model()
    
    # Test predictions
    print("\n🧪 Testing predictions:")
    test_notifications = [
        "URGENT: Server down!",
        "New message from John",
        "Meeting starts in 5 minutes",
        "Someone liked your photo",
        "CRITICAL: Security breach detected",
        "Weekly newsletter"
    ]
    
    for notif in test_notifications:
        result = classifier.predict(notif)
        status = "🔴 URGENT" if result['is_urgent'] else "🟢 Normal"
        print(f"{status} ({result['confidence']:.2%}): {notif}")
    
    print("\n✅ Training complete!")

if __name__ == "__main__":
    main()
