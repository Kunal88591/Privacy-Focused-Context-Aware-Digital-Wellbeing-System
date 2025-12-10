"""
VPN Manager Service
Handles VPN connection, monitoring, and leak detection
"""

import asyncio
import subprocess
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class VPNStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class VPNProtocol(str, Enum):
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    IKEV2 = "ikev2"


class VPNManager:
    """Manage VPN connections and monitor for privacy leaks"""
    
    def __init__(self):
        self.status = VPNStatus.DISCONNECTED
        self.current_server = None
        self.connection_time = None
        self.protocol = VPNProtocol.OPENVPN
        self.kill_switch_enabled = True
        
    async def connect(self, server: str, protocol: VPNProtocol = VPNProtocol.OPENVPN) -> Dict:
        """Connect to VPN server"""
        try:
            logger.info(f"Connecting to VPN server: {server} using {protocol}")
            
            self.status = VPNStatus.CONNECTING
            self.protocol = protocol
            
            # Simulate VPN connection (in production, use actual VPN client)
            await asyncio.sleep(2)
            
            self.status = VPNStatus.CONNECTED
            self.current_server = server
            self.connection_time = datetime.now()
            
            # Get connection details
            details = await self._get_connection_details()
            
            logger.info(f"VPN connected successfully to {server}")
            
            return {
                "status": self.status,
                "server": self.current_server,
                "protocol": self.protocol,
                "connected_at": self.connection_time.isoformat(),
                "details": details
            }
            
        except Exception as e:
            logger.error(f"VPN connection failed: {str(e)}")
            self.status = VPNStatus.ERROR
            raise
    
    async def disconnect(self) -> Dict:
        """Disconnect from VPN"""
        try:
            if self.status != VPNStatus.CONNECTED:
                return {"status": "already_disconnected"}
            
            logger.info("Disconnecting VPN")
            
            # Simulate disconnection
            await asyncio.sleep(1)
            
            duration = (datetime.now() - self.connection_time).total_seconds()
            
            self.status = VPNStatus.DISCONNECTED
            server = self.current_server
            self.current_server = None
            self.connection_time = None
            
            logger.info("VPN disconnected")
            
            return {
                "status": self.status,
                "previous_server": server,
                "session_duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"VPN disconnection failed: {str(e)}")
            raise
    
    async def get_status(self) -> Dict:
        """Get current VPN status"""
        result = {
            "status": self.status,
            "server": self.current_server,
            "protocol": self.protocol,
            "kill_switch_enabled": self.kill_switch_enabled
        }
        
        if self.status == VPNStatus.CONNECTED:
            result["connected_at"] = self.connection_time.isoformat()
            duration = (datetime.now() - self.connection_time).total_seconds()
            result["uptime_seconds"] = duration
            
            # Check for leaks
            leak_test = await self.check_for_leaks()
            result["leak_test"] = leak_test
        
        return result
    
    async def check_for_leaks(self) -> Dict:
        """Check for DNS, IP, and WebRTC leaks"""
        if self.status != VPNStatus.CONNECTED:
            return {"status": "not_connected"}
        
        # Simulate leak detection (in production, use actual leak detection)
        leak_results = {
            "dns_leak": await self._check_dns_leak(),
            "ip_leak": await self._check_ip_leak(),
            "webrtc_leak": await self._check_webrtc_leak(),
            "timestamp": datetime.now().isoformat()
        }
        
        leak_results["has_leaks"] = any([
            leak_results["dns_leak"]["detected"],
            leak_results["ip_leak"]["detected"],
            leak_results["webrtc_leak"]["detected"]
        ])
        
        return leak_results
    
    async def _check_dns_leak(self) -> Dict:
        """Check for DNS leaks"""
        # Simulated DNS leak check
        return {
            "detected": False,
            "dns_servers": ["10.8.0.1"],
            "expected_region": "Netherlands",
            "actual_region": "Netherlands"
        }
    
    async def _check_ip_leak(self) -> Dict:
        """Check for IP leaks"""
        # Simulated IP leak check
        return {
            "detected": False,
            "vpn_ip": "185.220.101.42",
            "real_ip_hidden": True
        }
    
    async def _check_webrtc_leak(self) -> Dict:
        """Check for WebRTC leaks"""
        # Simulated WebRTC leak check
        return {
            "detected": False,
            "local_ips_exposed": [],
            "webrtc_blocked": True
        }
    
    async def _get_connection_details(self) -> Dict:
        """Get detailed connection information"""
        return {
            "ip_address": "185.220.101.42",
            "location": "Amsterdam, Netherlands",
            "isp": "M247 Ltd",
            "latency_ms": 45,
            "download_mbps": 95.3,
            "upload_mbps": 87.2
        }
    
    async def enable_kill_switch(self) -> Dict:
        """Enable VPN kill switch (blocks internet if VPN disconnects)"""
        self.kill_switch_enabled = True
        logger.info("VPN kill switch enabled")
        
        return {
            "kill_switch_enabled": True,
            "message": "Internet will be blocked if VPN disconnects"
        }
    
    async def disable_kill_switch(self) -> Dict:
        """Disable VPN kill switch"""
        self.kill_switch_enabled = False
        logger.info("VPN kill switch disabled")
        
        return {
            "kill_switch_enabled": False,
            "message": "Internet will remain accessible if VPN disconnects"
        }
    
    async def get_available_servers(self) -> List[Dict]:
        """Get list of available VPN servers"""
        # Simulated server list
        return [
            {
                "id": "nl-01",
                "name": "Netherlands #1",
                "location": "Amsterdam",
                "load": 45,
                "latency_ms": 35,
                "protocols": ["openvpn", "wireguard"]
            },
            {
                "id": "us-ny-01",
                "name": "United States (New York) #1",
                "location": "New York",
                "load": 62,
                "latency_ms": 120,
                "protocols": ["openvpn", "wireguard", "ikev2"]
            },
            {
                "id": "sg-01",
                "name": "Singapore #1",
                "location": "Singapore",
                "load": 38,
                "latency_ms": 180,
                "protocols": ["openvpn", "wireguard"]
            },
            {
                "id": "uk-01",
                "name": "United Kingdom #1",
                "location": "London",
                "load": 55,
                "latency_ms": 25,
                "protocols": ["openvpn", "wireguard"]
            },
            {
                "id": "jp-01",
                "name": "Japan #1",
                "location": "Tokyo",
                "load": 41,
                "latency_ms": 200,
                "protocols": ["openvpn", "wireguard"]
            }
        ]
    
    async def get_recommended_server(self, criteria: str = "fastest") -> Dict:
        """Get recommended server based on criteria"""
        servers = await self.get_available_servers()
        
        if criteria == "fastest":
            # Lowest latency
            recommended = min(servers, key=lambda x: x["latency_ms"])
        elif criteria == "least_loaded":
            # Lowest load
            recommended = min(servers, key=lambda x: x["load"])
        else:
            # Default to first server
            recommended = servers[0]
        
        return {
            "recommended_server": recommended,
            "criteria": criteria,
            "reason": f"Selected based on {criteria} criteria"
        }


# Global VPN manager instance
vpn_manager = VPNManager()
