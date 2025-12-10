"""
Advanced Privacy API Endpoints
Provides API for VPN, caller masking, location spoofing, and network security
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

from app.services.vpn_manager import vpn_manager, VPNProtocol
from app.services.caller_masking import caller_masking, CallType
from app.services.location_spoofing import location_spoofing, LocationMode
from app.services.network_monitor import network_monitor, ThreatLevel
from app.services.privacy_scoring import privacy_scoring

router = APIRouter(prefix="/api/v1/privacy", tags=["Advanced Privacy"])


# Request/Response Models

class VPNConnectRequest(BaseModel):
    server: str = Field(..., description="VPN server ID")
    protocol: VPNProtocol = Field(VPNProtocol.OPENVPN, description="VPN protocol")


class CallScreenRequest(BaseModel):
    phone_number: str = Field(..., description="Incoming phone number")
    caller_name: Optional[str] = Field(None, description="Caller name if available")


class BlockNumberRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to block")


class ReportSpamRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to report")
    category: CallType = Field(CallType.SPAM, description="Spam category")


class SetLocationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")


class SetLocationModeRequest(BaseModel):
    mode: LocationMode = Field(..., description="Location privacy mode")


class BlockDomainRequest(BaseModel):
    domain: str = Field(..., description="Domain to block")
    reason: Optional[str] = Field("Manual block", description="Block reason")


# ============ VPN Endpoints ============

@router.post("/vpn/connect")
async def connect_vpn(request: VPNConnectRequest):
    """Connect to VPN server"""
    try:
        result = await vpn_manager.connect(request.server, request.protocol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VPN connection failed: {str(e)}")


@router.post("/vpn/disconnect")
async def disconnect_vpn():
    """Disconnect from VPN"""
    try:
        result = await vpn_manager.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VPN disconnection failed: {str(e)}")


@router.get("/vpn/status")
async def get_vpn_status():
    """Get VPN connection status"""
    try:
        result = await vpn_manager.get_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get VPN status: {str(e)}")


@router.get("/vpn/servers")
async def get_vpn_servers():
    """Get list of available VPN servers"""
    try:
        servers = await vpn_manager.get_available_servers()
        return {"servers": servers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get VPN servers: {str(e)}")


@router.get("/vpn/recommended-server")
async def get_recommended_server(criteria: str = "fastest"):
    """Get recommended VPN server"""
    try:
        result = await vpn_manager.get_recommended_server(criteria)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {str(e)}")


@router.post("/vpn/kill-switch/enable")
async def enable_kill_switch():
    """Enable VPN kill switch"""
    try:
        result = await vpn_manager.enable_kill_switch()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable kill switch: {str(e)}")


@router.post("/vpn/kill-switch/disable")
async def disable_kill_switch():
    """Disable VPN kill switch"""
    try:
        result = await vpn_manager.disable_kill_switch()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable kill switch: {str(e)}")


@router.get("/vpn/leak-test")
async def check_vpn_leaks():
    """Check for VPN leaks (DNS, IP, WebRTC)"""
    try:
        result = await vpn_manager.check_for_leaks()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Leak test failed: {str(e)}")


# ============ Caller ID Masking Endpoints ============

@router.post("/caller/screen")
async def screen_incoming_call(request: CallScreenRequest):
    """Screen an incoming call"""
    try:
        result = await caller_masking.screen_call(request.phone_number, request.caller_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call screening failed: {str(e)}")


@router.post("/caller/block")
async def block_phone_number(request: BlockNumberRequest):
    """Block a phone number"""
    try:
        result = await caller_masking.block_number(request.phone_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block number: {str(e)}")


@router.post("/caller/unblock")
async def unblock_phone_number(request: BlockNumberRequest):
    """Unblock a phone number"""
    try:
        result = await caller_masking.unblock_number(request.phone_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unblock number: {str(e)}")


@router.post("/caller/report-spam")
async def report_spam_number(request: ReportSpamRequest):
    """Report a number as spam"""
    try:
        result = await caller_masking.report_spam(request.phone_number, request.category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to report spam: {str(e)}")


@router.get("/caller/history")
async def get_call_history(limit: int = 50):
    """Get call screening history"""
    try:
        history = await caller_masking.get_call_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/caller/statistics")
async def get_spam_statistics():
    """Get spam call statistics"""
    try:
        stats = await caller_masking.get_spam_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/caller/masking/enable")
async def enable_caller_masking():
    """Enable caller ID masking for outgoing calls"""
    try:
        result = await caller_masking.enable_masking()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable masking: {str(e)}")


@router.post("/caller/masking/disable")
async def disable_caller_masking():
    """Disable caller ID masking for outgoing calls"""
    try:
        result = await caller_masking.disable_masking()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable masking: {str(e)}")


# ============ Location Spoofing Endpoints ============

@router.post("/location/mode")
async def set_location_mode(request: SetLocationModeRequest):
    """Set location privacy mode"""
    try:
        result = await location_spoofing.set_mode(request.mode)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set location mode: {str(e)}")


@router.post("/location/set-real")
async def set_real_location(request: SetLocationRequest):
    """Set real location (for tracking)"""
    try:
        result = await location_spoofing.set_real_location(request.latitude, request.longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set real location: {str(e)}")


@router.post("/location/set-spoofed")
async def set_spoofed_location(request: SetLocationRequest):
    """Set a specific spoofed location"""
    try:
        result = await location_spoofing.set_spoofed_location(request.latitude, request.longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set spoofed location: {str(e)}")


@router.get("/location/current")
async def get_current_location():
    """Get current location (respecting privacy mode)"""
    try:
        result = await location_spoofing.get_location()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location: {str(e)}")


@router.post("/location/city/{city}")
async def spoof_to_city(city: str):
    """Spoof location to a specific city"""
    try:
        result = await location_spoofing.select_city_location(city)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to spoof to city: {str(e)}")


@router.get("/location/cities")
async def get_available_cities():
    """Get list of available cities for spoofing"""
    try:
        cities = await location_spoofing.get_available_cities()
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cities: {str(e)}")


@router.get("/location/status")
async def get_location_status():
    """Get location spoofing status"""
    try:
        result = await location_spoofing.get_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location status: {str(e)}")


@router.get("/location/verify")
async def verify_location_privacy():
    """Verify location privacy is working"""
    try:
        result = await location_spoofing.verify_location_privacy()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ============ Network Security Endpoints ============

@router.post("/network/monitoring/start")
async def start_network_monitoring():
    """Start network security monitoring"""
    try:
        result = await network_monitor.start_monitoring()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/network/monitoring/stop")
async def stop_network_monitoring():
    """Stop network security monitoring"""
    try:
        result = await network_monitor.stop_monitoring()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.post("/network/scan")
async def scan_network():
    """Scan network traffic for threats"""
    try:
        result = await network_monitor.scan_network_traffic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network scan failed: {str(e)}")


@router.get("/network/threats")
async def get_threats(limit: int = 50, level: Optional[ThreatLevel] = None):
    """Get detected threats"""
    try:
        threats = await network_monitor.get_threats(limit, level)
        return {"threats": threats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threats: {str(e)}")


@router.get("/network/threat-statistics")
async def get_threat_statistics():
    """Get threat statistics"""
    try:
        stats = await network_monitor.get_threat_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.post("/network/domain/block")
async def block_domain(request: BlockDomainRequest):
    """Block a domain"""
    try:
        result = await network_monitor.block_domain(request.domain, request.reason)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block domain: {str(e)}")


@router.post("/network/domain/unblock")
async def unblock_domain(request: BlockDomainRequest):
    """Unblock a domain"""
    try:
        result = await network_monitor.unblock_domain(request.domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unblock domain: {str(e)}")


@router.post("/network/domain/whitelist")
async def whitelist_domain(request: BlockDomainRequest):
    """Add domain to whitelist"""
    try:
        result = await network_monitor.whitelist_domain(request.domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to whitelist domain: {str(e)}")


@router.get("/network/domain/check/{domain}")
async def check_domain_safety(domain: str):
    """Check if a domain is safe"""
    try:
        result = await network_monitor.check_domain_safety(domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain check failed: {str(e)}")


@router.get("/network/statistics")
async def get_network_statistics():
    """Get network statistics"""
    try:
        stats = await network_monitor.get_network_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network statistics: {str(e)}")


@router.get("/network/security-score")
async def get_network_security_score():
    """Get network security score"""
    try:
        result = await network_monitor.get_security_score()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate security score: {str(e)}")


@router.post("/network/firewall/enable")
async def enable_firewall():
    """Enable firewall protection"""
    try:
        result = await network_monitor.enable_firewall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable firewall: {str(e)}")


@router.post("/network/firewall/disable")
async def disable_firewall():
    """Disable firewall protection"""
    try:
        result = await network_monitor.disable_firewall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable firewall: {str(e)}")


@router.get("/network/firewall/status")
async def get_firewall_status():
    """Get firewall status"""
    try:
        result = await network_monitor.get_firewall_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get firewall status: {str(e)}")


# ============ Privacy Scoring Endpoints ============

@router.get("/score")
async def get_privacy_score():
    """Calculate comprehensive privacy score"""
    try:
        result = await privacy_scoring.calculate_privacy_score()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate privacy score: {str(e)}")


@router.get("/score/history")
async def get_score_history(limit: int = 10):
    """Get privacy score history"""
    try:
        history = await privacy_scoring.get_score_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get score history: {str(e)}")


@router.get("/score/trend")
async def get_score_trend():
    """Get privacy score trend analysis"""
    try:
        trend = await privacy_scoring.get_score_trend()
        return trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze trend: {str(e)}")


@router.get("/health")
async def privacy_health_check():
    """Check if all privacy services are ready"""
    return {
        "status": "healthy",
        "services": {
            "vpn_manager": "ready",
            "caller_masking": "ready",
            "location_spoofing": "ready",
            "network_monitor": "ready",
            "privacy_scoring": "ready"
        },
        "timestamp": datetime.now().isoformat()
    }
