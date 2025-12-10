"""
AI Model Training - Focus Time Predictor
Predicts optimal focus times based on user behavior patterns
Learns when user is most productive and least distracted
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import json
import os
from datetime import datetime, timedelta

class FocusTimePredictor:
    """Predict optimal focus periods for the user"""
    
    def __init__(self, model_path='../models'):
        """Initialize the focus predictor"""
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    def extract_temporal_features(self, hour, day_of_week):
        """Extract time-based features"""
        
        return {
            'hour': hour,
            'day_of_week': day_of_week,
            'is_morning': 1 if 6 <= hour < 12 else 0,
            'is_afternoon': 1 if 12 <= hour < 17 else 0,
            'is_evening': 1 if 17 <= hour < 22 else 0,
            'is_night': 1 if hour >= 22 or hour < 6 else 0,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'is_monday': 1 if day_of_week == 0 else 0,
            'is_friday': 1 if day_of_week == 4 else 0,
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'day_sin': np.sin(2 * np.pi * day_of_week / 7),
            'day_cos': np.cos(2 * np.pi * day_of_week / 7),
        }
    
    def extract_behavioral_features(self, avg_distractions, avg_screen_time, 
                                   avg_notifications, recent_productivity):
        """Extract user behavior features"""
        
        return {
            'avg_distractions_per_hour': avg_distractions,
            'avg_screen_time_minutes': avg_screen_time,
            'avg_notifications_per_hour': avg_notifications,
            'recent_productivity_score': recent_productivity,
            'distraction_level': self._categorize_distractions(avg_distractions),
            'screen_time_level': self._categorize_screen_time(avg_screen_time),
        }
    
    def _categorize_distractions(self, count):
        """Categorize distraction count (0=low, 1=medium, 2=high)"""
        if count < 5:
            return 0
        elif count < 15:
            return 1
        else:
            return 2
    
    def _categorize_screen_time(self, minutes):
        """Categorize screen time (0=low, 1=medium, 2=high)"""
        if minutes < 30:
            return 0
        elif minutes < 90:
            return 1
        else:
            return 2
    
    def generate_training_data(self, num_samples=5000):
        """Generate synthetic training data"""
        
        np.random.seed(42)
        data = []
        
        # Define focus probability patterns by hour
        focus_probabilities = {
            # Early morning (5-8 AM): High focus for early birds
            5: 0.6, 6: 0.75, 7: 0.8, 8: 0.85,
            # Mid-morning (9-11 AM): Peak focus time
            9: 0.9, 10: 0.95, 11: 0.9,
            # Lunch (12-1 PM): Lower focus
            12: 0.5, 13: 0.4,
            # Early afternoon (2-4 PM): Moderate focus
            14: 0.7, 15: 0.75, 16: 0.8,
            # Late afternoon (5-6 PM): Declining focus
            17: 0.6, 18: 0.5,
            # Evening (7-10 PM): Variable focus
            19: 0.5, 20: 0.6, 21: 0.65, 22: 0.5,
            # Night/Late night: Low focus
            23: 0.3, 0: 0.2, 1: 0.15, 2: 0.1, 3: 0.1, 4: 0.2,
        }
        
        for _ in range(num_samples):
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            
            # Base focus probability from time patterns
            base_prob = focus_probabilities.get(hour, 0.5)
            
            # Adjust for weekends (slightly lower focus)
            if day_of_week >= 5:
                base_prob *= 0.85
            
            # Generate behavioral metrics
            # Good focus periods have fewer distractions
            if np.random.random() < base_prob:
                # High focus state
                avg_distractions = np.random.poisson(3)
                avg_screen_time = np.random.normal(45, 15)
                avg_notifications = np.random.poisson(4)
                recent_productivity = np.random.uniform(70, 95)
                is_focus_time = 1
            else:
                # Low focus state
                avg_distractions = np.random.poisson(12)
                avg_screen_time = np.random.normal(120, 30)
                avg_notifications = np.random.poisson(15)
                recent_productivity = np.random.uniform(30, 60)
                is_focus_time = 0
            
            # Add noise
            avg_distractions = max(0, avg_distractions + np.random.randint(-2, 3))
            avg_screen_time = max(0, avg_screen_time + np.random.normal(0, 10))
            avg_notifications = max(0, avg_notifications + np.random.randint(-3, 4))
            recent_productivity = np.clip(recent_productivity + np.random.normal(0, 5), 0, 100)
            
            data.append({
                'hour': hour,
                'day_of_week': day_of_week,
                'avg_distractions': avg_distractions,
                'avg_screen_time': avg_screen_time,
                'avg_notifications': avg_notifications,
                'recent_productivity': recent_productivity,
                'is_focus_time': is_focus_time
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df):
        """Prepare feature matrix from dataframe"""
        
        temporal_features = df.apply(
            lambda row: self.extract_temporal_features(row['hour'], row['day_of_week']),
            axis=1
        )
        
        behavioral_features = df.apply(
            lambda row: self.extract_behavioral_features(
                row['avg_distractions'],
                row['avg_screen_time'],
                row['avg_notifications'],
                row['recent_productivity']
            ),
            axis=1
        )
        
        temporal_df = pd.DataFrame(temporal_features.tolist())
        behavioral_df = pd.DataFrame(behavioral_features.tolist())
        
        features = pd.concat([
            temporal_df.reset_index(drop=True),
            behavioral_df.reset_index(drop=True)
        ], axis=1)
        
        return features
    
    def train(self, num_samples=5000):
        """Train the focus time prediction model"""
        
        print("🤖 Generating training data...")
        df = self.generate_training_data(num_samples)
        
        print(f"📊 Focus time distribution: {df['is_focus_time'].value_counts().to_dict()}")
        
        print("📊 Preparing features...")
        X = self.prepare_features(df)
        y = df['is_focus_time'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        print("⚖️ Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("🎯 Training focus time predictor...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_acc = self.model.score(X_train_scaled, y_train)
        test_acc = self.model.score(X_test_scaled, y_test)
        
        # Get predictions for detailed metrics
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate precision, recall, F1
        from sklearn.metrics import precision_score, recall_score, f1_score
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"✅ Training Accuracy: {train_acc:.3f}")
        print(f"✅ Testing Accuracy: {test_acc:.3f}")
        print(f"✅ Precision: {precision:.3f}")
        print(f"✅ Recall: {recall:.3f}")
        print(f"✅ F1 Score: {f1:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 Top 10 Most Important Features:")
        print(feature_importance.head(10).to_string(index=False))
        
        # Save models
        self.save_models()
        
        # Demo predictions
        self.demo_predictions(df.sample(5))
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'num_samples': num_samples
        }
    
    def save_models(self):
        """Save trained models to disk"""
        
        print(f"💾 Saving models to {self.model_path}...")
        
        # Save model
        model_file = os.path.join(self.model_path, 'focus_predictor.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save scaler
        scaler_file = os.path.join(self.model_path, 'focus_scaler.pkl')
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print("✅ Models saved successfully!")
    
    def load_models(self):
        """Load trained models from disk"""
        
        model_file = os.path.join(self.model_path, 'focus_predictor.pkl')
        scaler_file = os.path.join(self.model_path, 'focus_scaler.pkl')
        
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_file, 'rb') as f:
            self.scaler = pickle.load(f)
        
        print("✅ Models loaded successfully!")
    
    def predict_focus_time(self, hour, day_of_week, avg_distractions,
                          avg_screen_time, avg_notifications, recent_productivity):
        """Predict if this is a good focus time"""
        
        df = pd.DataFrame([{
            'hour': hour,
            'day_of_week': day_of_week,
            'avg_distractions': avg_distractions,
            'avg_screen_time': avg_screen_time,
            'avg_notifications': avg_notifications,
            'recent_productivity': recent_productivity
        }])
        
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        is_focus = self.model.predict(X_scaled)[0]
        confidence = self.model.predict_proba(X_scaled)[0][1]
        
        return {
            'is_focus_time': bool(is_focus),
            'confidence': float(confidence),
            'focus_score': int(confidence * 100)
        }
    
    def get_daily_focus_schedule(self, day_of_week, avg_distractions=5,
                                avg_screen_time=60, avg_notifications=8,
                                recent_productivity=75):
        """Get predicted focus times for entire day"""
        
        schedule = []
        
        for hour in range(24):
            prediction = self.predict_focus_time(
                hour, day_of_week, avg_distractions,
                avg_screen_time, avg_notifications, recent_productivity
            )
            
            schedule.append({
                'hour': hour,
                'time': f"{hour:02d}:00",
                'is_focus_time': prediction['is_focus_time'],
                'focus_score': prediction['focus_score']
            })
        
        return schedule
    
    def demo_predictions(self, sample_df):
        """Demo predictions on sample data"""
        
        print("\n🎯 Sample Predictions:")
        print("-" * 80)
        
        for _, row in sample_df.iterrows():
            result = self.predict_focus_time(
                int(row['hour']),
                int(row['day_of_week']),
                row['avg_distractions'],
                row['avg_screen_time'],
                row['avg_notifications'],
                row['recent_productivity']
            )
            
            actual = row['is_focus_time']
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            print(f"Time: {day_names[int(row['day_of_week'])]} {int(row['hour']):02d}:00")
            print(f"Distractions: {row['avg_distractions']:.0f} | "
                  f"Screen: {row['avg_screen_time']:.0f}m | "
                  f"Notifications: {row['avg_notifications']:.0f}")
            print(f"Actual: {'Focus' if actual else 'Distracted'} | "
                  f"Predicted: {'Focus' if result['is_focus_time'] else 'Distracted'} | "
                  f"Score: {result['focus_score']}")
            print("-" * 80)


if __name__ == "__main__":
    # Train the focus time predictor
    predictor = FocusTimePredictor()
    results = predictor.train(num_samples=5000)
    
    print("\n🎉 Focus Time Predictor Training Complete!")
    print(f"📊 Final Results: {results}")
    
    # Demo: Get focus schedule for Monday
    print("\n📅 Sample Focus Schedule for Monday:")
    schedule = predictor.get_daily_focus_schedule(day_of_week=0)
    focus_periods = [s for s in schedule if s['is_focus_time']]
    
    print(f"\n✅ Recommended Focus Periods ({len(focus_periods)} hours):")
    for period in focus_periods:
        print(f"  • {period['time']} - Focus Score: {period['focus_score']}")
