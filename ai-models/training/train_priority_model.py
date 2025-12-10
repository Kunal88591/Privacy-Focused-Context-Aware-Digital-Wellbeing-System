"""
AI Model Training - Notification Priority Scorer
Scores notifications on a scale of 0-100 for priority
Uses ML to learn user's notification importance patterns
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import json
import os
from datetime import datetime, time

class NotificationPriorityScorer:
    """Train a model to score notification priority (0-100)"""
    
    def __init__(self, model_path='../models'):
        """Initialize the priority scorer"""
        self.model_path = model_path
        self.text_vectorizer = TfidfVectorizer(max_features=50)
        self.feature_scaler = StandardScaler()
        self.priority_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    def extract_temporal_features(self, timestamp):
        """Extract time-based features"""
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            'is_work_hours': 1 if 9 <= dt.hour <= 17 else 0,
            'is_sleep_hours': 1 if dt.hour < 7 or dt.hour > 22 else 0,
        }
    
    def extract_text_features(self, text):
        """Extract text-based features"""
        text_lower = text.lower()
        
        # Urgency keywords with weights
        urgency_keywords = {
            'urgent': 90, 'emergency': 95, 'asap': 85, 'critical': 90,
            'important': 80, 'deadline': 85, 'expires': 75, 'due': 70,
            'alert': 80, 'warning': 75, 'security': 85, 'payment': 70,
            'meeting': 60, 'reminder': 50, 'breaking': 85
        }
        
        # Check for urgency indicators
        max_urgency = 0
        urgency_count = 0
        for keyword, weight in urgency_keywords.items():
            if keyword in text_lower:
                max_urgency = max(max_urgency, weight)
                urgency_count += 1
        
        return {
            'text_length': len(text),
            'has_uppercase': 1 if any(c.isupper() for c in text) else 0,
            'has_numbers': 1 if any(c.isdigit() for c in text) else 0,
            'has_exclamation': text.count('!'),
            'has_question': 1 if '?' in text else 0,
            'urgency_score': max_urgency,
            'urgency_keyword_count': urgency_count,
            'all_caps_words': sum(1 for word in text.split() if word.isupper() and len(word) > 1)
        }
    
    def extract_app_features(self, app_name):
        """Extract app-based features"""
        # High priority apps
        high_priority_apps = {
            'messages', 'whatsapp', 'telegram', 'signal', 'phone',
            'calendar', 'email', 'gmail', 'outlook', 'slack',
            'teams', 'zoom', 'meet'
        }
        
        # Medium priority apps
        medium_priority_apps = {
            'twitter', 'linkedin', 'work', 'banking', 'paypal',
            'venmo', 'security', 'authenticator'
        }
        
        # Low priority apps
        low_priority_apps = {
            'facebook', 'instagram', 'tiktok', 'youtube', 'games',
            'news', 'weather', 'shopping'
        }
        
        app_lower = app_name.lower()
        
        is_high_priority = any(app in app_lower for app in high_priority_apps)
        is_medium_priority = any(app in app_lower for app in medium_priority_apps)
        is_low_priority = any(app in app_lower for app in low_priority_apps)
        
        return {
            'app_priority_high': 1 if is_high_priority else 0,
            'app_priority_medium': 1 if is_medium_priority else 0,
            'app_priority_low': 1 if is_low_priority else 0,
        }
    
    def generate_training_data(self, num_samples=2000):
        """Generate synthetic training data with priority scores"""
        
        np.random.seed(42)
        data = []
        
        # High priority scenarios (70-100 score)
        high_priority_examples = [
            ("URGENT: Meeting starts in 5 minutes", "Calendar", 95),
            ("Security Alert: Unusual login detected", "Security", 98),
            ("Payment Due Today - Avoid Late Fee", "Banking", 85),
            ("Emergency: Server down", "Work Slack", 100),
            ("CRITICAL: Password reset required", "Email", 90),
            ("Your flight leaves in 1 hour", "Travel", 95),
            ("Breaking: Important news alert", "News", 75),
            ("Deadline: Project submission in 2 hours", "Work", 88),
            ("Mom calling", "Phone", 80),
            ("Doctor appointment reminder - 30 min", "Calendar", 85),
        ]
        
        # Medium priority scenarios (40-69 score)
        medium_priority_examples = [
            ("New message from colleague", "Slack", 60),
            ("Your package has been delivered", "Shopping", 55),
            ("Weekly team meeting tomorrow", "Calendar", 50),
            ("LinkedIn: Someone viewed your profile", "LinkedIn", 45),
            ("New email from newsletter", "Email", 40),
            ("Reminder: Task due this week", "Productivity", 65),
            ("Weather alert: Rain expected", "Weather", 50),
            ("Friend tagged you in a post", "Facebook", 42),
            ("New comment on your post", "Social", 45),
            ("Daily digest from blog", "News", 40),
        ]
        
        # Low priority scenarios (0-39 score)
        low_priority_examples = [
            ("Someone liked your photo", "Instagram", 25),
            ("New video from subscribed channel", "YouTube", 20),
            ("Flash sale: 50% off today", "Shopping", 30),
            ("You have new followers", "Twitter", 22),
            ("Daily horoscope", "Lifestyle", 10),
            ("Recommended article for you", "News", 18),
            ("New game level unlocked", "Games", 15),
            ("Check out trending posts", "Social", 20),
            ("Weekly app usage summary", "System", 35),
            ("Tips: How to improve productivity", "Blog", 25),
        ]
        
        # Generate samples with variations
        all_examples = (
            high_priority_examples * (num_samples // 60) +
            medium_priority_examples * (num_samples // 60) +
            low_priority_examples * (num_samples // 60)
        )
        
        # Add randomness and time variations
        for text, app, base_priority in all_examples[:num_samples]:
            # Add slight random variation to priority
            priority = np.clip(base_priority + np.random.randint(-5, 6), 0, 100)
            
            # Generate random timestamp
            hour = np.random.randint(0, 24)
            day = np.random.randint(0, 7)
            timestamp = f"2024-12-{10 + day:02d}T{hour:02d}:{np.random.randint(0, 60):02d}:00Z"
            
            # Adjust priority based on time (sleep hours decrease priority)
            if hour < 7 or hour > 22:
                priority = int(priority * 0.7)  # Reduce priority during sleep
            
            # Work hours increase work-related priority
            if 9 <= hour <= 17 and any(word in app.lower() for word in ['work', 'slack', 'email', 'calendar']):
                priority = min(100, int(priority * 1.1))
            
            data.append({
                'text': text,
                'app_name': app,
                'timestamp': timestamp,
                'priority_score': priority
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df, fit_vectorizer=False):
        """Prepare feature matrix from dataframe"""
        
        # Extract all features
        temporal_features = df['timestamp'].apply(self.extract_temporal_features)
        text_features = df['text'].apply(self.extract_text_features)
        app_features = df['app_name'].apply(self.extract_app_features)
        
        # Combine into dataframe
        temporal_df = pd.DataFrame(temporal_features.tolist())
        text_df = pd.DataFrame(text_features.tolist())
        app_df = pd.DataFrame(app_features.tolist())
        
        # Text vectorization
        if fit_vectorizer:
            text_vectors = self.text_vectorizer.fit_transform(df['text']).toarray()
        else:
            text_vectors = self.text_vectorizer.transform(df['text']).toarray()
        
        text_vector_df = pd.DataFrame(
            text_vectors,
            columns=[f'text_vec_{i}' for i in range(text_vectors.shape[1])]
        )
        
        # Concatenate all features
        features = pd.concat([
            temporal_df.reset_index(drop=True),
            text_df.reset_index(drop=True),
            app_df.reset_index(drop=True),
            text_vector_df.reset_index(drop=True)
        ], axis=1)
        
        return features
    
    def train(self, num_samples=2000):
        """Train the priority scoring model"""
        
        print("🤖 Generating training data...")
        df = self.generate_training_data(num_samples)
        
        print("📊 Preparing features...")
        X = self.prepare_features(df, fit_vectorizer=True)
        y = df['priority_score'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        print("⚖️ Scaling features...")
        X_train_scaled = self.feature_scaler.fit_transform(X_train)
        X_test_scaled = self.feature_scaler.transform(X_test)
        
        # Train model
        print("🎯 Training priority scoring model...")
        self.priority_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.priority_model.score(X_train_scaled, y_train)
        test_score = self.priority_model.score(X_test_scaled, y_test)
        
        # Calculate mean absolute error
        y_pred = self.priority_model.predict(X_test_scaled)
        mae = np.mean(np.abs(y_test - y_pred))
        
        print(f"✅ Training R² Score: {train_score:.3f}")
        print(f"✅ Testing R² Score: {test_score:.3f}")
        print(f"✅ Mean Absolute Error: {mae:.2f} points")
        
        # Save models
        self.save_models()
        
        # Test predictions
        self.demo_predictions(df.sample(5))
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'mae': mae,
            'num_samples': num_samples
        }
    
    def save_models(self):
        """Save trained models to disk"""
        
        print(f"💾 Saving models to {self.model_path}...")
        
        # Save priority model
        model_file = os.path.join(self.model_path, 'priority_scorer.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(self.priority_model, f)
        
        # Save text vectorizer
        vectorizer_file = os.path.join(self.model_path, 'priority_text_vectorizer.pkl')
        with open(vectorizer_file, 'wb') as f:
            pickle.dump(self.text_vectorizer, f)
        
        # Save feature scaler
        scaler_file = os.path.join(self.model_path, 'priority_feature_scaler.pkl')
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.feature_scaler, f)
        
        print("✅ Models saved successfully!")
    
    def load_models(self):
        """Load trained models from disk"""
        
        model_file = os.path.join(self.model_path, 'priority_scorer.pkl')
        vectorizer_file = os.path.join(self.model_path, 'priority_text_vectorizer.pkl')
        scaler_file = os.path.join(self.model_path, 'priority_feature_scaler.pkl')
        
        with open(model_file, 'rb') as f:
            self.priority_model = pickle.load(f)
        
        with open(vectorizer_file, 'rb') as f:
            self.text_vectorizer = pickle.load(f)
        
        with open(scaler_file, 'rb') as f:
            self.feature_scaler = pickle.load(f)
        
        print("✅ Models loaded successfully!")
    
    def predict_priority(self, text, app_name, timestamp):
        """Predict priority score for a notification"""
        
        df = pd.DataFrame([{
            'text': text,
            'app_name': app_name,
            'timestamp': timestamp
        }])
        
        X = self.prepare_features(df, fit_vectorizer=False)
        X_scaled = self.feature_scaler.transform(X)
        
        priority = self.priority_model.predict(X_scaled)[0]
        return int(np.clip(priority, 0, 100))
    
    def demo_predictions(self, sample_df):
        """Demo predictions on sample data"""
        
        print("\n🎯 Sample Predictions:")
        print("-" * 80)
        
        for _, row in sample_df.iterrows():
            predicted = self.predict_priority(
                row['text'],
                row['app_name'],
                row['timestamp']
            )
            actual = row['priority_score']
            
            print(f"Text: {row['text'][:60]}...")
            print(f"App: {row['app_name']}")
            print(f"Actual Priority: {actual} | Predicted: {predicted} | Error: {abs(actual - predicted)}")
            print("-" * 80)


if __name__ == "__main__":
    # Train the priority scoring model
    scorer = NotificationPriorityScorer()
    results = scorer.train(num_samples=2000)
    
    print("\n🎉 Priority Scoring Model Training Complete!")
    print(f"📊 Final Results: {results}")
