"""
Privacy API endpoints
Handles VPN, caller ID masking, and privacy features
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Response models
class VPNStatusResponse(BaseModel):
    status: str  # "enabled" or "disabled"
    vpn_server: Optional[str] = None
    ip_address: Optional[str] = None

class PrivacyStatusResponse(BaseModel):
    vpn_enabled: bool
    caller_id_masked: bool
    location_spoofed: bool
    auto_wipe_armed: bool
    untrusted_network_count: int
    encryption_status: str

# Mock privacy state
privacy_state = {
    "vpn_enabled": False,
    "caller_id_masked": False,
    "location_spoofed": False,
    "auto_wipe_armed": True,
    "untrusted_network_count": 0,
}

@router.post("/vpn/enable", response_model=VPNStatusResponse)
async def enable_vpn():
    """Enable VPN for all traffic"""
    
    privacy_state["vpn_enabled"] = True
    
    return VPNStatusResponse(
        status="enabled",
        vpn_server="us-west-1.vpn.example.com",
        ip_address="10.8.0.5"
    )

@router.post("/vpn/disable", response_model=VPNStatusResponse)
async def disable_vpn():
    """Disable VPN"""
    
    privacy_state["vpn_enabled"] = False
    
    return VPNStatusResponse(
        status="disabled"
    )

@router.post("/mask-caller")
async def mask_caller_id(enable: bool = True):
    """Enable or disable caller ID masking"""
    
    privacy_state["caller_id_masked"] = enable
    
    return {
        "status": "enabled" if enable else "disabled",
        "message": "Caller ID masking updated"
    }

@router.post("/location-spoof")
async def toggle_location_spoofing(enable: bool = True):
    """Enable or disable location spoofing"""
    
    privacy_state["location_spoofed"] = enable
    
    return {
        "status": "enabled" if enable else "disabled",
        "message": "Location spoofing updated"
    }

@router.get("/status", response_model=PrivacyStatusResponse)
async def get_privacy_status():
    """Get current privacy status"""
    
    return PrivacyStatusResponse(
        vpn_enabled=privacy_state["vpn_enabled"],
        caller_id_masked=privacy_state["caller_id_masked"],
        location_spoofed=privacy_state["location_spoofed"],
        auto_wipe_armed=privacy_state["auto_wipe_armed"],
        untrusted_network_count=privacy_state["untrusted_network_count"],
        encryption_status="active"
    )

@router.post("/auto-wipe/test")
async def test_auto_wipe():
    """Test auto-wipe trigger (for demonstration)"""
    
    privacy_state["untrusted_network_count"] += 1
    
    if privacy_state["untrusted_network_count"] >= 3:
        return {
            "status": "triggered",
            "message": "Auto-wipe triggered! Device data would be erased.",
            "count": privacy_state["untrusted_network_count"]
        }
    
    return {
        "status": "warning",
        "message": f"Untrusted network detected ({privacy_state['untrusted_network_count']}/3)",
        "count": privacy_state["untrusted_network_count"]
    }
