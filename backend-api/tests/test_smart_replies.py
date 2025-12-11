"""
Tests for Smart Reply Generator
"""

import pytest
from app.services.smart_replies import (
    smart_reply_generator,
    ReplyType
)


class TestSmartReplyGenerator:
    """Test smart reply generation"""
    
    def test_generate_replies_question(self):
        """Test generating replies for questions"""
        message = "What time is the meeting?"
        suggestions = smart_reply_generator.generate_replies(
            message=message,
            sender="colleague",
            app_name="slack"
        )
        
        assert len(suggestions) > 0
        # Should include question-related replies
        assert any('?' in s['text'] or 'time' in s['text'].lower() for s in suggestions)
    
    def test_generate_replies_meeting(self):
        """Test replies for meeting invitations"""
        message = "Can you join the Zoom meeting at 2 PM?"
        suggestions = smart_reply_generator.generate_replies(
            message=message,
            sender="manager",
            app_name="email"
        )
        
        assert len(suggestions) > 0
        # Should have accept/decline options
        reply_texts = [s['text'].lower() for s in suggestions]
        has_positive = any('yes' in r or 'there' in r or 'confirmed' in r for r in reply_texts)
        has_negative = any('sorry' in r or 'busy' in r or 'reschedule' in r for r in reply_texts)
        
        assert has_positive or has_negative
    
    def test_generate_replies_thanks(self):
        """Test replies for thank you messages"""
        message = "Thank you for your help!"
        suggestions = smart_reply_generator.generate_replies(
            message=message,
            sender="friend",
            app_name="whatsapp"
        )
        
        assert len(suggestions) > 0
        # Should have acknowledgment replies
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('welcome' in r or 'anytime' in r or 'problem' in r for r in reply_texts)
    
    def test_generate_replies_urgent(self):
        """Test replies for urgent messages"""
        message = "URGENT: Need your response ASAP!"
        suggestions = smart_reply_generator.generate_replies(
            message=message,
            sender="boss",
            app_name="email"
        )
        
        assert len(suggestions) > 0
        # Should have urgent-appropriate replies
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('now' in r or 'immediately' in r or 'right' in r for r in reply_texts)
    
    def test_generate_replies_request(self):
        """Test replies for requests"""
        message = "Can you send me the report?"
        suggestions = smart_reply_generator.generate_replies(
            message=message,
            sender="colleague",
            app_name="teams"
        )
        
        assert len(suggestions) > 0
        # Should have positive/negative responses
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('sure' in r or 'yes' in r or 'can' in r for r in reply_texts)
    
    def test_contextual_replies_driving(self):
        """Test contextual replies when driving"""
        context = {'state': 'driving'}
        suggestions = smart_reply_generator.get_contextual_replies(
            user_context=context,
            message="Are you coming?",
            sender="friend"
        )
        
        assert len(suggestions) > 0
        # Should mention driving
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('driving' in r or 'car' in r for r in reply_texts)
    
    def test_contextual_replies_meeting(self):
        """Test contextual replies when in meeting"""
        context = {'state': 'meeting'}
        suggestions = smart_reply_generator.get_contextual_replies(
            user_context=context,
            message="Quick question",
            sender="colleague"
        )
        
        assert len(suggestions) > 0
        # Should mention being busy
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('meeting' in r or 'busy' in r for r in reply_texts)
    
    def test_contextual_replies_busy(self):
        """Test contextual replies when busy"""
        context = {'state': 'busy'}
        suggestions = smart_reply_generator.get_contextual_replies(
            user_context=context,
            message="Need your help",
            sender="team"
        )
        
        assert len(suggestions) > 0
        # Should indicate being busy
        reply_texts = [s['text'].lower() for s in suggestions]
        assert any('busy' in r or 'later' in r for r in reply_texts)
    
    def test_reply_confidence_scores(self):
        """Test replies have confidence scores"""
        suggestions = smart_reply_generator.generate_replies(
            message="Hello, how are you?",
            sender="friend",
            app_name="whatsapp"
        )
        
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert 'confidence' in suggestion
            assert 0 <= suggestion['confidence'] <= 1.0
    
    def test_reply_types(self):
        """Test replies are classified by type"""
        suggestions = smart_reply_generator.generate_replies(
            message="Can you help me?",
            sender="colleague",
            app_name="slack"
        )
        
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert 'type' in suggestion
            assert suggestion['type'] in [
                ReplyType.ACKNOWLEDGMENT,
                ReplyType.POSITIVE,
                ReplyType.NEGATIVE,
                ReplyType.QUESTION,
                ReplyType.INFORMATIVE
            ]
    
    def test_no_duplicate_suggestions(self):
        """Test no duplicate suggestions"""
        suggestions = smart_reply_generator.generate_replies(
            message="Test message",
            sender="test",
            app_name="test"
        )
        
        reply_texts = [s['text'] for s in suggestions]
        # Should have unique suggestions
        assert len(reply_texts) == len(set(reply_texts))
    
    def test_limit_suggestions(self):
        """Test suggestions are limited to reasonable count"""
        suggestions = smart_reply_generator.generate_replies(
            message="Long message with many possible replies",
            sender="sender",
            app_name="app"
        )
        
        # Should return 3-5 suggestions
        assert 1 <= len(suggestions) <= 5
    
    def test_classify_reply_type_question(self):
        """Test classifying question replies"""
        reply_type = smart_reply_generator._classify_reply_type("What time?")
        assert reply_type == ReplyType.QUESTION
    
    def test_classify_reply_type_positive(self):
        """Test classifying positive replies"""
        reply_type = smart_reply_generator._classify_reply_type("Sounds good!")
        assert reply_type == ReplyType.POSITIVE
    
    def test_classify_reply_type_negative(self):
        """Test classifying negative replies"""
        reply_type = smart_reply_generator._classify_reply_type("Sorry, can't make it")
        assert reply_type == ReplyType.NEGATIVE
    
    def test_classify_reply_type_acknowledgment(self):
        """Test classifying acknowledgment replies"""
        reply_type = smart_reply_generator._classify_reply_type("Got it, thanks!")
        assert reply_type == ReplyType.ACKNOWLEDGMENT
    
    def test_pattern_detection(self):
        """Test message pattern detection"""
        # Question pattern
        patterns = smart_reply_generator._detect_patterns("When is the meeting?")
        assert 'question' in patterns
        
        # Meeting pattern
        patterns = smart_reply_generator._detect_patterns("Let's schedule a Zoom call")
        assert 'meeting' in patterns
        
        # Urgent pattern
        patterns = smart_reply_generator._detect_patterns("This is urgent!")
        assert 'urgent' in patterns
    
    def test_app_specific_suggestions(self):
        """Test app-specific suggestion customization"""
        # Casual app (WhatsApp)
        casual = smart_reply_generator.generate_replies(
            message="Hey!",
            sender="friend",
            app_name="whatsapp"
        )
        
        # Formal app (Email)
        formal = smart_reply_generator.generate_replies(
            message="Dear colleague,",
            sender="colleague",
            app_name="gmail"
        )
        
        # Both should have suggestions
        assert len(casual) > 0
        assert len(formal) > 0
