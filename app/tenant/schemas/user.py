# app/tenant/schemas/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.tenant.models.user import UserRole

class UserBase(BaseModel):
    """Base schema for User"""
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: Optional[str] = Field(None, description="User's phone number")
    role: UserRole = Field(..., description="User's role in the system")
    is_active: bool = Field(True, description="Whether user is active")

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="User's password")
    firm_id: str = Field(..., description="ID of the CA firm this user belongs to")

class UserUpdate(BaseModel):
    """Schema for updating user details"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """Schema for user response (no password)"""
    user_id: str
    firm_id: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class UserList(BaseModel):
    """Schema for listing users"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int

class UserEntityMapBase(BaseModel):
    """Base schema for User-Entity mapping"""
    user_id: str
    company_id: str
    permissions: Optional[dict] = Field(None, description="JSON permissions for this entity")
    is_active: bool = Field(True, description="Whether mapping is active")

class UserEntityMapCreate(UserEntityMapBase):
    """Schema for creating user-entity mapping"""
    pass

class UserEntityMapUpdate(BaseModel):
    """Schema for updating user-entity mapping"""
    permissions: Optional[dict] = None
    is_active: Optional[bool] = None

class UserEntityMapResponse(UserEntityMapBase):
    """Schema for user-entity mapping response"""
    mapping_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class UserEntityAccess(BaseModel):
    """Schema for user's entity access summary"""
    user_id: str
    accessible_entities: List[dict]  # List of {company_id, company_name, permissions}
    total_entities: int

class ChangePassword(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class ResetPassword(BaseModel):
    """Schema for password reset"""
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)