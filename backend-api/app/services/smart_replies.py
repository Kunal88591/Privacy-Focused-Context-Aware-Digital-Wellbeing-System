"""
Smart Reply Suggestions
AI-powered quick response generation for notifications
"""

from typing import Dict, List, Optional
from datetime import datetime
import re


class ReplyType:
    """Types of smart replies"""
    ACKNOWLEDGMENT = "acknowledgment"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    QUESTION = "question"
    INFORMATIVE = "informative"


class SmartReplyGenerator:
    """Generate contextual quick reply suggestions"""
    
    def __init__(self):
        # Pre-defined reply templates
        self.templates = {
            # Generic acknowledgments
            'acknowledgment': [
                "Got it, thanks!",
                "Thanks for letting me know",
                "Understood",
                "Noted",
                "Will do"
            ],
            
            # Positive responses
            'positive': [
                "Sounds good!",
                "Great, thanks!",
                "Perfect!",
                "Awesome!",
                "Yes, please"
            ],
            
            # Negative responses
            'negative': [
                "Sorry, can't right now",
                "Maybe later",
                "Not today, thanks",
                "I'll pass",
                "No thanks"
            ],
            
            # Time-related
            'time_delay': [
                "Running late, be there soon",
                "On my way",
                "Give me 10 minutes",
                "Almost there",
                "Just left"
            ],
            
            # Questions
            'questions': [
                "What time?",
                "Where?",
                "Can you send more details?",
                "When do you need this?",
                "How urgent is this?"
            ],
            
            # Meeting responses
            'meeting_accept': [
                "I'll be there",
                "Accepted, see you then",
                "Works for me",
                "I can make it",
                "Confirmed"
            ],
            
            'meeting_decline': [
                "Sorry, I'm busy then",
                "Can we reschedule?",
                "I have a conflict",
                "Not available at that time",
                "Could we do another time?"
            ],
            
            # Work-related
            'work_acknowledge': [
                "Working on it",
                "Will get this done today",
                "On it!",
                "Reviewing now",
                "I'll handle this"
            ],
            
            # Social
            'social_positive': [
                "😊",
                "Sounds fun!",
                "Count me in!",
                "Love it!",
                "Haha, nice!"
            ]
        }
        
        # Keyword patterns for context detection
        self.patterns = {
            'question': [r'\?', r'what', r'when', r'where', r'how', r'why', r'can you'],
            'meeting': [r'meeting', r'call', r'zoom', r'teams', r'conference'],
            'urgent': [r'urgent', r'asap', r'immediately', r'now', r'emergency'],
            'time': [r'time', r'when', r'schedule', r'late', r'early'],
            'location': [r'where', r'location', r'address', r'place'],
            'thanks': [r'thank', r'thanks', r'appreciate'],
            'request': [r'can you', r'could you', r'please', r'would you'],
        }
    
    def generate_replies(
        self,
        message: str,
        sender: str,
        app_name: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate smart reply suggestions
        
        Args:
            message: The notification message
            sender: Who sent it
            app_name: Which app
            context: Additional context (time, user state, etc.)
            
        Returns:
            List of suggested replies with confidence scores
        """
        # Analyze message
        message_lower = message.lower()
        detected_patterns = self._detect_patterns(message_lower)
        
        # Generate appropriate replies
        suggestions = []
        
        # Handle different contexts
        if 'question' in detected_patterns:
            suggestions.extend(self._get_question_replies(message_lower))
        
        if 'meeting' in detected_patterns:
            suggestions.extend(self._get_meeting_replies())
        
        if 'urgent' in detected_patterns:
            suggestions.extend(self._get_urgent_replies())
        
        if 'thanks' in detected_patterns:
            suggestions.extend(self._get_thanks_replies())
        
        if 'request' in detected_patterns:
            suggestions.extend(self._get_request_replies())
        
        # Add generic replies if we don't have enough
        if len(suggestions) < 3:
            suggestions.extend(self._get_generic_replies())
        
        # Score and rank suggestions
        scored_suggestions = self._score_suggestions(
            suggestions,
            message_lower,
            detected_patterns,
            app_name
        )
        
        # Return top 3-5 suggestions
        return scored_suggestions[:5]
    
    def _detect_patterns(self, message: str) -> List[str]:
        """Detect patterns in message"""
        detected = []
        
        for pattern_name, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message, re.IGNORECASE):
                    detected.append(pattern_name)
                    break
        
        return detected
    
    def _get_question_replies(self, message: str) -> List[str]:
        """Get replies for questions"""
        replies = []
        
        # Time-related questions
        if any(word in message for word in ['when', 'time']):
            replies.extend([
                "Let me check my calendar",
                "How about tomorrow?",
                "What time works for you?"
            ])
        
        # Location questions
        if any(word in message for word in ['where', 'location']):
            replies.extend([
                "I'll send you the address",
                "Same place as last time?",
                "Where do you suggest?"
            ])
        
        # General questions
        replies.extend(self.templates['questions'][:2])
        
        return replies
    
    def _get_meeting_replies(self) -> List[str]:
        """Get meeting-related replies"""
        return (
            self.templates['meeting_accept'][:2] +
            self.templates['meeting_decline'][:1]
        )
    
    def _get_urgent_replies(self) -> List[str]:
        """Get replies for urgent messages"""
        return [
            "On it right now",
            "Handling this immediately",
            "Got it, this is priority"
        ]
    
    def _get_thanks_replies(self) -> List[str]:
        """Get replies for thank you messages"""
        return [
            "You're welcome!",
            "Happy to help!",
            "Anytime!",
            "No problem!"
        ]
    
    def _get_request_replies(self) -> List[str]:
        """Get replies for requests"""
        return [
            "Sure, I can do that",
            "Yes, give me a moment",
            "Let me check and get back to you",
            "Sorry, I can't help with this"
        ]
    
    def _get_generic_replies(self) -> List[str]:
        """Get generic replies"""
        return (
            self.templates['acknowledgment'][:2] +
            self.templates['positive'][:2] +
            self.templates['negative'][:1]
        )
    
    def _score_suggestions(
        self,
        suggestions: List[str],
        message: str,
        patterns: List[str],
        app_name: str
    ) -> List[Dict]:
        """Score and rank suggestions"""
        scored = []
        
        for suggestion in suggestions:
            score = 0.5  # Base score
            
            # Increase score based on context match
            if 'question' in patterns and '?' in suggestion:
                score += 0.2
            
            if 'urgent' in patterns and any(word in suggestion.lower() for word in ['now', 'immediately', 'right']):
                score += 0.3
            
            if 'meeting' in patterns and any(word in suggestion.lower() for word in ['meeting', 'there', 'confirmed']):
                score += 0.2
            
            # App-specific scoring
            if 'whatsapp' in app_name.lower() or 'messenger' in app_name.lower():
                # More casual for messaging apps
                if any(emoji in suggestion for emoji in ['😊', '👍', '!']):
                    score += 0.1
            
            if 'email' in app_name.lower() or 'gmail' in app_name.lower():
                # More formal for email
                if suggestion.endswith('.') or 'thank' in suggestion.lower():
                    score += 0.1
            
            # Avoid duplicates
            suggestion_lower = suggestion.lower()
            if any(s['text'].lower() == suggestion_lower for s in scored):
                continue
            
            scored.append({
                'text': suggestion,
                'confidence': min(score, 1.0),
                'type': self._classify_reply_type(suggestion)
            })
        
        # Sort by confidence
        scored.sort(key=lambda x: x['confidence'], reverse=True)
        
        return scored
    
    def _classify_reply_type(self, reply: str) -> str:
        """Classify the type of reply"""
        reply_lower = reply.lower()
        
        if '?' in reply:
            return ReplyType.QUESTION
        
        if any(word in reply_lower for word in ['yes', 'sure', 'great', 'sounds good', 'perfect']):
            return ReplyType.POSITIVE
        
        if any(word in reply_lower for word in ['no', 'sorry', 'can\'t', 'not']):
            return ReplyType.NEGATIVE
        
        if any(word in reply_lower for word in ['thanks', 'got it', 'noted', 'understood']):
            return ReplyType.ACKNOWLEDGMENT
        
        return ReplyType.INFORMATIVE
    
    def learn_from_response(
        self,
        message: str,
        suggested_reply: str,
        actual_reply: str,
        was_used: bool
    ):
        """
        Learn from user's actual responses to improve suggestions
        This would integrate with ML models in production
        
        Args:
            message: Original message
            suggested_reply: What we suggested
            actual_reply: What user actually sent
            was_used: Whether user used our suggestion
        """
        # In production, this would:
        # 1. Store the interaction
        # 2. Update ML model with feedback
        # 3. Adjust scoring algorithm
        # For now, just log
        pass
    
    def get_contextual_replies(
        self,
        user_context: Dict,
        message: str,
        sender: str
    ) -> List[Dict]:
        """
        Get replies based on user's current context
        
        Args:
            user_context: User's current state (busy, driving, etc.)
            message: The message
            sender: Who sent it
            
        Returns:
            Context-appropriate reply suggestions
        """
        context_state = user_context.get('state', 'available')
        
        if context_state == 'driving':
            return [
                {'text': "I'm driving, will respond soon", 'confidence': 0.9, 'type': 'informative'},
                {'text': "Call you when I arrive", 'confidence': 0.8, 'type': 'informative'},
                {'text': "In the car, text you later", 'confidence': 0.7, 'type': 'informative'}
            ]
        
        if context_state == 'meeting':
            return [
                {'text': "In a meeting, will reply after", 'confidence': 0.9, 'type': 'informative'},
                {'text': "Busy right now, talk soon", 'confidence': 0.8, 'type': 'informative'},
                {'text': "Can this wait an hour?", 'confidence': 0.7, 'type': 'question'}
            ]
        
        if context_state == 'sleeping':
            # Probably shouldn't reply, but if they do:
            return [
                {'text': "Just woke up, what's up?", 'confidence': 0.6, 'type': 'question'},
                {'text': "Sorry for late reply", 'confidence': 0.7, 'type': 'acknowledgment'}
            ]
        
        if context_state == 'busy':
            return [
                {'text': "Swamped right now, later?", 'confidence': 0.8, 'type': 'question'},
                {'text': "Bit busy, will get back to you", 'confidence': 0.9, 'type': 'informative'},
                {'text': "Can we talk this evening?", 'confidence': 0.7, 'type': 'question'}
            ]
        
        # Default to standard replies
        return self.generate_replies(message, sender, 'default')


# Singleton instance
smart_reply_generator = SmartReplyGenerator()
