"""
Network Security Service - Network Monitoring and Threat Detection
Monitors network connections, detects threats, and provides security recommendations
"""

import re
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class ThreatLevel(str, Enum):
    """Network threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ConnectionType(str, Enum):
    """Type of network connection"""
    WIFI = "wifi"
    CELLULAR = "cellular"
    ETHERNET = "ethernet"
    VPN = "vpn"
    UNKNOWN = "unknown"


class NetworkSecurityService:
    """Network security monitoring and threat detection"""
    
    def __init__(self):
        # Active connections tracking
        self.active_connections = []
        
        # Threat database
        self.known_threats = self._load_threat_database()
        
        # Network statistics
        self.network_stats = {
            "total_connections": 0,
            "blocked_connections": 0,
            "suspicious_connections": 0,
            "data_transferred_mb": 0
        }
        
        # Security events log
        self.security_events = []
        
        # Whitelist and blacklist
        self.whitelist = set()
        self.blacklist = set()
    
    def _load_threat_database(self) -> Dict[str, Dict]:
        """Load known threat IP addresses and domains"""
        return {
            # Known malicious IPs/domains
            "malicious_ips": {
                "203.0.113.100": {"threat": "malware_server", "severity": ThreatLevel.CRITICAL},
                "198.51.100.50": {"threat": "phishing_site", "severity": ThreatLevel.HIGH},
                "192.0.2.25": {"threat": "botnet_c2", "severity": ThreatLevel.CRITICAL},
            },
            "malicious_domains": {
                "malicious-site.com": {"threat": "phishing", "severity": ThreatLevel.HIGH},
                "fake-bank.net": {"threat": "credential_theft", "severity": ThreatLevel.CRITICAL},
                "ad-tracker.io": {"threat": "tracking", "severity": ThreatLevel.MEDIUM},
            },
            "suspicious_ports": {
                1433: {"service": "SQL Server", "risk": "database_attack"},
                3389: {"service": "RDP", "risk": "remote_access"},
                22: {"service": "SSH", "risk": "brute_force"},
                23: {"service": "Telnet", "risk": "unencrypted"},
            }
        }
    
    async def scan_active_connections(self) -> Dict:
        """
        Scan current network connections for threats
        
        Returns:
            Scan results with threat analysis
        """
        try:
            # Get active network connections
            connections = await self._get_network_connections()
            
            threats_found = []
            suspicious_connections = []
            safe_connections = []
            
            for conn in connections:
                # Check against threat database
                threat_check = self._check_threat(conn)
                
                if threat_check["is_threat"]:
                    threats_found.append({
                        **conn,
                        **threat_check
                    })
                elif threat_check["is_suspicious"]:
                    suspicious_connections.append({
                        **conn,
                        **threat_check
                    })
                else:
                    safe_connections.append(conn)
            
            self.active_connections = connections
            
            return {
                "scan_time": datetime.now().isoformat(),
                "total_connections": len(connections),
                "threats_found": len(threats_found),
                "suspicious": len(suspicious_connections),
                "safe": len(safe_connections),
                "threats": threats_found,
                "suspicious_list": suspicious_connections,
                "security_score": self._calculate_connection_security_score(
                    len(connections), len(threats_found), len(suspicious_connections)
                )
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "scan_time": datetime.now().isoformat()
            }
    
    async def _get_network_connections(self) -> List[Dict]:
        """Get active network connections"""
        # In production, would use netstat, ss, or similar
        # Simulated connections for demo
        return [
            {
                "local_address": "192.168.1.100",
                "local_port": 54321,
                "remote_address": "93.184.216.34",  # example.com
                "remote_port": 443,
                "state": "ESTABLISHED",
                "protocol": "TCP",
                "process": "chrome"
            },
            {
                "local_address": "192.168.1.100",
                "local_port": 54322,
                "remote_address": "142.250.185.78",  # Google
                "remote_port": 443,
                "state": "ESTABLISHED",
                "protocol": "TCP",
                "process": "firefox"
            },
            {
                "local_address": "192.168.1.100",
                "local_port": 54323,
                "remote_address": "203.0.113.100",  # Malicious (from threat DB)
                "remote_port": 8080,
                "state": "ESTABLISHED",
                "protocol": "TCP",
                "process": "unknown"
            }
        ]
    
    def _check_threat(self, connection: Dict) -> Dict:
        """Check if connection is a threat"""
        remote_ip = connection.get("remote_address")
        remote_port = connection.get("remote_port")
        
        # Check IP against threat database
        if remote_ip in self.known_threats["malicious_ips"]:
            threat_info = self.known_threats["malicious_ips"][remote_ip]
            return {
                "is_threat": True,
                "is_suspicious": False,
                "threat_type": threat_info["threat"],
                "severity": threat_info["severity"],
                "recommendation": "Block immediately",
                "details": f"Known malicious IP: {threat_info['threat']}"
            }
        
        # Check blacklist
        if remote_ip in self.blacklist:
            return {
                "is_threat": True,
                "is_suspicious": False,
                "threat_type": "blacklisted",
                "severity": ThreatLevel.HIGH,
                "recommendation": "Blocked by user",
                "details": "IP is in your blacklist"
            }
        
        # Check whitelist
        if remote_ip in self.whitelist:
            return {
                "is_threat": False,
                "is_suspicious": False,
                "status": "trusted",
                "details": "IP is in your whitelist"
            }
        
        # Check suspicious ports
        if remote_port in self.known_threats["suspicious_ports"]:
            port_info = self.known_threats["suspicious_ports"][remote_port]
            return {
                "is_threat": False,
                "is_suspicious": True,
                "threat_type": "suspicious_port",
                "severity": ThreatLevel.MEDIUM,
                "service": port_info["service"],
                "risk": port_info["risk"],
                "recommendation": "Monitor connection",
                "details": f"Connection to potentially risky port: {port_info['service']}"
            }
        
        # Check for unusual patterns
        if connection.get("process") == "unknown":
            return {
                "is_threat": False,
                "is_suspicious": True,
                "threat_type": "unknown_process",
                "severity": ThreatLevel.LOW,
                "recommendation": "Investigate process",
                "details": "Connection from unknown process"
            }
        
        # Safe connection
        return {
            "is_threat": False,
            "is_suspicious": False,
            "status": "safe"
        }
    
    def _calculate_connection_security_score(self, total: int, threats: int, suspicious: int) -> int:
        """Calculate security score based on connections"""
        if total == 0:
            return 100
        
        threat_penalty = (threats / total) * 60
        suspicious_penalty = (suspicious / total) * 30
        
        score = 100 - threat_penalty - suspicious_penalty
        return max(0, int(score))
    
    async def monitor_network_traffic(self, duration_seconds: int = 60) -> Dict:
        """
        Monitor network traffic for specified duration
        
        Args:
            duration_seconds: Duration to monitor
            
        Returns:
            Traffic analysis results
        """
        # Simulated traffic monitoring
        await asyncio.sleep(min(duration_seconds, 5))  # Demo simulation
        
        return {
            "monitoring_duration_seconds": duration_seconds,
            "total_packets": 15234,
            "total_bytes": 45623421,
            "total_mb": 43.5,
            "upload_mb": 5.2,
            "download_mb": 38.3,
            "protocols": {
                "TCP": 12456,
                "UDP": 2345,
                "ICMP": 433
            },
            "top_destinations": [
                {"domain": "google.com", "packets": 3421, "mb": 12.3},
                {"domain": "cloudflare.com", "packets": 2134, "mb": 8.7},
                {"domain": "github.com", "packets": 1876, "mb": 6.5}
            ],
            "security_events": len([e for e in self.security_events if 
                                  (datetime.now() - datetime.fromisoformat(e["timestamp"])).seconds < duration_seconds])
        }
    
    def detect_dns_leak(self) -> Dict:
        """
        Check for DNS leaks
        
        Returns:
            DNS leak detection results
        """
        # In production, would check DNS queries against VPN DNS servers
        # Simulated for demo
        
        using_vpn = False  # Would check actual VPN status
        dns_servers = ["8.8.8.8", "8.8.4.4"]  # Would get from system
        
        is_leaking = using_vpn and any(dns in ["8.8.8.8", "1.1.1.1"] for dns in dns_servers)
        
        return {
            "dns_leak_detected": is_leaking,
            "dns_servers": dns_servers,
            "vpn_active": using_vpn,
            "severity": ThreatLevel.HIGH if is_leaking else ThreatLevel.INFO,
            "recommendation": "Use VPN DNS servers" if is_leaking else "DNS configuration is secure",
            "details": {
                "your_dns": dns_servers,
                "expected_vpn_dns": ["10.0.0.1", "10.0.0.2"] if using_vpn else None
            }
        }
    
    def detect_mitm_attack(self) -> Dict:
        """
        Detect potential Man-in-the-Middle (MITM) attacks
        
        Returns:
            MITM detection results
        """
        # Check for SSL/TLS issues, certificate warnings, etc.
        # Simulated for demo
        
        indicators = []
        score = 0
        
        # Check 1: Certificate warnings
        has_cert_warnings = False
        if has_cert_warnings:
            indicators.append("SSL certificate warnings detected")
            score += 40
        
        # Check 2: Unusual gateway
        default_gateway = "192.168.1.1"
        expected_gateway = "192.168.1.1"
        if default_gateway != expected_gateway:
            indicators.append("Unexpected default gateway")
            score += 30
        
        # Check 3: ARP spoofing detection
        arp_spoofing = False
        if arp_spoofing:
            indicators.append("Possible ARP spoofing")
            score += 50
        
        mitm_detected = score >= 40
        
        return {
            "mitm_detected": mitm_detected,
            "confidence": score,
            "indicators": indicators,
            "severity": ThreatLevel.CRITICAL if score >= 70 else ThreatLevel.MEDIUM if score >= 40 else ThreatLevel.LOW,
            "recommendation": "Disconnect immediately and scan network" if mitm_detected else "Network appears secure",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_network_encryption(self) -> Dict:
        """
        Check if network connections are encrypted
        
        Returns:
            Encryption analysis
        """
        # Analyze active connections for encryption
        encrypted_count = 0
        unencrypted_count = 0
        
        for conn in self.active_connections:
            port = conn.get("remote_port")
            # Common encrypted ports
            if port in [443, 22, 993, 995, 465]:
                encrypted_count += 1
            # Common unencrypted ports
            elif port in [80, 21, 23, 25]:
                unencrypted_count += 1
        
        total = encrypted_count + unencrypted_count
        encryption_percentage = (encrypted_count / total * 100) if total > 0 else 0
        
        return {
            "encrypted_connections": encrypted_count,
            "unencrypted_connections": unencrypted_count,
            "encryption_percentage": round(encryption_percentage, 1),
            "grade": "A" if encryption_percentage >= 90 else "B" if encryption_percentage >= 70 else "C" if encryption_percentage >= 50 else "F",
            "recommendation": "Good encryption coverage" if encryption_percentage >= 80 else "Increase use of HTTPS and encrypted protocols",
            "unencrypted_protocols": ["HTTP", "FTP"] if unencrypted_count > 0 else []
        }
    
    def add_to_blacklist(self, ip_or_domain: str, reason: Optional[str] = None) -> Dict:
        """Add IP or domain to blacklist"""
        self.blacklist.add(ip_or_domain)
        
        # Log security event
        self.security_events.append({
            "type": "blacklist_add",
            "target": ip_or_domain,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "blacklisted": ip_or_domain,
            "reason": reason,
            "total_blacklisted": len(self.blacklist)
        }
    
    def add_to_whitelist(self, ip_or_domain: str) -> Dict:
        """Add IP or domain to whitelist"""
        self.whitelist.add(ip_or_domain)
        
        return {
            "success": True,
            "whitelisted": ip_or_domain,
            "total_whitelisted": len(self.whitelist)
        }
    
    def get_security_events(self, hours: int = 24, severity: Optional[ThreatLevel] = None) -> List[Dict]:
        """
        Get security events from specified period
        
        Args:
            hours: Number of hours of history
            severity: Filter by severity level
            
        Returns:
            List of security events
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        events = self.security_events
        
        # Filter by severity if specified
        if severity:
            events = [e for e in events if e.get("severity") == severity]
        
        return events[-100:]  # Last 100 events
    
    def get_network_security_assessment(self) -> Dict:
        """
        Get comprehensive network security assessment
        
        Returns:
            Security score and recommendations
        """
        score = 100
        issues = []
        recommendations = []
        
        # Check for active threats
        if self.network_stats["suspicious_connections"] > 0:
            score -= 20
            issues.append(f"{self.network_stats['suspicious_connections']} suspicious connections detected")
            recommendations.append("Review and block suspicious connections")
        
        # DNS leak check
        dns_check = self.detect_dns_leak()
        if dns_check["dns_leak_detected"]:
            score -= 25
            issues.append("DNS leak detected")
            recommendations.append("Configure VPN DNS to prevent leaks")
        
        # MITM check
        mitm_check = self.detect_mitm_attack()
        if mitm_check["mitm_detected"]:
            score -= 40
            issues.append("Possible MITM attack detected")
            recommendations.append("Disconnect from network immediately")
        
        # Encryption check
        encryption_check = self.check_network_encryption()
        if encryption_check["encryption_percentage"] < 70:
            score -= 15
            issues.append("Low encryption coverage")
            recommendations.append("Use HTTPS and encrypted connections")
        
        return {
            "security_score": max(0, score),
            "max_score": 100,
            "grade": self._get_security_grade(score),
            "status": "secure" if score >= 80 else "vulnerable",
            "issues": issues,
            "recommendations": recommendations,
            "checks": {
                "dns_leak": not dns_check["dns_leak_detected"],
                "mitm_protected": not mitm_check["mitm_detected"],
                "encryption_adequate": encryption_check["encryption_percentage"] >= 70,
                "no_active_threats": self.network_stats["suspicious_connections"] == 0
            }
        }
    
    def _get_security_grade(self, score: int) -> str:
        """Convert security score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_network_insights(self) -> Dict:
        """Get insights about network security"""
        assessment = self.get_network_security_assessment()
        
        insights = []
        
        # Threat detection
        if self.network_stats["suspicious_connections"] > 0:
            insights.append({
                "type": "warning",
                "title": "Suspicious Activity",
                "message": f"{self.network_stats['suspicious_connections']} suspicious connections detected"
            })
        
        # Blacklist effectiveness
        if len(self.blacklist) > 0:
            insights.append({
                "type": "positive",
                "title": "Active Protection",
                "message": f"{len(self.blacklist)} threats blocked by blacklist"
            })
        
        # Recent security events
        recent_events = self.get_security_events(hours=1)
        if recent_events:
            insights.append({
                "type": "info",
                "title": "Recent Activity",
                "message": f"{len(recent_events)} security events in the last hour"
            })
        
        return {
            "insights": insights,
            "security_assessment": assessment,
            "statistics": self.network_stats,
            "active_protections": {
                "blacklist_count": len(self.blacklist),
                "whitelist_count": len(self.whitelist)
            }
        }


# Singleton instance
network_security_service = NetworkSecurityService()
