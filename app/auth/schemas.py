# app/auth/schemas.py
"""
Authentication schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.tenant.models.user import UserRole

class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(BaseModel):
    """User registration request"""
    firm_id: Optional[str] = Field(None, description="CA Firm ID (required for non-TRENOR_ADMIN users)")
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.CA_STAFF)

class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)

class UserProfile(BaseModel):
    """User profile response"""
    user_id: str
    firm_id: str
    email: str
    name: str
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}