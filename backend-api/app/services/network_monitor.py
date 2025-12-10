"""
Network Security Monitor
Monitors network traffic, detects threats, and provides security insights
"""

import asyncio
import random
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class ThreatLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(str, Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    SUSPICIOUS_DOMAIN = "suspicious_domain"
    PORT_SCAN = "port_scan"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DDOS = "ddos"


class NetworkSecurityMonitor:
    """Monitor network security and detect threats"""
    
    def __init__(self):
        self.monitoring_enabled = True
        self.threats_detected = []
        self.blocked_domains = set()
        self.whitelisted_domains = set()
        self.connection_log = []
        self.firewall_rules = []
        
    async def start_monitoring(self) -> Dict:
        """Start network monitoring"""
        self.monitoring_enabled = True
        logger.info("Network security monitoring started")
        
        return {
            "status": "monitoring",
            "started_at": datetime.now().isoformat(),
            "message": "Network security monitoring is active"
        }
    
    async def stop_monitoring(self) -> Dict:
        """Stop network monitoring"""
        self.monitoring_enabled = False
        logger.info("Network security monitoring stopped")
        
        return {
            "status": "stopped",
            "stopped_at": datetime.now().isoformat()
        }
    
    async def scan_network_traffic(self) -> Dict:
        """Scan current network traffic for threats"""
        if not self.monitoring_enabled:
            return {"status": "monitoring_disabled"}
        
        # Simulate network scan
        await asyncio.sleep(1)
        
        # Generate simulated scan results
        scan_results = {
            "scan_id": f"scan_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "connections_scanned": random.randint(50, 200),
            "threats_found": 0,
            "suspicious_connections": [],
            "safe_connections": 0
        }
        
        # Simulate finding threats (10% chance)
        if random.random() < 0.1:
            threat = await self._generate_threat()
            self.threats_detected.append(threat)
            scan_results["threats_found"] = 1
            scan_results["suspicious_connections"].append(threat)
        
        scan_results["safe_connections"] = scan_results["connections_scanned"] - scan_results["threats_found"]
        
        return scan_results
    
    async def _generate_threat(self) -> Dict:
        """Generate a simulated threat for testing"""
        threat_types = list(ThreatType)
        threat_levels = [ThreatLevel.LOW, ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        
        threat_type = random.choice(threat_types)
        threat_level = random.choice(threat_levels)
        
        threat = {
            "id": f"threat_{int(datetime.now().timestamp())}",
            "type": threat_type,
            "level": threat_level,
            "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "destination": "suspicious-domain.com",
            "detected_at": datetime.now().isoformat(),
            "description": self._get_threat_description(threat_type),
            "blocked": threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        }
        
        return threat
    
    def _get_threat_description(self, threat_type: ThreatType) -> str:
        """Get description for threat type"""
        descriptions = {
            ThreatType.MALWARE: "Malicious software detected attempting to download",
            ThreatType.PHISHING: "Phishing attempt detected - suspicious login page",
            ThreatType.SUSPICIOUS_DOMAIN: "Connection to known suspicious domain",
            ThreatType.PORT_SCAN: "Port scanning activity detected",
            ThreatType.DATA_LEAK: "Potential data exfiltration detected",
            ThreatType.UNAUTHORIZED_ACCESS: "Unauthorized access attempt",
            ThreatType.DDOS: "DDoS attack pattern detected"
        }
        return descriptions.get(threat_type, "Unknown threat")
    
    async def get_threats(self, limit: int = 50, level: Optional[ThreatLevel] = None) -> List[Dict]:
        """Get detected threats"""
        threats = self.threats_detected[-limit:]
        
        if level:
            threats = [t for t in threats if t["level"] == level]
        
        return threats
    
    async def get_threat_statistics(self) -> Dict:
        """Get threat statistics"""
        total_threats = len(self.threats_detected)
        
        if total_threats == 0:
            return {
                "total_threats": 0,
                "by_level": {},
                "by_type": {},
                "blocked_count": 0
            }
        
        # Count by level
        level_counts = defaultdict(int)
        for threat in self.threats_detected:
            level_counts[threat["level"]] += 1
        
        # Count by type
        type_counts = defaultdict(int)
        for threat in self.threats_detected:
            type_counts[threat["type"]] += 1
        
        # Count blocked
        blocked_count = sum(1 for threat in self.threats_detected if threat["blocked"])
        
        return {
            "total_threats": total_threats,
            "by_level": dict(level_counts),
            "by_type": dict(type_counts),
            "blocked_count": blocked_count,
            "blocked_percentage": round((blocked_count / total_threats) * 100, 2)
        }
    
    async def block_domain(self, domain: str, reason: str = "Manual block") -> Dict:
        """Block a domain"""
        self.blocked_domains.add(domain)
        logger.info(f"Blocked domain: {domain}")
        
        return {
            "domain": domain,
            "status": "blocked",
            "reason": reason,
            "blocked_at": datetime.now().isoformat()
        }
    
    async def unblock_domain(self, domain: str) -> Dict:
        """Unblock a domain"""
        if domain in self.blocked_domains:
            self.blocked_domains.remove(domain)
            logger.info(f"Unblocked domain: {domain}")
            return {
                "domain": domain,
                "status": "unblocked"
            }
        else:
            return {
                "domain": domain,
                "status": "not_blocked"
            }
    
    async def whitelist_domain(self, domain: str) -> Dict:
        """Add domain to whitelist"""
        self.whitelisted_domains.add(domain)
        logger.info(f"Whitelisted domain: {domain}")
        
        return {
            "domain": domain,
            "status": "whitelisted",
            "whitelisted_at": datetime.now().isoformat()
        }
    
    async def get_blocked_domains(self) -> List[str]:
        """Get list of blocked domains"""
        return list(self.blocked_domains)
    
    async def get_whitelisted_domains(self) -> List[str]:
        """Get list of whitelisted domains"""
        return list(self.whitelisted_domains)
    
    async def check_domain_safety(self, domain: str) -> Dict:
        """Check if a domain is safe"""
        if domain in self.blocked_domains:
            return {
                "domain": domain,
                "safe": False,
                "status": "blocked",
                "reason": "Domain is in blocklist"
            }
        
        if domain in self.whitelisted_domains:
            return {
                "domain": domain,
                "safe": True,
                "status": "whitelisted",
                "reason": "Domain is trusted"
            }
        
        # Simulate domain reputation check
        risk_score = await self._calculate_domain_risk(domain)
        
        return {
            "domain": domain,
            "safe": risk_score < 50,
            "risk_score": risk_score,
            "status": "analyzed",
            "recommendation": "block" if risk_score >= 70 else "caution" if risk_score >= 40 else "allow"
        }
    
    async def _calculate_domain_risk(self, domain: str) -> int:
        """Calculate risk score for a domain (0-100)"""
        risk_score = 0
        
        # Check for suspicious patterns
        suspicious_keywords = ['download', 'free', 'prize', 'winner', 'urgent', 'verify', 'account']
        for keyword in suspicious_keywords:
            if keyword in domain.lower():
                risk_score += 15
        
        # Check TLD
        suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.pw']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            risk_score += 20
        
        # Check for unusual characters
        if any(char in domain for char in ['_', '-' * 3]):
            risk_score += 10
        
        # Simulate reputation check (random for demo)
        risk_score += random.randint(0, 30)
        
        return min(risk_score, 100)
    
    async def get_network_statistics(self) -> Dict:
        """Get overall network statistics"""
        # Simulated network stats
        return {
            "uptime_hours": random.uniform(1, 100),
            "total_connections": random.randint(1000, 10000),
            "active_connections": random.randint(10, 100),
            "data_sent_mb": round(random.uniform(100, 5000), 2),
            "data_received_mb": round(random.uniform(500, 10000), 2),
            "average_latency_ms": random.randint(20, 150),
            "packet_loss_percentage": round(random.uniform(0, 2), 2)
        }
    
    async def enable_firewall(self) -> Dict:
        """Enable firewall protection"""
        logger.info("Firewall enabled")
        
        return {
            "firewall_enabled": True,
            "message": "Firewall protection is active",
            "enabled_at": datetime.now().isoformat()
        }
    
    async def disable_firewall(self) -> Dict:
        """Disable firewall protection"""
        logger.info("Firewall disabled")
        
        return {
            "firewall_enabled": False,
            "message": "Firewall protection is disabled",
            "disabled_at": datetime.now().isoformat()
        }
    
    async def get_firewall_status(self) -> Dict:
        """Get firewall status"""
        return {
            "enabled": True,  # Default enabled
            "rules_count": len(self.firewall_rules),
            "blocked_connections_today": random.randint(0, 50),
            "last_updated": datetime.now().isoformat()
        }
    
    async def add_firewall_rule(self, rule: Dict) -> Dict:
        """Add a firewall rule"""
        rule["id"] = f"rule_{len(self.firewall_rules) + 1}"
        rule["created_at"] = datetime.now().isoformat()
        
        self.firewall_rules.append(rule)
        logger.info(f"Added firewall rule: {rule['id']}")
        
        return {
            "rule": rule,
            "status": "added"
        }
    
    async def get_security_score(self) -> Dict:
        """Calculate overall network security score"""
        score = 100
        
        # Deduct points for threats
        threat_count = len(self.threats_detected)
        score -= min(threat_count * 2, 30)
        
        # Deduct points for critical threats
        critical_threats = sum(1 for t in self.threats_detected if t["level"] == ThreatLevel.CRITICAL)
        score -= critical_threats * 10
        
        # Bonus for monitoring enabled
        if self.monitoring_enabled:
            score += 0  # No change, baseline
        else:
            score -= 20
        
        score = max(0, min(score, 100))
        
        return {
            "security_score": score,
            "level": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor",
            "threats_detected": threat_count,
            "monitoring_active": self.monitoring_enabled,
            "timestamp": datetime.now().isoformat()
        }


# Global network security monitor instance
network_monitor = NetworkSecurityMonitor()
