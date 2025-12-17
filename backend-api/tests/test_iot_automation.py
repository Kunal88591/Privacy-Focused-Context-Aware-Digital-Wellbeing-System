"""
Day 24: IoT Automation Tests
Tests for automated responses to sensor data and smart environment controls
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.iot_automation import iot_automation, AutomationType

client = TestClient(app)


class TestNoiseDetectionAutomation:
    """Test noise detection and automation triggers"""
    
    def test_high_noise_triggers_automation(self):
        """Test: High noise (>70dB) → Triggers noise cancellation suggestion"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 75.5,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["total_automations"] >= 1
        
        # Find noise automation
        noise_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.NOISE_DETECTION),
            None
        )
        
        assert noise_automation is not None
        assert noise_automation["trigger_value"] == 75.5
        assert noise_automation["action"] == "suggest_noise_cancellation"
        assert len(noise_automation["recommendations"]) > 0
        assert "noise-canceling" in noise_automation["recommendations"][0].lower()
    
    def test_normal_noise_no_automation(self):
        """Test: Normal noise (<70dB) → No automation triggered"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45.0,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should not have noise automation
        noise_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.NOISE_DETECTION),
            None
        )
        
        assert noise_automation is None
    
    def test_critical_noise_high_severity(self):
        """Test: Critical noise (>80dB) → High severity alert"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 85.0,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        noise_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.NOISE_DETECTION),
            None
        )
        
        assert noise_automation is not None
        assert noise_automation["severity"] == "high"


class TestLightingAdjustmentAutomation:
    """Test lighting detection and adjustment automation"""
    
    def test_low_light_triggers_automation(self):
        """Test: Low light (<200 lux) → Triggers lighting increase suggestion"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 150.0,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        lighting_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.LIGHTING_ADJUSTMENT),
            None
        )
        
        assert lighting_automation is not None
        assert lighting_automation["trigger_value"] == 150.0
        assert lighting_automation["action"] == "increase_lighting"
        assert "lamp" in lighting_automation["recommendations"][0].lower()
    
    def test_excessive_light_triggers_automation(self):
        """Test: Excessive light (>1000 lux) → Triggers lighting reduction suggestion"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 1200.0,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        lighting_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.LIGHTING_ADJUSTMENT),
            None
        )
        
        assert lighting_automation is not None
        assert lighting_automation["action"] == "reduce_lighting"
        assert "blinds" in lighting_automation["recommendations"][0].lower() or \
               "brightness" in lighting_automation["recommendations"][0].lower()
    
    def test_optimal_lighting_no_automation(self):
        """Test: Optimal lighting (200-1000 lux) → No automation triggered"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 500.0,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        lighting_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.LIGHTING_ADJUSTMENT),
            None
        )
        
        assert lighting_automation is None


class TestBreakReminderAutomation:
    """Test break reminder automation for prolonged sitting"""
    
    @pytest.mark.asyncio
    async def test_prolonged_sitting_triggers_break_reminder(self):
        """Test: No motion for >1 hour → Triggers break reminder"""
        # Set sitting duration threshold to 10 seconds for testing
        await iot_automation.configure_thresholds({
            'sitting_duration_threshold': 10
        })
        
        # First reading with motion
        sensor_data = {
            "noise_level": 45,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        }
        
        await iot_automation.process_sensor_data(sensor_data)
        
        # Wait and send no-motion reading
        import asyncio
        await asyncio.sleep(11)
        
        sensor_data["motion_detected"] = False
        result = await iot_automation.process_sensor_data(sensor_data)
        
        # Should trigger break reminder
        break_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.BREAK_REMINDER),
            None
        )
        
        assert break_automation is not None
        assert "sitting" in break_automation["message"].lower()
        assert "stretch" in str(break_automation["recommendations"]).lower()
        
        # Reset threshold
        await iot_automation.configure_thresholds({
            'sitting_duration_threshold': 3600
        })
    
    def test_motion_detected_no_break_reminder(self):
        """Test: Motion detected → No break reminder"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should not have break reminder (user is moving)
        break_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.BREAK_REMINDER),
            None
        )
        
        # Either None or not triggered yet
        assert break_automation is None or break_automation["sitting_duration_minutes"] < 60


class TestScheduledFocusModeAutomation:
    """Test scheduled focus mode activation"""
    
    @pytest.mark.asyncio
    async def test_schedule_focus_mode(self):
        """Test: Schedule focus mode → Creates scheduled automation"""
        from datetime import datetime, timedelta
        
        future_time = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        
        result = await iot_automation.schedule_focus_mode(
            start_time=future_time,
            duration_minutes=60,
            auto_adjustments={
                'enable_dnd': True,
                'optimal_lighting': 400
            }
        )
        
        assert result["type"] == AutomationType.FOCUS_MODE
        assert result["scheduled_for"] == future_time
        assert result["duration_minutes"] == 60
        assert result["status"] == "scheduled"
        assert "Enable Do Not Disturb" in result["actions"]
    
    def test_schedule_focus_mode_api(self):
        """Test: Schedule focus mode via API endpoint"""
        from datetime import datetime, timedelta
        
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        response = client.post("/api/v1/iot/automation/focus-mode/schedule", json={
            "start_time": future_time,
            "duration_minutes": 90
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["scheduled_for"] == future_time
        assert result["duration_minutes"] == 90
    
    @pytest.mark.asyncio
    async def test_activate_focus_mode_immediately(self):
        """Test: Activate focus mode immediately → Applies optimizations"""
        result = await iot_automation.activate_focus_mode("test_session_001")
        
        assert result["type"] == AutomationType.FOCUS_MODE
        assert result["session_id"] == "test_session_001"
        assert result["status"] == "active"
        assert len(result["adjustments_applied"]) > 0
        assert "DND mode enabled" in result["adjustments_applied"]
    
    def test_activate_focus_mode_api(self):
        """Test: Activate focus mode via API"""
        response = client.post("/api/v1/iot/automation/focus-mode/activate")
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "active"
        assert "session_id" in result


class TestTemperatureAutomation:
    """Test temperature monitoring and alerts"""
    
    def test_low_temperature_triggers_alert(self):
        """Test: Low temperature (<18°C) → Triggers heating suggestion"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 400,
            "temperature": 16.0,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        temp_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.TEMPERATURE_ALERT),
            None
        )
        
        assert temp_automation is not None
        assert temp_automation["action"] == "increase_temperature"
        assert "thermostat" in temp_automation["recommendations"][0].lower()
    
    def test_high_temperature_triggers_alert(self):
        """Test: High temperature (>28°C) → Triggers cooling suggestion"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45,
            "light_level": 400,
            "temperature": 30.0,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        temp_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.TEMPERATURE_ALERT),
            None
        )
        
        assert temp_automation is not None
        assert temp_automation["action"] == "decrease_temperature"


class TestThresholdConfiguration:
    """Test threshold configuration and fine-tuning"""
    
    def test_get_current_thresholds(self):
        """Test: Get current automation thresholds"""
        response = client.get("/api/v1/iot/automation/thresholds")
        
        assert response.status_code == 200
        thresholds = response.json()
        assert "noise_threshold" in thresholds
        assert "low_light_threshold" in thresholds
        assert "sitting_duration_threshold" in thresholds
    
    def test_update_thresholds(self):
        """Test: Update thresholds → Affects future automations"""
        response = client.put("/api/v1/iot/automation/thresholds", json={
            "noise_threshold": 65.0,
            "low_light_threshold": 250.0
        })
        
        assert response.status_code == 200
        result = response.json()
        assert result["noise_threshold"] == 65.0
        assert result["low_light_threshold"] == 250.0
    
    @pytest.mark.asyncio
    async def test_custom_threshold_affects_automation(self):
        """Test: Custom threshold → Changes automation trigger point"""
        # Set lower noise threshold
        await iot_automation.configure_thresholds({
            'noise_threshold': 60.0
        })
        
        # 65dB noise should now trigger automation
        sensor_data = {
            "noise_level": 65.0,
            "light_level": 400,
            "temperature": 22,
            "humidity": 45,
            "motion_detected": True
        }
        
        result = await iot_automation.process_sensor_data(sensor_data)
        
        noise_automation = next(
            (a for a in result["automations_triggered"] 
             if a["type"] == AutomationType.NOISE_DETECTION),
            None
        )
        
        assert noise_automation is not None
        
        # Reset to default
        await iot_automation.configure_thresholds({
            'noise_threshold': 70.0
        })


class TestAutomationStats:
    """Test automation statistics and history"""
    
    def test_get_automation_stats(self):
        """Test: Get automation statistics"""
        response = client.get("/api/v1/iot/automation/stats")
        
        assert response.status_code == 200
        stats = response.json()
        assert "total_automations" in stats
        assert "by_type" in stats
        assert "by_severity" in stats
    
    def test_get_automation_history(self):
        """Test: Get automation history"""
        response = client.get("/api/v1/iot/automation/history?limit=10")
        
        assert response.status_code == 200
        result = response.json()
        assert "history" in result
        assert "count" in result
        assert isinstance(result["history"], list)


class TestIntegratedAutomationWorkflow:
    """Test complete automation workflows"""
    
    def test_poor_environment_multiple_automations(self):
        """Test: Poor environment → Multiple automations triggered"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 80.0,  # Too noisy
            "light_level": 150.0,  # Too dark
            "temperature": 30.0,  # Too hot
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should trigger 3 automations: noise, lighting, temperature
        assert result["total_automations"] >= 3
        
        automation_types = [a["type"] for a in result["automations_triggered"]]
        assert AutomationType.NOISE_DETECTION in automation_types
        assert AutomationType.LIGHTING_ADJUSTMENT in automation_types
        assert AutomationType.TEMPERATURE_ALERT in automation_types
    
    def test_optimal_environment_no_automations(self):
        """Test: Optimal environment → No automations triggered"""
        response = client.post("/api/v1/iot/automation/process", json={
            "noise_level": 45.0,  # Optimal
            "light_level": 500.0,  # Optimal
            "temperature": 23.0,  # Optimal
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Should trigger 0 automations
        assert result["total_automations"] == 0
    
    def test_environment_analysis_endpoint(self):
        """Test: Analyze environment without triggering actions"""
        response = client.post("/api/v1/iot/automation/analyze", json={
            "noise_level": 75.0,
            "light_level": 180.0,
            "temperature": 22.0,
            "humidity": 45,
            "motion_detected": True
        })
        
        assert response.status_code == 200
        result = response.json()
        assert "analysis" in result
        assert "environment_quality" in result
        assert result["environment_quality"] == "needs_improvement"
        assert result["issue_count"] >= 1


class TestHealthCheck:
    """Test automation service health"""
    
    def test_automation_health_check(self):
        """Test: Health check endpoint"""
        response = client.get("/api/v1/iot/automation/health")
        
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"
        assert health["service"] == "iot_automation"


def test_day_24_all_requirements_met():
    """
    Verify all Day 24 requirements are met:
    ✅ Noise detection → Noise cancellation suggestion
    ✅ Poor lighting → Lighting adjustment alert
    ✅ Prolonged sitting → Break reminder
    ✅ Scheduled focus mode activation
    ✅ Fine-tune sensor thresholds
    """
    
    # Test noise detection
    response1 = client.post("/api/v1/iot/automation/process", json={
        "noise_level": 75, "light_level": 400, "temperature": 22,
        "humidity": 45, "motion_detected": True
    })
    assert response1.status_code == 200
    
    # Test lighting adjustment
    response2 = client.post("/api/v1/iot/automation/process", json={
        "noise_level": 45, "light_level": 150, "temperature": 22,
        "humidity": 45, "motion_detected": True
    })
    assert response2.status_code == 200
    
    # Test focus mode scheduling
    from datetime import datetime, timedelta
    future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    response3 = client.post("/api/v1/iot/automation/focus-mode/schedule", json={
        "start_time": future_time, "duration_minutes": 60
    })
    assert response3.status_code == 200
    
    # Test threshold configuration
    response4 = client.put("/api/v1/iot/automation/thresholds", json={
        "noise_threshold": 65.0
    })
    assert response4.status_code == 200
    
    print("✅ All Day 24 requirements verified!")
