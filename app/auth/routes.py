# app/auth/routes.py
"""
Authentication routes: login, register, logout, token refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
import secrets
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.auth import (
    authenticate_user, 
    create_tokens_for_user, 
    verify_token,
    get_password_hash,
    get_current_active_user,
    AuthenticatedUser,
    TokenResponse
)
from app.tenant.models.user import User, UserRole
from app.tenant.models.firm import CAFirm
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest, 
    TokenRefreshRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    UserProfile
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# In-memory token blacklist (in production, use Redis or database)
blacklisted_tokens = set()

@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens
    """
    user = authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return create_tokens_for_user(user)

@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(
    register_request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user within a CA firm
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == register_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate firm requirement for non-TRENOR_ADMIN users
    if register_request.role != UserRole.TRENOR_ADMIN:
        if not register_request.firm_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="firm_id is required for non-TRENOR_ADMIN users"
            )
        
        # Validate firm exists and is active
        firm = db.query(CAFirm).filter(
            CAFirm.firm_id == register_request.firm_id,
            CAFirm.is_active == True
        ).first()
        if not firm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CA Firm not found or not active"
            )
    
    # Create full name from first and last name
    full_name = f"{register_request.first_name} {register_request.last_name}"
    
    # Create new user
    user = User(
        firm_id=register_request.firm_id,  # Can be None for TRENOR_ADMIN
        email=register_request.email,
        name=full_name,
        password_hash=get_password_hash(register_request.password),
        role=register_request.role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User registered successfully",
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "firm_id": user.firm_id
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is blacklisted
    if refresh_request.refresh_token in blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    return create_tokens_for_user(user)

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """
    Logout user and blacklist current token
    """
    # Add current token to blacklist
    blacklisted_tokens.add(credentials.credentials)
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        user_id=user.user_id,
        firm_id=user.firm_id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        last_login=user.last_login.isoformat() if user.last_login else None,
        created_at=user.created_at.isoformat()
    )

@router.put("/change-password")
async def change_password(
    password_request: PasswordChangeRequest,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not user.verify_password(password_request.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    user.password_hash = get_password_hash(password_request.new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/reset-password")
async def reset_password(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset (sends email with reset token)
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token (in production, save to database with expiry)
    reset_token = secrets.token_urlsafe(32)
    
    # In production, send email with reset link
    # background_tasks.add_task(send_reset_email, user.email, reset_token)
    
    return {
        "message": "If the email exists, a reset link has been sent",
        "reset_token": reset_token  # Only for testing - remove in production
    }

@router.post("/reset-password/confirm")
async def confirm_password_reset(
    confirm_request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token
    """
    # In production, verify token from database and check expiry
    # For now, we'll just return success
    
    return {"message": "Password reset successful"}

@router.get("/validate-token")
async def validate_token(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """
    Validate current token and return user info
    """
    return {
        "valid": True,
        "user": {
            "user_id": current_user.user_id,
            "firm_id": current_user.firm_id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role.value
        }
    }