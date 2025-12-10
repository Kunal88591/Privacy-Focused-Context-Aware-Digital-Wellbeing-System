"""
Caller ID Masking Service
Blocks spam calls, masks caller information, and provides call screening
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class CallType(str, Enum):
    SPAM = "spam"
    TELEMARKETER = "telemarketer"
    SCAM = "scam"
    UNKNOWN = "unknown"
    CONTACT = "contact"
    VERIFIED = "verified"


class CallerIDMasking:
    """Manage caller ID masking and spam detection"""
    
    def __init__(self):
        self.blocked_numbers = set()
        self.spam_database = self._init_spam_database()
        self.call_history = []
        self.masking_enabled = True
        
    def _init_spam_database(self) -> Dict[str, CallType]:
        """Initialize spam number database (simulated)"""
        return {
            "+1-800-SPAM": CallType.SPAM,
            "+1-555-SCAM": CallType.SCAM,
            "+1-900-SALES": CallType.TELEMARKETER,
        }
    
    async def screen_call(self, phone_number: str, caller_name: Optional[str] = None) -> Dict:
        """Screen incoming call and determine if it should be blocked"""
        
        # Normalize phone number
        normalized_number = self._normalize_phone_number(phone_number)
        
        # Check if number is blocked
        if normalized_number in self.blocked_numbers:
            return await self._handle_blocked_call(normalized_number, caller_name)
        
        # Check spam database
        call_type = self._check_spam_database(normalized_number)
        
        # Generate risk score
        risk_score = await self._calculate_risk_score(normalized_number, caller_name, call_type)
        
        # Decide action
        action = await self._decide_action(risk_score, call_type)
        
        # Log call
        call_record = {
            "phone_number": normalized_number,
            "caller_name": caller_name or "Unknown",
            "call_type": call_type,
            "risk_score": risk_score,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        self.call_history.append(call_record)
        
        return call_record
    
    def _normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number format"""
        # Remove all non-numeric characters except +
        normalized = re.sub(r'[^\d+]', '', phone_number)
        return normalized
    
    def _check_spam_database(self, phone_number: str) -> CallType:
        """Check if number is in spam database"""
        if phone_number in self.spam_database:
            return self.spam_database[phone_number]
        
        # Pattern matching for known spam patterns
        if re.match(r'\+1-800-', phone_number):
            return CallType.TELEMARKETER
        if re.match(r'\+1-900-', phone_number):
            return CallType.TELEMARKETER
        
        return CallType.UNKNOWN
    
    async def _calculate_risk_score(self, phone_number: str, caller_name: Optional[str], 
                                    call_type: CallType) -> int:
        """Calculate risk score (0-100) for incoming call"""
        
        risk_score = 0
        
        # Base score from call type
        type_scores = {
            CallType.SPAM: 90,
            CallType.SCAM: 95,
            CallType.TELEMARKETER: 70,
            CallType.UNKNOWN: 30,
            CallType.CONTACT: 0,
            CallType.VERIFIED: 0
        }
        risk_score += type_scores.get(call_type, 30)
        
        # Caller name analysis
        if not caller_name or caller_name == "Unknown":
            risk_score += 10
        
        # Pattern analysis
        if re.search(r'(lottery|prize|winner|urgent)', caller_name or '', re.IGNORECASE):
            risk_score += 20
        
        # Call frequency (simplified)
        recent_calls = sum(1 for call in self.call_history[-10:] 
                          if call['phone_number'] == phone_number)
        if recent_calls > 2:
            risk_score += 15
        
        return min(risk_score, 100)
    
    async def _decide_action(self, risk_score: int, call_type: CallType) -> str:
        """Decide what action to take for the call"""
        
        if risk_score >= 80:
            return "block"
        elif risk_score >= 50:
            return "silent"  # Silent ring, show notification only
        elif risk_score >= 30:
            return "screen"  # Show screening prompt
        else:
            return "allow"
    
    async def _handle_blocked_call(self, phone_number: str, caller_name: Optional[str]) -> Dict:
        """Handle a blocked call"""
        
        call_record = {
            "phone_number": phone_number,
            "caller_name": caller_name or "Blocked",
            "call_type": CallType.SPAM,
            "risk_score": 100,
            "action": "block",
            "timestamp": datetime.now().isoformat(),
            "reason": "Number in blocklist"
        }
        
        self.call_history.append(call_record)
        logger.info(f"Blocked call from {phone_number}")
        
        return call_record
    
    async def block_number(self, phone_number: str) -> Dict:
        """Add number to blocklist"""
        normalized = self._normalize_phone_number(phone_number)
        self.blocked_numbers.add(normalized)
        
        logger.info(f"Added {normalized} to blocklist")
        
        return {
            "phone_number": normalized,
            "status": "blocked",
            "blocked_at": datetime.now().isoformat()
        }
    
    async def unblock_number(self, phone_number: str) -> Dict:
        """Remove number from blocklist"""
        normalized = self._normalize_phone_number(phone_number)
        
        if normalized in self.blocked_numbers:
            self.blocked_numbers.remove(normalized)
            logger.info(f"Removed {normalized} from blocklist")
            return {
                "phone_number": normalized,
                "status": "unblocked"
            }
        else:
            return {
                "phone_number": normalized,
                "status": "not_in_blocklist"
            }
    
    async def get_call_history(self, limit: int = 50) -> List[Dict]:
        """Get recent call history"""
        return self.call_history[-limit:]
    
    async def get_spam_statistics(self) -> Dict:
        """Get spam call statistics"""
        total_calls = len(self.call_history)
        
        if total_calls == 0:
            return {
                "total_calls": 0,
                "spam_calls": 0,
                "blocked_calls": 0,
                "spam_percentage": 0
            }
        
        spam_calls = sum(1 for call in self.call_history 
                        if call['call_type'] in [CallType.SPAM, CallType.SCAM, CallType.TELEMARKETER])
        blocked_calls = sum(1 for call in self.call_history 
                           if call['action'] == 'block')
        
        return {
            "total_calls": total_calls,
            "spam_calls": spam_calls,
            "blocked_calls": blocked_calls,
            "spam_percentage": round((spam_calls / total_calls) * 100, 2),
            "blocked_percentage": round((blocked_calls / total_calls) * 100, 2)
        }
    
    async def enable_masking(self) -> Dict:
        """Enable caller ID masking"""
        self.masking_enabled = True
        logger.info("Caller ID masking enabled")
        
        return {
            "masking_enabled": True,
            "message": "Your phone number will be masked for outgoing calls"
        }
    
    async def disable_masking(self) -> Dict:
        """Disable caller ID masking"""
        self.masking_enabled = False
        logger.info("Caller ID masking disabled")
        
        return {
            "masking_enabled": False,
            "message": "Your real phone number will be shown for outgoing calls"
        }
    
    async def get_masked_number(self, real_number: str) -> str:
        """Generate masked phone number"""
        if not self.masking_enabled:
            return real_number
        
        # Generate consistent masked number using hash
        hash_object = hashlib.md5(real_number.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert hash to phone number format
        masked = f"+1-{hash_hex[0:3]}-{hash_hex[3:6]}-{hash_hex[6:10]}"
        
        return masked
    
    async def report_spam(self, phone_number: str, category: CallType = CallType.SPAM) -> Dict:
        """Report a number as spam"""
        normalized = self._normalize_phone_number(phone_number)
        
        # Add to spam database
        self.spam_database[normalized] = category
        
        # Also block it
        await self.block_number(normalized)
        
        logger.info(f"Reported {normalized} as {category}")
        
        return {
            "phone_number": normalized,
            "category": category,
            "status": "reported_and_blocked",
            "reported_at": datetime.now().isoformat()
        }


# Global caller ID masking instance
caller_masking = CallerIDMasking()
