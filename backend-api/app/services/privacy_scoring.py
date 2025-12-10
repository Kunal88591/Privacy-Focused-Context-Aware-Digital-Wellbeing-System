"""
Enhanced Privacy Scoring Service
Calculates comprehensive privacy score based on all privacy components
"""

import logging
from typing import Dict, List
from datetime import datetime
from app.services.vpn_manager import vpn_manager
from app.services.caller_masking import caller_masking
from app.services.location_spoofing import location_spoofing
from app.services.network_monitor import network_monitor

logger = logging.getLogger(__name__)


class PrivacyScoring:
    """Calculate and track comprehensive privacy scores"""
    
    def __init__(self):
        self.score_history = []
        self.weights = {
            "vpn": 0.30,  # 30% weight
            "caller_masking": 0.20,  # 20% weight
            "location_privacy": 0.25,  # 25% weight
            "network_security": 0.25  # 25% weight
        }
    
    async def calculate_privacy_score(self) -> Dict:
        """Calculate overall privacy score (0-100)"""
        
        # Get scores from each component
        vpn_score = await self._calculate_vpn_score()
        caller_score = await self._calculate_caller_score()
        location_score = await self._calculate_location_score()
        network_score = await self._calculate_network_score()
        
        # Calculate weighted total
        total_score = (
            vpn_score * self.weights["vpn"] +
            caller_score * self.weights["caller_masking"] +
            location_score * self.weights["location_privacy"] +
            network_score * self.weights["network_security"]
        )
        
        total_score = round(total_score, 1)
        
        # Determine privacy level
        privacy_level = self._get_privacy_level(total_score)
        
        # Get recommendations
        recommendations = await self._get_recommendations(
            vpn_score, caller_score, location_score, network_score
        )
        
        # Build result
        result = {
            "overall_score": total_score,
            "privacy_level": privacy_level,
            "component_scores": {
                "vpn": {
                    "score": vpn_score,
                    "weight": self.weights["vpn"],
                    "contribution": round(vpn_score * self.weights["vpn"], 1)
                },
                "caller_masking": {
                    "score": caller_score,
                    "weight": self.weights["caller_masking"],
                    "contribution": round(caller_score * self.weights["caller_masking"], 1)
                },
                "location_privacy": {
                    "score": location_score,
                    "weight": self.weights["location_privacy"],
                    "contribution": round(location_score * self.weights["location_privacy"], 1)
                },
                "network_security": {
                    "score": network_score,
                    "weight": self.weights["network_security"],
                    "contribution": round(network_score * self.weights["network_security"], 1)
                }
            },
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in history
        self.score_history.append(result)
        
        return result
    
    async def _calculate_vpn_score(self) -> float:
        """Calculate VPN privacy score"""
        try:
            status = await vpn_manager.get_status()
            
            score = 0
            
            # VPN connected
            if status["status"] == "connected":
                score += 70
                
                # Kill switch enabled
                if status.get("kill_switch_enabled"):
                    score += 15
                
                # No leaks detected
                leak_test = status.get("leak_test", {})
                if leak_test and not leak_test.get("has_leaks"):
                    score += 15
            else:
                score = 20  # Base score for having VPN available
            
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating VPN score: {e}")
            return 50  # Default score on error
    
    async def _calculate_caller_score(self) -> float:
        """Calculate caller masking privacy score"""
        try:
            # Check if masking is enabled
            score = 0
            
            if caller_masking.masking_enabled:
                score += 60
            else:
                score += 20
            
            # Get spam statistics
            stats = await caller_masking.get_spam_statistics()
            
            # Bonus for blocking spam
            if stats["total_calls"] > 0:
                blocked_percentage = stats.get("blocked_percentage", 0)
                score += min(blocked_percentage / 2, 20)  # Up to 20 points
            
            # Bonus for having blocklist
            if len(caller_masking.blocked_numbers) > 0:
                score += 10
            
            # Cap additional bonuses
            return min(score, 100)
            
        except Exception as e:
            logger.error(f"Error calculating caller score: {e}")
            return 50
    
    async def _calculate_location_score(self) -> float:
        """Calculate location privacy score"""
        try:
            status = await location_spoofing.get_status()
            mode = status["mode"]
            
            # Score based on mode
            mode_scores = {
                "real": 0,
                "approximate": 50,
                "spoofed": 90,
                "random": 100
            }
            
            score = mode_scores.get(mode, 30)
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating location score: {e}")
            return 50
    
    async def _calculate_network_score(self) -> float:
        """Calculate network security score"""
        try:
            security_score_data = await network_monitor.get_security_score()
            score = security_score_data["security_score"]
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating network score: {e}")
            return 50
    
    def _get_privacy_level(self, score: float) -> str:
        """Get privacy level description"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical"
    
    async def _get_recommendations(self, vpn_score: float, caller_score: float,
                                   location_score: float, network_score: float) -> List[Dict]:
        """Get privacy improvement recommendations"""
        recommendations = []
        
        # VPN recommendations
        if vpn_score < 70:
            recommendations.append({
                "category": "vpn",
                "priority": "high",
                "message": "Enable VPN to protect your internet connection",
                "action": "connect_vpn"
            })
        elif vpn_score < 90:
            status = await vpn_manager.get_status()
            if not status.get("kill_switch_enabled"):
                recommendations.append({
                    "category": "vpn",
                    "priority": "medium",
                    "message": "Enable VPN kill switch for maximum protection",
                    "action": "enable_kill_switch"
                })
        
        # Caller masking recommendations
        if caller_score < 60:
            recommendations.append({
                "category": "caller_masking",
                "priority": "medium",
                "message": "Enable caller ID masking to protect your phone number",
                "action": "enable_caller_masking"
            })
        
        # Location recommendations
        if location_score < 50:
            recommendations.append({
                "category": "location",
                "priority": "high",
                "message": "Enable location spoofing to protect your real location",
                "action": "enable_location_spoofing"
            })
        
        # Network security recommendations
        if network_score < 70:
            recommendations.append({
                "category": "network",
                "priority": "high",
                "message": "Network security issues detected. Run a security scan",
                "action": "scan_network"
            })
        
        return recommendations
    
    async def get_score_history(self, limit: int = 10) -> List[Dict]:
        """Get privacy score history"""
        return self.score_history[-limit:]
    
    async def get_score_trend(self) -> Dict:
        """Analyze privacy score trend"""
        if len(self.score_history) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need more data to determine trend"
            }
        
        recent_scores = [s["overall_score"] for s in self.score_history[-10:]]
        
        # Simple trend analysis
        if len(recent_scores) >= 2:
            first_half = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
            second_half = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
            
            diff = second_half - first_half
            
            if diff > 5:
                trend = "improving"
            elif diff < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_score": recent_scores[-1],
            "previous_score": recent_scores[0],
            "change": round(recent_scores[-1] - recent_scores[0], 1),
            "message": self._get_trend_message(trend)
        }
    
    def _get_trend_message(self, trend: str) -> str:
        """Get message for trend"""
        messages = {
            "improving": "Your privacy score is improving! Keep up the good work.",
            "declining": "Your privacy score is declining. Review recommendations.",
            "stable": "Your privacy score is stable."
        }
        return messages.get(trend, "Unknown trend")


# Global privacy scoring instance
privacy_scoring = PrivacyScoring()
