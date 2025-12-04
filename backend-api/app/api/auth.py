"""
Authentication API endpoints
Handles user registration, login, and token management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

# Request/Response models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime

# Mock user database (replace with real database)
users_db = {}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user account"""
    
    # Check if user already exists
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user (in real app, hash password)
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_data.email] = {
        "user_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password,  # TODO: Hash password
        "created_at": datetime.utcnow()
    }
    
    return UserResponse(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        created_at=datetime.utcnow()
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login and receive access token"""
    
    # Verify credentials
    user = users_db.get(credentials.email)
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT tokens (simplified - use proper JWT library in production)
    access_token = f"access_token_{user['user_id']}"
    refresh_token = f"refresh_token_{user['user_id']}"
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    # TODO: Implement token refresh logic
    return {"access_token": "new_access_token"}

@router.get("/me")
async def get_current_user():
    """Get current user information"""
    # TODO: Extract user from JWT token
    return {"user_id": "user_1", "username": "demo_user"}
