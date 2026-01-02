"""
Custom Exception Classes
Application-specific exceptions for better error handling
"""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""
    
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class ValidationError(BaseAPIException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(BaseAPIException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundError(BaseAPIException):
    """Raised when requested resource is not found"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateResourceError(BaseAPIException):
    """Raised when trying to create a duplicate resource"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} already exists"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {"retry_after_seconds": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ServiceUnavailableError(BaseAPIException):
    """Raised when a required service is unavailable"""
    
    def __init__(self, service: str):
        super().__init__(
            message=f"{service} is currently unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class DatabaseError(BaseAPIException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CacheError(BaseAPIException):
    """Raised when cache operation fails"""
    
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceError(BaseAPIException):
    """Raised when external API call fails"""
    
    def __init__(self, service: str, message: str = None):
        error_message = f"External service error: {service}"
        if message:
            error_message += f" - {message}"
        super().__init__(
            message=error_message,
            status_code=status.HTTP_502_BAD_GATEWAY
        )
