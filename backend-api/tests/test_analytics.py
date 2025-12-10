"""
Tests for Analytics API
Comprehensive test suite for analytics tracking and insights generation
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from app.main import app
from app.services.analytics_tracker import analytics_tracker
from app.services.insights_generator import insights_generator


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_analytics():
    """Reset analytics data before each test"""
    from collections import defaultdict
    analytics_tracker.data_store = {
        'sessions': [],
        'screen_time': [],
        'focus_sessions': [],
        'breaks': [],
        'notifications': [],
        'app_usage': defaultdict(lambda: {'total_time': 0, 'open_count': 0, 'last_used': None}),
        'productivity_scores': [],
        'wellbeing_scores': [],
        'goals': [],
        'distractions': [],
    }
    yield


# ==================== Tracking Tests ====================

def test_track_session():
    """Test session tracking"""
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    
    response = client.post("/api/v1/analytics/track/session", json={
        "user_id": "user123",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "device_type": "mobile"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["user_id"] == "user123"
    assert data["data"]["duration_minutes"] == 120


def test_track_screen_time():
    """Test screen time tracking"""
    response = client.post("/api/v1/analytics/track/screen-time", json={
        "user_id": "user123",
        "app_name": "Instagram",
        "duration_minutes": 45.5,
        "category": "social_media",
        "timestamp": datetime.now().isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["app_name"] == "Instagram"
    assert data["data"]["duration_minutes"] == 45.5


def test_track_focus_session():
    """Test focus session tracking"""
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=90)
    
    response = client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "quality_score": 85,
        "task_name": "Write documentation"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["quality_score"] == 85
    assert data["data"]["task_name"] == "Write documentation"


def test_track_break():
    """Test break tracking"""
    response = client.post("/api/v1/analytics/track/break", json={
        "user_id": "user123",
        "duration_minutes": 15,
        "break_type": "short",
        "timestamp": datetime.now().isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["duration_minutes"] == 15


def test_track_notification():
    """Test notification tracking"""
    response = client.post("/api/v1/analytics/track/notification", json={
        "user_id": "user123",
        "app_name": "WhatsApp",
        "priority": 75,
        "was_interacted": True,
        "timestamp": datetime.now().isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["priority"] == 75
    assert data["data"]["was_interacted"] is True


def test_track_distraction():
    """Test distraction tracking"""
    response = client.post("/api/v1/analytics/track/distraction", json={
        "user_id": "user123",
        "source": "Social Media",
        "severity": 4,
        "duration_seconds": 180,
        "timestamp": datetime.now().isoformat()
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["severity"] == 4


# ==================== Goal Management Tests ====================

def test_set_goal():
    """Test setting a goal"""
    response = client.post("/api/v1/analytics/goals", json={
        "user_id": "user123",
        "goal_type": "daily_focus_time",
        "target_value": 240,
        "current_value": 0
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["goal_type"] == "daily_focus_time"
    assert data["data"]["target_value"] == 240


def test_update_goal():
    """Test updating goal progress"""
    # First set a goal
    client.post("/api/v1/analytics/goals", json={
        "user_id": "user123",
        "goal_type": "daily_focus_time",
        "target_value": 240,
        "current_value": 0
    })
    
    # Update progress
    response = client.put("/api/v1/analytics/goals/0", json={
        "goal_index": 0,
        "new_value": 120
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["current_value"] == 120
    assert data["data"]["progress_percent"] == 50.0


def test_get_goals():
    """Test getting all goals"""
    # Set multiple goals
    client.post("/api/v1/analytics/goals", json={
        "user_id": "user123",
        "goal_type": "daily_focus_time",
        "target_value": 240,
        "current_value": 0
    })
    
    client.post("/api/v1/analytics/goals", json={
        "user_id": "user123",
        "goal_type": "screen_time_limit",
        "target_value": 360,
        "current_value": 200
    })
    
    response = client.get("/api/v1/analytics/goals?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 2


# ==================== Analytics Summary Tests ====================

def test_get_daily_summary():
    """Test daily summary generation"""
    # Track some data
    now = datetime.now()
    
    # Track screen time
    client.post("/api/v1/analytics/track/screen-time", json={
        "user_id": "user123",
        "app_name": "Chrome",
        "duration_minutes": 60,
        "category": "productivity",
        "timestamp": now.isoformat()
    })
    
    # Track focus session
    client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(hours=1)).isoformat(),
        "quality_score": 80
    })
    
    # Get summary
    response = client.get("/api/v1/analytics/summary/daily?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_screen_time_minutes" in data["data"]
    assert "total_focus_time_minutes" in data["data"]
    assert "productivity_score" in data["data"]


def test_get_weekly_trends():
    """Test weekly trends analysis"""
    # Track data for multiple days
    for i in range(7):
        day = datetime.now() - timedelta(days=i)
        
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(hours=2)).isoformat(),
            "quality_score": 70 + i * 2
        })
    
    response = client.get("/api/v1/analytics/summary/weekly?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "daily_summaries" in data["data"]
    assert "weekly_averages" in data["data"]
    assert "best_day" in data["data"]
    assert "worst_day" in data["data"]


def test_get_app_usage():
    """Test app usage breakdown"""
    # Track usage for multiple apps
    apps = [("Chrome", 120), ("Slack", 60), ("Instagram", 45), ("VSCode", 180)]
    now = datetime.now()
    
    for app_name, duration in apps:
        client.post("/api/v1/analytics/track/screen-time", json={
            "user_id": "user123",
            "app_name": app_name,
            "duration_minutes": duration,
            "category": "productivity",
            "timestamp": now.isoformat()
        })
    
    response = client.get("/api/v1/analytics/apps/usage?user_id=user123&days=7")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "apps" in data["data"]
    assert len(data["data"]["apps"]) == 4
    # VSCode should be first (most time)
    assert data["data"]["apps"][0]["app_name"] == "VSCode"


# ==================== Insights Tests ====================

def test_get_productivity_insights():
    """Test productivity insights generation"""
    # Set up data for insights
    now = datetime.now()
    
    for i in range(7):
        day = now - timedelta(days=i)
        
        # Focus session
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(minutes=60)).isoformat(),
            "quality_score": 50
        })
        
        # Distractions
        for j in range(25):
            client.post("/api/v1/analytics/track/distraction", json={
                "user_id": "user123",
                "source": "Social Media",
                "severity": 3,
                "timestamp": day.isoformat()
            })
    
    response = client.get("/api/v1/analytics/insights/productivity?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "insights" in data["data"]
    assert "recommendations" in data["data"]
    # Should have warnings about low focus and high distractions
    assert len(data["data"]["insights"]) > 0


def test_get_usage_patterns():
    """Test usage pattern detection"""
    # Create consistent focus pattern
    now = datetime.now()
    
    for i in range(7):
        day = now - timedelta(days=i)
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(hours=3)).isoformat(),
            "quality_score": 75
        })
    
    response = client.get("/api/v1/analytics/insights/patterns?user_id=user123&days=7")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "patterns" in data["data"]


def test_get_peak_hours():
    """Test peak hours identification"""
    # Create hourly activity data
    now = datetime.now()
    
    for hour in [9, 10, 14, 15]:
        time = now.replace(hour=hour, minute=0)
        client.post("/api/v1/analytics/track/screen-time", json={
            "user_id": "user123",
            "app_name": "Work App",
            "duration_minutes": 50,
            "category": "productivity",
            "timestamp": time.isoformat()
        })
    
    response = client.get(f"/api/v1/analytics/insights/peak-hours?user_id=user123")
    
    # If error, print details for debugging
    if response.status_code != 200:
        print(f"Error: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Peak hours endpoint may return empty if no hourly breakdown
    assert "data" in data


def test_get_optimal_schedule():
    """Test optimal schedule prediction"""
    # Set up weekly data
    now = datetime.now()
    
    for i in range(7):
        day = now - timedelta(days=i)
        
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(hours=3)).isoformat(),
            "quality_score": 80
        })
    
    response = client.get("/api/v1/analytics/insights/optimal-schedule?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "optimal_focus_blocks" in data["data"]
    assert "suggested_break_times" in data["data"]


def test_get_personalized_tips():
    """Test personalized tips generation"""
    # Set up some data
    now = datetime.now()
    
    for i in range(5):
        day = now - timedelta(days=i)
        
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(minutes=30)).isoformat(),
            "quality_score": 40
        })
    
    response = client.get("/api/v1/analytics/insights/personalized-tips?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert len(data["data"]) > 0
    # Tips should have required fields
    assert "category" in data["data"][0]
    assert "tip" in data["data"][0]


def test_get_wellbeing_score():
    """Test wellbeing score calculation"""
    # Track wellbeing data
    now = datetime.now()
    
    # Screen time
    client.post("/api/v1/analytics/track/screen-time", json={
        "user_id": "user123",
        "app_name": "Work App",
        "duration_minutes": 360,
        "category": "productivity",
        "timestamp": now.isoformat()
    })
    
    # Breaks
    for i in range(5):
        client.post("/api/v1/analytics/track/break", json={
            "user_id": "user123",
            "duration_minutes": 10,
            "break_type": "short",
            "timestamp": now.isoformat()
        })
    
    # Focus session
    client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "quality_score": 70
    })
    
    response = client.get("/api/v1/analytics/insights/wellbeing-score?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "overall_score" in data["data"]
    assert "level" in data["data"]
    assert "components" in data["data"]


def test_get_comparison_report():
    """Test comparison report generation"""
    # Track data
    now = datetime.now()
    
    client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(hours=4)).isoformat(),
        "quality_score": 85
    })
    
    response = client.get("/api/v1/analytics/insights/comparison?user_id=user123&include_benchmark=true")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "overall_status" in data["data"]
    assert "comparisons" in data["data"]


# ==================== Export & Dashboard Tests ====================

def test_export_analytics_data():
    """Test data export"""
    # Track some data
    now = datetime.now()
    
    client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": now.isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "quality_score": 75
    })
    
    response = client.get("/api/v1/analytics/export?user_id=user123&format=json")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "daily_summary" in data["data"]


def test_get_dashboard_data():
    """Test comprehensive dashboard endpoint"""
    # Set up comprehensive data
    now = datetime.now()
    
    # Multiple days of data
    for i in range(7):
        day = now - timedelta(days=i)
        
        # Focus session
        client.post("/api/v1/analytics/track/focus-session", json={
            "user_id": "user123",
            "start_time": day.isoformat(),
            "end_time": (day + timedelta(hours=2)).isoformat(),
            "quality_score": 75
        })
        
        # Screen time
        client.post("/api/v1/analytics/track/screen-time", json={
            "user_id": "user123",
            "app_name": "Work App",
            "duration_minutes": 120,
            "category": "productivity",
            "timestamp": day.isoformat()
        })
        
        # Breaks
        client.post("/api/v1/analytics/track/break", json={
            "user_id": "user123",
            "duration_minutes": 15,
            "break_type": "short",
            "timestamp": day.isoformat()
        })
    
    response = client.get("/api/v1/analytics/dashboard?user_id=user123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "today" in data["data"]
    assert "week" in data["data"]
    assert "top_apps" in data["data"]
    assert "insights" in data["data"]
    assert "wellbeing" in data["data"]
    assert "tips" in data["data"]


# ==================== Error Handling Tests ====================

def test_invalid_date_format():
    """Test error handling for invalid date format"""
    response = client.get("/api/v1/analytics/summary/daily?user_id=user123&date=invalid-date")
    
    assert response.status_code == 400


def test_invalid_quality_score():
    """Test validation for focus quality score"""
    response = client.post("/api/v1/analytics/track/focus-session", json={
        "user_id": "user123",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "quality_score": 150  # Invalid: > 100
    })
    
    assert response.status_code == 422  # Validation error


def test_goal_not_found():
    """Test error when updating non-existent goal"""
    response = client.put("/api/v1/analytics/goals/999", json={
        "goal_index": 999,
        "new_value": 100
    })
    
    assert response.status_code == 404


# ==================== Analytics Tracker Unit Tests ====================

def test_analytics_tracker_productivity_score_calculation():
    """Test productivity score calculation logic"""
    score = analytics_tracker._calculate_productivity_score(
        focus_time=240,  # 4 hours
        focus_quality=80,
        distractions=10,
        breaks_taken=5
    )
    
    assert 0 <= score <= 100
    assert score > 70  # Should be good with these metrics


def test_analytics_tracker_hourly_breakdown():
    """Test hourly breakdown generation"""
    screen_time_data = [
        {'hour': 9, 'duration_minutes': 60},
        {'hour': 10, 'duration_minutes': 45},
        {'hour': 9, 'duration_minutes': 30}  # Same hour
    ]
    
    breakdown = analytics_tracker._get_hourly_breakdown(screen_time_data)
    
    assert len(breakdown) == 24
    assert breakdown[9]['minutes'] == 90  # 60 + 30
    assert breakdown[10]['minutes'] == 45


def test_analytics_tracker_trend_analysis():
    """Test trend detection"""
    improving = [50, 55, 60, 65, 70]
    declining = [70, 65, 60, 55, 50]
    stable = [60, 61, 59, 60, 61]
    
    assert analytics_tracker._analyze_trend(improving) == 'improving'
    assert analytics_tracker._analyze_trend(declining) == 'declining'
    assert analytics_tracker._analyze_trend(stable) == 'stable'


# ==================== Insights Generator Unit Tests ====================

def test_insights_generator_consistency_calculation():
    """Test consistency score calculation"""
    consistent = [100, 102, 98, 101, 99]
    inconsistent = [50, 100, 30, 90, 20]
    
    consistent_score = insights_generator._calculate_consistency(consistent)
    inconsistent_score = insights_generator._calculate_consistency(inconsistent)
    
    assert consistent_score > inconsistent_score
    assert 0 <= consistent_score <= 1


def test_insights_generator_wellbeing_recommendations():
    """Test wellbeing recommendation generation"""
    recs = insights_generator._get_wellbeing_recommendations(
        screen_score=30,  # Low
        break_score=40,   # Low
        focus_quality=90,  # High
        notification_score=80  # High
    )
    
    assert len(recs) > 0
    # Should recommend reducing screen time and taking more breaks
    assert any('screen time' in rec.lower() for rec in recs)
    assert any('break' in rec.lower() for rec in recs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
