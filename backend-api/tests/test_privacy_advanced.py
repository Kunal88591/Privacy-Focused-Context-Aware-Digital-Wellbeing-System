"""
Tests for Advanced Privacy Features (Day 9)
Tests VPN, caller masking, location spoofing, network monitoring, and privacy scoring
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.vpn_manager import vpn_manager, VPNProtocol, VPNStatus
from app.services.caller_masking import caller_masking, CallType
from app.services.location_spoofing import location_spoofing, LocationMode
from app.services.network_monitor import network_monitor, ThreatLevel, ThreatType
from app.services.privacy_scoring import privacy_scoring


client = TestClient(app)


# ============ VPN Manager Tests ============

@pytest.mark.asyncio
async def test_vpn_connect():
    """Test VPN connection"""
    result = await vpn_manager.connect("us-east-1", VPNProtocol.OPENVPN)
    assert result["success"] is True
    assert result["status"] == "connected"
    assert "server" in result


@pytest.mark.asyncio
async def test_vpn_status():
    """Test getting VPN status"""
    await vpn_manager.connect("us-east-1", VPNProtocol.OPENVPN)
    status = await vpn_manager.get_status()
    assert status["connected"] is True
    assert "uptime" in status


@pytest.mark.asyncio
async def test_vpn_disconnect():
    """Test VPN disconnection"""
    await vpn_manager.connect("us-east-1", VPNProtocol.OPENVPN)
    result = await vpn_manager.disconnect()
    assert result["success"] is True
    assert result["status"] == "disconnected"


@pytest.mark.asyncio
async def test_vpn_servers():
    """Test getting available VPN servers"""
    servers = await vpn_manager.get_available_servers()
    assert len(servers) > 0
    assert all("id" in s for s in servers)
    assert all("location" in s for s in servers)


@pytest.mark.asyncio
async def test_vpn_recommended_server():
    """Test getting recommended VPN server"""
    result = await vpn_manager.get_recommended_server("fastest")
    assert "server" in result
    assert "reason" in result


@pytest.mark.asyncio
async def test_vpn_kill_switch():
    """Test VPN kill switch"""
    enable_result = await vpn_manager.enable_kill_switch()
    assert enable_result["kill_switch_enabled"] is True
    
    disable_result = await vpn_manager.disable_kill_switch()
    assert disable_result["kill_switch_enabled"] is False


@pytest.mark.asyncio
async def test_vpn_leak_detection():
    """Test VPN leak detection"""
    await vpn_manager.connect("us-east-1", VPNProtocol.OPENVPN)
    result = await vpn_manager.check_for_leaks()
    assert "leaks_detected" in result
    assert "dns_leak" in result
    assert "ip_leak" in result
    assert "webrtc_leak" in result


# ============ Caller ID Masking Tests ============

@pytest.mark.asyncio
async def test_screen_call():
    """Test call screening"""
    result = await caller_masking.screen_call("+1234567890", "John Doe")
    assert "phone_number" in result
    assert "risk_score" in result
    assert "recommendation" in result
    assert 0 <= result["risk_score"] <= 100


@pytest.mark.asyncio
async def test_screen_spam_call():
    """Test screening known spam number"""
    # Add to spam database first
    await caller_masking.report_spam("+1999999999", CallType.SPAM)
    
    result = await caller_masking.screen_call("+1999999999", "Spam Caller")
    assert result["is_spam"] is True
    assert result["risk_score"] > 50


@pytest.mark.asyncio
async def test_block_number():
    """Test blocking a phone number"""
    result = await caller_masking.block_number("+1111111111")
    assert result["success"] is True
    assert result["blocked"] is True


@pytest.mark.asyncio
async def test_unblock_number():
    """Test unblocking a phone number"""
    await caller_masking.block_number("+1111111111")
    result = await caller_masking.unblock_number("+1111111111")
    assert result["success"] is True
    assert result["blocked"] is False


@pytest.mark.asyncio
async def test_report_spam():
    """Test reporting spam"""
    result = await caller_masking.report_spam("+1888888888", CallType.TELEMARKETER)
    assert result["success"] is True
    assert result["reported"] is True


@pytest.mark.asyncio
async def test_call_history():
    """Test getting call history"""
    await caller_masking.screen_call("+1234567890", "Test")
    history = await caller_masking.get_call_history(10)
    assert len(history) > 0
    assert "phone_number" in history[0]


@pytest.mark.asyncio
async def test_spam_statistics():
    """Test spam statistics"""
    stats = await caller_masking.get_spam_statistics()
    assert "total_calls_screened" in stats
    assert "spam_calls_blocked" in stats
    assert "block_rate" in stats


@pytest.mark.asyncio
async def test_caller_masking():
    """Test enabling/disabling caller ID masking"""
    enable_result = await caller_masking.enable_masking()
    assert enable_result["masking_enabled"] is True
    
    disable_result = await caller_masking.disable_masking()
    assert disable_result["masking_enabled"] is False


# ============ Location Spoofing Tests ============

@pytest.mark.asyncio
async def test_set_location_mode():
    """Test setting location privacy mode"""
    result = await location_spoofing.set_mode(LocationMode.SPOOFED)
    assert result["success"] is True
    assert result["mode"] == "spoofed"


@pytest.mark.asyncio
async def test_set_real_location():
    """Test setting real location"""
    result = await location_spoofing.set_real_location(40.7128, -74.0060)
    assert result["success"] is True
    assert "real_location" in result


@pytest.mark.asyncio
async def test_set_spoofed_location():
    """Test setting spoofed location"""
    result = await location_spoofing.set_spoofed_location(51.5074, -0.1278)
    assert result["success"] is True
    assert "spoofed_location" in result


@pytest.mark.asyncio
async def test_get_location():
    """Test getting location based on mode"""
    await location_spoofing.set_mode(LocationMode.REAL_LOCATION)
    await location_spoofing.set_real_location(40.7128, -74.0060)
    
    result = await location_spoofing.get_location()
    assert "latitude" in result
    assert "longitude" in result
    assert "mode" in result


@pytest.mark.asyncio
async def test_select_city_location():
    """Test selecting a city location"""
    result = await location_spoofing.select_city_location("New York")
    assert result["success"] is True
    assert result["city"] == "New York"


@pytest.mark.asyncio
async def test_available_cities():
    """Test getting available cities"""
    cities = await location_spoofing.get_available_cities()
    assert len(cities) > 0
    assert "New York" in cities


@pytest.mark.asyncio
async def test_location_status():
    """Test getting location status"""
    status = await location_spoofing.get_status()
    assert "current_mode" in status
    assert "privacy_active" in status


@pytest.mark.asyncio
async def test_location_privacy_verification():
    """Test location privacy verification"""
    await location_spoofing.set_mode(LocationMode.SPOOFED)
    result = await location_spoofing.verify_location_privacy()
    assert "privacy_verified" in result


# ============ Network Security Monitor Tests ============

@pytest.mark.asyncio
async def test_start_monitoring():
    """Test starting network monitoring"""
    result = await network_monitor.start_monitoring()
    assert result["success"] is True
    assert result["monitoring"] is True


@pytest.mark.asyncio
async def test_stop_monitoring():
    """Test stopping network monitoring"""
    await network_monitor.start_monitoring()
    result = await network_monitor.stop_monitoring()
    assert result["success"] is True
    assert result["monitoring"] is False


@pytest.mark.asyncio
async def test_network_scan():
    """Test network scanning"""
    await network_monitor.start_monitoring()
    result = await network_monitor.scan_network_traffic()
    assert "threats_detected" in result
    assert "scan_duration" in result


@pytest.mark.asyncio
async def test_get_threats():
    """Test getting detected threats"""
    await network_monitor.start_monitoring()
    threats = await network_monitor.get_threats(10)
    assert isinstance(threats, list)


@pytest.mark.asyncio
async def test_threat_statistics():
    """Test threat statistics"""
    stats = await network_monitor.get_threat_statistics()
    assert "total_threats" in stats
    assert "threats_by_type" in stats
    assert "threats_by_level" in stats


@pytest.mark.asyncio
async def test_block_domain():
    """Test blocking a domain"""
    result = await network_monitor.block_domain("malicious.com", "Test block")
    assert result["success"] is True
    assert result["blocked"] is True


@pytest.mark.asyncio
async def test_unblock_domain():
    """Test unblocking a domain"""
    await network_monitor.block_domain("example.com", "Test")
    result = await network_monitor.unblock_domain("example.com")
    assert result["success"] is True
    assert result["blocked"] is False


@pytest.mark.asyncio
async def test_whitelist_domain():
    """Test whitelisting a domain"""
    result = await network_monitor.whitelist_domain("trusted.com")
    assert result["success"] is True
    assert result["whitelisted"] is True


@pytest.mark.asyncio
async def test_check_domain_safety():
    """Test checking domain safety"""
    result = await network_monitor.check_domain_safety("google.com")
    assert "domain" in result
    assert "is_safe" in result


@pytest.mark.asyncio
async def test_network_statistics():
    """Test network statistics"""
    stats = await network_monitor.get_network_statistics()
    assert "total_connections" in stats
    assert "blocked_connections" in stats


@pytest.mark.asyncio
async def test_security_score():
    """Test security score calculation"""
    result = await network_monitor.get_security_score()
    assert "score" in result
    assert 0 <= result["score"] <= 100


@pytest.mark.asyncio
async def test_firewall_management():
    """Test firewall enable/disable"""
    enable_result = await network_monitor.enable_firewall()
    assert enable_result["firewall_enabled"] is True
    
    disable_result = await network_monitor.disable_firewall()
    assert disable_result["firewall_enabled"] is False


@pytest.mark.asyncio
async def test_firewall_status():
    """Test getting firewall status"""
    status = await network_monitor.get_firewall_status()
    assert "enabled" in status
    assert "rules_count" in status


# ============ Privacy Scoring Tests ============

@pytest.mark.asyncio
async def test_calculate_privacy_score():
    """Test calculating overall privacy score"""
    result = await privacy_scoring.calculate_privacy_score()
    assert "overall_score" in result
    assert "component_scores" in result
    assert 0 <= result["overall_score"] <= 100


@pytest.mark.asyncio
async def test_privacy_score_components():
    """Test privacy score components"""
    result = await privacy_scoring.calculate_privacy_score()
    components = result["component_scores"]
    
    assert "vpn_score" in components
    assert "location_score" in components
    assert "network_score" in components
    assert "caller_score" in components


@pytest.mark.asyncio
async def test_score_history():
    """Test getting score history"""
    await privacy_scoring.calculate_privacy_score()
    history = await privacy_scoring.get_score_history(5)
    assert len(history) > 0
    assert "timestamp" in history[0]
    assert "score" in history[0]


@pytest.mark.asyncio
async def test_score_trend():
    """Test score trend analysis"""
    # Calculate scores multiple times
    for _ in range(3):
        await privacy_scoring.calculate_privacy_score()
    
    trend = await privacy_scoring.get_score_trend()
    assert "trend" in trend
    assert "average_score" in trend


# ============ API Endpoint Tests ============

def test_vpn_connect_endpoint():
    """Test VPN connect API endpoint"""
    response = client.post("/api/v1/privacy/vpn/connect", json={
        "server": "us-east-1",
        "protocol": "openvpn"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert data["server"] == "us-east-1"


def test_vpn_status_endpoint():
    """Test VPN status API endpoint"""
    response = client.get("/api/v1/privacy/vpn/status")
    assert response.status_code == 200


def test_screen_call_endpoint():
    """Test call screening API endpoint"""
    response = client.post("/api/v1/privacy/caller/screen", json={
        "phone_number": "+1234567890",
        "caller_name": "Test Caller"
    })
    assert response.status_code == 200
    assert "risk_score" in response.json()


def test_set_location_mode_endpoint():
    """Test location mode API endpoint"""
    response = client.post("/api/v1/privacy/location/mode", json={
        "mode": "spoofed"
    })
    assert response.status_code == 200


def test_network_scan_endpoint():
    """Test network scan API endpoint"""
    response = client.post("/api/v1/privacy/network/scan")
    assert response.status_code == 200


def test_privacy_score_endpoint():
    """Test privacy score API endpoint"""
    response = client.get("/api/v1/privacy/score")
    assert response.status_code == 200
    assert "overall_score" in response.json()


def test_privacy_health_endpoint():
    """Test privacy health check endpoint"""
    response = client.get("/api/v1/privacy/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
