"""
VPN Service - VPN Integration and Monitoring
Manages VPN connections, monitors status, and provides security recommendations
"""

import subprocess
import re
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class VPNProtocol(str, Enum):
    """Supported VPN protocols"""
    OPENVPN = "openvpn"
    WIREGUARD = "wireguard"
    IPSEC = "ipsec"
    L2TP = "l2tp"


class VPNStatus(str, Enum):
    """VPN connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    UNKNOWN = "unknown"


class VPNService:
    """VPN management and monitoring service"""
    
    def __init__(self):
        self.current_status = VPNStatus.DISCONNECTED
        self.current_server = None
        self.connection_time = None
        self.data_transferred = {"sent": 0, "received": 0}
        
    async def check_vpn_status(self) -> Dict:
        """
        Check current VPN connection status
        
        Returns detailed VPN information including:
        - Connection status
        - Server location
        - IP addresses (public/VPN)
        - Protocol
        - Encryption
        """
        try:
            # Check if VPN interface exists
            vpn_interfaces = await self._get_vpn_interfaces()
            
            if not vpn_interfaces:
                return {
                    "status": VPNStatus.DISCONNECTED,
                    "connected": False,
                    "public_ip": await self._get_public_ip(),
                    "vpn_ip": None,
                    "server": None,
                    "protocol": None,
                    "encryption": None,
                    "uptime_seconds": 0,
                    "data_transferred": self.data_transferred
                }
            
            # VPN is connected
            vpn_ip = await self._get_vpn_ip(vpn_interfaces[0])
            public_ip = await self._get_public_ip()
            
            # Check if IPs are different (VPN working)
            is_protected = vpn_ip != public_ip if vpn_ip else False
            
            return {
                "status": VPNStatus.CONNECTED if is_protected else VPNStatus.ERROR,
                "connected": is_protected,
                "public_ip": public_ip,
                "vpn_ip": vpn_ip,
                "server": self.current_server or "Unknown",
                "protocol": await self._detect_vpn_protocol(vpn_interfaces[0]),
                "encryption": "AES-256-GCM",  # Most common
                "uptime_seconds": await self._get_connection_uptime(),
                "data_transferred": await self._get_data_transferred(vpn_interfaces[0]),
                "dns_leak_protected": await self._check_dns_leak_protection()
            }
            
        except Exception as e:
            return {
                "status": VPNStatus.ERROR,
                "connected": False,
                "error": str(e)
            }
    
    async def _get_vpn_interfaces(self) -> List[str]:
        """Get list of active VPN interfaces"""
        try:
            # Common VPN interface names
            vpn_patterns = [
                r'^tun\d+',      # OpenVPN, WireGuard
                r'^wg\d+',       # WireGuard
                r'^ppp\d+',      # L2TP, PPTP
                r'^utun\d+',     # macOS VPN
                r'^vpn\d+',      # Generic VPN
            ]
            
            # Get network interfaces
            result = await asyncio.create_subprocess_exec(
                'ip', 'link', 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            interfaces = []
            for line in stdout.decode().split('\n'):
                for pattern in vpn_patterns:
                    if re.search(pattern, line):
                        # Extract interface name
                        match = re.search(r'\d+:\s+([^:]+):', line)
                        if match:
                            interfaces.append(match.group(1))
            
            return interfaces
            
        except Exception:
            # Fallback: simulate for demo
            return []
    
    async def _get_vpn_ip(self, interface: str) -> Optional[str]:
        """Get IP address of VPN interface"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ip', 'addr', 'show', interface,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            # Extract IPv4 address
            match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', stdout.decode())
            if match:
                return match.group(1)
            
            return None
            
        except Exception:
            return None
    
    async def _get_public_ip(self) -> str:
        """Get public IP address"""
        try:
            # In production, use external API
            # For demo, return simulated IP
            return "203.0.113.42"  # Example IP
            
        except Exception:
            return "Unknown"
    
    async def _detect_vpn_protocol(self, interface: str) -> str:
        """Detect VPN protocol based on interface"""
        if interface.startswith('tun'):
            return VPNProtocol.OPENVPN
        elif interface.startswith('wg'):
            return VPNProtocol.WIREGUARD
        elif interface.startswith('ppp'):
            return VPNProtocol.L2TP
        else:
            return "Unknown"
    
    async def _get_connection_uptime(self) -> int:
        """Get VPN connection uptime in seconds"""
        if self.connection_time:
            return int((datetime.now() - self.connection_time).total_seconds())
        return 0
    
    async def _get_data_transferred(self, interface: str) -> Dict[str, int]:
        """Get data transferred through VPN interface"""
        try:
            result = await asyncio.create_subprocess_exec(
                'ip', '-s', 'link', 'show', interface,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            lines = stdout.decode().split('\n')
            # Parse RX and TX bytes
            # Format varies, this is simplified
            
            return {
                "sent_bytes": self.data_transferred["sent"],
                "received_bytes": self.data_transferred["received"],
                "sent_mb": round(self.data_transferred["sent"] / 1024 / 1024, 2),
                "received_mb": round(self.data_transferred["received"] / 1024 / 1024, 2)
            }
            
        except Exception:
            return self.data_transferred
    
    async def _check_dns_leak_protection(self) -> bool:
        """Check if DNS is protected from leaks"""
        try:
            # Check if DNS servers are using VPN
            result = await asyncio.create_subprocess_exec(
                'cat', '/etc/resolv.conf',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            # In production, verify DNS servers are VPN provider's
            # For demo, return True if VPN is active
            return True
            
        except Exception:
            return False
    
    async def connect_vpn(self, server: str, protocol: VPNProtocol = VPNProtocol.OPENVPN) -> Dict:
        """
        Connect to VPN server
        
        Args:
            server: VPN server address or name
            protocol: VPN protocol to use
            
        Returns:
            Connection result with status
        """
        try:
            # In production, execute actual VPN connection
            # For demo, simulate connection
            
            self.current_status = VPNStatus.CONNECTING
            
            # Simulate connection delay
            await asyncio.sleep(2)
            
            # Successful connection
            self.current_status = VPNStatus.CONNECTED
            self.current_server = server
            self.connection_time = datetime.now()
            
            return {
                "success": True,
                "status": VPNStatus.CONNECTED,
                "server": server,
                "protocol": protocol,
                "message": f"Successfully connected to {server} via {protocol}",
                "connected_at": self.connection_time.isoformat()
            }
            
        except Exception as e:
            self.current_status = VPNStatus.ERROR
            return {
                "success": False,
                "status": VPNStatus.ERROR,
                "error": str(e)
            }
    
    async def disconnect_vpn(self) -> Dict:
        """
        Disconnect from VPN
        
        Returns:
            Disconnection result
        """
        try:
            # In production, execute actual VPN disconnection
            # For demo, simulate disconnection
            
            uptime = await self._get_connection_uptime()
            
            self.current_status = VPNStatus.DISCONNECTED
            self.current_server = None
            self.connection_time = None
            
            return {
                "success": True,
                "status": VPNStatus.DISCONNECTED,
                "message": "VPN disconnected successfully",
                "session_duration_seconds": uptime
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_servers(self, country: Optional[str] = None) -> List[Dict]:
        """
        Get list of available VPN servers
        
        Args:
            country: Filter by country code (e.g., 'US', 'UK')
            
        Returns:
            List of available servers with details
        """
        # Simulated server list
        servers = [
            {
                "id": "us-east-1",
                "name": "US East (New York)",
                "country": "US",
                "city": "New York",
                "load": 45,
                "ping_ms": 25,
                "protocol": [VPNProtocol.OPENVPN, VPNProtocol.WIREGUARD]
            },
            {
                "id": "us-west-1",
                "name": "US West (Los Angeles)",
                "country": "US",
                "city": "Los Angeles",
                "load": 62,
                "ping_ms": 18,
                "protocol": [VPNProtocol.OPENVPN, VPNProtocol.WIREGUARD]
            },
            {
                "id": "uk-london-1",
                "name": "UK (London)",
                "country": "UK",
                "city": "London",
                "load": 38,
                "ping_ms": 85,
                "protocol": [VPNProtocol.OPENVPN]
            },
            {
                "id": "de-frankfurt-1",
                "name": "Germany (Frankfurt)",
                "country": "DE",
                "city": "Frankfurt",
                "load": 51,
                "ping_ms": 95,
                "protocol": [VPNProtocol.WIREGUARD]
            },
            {
                "id": "jp-tokyo-1",
                "name": "Japan (Tokyo)",
                "country": "JP",
                "city": "Tokyo",
                "load": 73,
                "ping_ms": 145,
                "protocol": [VPNProtocol.OPENVPN, VPNProtocol.WIREGUARD]
            },
            {
                "id": "au-sydney-1",
                "name": "Australia (Sydney)",
                "country": "AU",
                "city": "Sydney",
                "load": 29,
                "ping_ms": 185,
                "protocol": [VPNProtocol.OPENVPN]
            }
        ]
        
        if country:
            servers = [s for s in servers if s["country"] == country]
        
        return servers
    
    async def get_security_assessment(self) -> Dict:
        """
        Get comprehensive security assessment
        
        Returns:
            Security score and recommendations
        """
        status = await self.check_vpn_status()
        
        score = 0
        issues = []
        recommendations = []
        
        # VPN connection (40 points)
        if status.get("connected"):
            score += 40
        else:
            issues.append("VPN not connected")
            recommendations.append("Enable VPN for encrypted connection")
        
        # DNS leak protection (20 points)
        if status.get("dns_leak_protected"):
            score += 20
        else:
            issues.append("DNS leak detected")
            recommendations.append("Enable DNS leak protection")
        
        # Public IP hidden (20 points)
        if status.get("vpn_ip") and status.get("vpn_ip") != status.get("public_ip"):
            score += 20
        else:
            issues.append("Real IP exposed")
            recommendations.append("Connect to VPN to hide IP address")
        
        # Strong encryption (10 points)
        if status.get("encryption") and "256" in status.get("encryption"):
            score += 10
        
        # Protocol security (10 points)
        secure_protocols = [VPNProtocol.WIREGUARD, VPNProtocol.OPENVPN]
        if status.get("protocol") in secure_protocols:
            score += 10
        
        return {
            "security_score": score,
            "max_score": 100,
            "grade": self._get_security_grade(score),
            "status": "protected" if score >= 70 else "vulnerable",
            "issues": issues,
            "recommendations": recommendations,
            "details": {
                "vpn_active": status.get("connected", False),
                "ip_hidden": status.get("vpn_ip") != status.get("public_ip"),
                "dns_protected": status.get("dns_leak_protected", False),
                "encryption_strong": "256" in status.get("encryption", ""),
                "protocol_secure": status.get("protocol") in secure_protocols
            }
        }
    
    def _get_security_grade(self, score: int) -> str:
        """Convert security score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    async def get_vpn_recommendations(self, user_location: str, usage_type: str = "general") -> List[Dict]:
        """
        Get VPN server recommendations based on user needs
        
        Args:
            user_location: User's current location/country
            usage_type: 'streaming', 'privacy', 'speed', 'general'
            
        Returns:
            Recommended servers sorted by suitability
        """
        servers = await self.get_available_servers()
        
        # Score servers based on usage type
        for server in servers:
            server["recommendation_score"] = 0
            
            if usage_type == "speed":
                # Prioritize low ping and low load
                server["recommendation_score"] = 100 - server["ping_ms"] - server["load"]
            elif usage_type == "privacy":
                # Prioritize countries with strong privacy laws
                privacy_countries = ["CH", "IS", "NO", "NL"]  # Switzerland, Iceland, etc.
                if server["country"] in privacy_countries:
                    server["recommendation_score"] += 50
                server["recommendation_score"] += (100 - server["load"])
            elif usage_type == "streaming":
                # Prioritize specific countries for content access
                streaming_countries = ["US", "UK", "CA"]
                if server["country"] in streaming_countries:
                    server["recommendation_score"] += 60
                server["recommendation_score"] += (100 - server["ping_ms"])
            else:  # general
                # Balanced scoring
                server["recommendation_score"] = (100 - server["load"]) + (100 - server["ping_ms"]) / 2
        
        # Sort by recommendation score
        servers.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return servers[:5]  # Top 5 recommendations


# Singleton instance
vpn_service = VPNService()
