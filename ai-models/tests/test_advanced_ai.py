"""
Tests for Advanced AI Models
Tests priority scoring, focus prediction, suggestions, and behavior analysis
"""

import pytest
import sys
import os
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from training.train_priority_model import NotificationPriorityScorer
from training.train_focus_predictor import FocusTimePredictor
from training.context_suggestion_engine import ContextAwareSuggestionEngine
from training.behavior_analyzer import UserBehaviorAnalyzer


class TestNotificationPriorityScorer:
    """Test notification priority scoring model"""
    
    @pytest.fixture
    def scorer(self):
        """Create a scorer instance"""
        return NotificationPriorityScorer()
    
    def test_model_training(self, scorer):
        """Test that model trains successfully"""
        results = scorer.train(num_samples=500)
        
        assert results['train_score'] > 0.9
        assert results['test_score'] > 0.85
        assert results['mae'] < 5.0
        assert results['num_samples'] == 500
    
    def test_extract_temporal_features(self, scorer):
        """Test temporal feature extraction"""
        features = scorer.extract_temporal_features("2024-12-10T14:30:00Z")
        
        assert 'hour' in features
        assert 'day_of_week' in features
        assert 'is_work_hours' in features
        assert features['hour'] == 14
        assert features['is_work_hours'] == 1
    
    def test_extract_text_features(self, scorer):
        """Test text feature extraction"""
        features = scorer.extract_text_features("URGENT: Meeting in 5 minutes!")
        
        assert 'text_length' in features
        assert 'has_uppercase' in features
        assert 'urgency_score' in features
        assert features['has_uppercase'] == 1
        assert features['urgency_score'] >= 85
    
    def test_extract_app_features(self, scorer):
        """Test app feature extraction"""
        features = scorer.extract_app_features("WhatsApp")
        
        assert 'app_priority_high' in features
        assert features['app_priority_high'] == 1
    
    def test_urgent_notification_priority(self, scorer):
        """Test that urgent notifications get high priority"""
        scorer.train(num_samples=500)
        
        priority = scorer.predict_priority(
            "URGENT: Security alert detected",
            "Security",
            "2024-12-10T10:00:00Z"
        )
        
        assert priority >= 70
        assert priority <= 100
    
    def test_low_priority_notification(self, scorer):
        """Test that low priority notifications score low"""
        scorer.train(num_samples=500)
        
        priority = scorer.predict_priority(
            "Someone liked your photo",
            "Instagram",
            "2024-12-10T14:00:00Z"
        )
        
        assert priority >= 0
        assert priority <= 50


class TestFocusTimePredictor:
    """Test focus time prediction model"""
    
    @pytest.fixture
    def predictor(self):
        """Create a predictor instance"""
        return FocusTimePredictor()
    
    def test_model_training(self, predictor):
        """Test that model trains successfully"""
        results = predictor.train(num_samples=1000)
        
        assert results['train_accuracy'] > 0.9
        assert results['test_accuracy'] > 0.85
        assert results['precision'] > 0.8
        assert results['recall'] > 0.8
        assert results['f1_score'] > 0.8
    
    def test_extract_temporal_features(self, predictor):
        """Test temporal feature extraction"""
        features = predictor.extract_temporal_features(10, 1)
        
        assert 'hour' in features
        assert 'day_of_week' in features
        assert 'is_morning' in features
        assert features['hour'] == 10
        assert features['is_morning'] == 1
    
    def test_predict_focus_time(self, predictor):
        """Test focus time prediction"""
        predictor.train(num_samples=1000)
        
        result = predictor.predict_focus_time(
            hour=10,
            day_of_week=1,
            avg_distractions=3,
            avg_screen_time=30,
            avg_notifications=5,
            recent_productivity=80
        )
        
        assert 'is_focus_time' in result
        assert 'confidence' in result
        assert 'focus_score' in result
        assert isinstance(result['is_focus_time'], bool)
        assert 0 <= result['focus_score'] <= 100
    
    def test_get_daily_focus_schedule(self, predictor):
        """Test daily schedule generation"""
        predictor.train(num_samples=1000)
        
        schedule = predictor.get_daily_focus_schedule(day_of_week=1)
        
        assert len(schedule) == 24
        assert all('hour' in s for s in schedule)
        assert all('focus_score' in s for s in schedule)


class TestContextAwareSuggestionEngine:
    """Test context-aware suggestion engine"""
    
    @pytest.fixture
    def engine(self):
        """Create an engine instance"""
        return ContextAwareSuggestionEngine()
    
    def test_analyze_context_high_focus(self, engine):
        """Test context analysis for high focus state"""
        user_data = {
            'current_hour': 10,
            'focus_score': 85,
            'distraction_count': 2,
            'productivity_score': 80
        }
        
        contexts = engine.analyze_context(user_data)
        
        assert len(contexts) > 0
        assert any(c[0] == 'focus' for c in contexts)
    
    def test_analyze_context_distracted(self, engine):
        """Test context analysis for distracted state"""
        user_data = {
            'current_hour': 14,
            'focus_score': 30,
            'distraction_count': 15,
            'productivity_score': 40
        }
        
        contexts = engine.analyze_context(user_data)
        
        assert len(contexts) > 0
        assert any(c[0] == 'distraction' for c in contexts)
    
    def test_analyze_context_sleep_time(self, engine):
        """Test context analysis for sleep time"""
        user_data = {
            'current_hour': 23,
            'focus_score': 50,
            'sleep_hours': 6
        }
        
        contexts = engine.analyze_context(user_data)
        
        assert len(contexts) > 0
        assert any(c[0] == 'sleep' for c in contexts)
    
    def test_generate_suggestions(self, engine):
        """Test suggestion generation"""
        user_data = {
            'current_hour': 10,
            'focus_score': 85,
            'distraction_count': 2
        }
        
        suggestions = engine.generate_suggestions(user_data, max_suggestions=3)
        
        assert len(suggestions) <= 3
        for suggestion in suggestions:
            assert 'category' in suggestion
            assert 'text' in suggestion
            assert 'confidence' in suggestion
            assert 'priority' in suggestion
    
    def test_get_contextual_actions(self, engine):
        """Test action generation for suggestions"""
        suggestion = {'category': 'focus'}
        
        actions = engine.get_contextual_actions(suggestion)
        
        assert len(actions) > 0
        assert all('action' in a for a in actions)
        assert all('label' in a for a in actions)
    
    def test_get_daily_insights(self, engine):
        """Test daily insights generation"""
        user_stats = {
            'avg_focus_score': 75,
            'tasks_completed': 8,
            'screen_time_hours': 6,
            'privacy_score': 85
        }
        
        insights = engine.get_daily_insights(user_stats)
        
        assert len(insights) > 0
        for insight in insights:
            assert 'type' in insight
            assert 'title' in insight
            assert 'message' in insight


class TestUserBehaviorAnalyzer:
    """Test user behavior analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance"""
        return UserBehaviorAnalyzer()
    
    def test_track_focus_session(self, analyzer):
        """Test focus session tracking"""
        start = datetime.now()
        end = start + timedelta(minutes=45)
        
        session = analyzer.track_focus_session(start, end, quality_score=85)
        
        assert 'start_time' in session
        assert 'duration_minutes' in session
        assert 'quality_score' in session
        assert session['quality_score'] == 85
    
    def test_track_distraction(self, analyzer):
        """Test distraction tracking"""
        distraction = analyzer.track_distraction(
            datetime.now(),
            source="Social Media",
            severity=3
        )
        
        assert 'timestamp' in distraction
        assert 'source' in distraction
        assert 'severity' in distraction
        assert distraction['source'] == "Social Media"
    
    def test_track_notification(self, analyzer):
        """Test notification tracking"""
        notification = analyzer.track_notification(
            datetime.now(),
            app_name="WhatsApp",
            priority_score=75,
            was_handled=True
        )
        
        assert 'timestamp' in notification
        assert 'app_name' in notification
        assert 'priority_score' in notification
        assert notification['was_handled'] is True
    
    def test_analyze_focus_patterns(self, analyzer):
        """Test focus pattern analysis"""
        # Add some sample data
        now = datetime.now()
        for i in range(5):
            start = now - timedelta(hours=i*2)
            end = start + timedelta(minutes=40)
            analyzer.track_focus_session(start, end, quality_score=75 + i*2)
        
        analysis = analyzer.analyze_focus_patterns()
        
        assert 'total_sessions' in analysis
        assert 'avg_quality_score' in analysis
        assert analysis['total_sessions'] >= 5
    
    def test_analyze_distraction_patterns(self, analyzer):
        """Test distraction pattern analysis"""
        # Add sample distractions
        for i in range(10):
            analyzer.track_distraction(
                datetime.now() - timedelta(hours=i),
                source="Social Media",
                severity=2
            )
        
        analysis = analyzer.analyze_distraction_patterns()
        
        assert 'total_distractions' in analysis
        assert 'top_sources' in analysis
        assert analysis['total_distractions'] >= 10
    
    def test_generate_productivity_insights(self, analyzer):
        """Test productivity insights generation"""
        # Add sample data
        now = datetime.now()
        for i in range(3):
            start = now - timedelta(hours=i*2)
            end = start + timedelta(minutes=45)
            analyzer.track_focus_session(start, end, quality_score=80)
        
        insights = analyzer.generate_productivity_insights()
        
        assert 'productivity_score' in insights
        assert 'focus_insights' in insights
        assert 'recommendations' in insights
        assert 0 <= insights['productivity_score'] <= 100


# Integration test
def test_ai_models_integration():
    """Test that all AI models work together"""
    
    # Priority scoring
    scorer = NotificationPriorityScorer()
    scorer.train(num_samples=200)
    priority = scorer.predict_priority(
        "Meeting in 10 minutes",
        "Calendar",
        datetime.now().isoformat()
    )
    assert 0 <= priority <= 100
    
    # Focus prediction
    predictor = FocusTimePredictor()
    predictor.train(num_samples=500)
    focus_result = predictor.predict_focus_time(
        hour=10, day_of_week=1,
        avg_distractions=3, avg_screen_time=30,
        avg_notifications=5, recent_productivity=75
    )
    assert 'is_focus_time' in focus_result
    
    # Suggestions
    engine = ContextAwareSuggestionEngine()
    suggestions = engine.generate_suggestions({
        'current_hour': 10,
        'focus_score': focus_result['focus_score'],
        'distraction_count': 3
    })
    assert isinstance(suggestions, list)
    
    # Behavior analysis
    analyzer = UserBehaviorAnalyzer()
    analyzer.track_focus_session(
        datetime.now(),
        datetime.now() + timedelta(minutes=45),
        quality_score=focus_result['focus_score']
    )
    insights = analyzer.generate_productivity_insights()
    assert 'productivity_score' in insights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
