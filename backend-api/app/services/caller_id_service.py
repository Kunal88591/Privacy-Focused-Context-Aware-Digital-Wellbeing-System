"""
Caller ID Service - Caller ID Masking and Management
Provides caller identification, spam detection, and privacy protection
"""

import re
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class CallerType(str, Enum):
    """Type of caller"""
    CONTACT = "contact"
    SPAM = "spam"
    SCAM = "scam"
    TELEMARKETER = "telemarketer"
    UNKNOWN = "unknown"
    BLOCKED = "blocked"


class MaskingLevel(str, Enum):
    """Level of caller ID masking"""
    NONE = "none"
    PARTIAL = "partial"  # Show first 3 digits
    FULL = "full"        # Show nothing
    CUSTOM = "custom"    # Custom display


class CallerIDService:
    """Caller ID masking and spam detection service"""
    
    def __init__(self):
        # Simulated spam database
        self.spam_database = self._load_spam_database()
        
        # User's blocked numbers
        self.blocked_numbers = set()
        
        # Call history
        self.call_history = []
        
        # Masking settings
        self.masking_enabled = False
        self.masking_level = MaskingLevel.NONE
        self.custom_caller_id = None
    
    def _load_spam_database(self) -> Dict[str, Dict]:
        """Load spam/scam number database"""
        # Simulated spam database with known patterns
        return {
            # Known spam numbers (hashed for privacy)
            self._hash_number("1234567890"): {
                "type": CallerType.SPAM,
                "reports": 1523,
                "category": "Robocall",
                "last_reported": "2024-12-08"
            },
            self._hash_number("5555555555"): {
                "type": CallerType.TELEMARKETER,
                "reports": 892,
                "category": "Sales",
                "last_reported": "2024-12-09"
            },
            self._hash_number("9876543210"): {
                "type": CallerType.SCAM,
                "reports": 3421,
                "category": "IRS Scam",
                "last_reported": "2024-12-10"
            }
        }
    
    def _hash_number(self, number: str) -> str:
        """Hash phone number for privacy"""
        clean_number = re.sub(r'\D', '', number)
        return hashlib.sha256(clean_number.encode()).hexdigest()[:16]
    
    def identify_caller(self, phone_number: str, caller_name: Optional[str] = None) -> Dict:
        """
        Identify caller and detect spam/scam
        
        Args:
            phone_number: Caller's phone number
            caller_name: Caller's name if available
            
        Returns:
            Caller identification result
        """
        # Clean phone number
        clean_number = re.sub(r'\D', '', phone_number)
        hashed = self._hash_number(clean_number)
        
        # Check if blocked
        if clean_number in self.blocked_numbers:
            return {
                "phone_number": self._mask_number(clean_number),
                "original_number": phone_number,
                "caller_name": caller_name or "Blocked Number",
                "caller_type": CallerType.BLOCKED,
                "is_spam": True,
                "is_blocked": True,
                "confidence": 100,
                "recommendation": "block",
                "details": "Number is in your blocked list"
            }
        
        # Check spam database
        if hashed in self.spam_database:
            spam_info = self.spam_database[hashed]
            return {
                "phone_number": self._mask_number(clean_number),
                "original_number": phone_number,
                "caller_name": caller_name or "Spam Caller",
                "caller_type": spam_info["type"],
                "is_spam": True,
                "is_blocked": False,
                "confidence": min(100, spam_info["reports"] // 10),
                "reports_count": spam_info["reports"],
                "category": spam_info["category"],
                "last_reported": spam_info["last_reported"],
                "recommendation": "block" if spam_info["reports"] > 1000 else "ignore",
                "details": f"Reported {spam_info['reports']} times as {spam_info['category']}"
            }
        
        # Check for spam patterns
        spam_pattern_result = self._check_spam_patterns(clean_number)
        if spam_pattern_result["is_suspicious"]:
            return {
                "phone_number": self._mask_number(clean_number),
                "original_number": phone_number,
                "caller_name": caller_name or "Suspicious Number",
                "caller_type": CallerType.UNKNOWN,
                "is_spam": False,
                "is_suspicious": True,
                "confidence": spam_pattern_result["confidence"],
                "patterns_matched": spam_pattern_result["patterns"],
                "recommendation": "caution",
                "details": spam_pattern_result["reason"]
            }
        
        # Unknown but safe
        return {
            "phone_number": self._mask_number(clean_number),
            "original_number": phone_number,
            "caller_name": caller_name or "Unknown Caller",
            "caller_type": CallerType.UNKNOWN,
            "is_spam": False,
            "is_blocked": False,
            "is_suspicious": False,
            "confidence": 0,
            "recommendation": "answer",
            "details": "Number not found in spam database"
        }
    
    def _check_spam_patterns(self, number: str) -> Dict:
        """Check for common spam number patterns"""
        patterns_matched = []
        confidence = 0
        
        # Pattern 1: Repeated digits (e.g., 1111111111)
        if len(set(number)) <= 2:
            patterns_matched.append("repeated_digits")
            confidence += 30
        
        # Pattern 2: Sequential numbers (e.g., 1234567890)
        if self._is_sequential(number):
            patterns_matched.append("sequential")
            confidence += 25
        
        # Pattern 3: Known spam area codes
        spam_area_codes = ["800", "888", "900", "555"]
        if number[:3] in spam_area_codes:
            patterns_matched.append("spam_area_code")
            confidence += 20
        
        # Pattern 4: Too short or too long
        if len(number) < 10 or len(number) > 11:
            patterns_matched.append("invalid_length")
            confidence += 15
        
        # Pattern 5: Starts with 1 (toll-free)
        if number.startswith("1") and len(number) == 11:
            patterns_matched.append("toll_free")
            confidence += 10
        
        is_suspicious = confidence >= 40
        
        return {
            "is_suspicious": is_suspicious,
            "confidence": min(confidence, 100),
            "patterns": patterns_matched,
            "reason": f"Matched {len(patterns_matched)} spam patterns" if is_suspicious else "No spam patterns detected"
        }
    
    def _is_sequential(self, number: str) -> bool:
        """Check if number is sequential"""
        for i in range(len(number) - 3):
            if number[i:i+4] in "0123456789" or number[i:i+4] in "9876543210":
                return True
        return False
    
    def _mask_number(self, number: str) -> str:
        """Mask phone number based on settings"""
        if not self.masking_enabled:
            return number
        
        if self.masking_level == MaskingLevel.FULL:
            return "*" * len(number)
        elif self.masking_level == MaskingLevel.PARTIAL:
            if len(number) >= 10:
                return number[:3] + "*" * (len(number) - 6) + number[-3:]
            else:
                return "*" * len(number)
        elif self.masking_level == MaskingLevel.CUSTOM and self.custom_caller_id:
            return self.custom_caller_id
        else:
            return number
    
    def enable_masking(self, level: MaskingLevel = MaskingLevel.PARTIAL, custom_id: Optional[str] = None) -> Dict:
        """
        Enable caller ID masking
        
        Args:
            level: Masking level
            custom_id: Custom caller ID for outgoing calls
            
        Returns:
            Masking configuration result
        """
        self.masking_enabled = True
        self.masking_level = level
        self.custom_caller_id = custom_id
        
        return {
            "success": True,
            "masking_enabled": True,
            "level": level,
            "custom_id": custom_id,
            "message": f"Caller ID masking enabled at {level} level"
        }
    
    def disable_masking(self) -> Dict:
        """Disable caller ID masking"""
        self.masking_enabled = False
        
        return {
            "success": True,
            "masking_enabled": False,
            "message": "Caller ID masking disabled"
        }
    
    def block_number(self, phone_number: str, reason: Optional[str] = None) -> Dict:
        """
        Block a phone number
        
        Args:
            phone_number: Number to block
            reason: Reason for blocking
            
        Returns:
            Block result
        """
        clean_number = re.sub(r'\D', '', phone_number)
        self.blocked_numbers.add(clean_number)
        
        return {
            "success": True,
            "blocked_number": self._mask_number(clean_number),
            "reason": reason,
            "total_blocked": len(self.blocked_numbers),
            "message": f"Number {self._mask_number(clean_number)} has been blocked"
        }
    
    def unblock_number(self, phone_number: str) -> Dict:
        """Unblock a phone number"""
        clean_number = re.sub(r'\D', '', phone_number)
        
        if clean_number in self.blocked_numbers:
            self.blocked_numbers.remove(clean_number)
            return {
                "success": True,
                "unblocked_number": self._mask_number(clean_number),
                "total_blocked": len(self.blocked_numbers),
                "message": f"Number {self._mask_number(clean_number)} has been unblocked"
            }
        else:
            return {
                "success": False,
                "error": "Number not found in blocked list"
            }
    
    def get_blocked_numbers(self) -> List[Dict]:
        """Get list of blocked numbers"""
        return [
            {
                "number": self._mask_number(num),
                "blocked_at": datetime.now().isoformat()  # Would store actual timestamp
            }
            for num in self.blocked_numbers
        ]
    
    def report_spam(self, phone_number: str, category: str, description: Optional[str] = None) -> Dict:
        """
        Report a number as spam
        
        Args:
            phone_number: Number to report
            category: Spam category (robocall, telemarketer, scam, etc.)
            description: Optional description
            
        Returns:
            Report result
        """
        clean_number = re.sub(r'\D', '', phone_number)
        hashed = self._hash_number(clean_number)
        
        # Add or update in spam database
        if hashed in self.spam_database:
            self.spam_database[hashed]["reports"] += 1
            self.spam_database[hashed]["last_reported"] = datetime.now().strftime("%Y-%m-%d")
        else:
            self.spam_database[hashed] = {
                "type": CallerType.SPAM,
                "reports": 1,
                "category": category,
                "last_reported": datetime.now().strftime("%Y-%m-%d")
            }
        
        return {
            "success": True,
            "message": "Thank you for reporting spam",
            "total_reports": self.spam_database[hashed]["reports"],
            "category": category
        }
    
    def get_call_statistics(self, days: int = 7) -> Dict:
        """
        Get call statistics for the specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Call statistics
        """
        # Simulated statistics
        total_calls = 45
        spam_calls = 12
        blocked_calls = 8
        answered_calls = 25
        
        return {
            "period_days": days,
            "total_calls": total_calls,
            "spam_calls": spam_calls,
            "blocked_calls": blocked_calls,
            "answered_calls": answered_calls,
            "missed_calls": total_calls - answered_calls - blocked_calls,
            "spam_percentage": round((spam_calls / total_calls) * 100, 1) if total_calls > 0 else 0,
            "blocked_percentage": round((blocked_calls / total_calls) * 100, 1) if total_calls > 0 else 0,
            "spam_by_category": {
                "robocall": 5,
                "telemarketer": 4,
                "scam": 2,
                "other": 1
            },
            "busiest_hours": [
                {"hour": 10, "calls": 8},
                {"hour": 14, "calls": 7},
                {"hour": 16, "calls": 6}
            ]
        }
    
    def get_caller_insights(self) -> Dict:
        """Get insights about calling patterns and security"""
        stats = self.get_call_statistics()
        
        insights = []
        recommendations = []
        
        # High spam rate
        if stats["spam_percentage"] > 25:
            insights.append({
                "type": "warning",
                "title": "High Spam Call Rate",
                "message": f"{stats['spam_percentage']}% of your calls are spam"
            })
            recommendations.append("Enable aggressive spam filtering")
        
        # Blocking effectiveness
        if stats["blocked_calls"] > 5:
            insights.append({
                "type": "positive",
                "title": "Effective Blocking",
                "message": f"Blocked {stats['blocked_calls']} unwanted calls"
            })
        
        # Masking suggestion
        if not self.masking_enabled:
            recommendations.append("Enable caller ID masking for outgoing calls")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "security_score": self._calculate_caller_security_score(stats),
            "statistics": stats
        }
    
    def _calculate_caller_security_score(self, stats: Dict) -> int:
        """Calculate security score based on call patterns"""
        score = 100
        
        # Deduct for spam calls
        score -= min(stats["spam_percentage"], 30)
        
        # Bonus for using blocking
        if self.blocked_numbers:
            score += min(len(self.blocked_numbers), 10)
        
        # Bonus for masking
        if self.masking_enabled:
            score += 10
        
        return max(0, min(100, score))


# Singleton instance
caller_id_service = CallerIDService()
