"""
Utility Functions for Security and Validation
Common utilities used across the application
"""

import hashlib
import secrets
import re
from typing import Optional
from datetime import datetime, timedelta


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash a password using SHA-256 with salt
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
    
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    salted = f"{password}{salt}".encode('utf-8')
    
    # Hash using SHA-256
    hashed = hashlib.sha256(salted).hexdigest()
    
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Stored hashed password
        salt: Salt used in hashing
    
    Returns:
        True if password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed_password


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Token length in bytes (default 32)
    
    Returns:
        Hexadecimal token string
    """
    return secrets.token_urlsafe(length)


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Sanitize user input string
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    # Remove dangerous characters
    sanitized = re.sub(r'[<>\"\'&]', '', text)
    
    # Truncate to max length
    sanitized = sanitized[:max_length]
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def format_error_response(message: str, code: str = None, details: dict = None) -> dict:
    """
    Format a standardized error response
    
    Args:
        message: Error message
        code: Optional error code
        details: Optional additional details
    
    Returns:
        Formatted error dictionary
    """
    response = {
        "error": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if code:
        response["code"] = code
    
    if details:
        response["details"] = details
    
    return response


def format_success_response(data: any, message: str = "Success") -> dict:
    """
    Format a standardized success response
    
    Args:
        data: Response data
        message: Success message
    
    Returns:
        Formatted response dictionary
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


def calculate_pagination(page: int, page_size: int, total_items: int) -> dict:
    """
    Calculate pagination metadata
    
    Args:
        page: Current page number (1-indexed)
        page_size: Items per page
        total_items: Total number of items
    
    Returns:
        Pagination metadata dictionary
    """
    total_pages = (total_items + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }


def time_ago(timestamp: datetime) -> str:
    """
    Convert timestamp to human-readable time ago format
    
    Args:
        timestamp: Datetime to convert
    
    Returns:
        Human-readable string (e.g., "2 hours ago")
    """
    now = datetime.utcnow()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
