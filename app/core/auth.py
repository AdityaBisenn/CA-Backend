# app/core/auth.py
"""
JWT Authentication and Authorization utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.tenant.models.user import User, UserRole
from app.tenant.models.firm import CAFirm

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Direct bcrypt usage

# HTTP Bearer token extractor
security = HTTPBearer()

class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    firm_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None
    
class TokenResponse(BaseModel):
    """Authentication response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class AuthenticatedUser(BaseModel):
    """Current authenticated user info"""
    user_id: str
    firm_id: str
    email: str
    name: str
    role: UserRole
    is_active: bool

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    return user

def create_tokens_for_user(user: User) -> TokenResponse:
    """Create access and refresh tokens for a user"""
    token_data = {
        "user_id": user.user_id,
        "firm_id": user.firm_id,
        "email": user.email,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "user_id": user.user_id,
            "firm_id": user.firm_id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "is_active": user.is_active
        }
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthenticatedUser:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception
            
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    
    return AuthenticatedUser(
        user_id=user.user_id,
        firm_id=user.firm_id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active
    )

async def get_current_active_user(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles"""
    def decorator(current_user: AuthenticatedUser = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return decorator

# Pre-defined role dependencies
async def require_trenor_admin(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
) -> AuthenticatedUser:
    """Require TRENOR_ADMIN role"""
    if current_user.role != UserRole.TRENOR_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires TRENOR_ADMIN role"
        )
    return current_user

async def require_firm_admin(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
) -> AuthenticatedUser:
    """Require CA_FIRM_ADMIN role or higher"""
    allowed_roles = [UserRole.TRENOR_ADMIN, UserRole.CA_FIRM_ADMIN]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires CA_FIRM_ADMIN role or higher"
        )
    return current_user

async def require_staff_access(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
) -> AuthenticatedUser:
    """Require CA_STAFF role or higher"""
    allowed_roles = [UserRole.TRENOR_ADMIN, UserRole.CA_FIRM_ADMIN, UserRole.CA_STAFF]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires CA_STAFF role or higher"
        )
    return current_user

async def require_staff_or_above(
    current_user: AuthenticatedUser = Depends(get_current_active_user)
) -> AuthenticatedUser:
    """Require CA_STAFF role or higher (alias for require_staff_access)"""
    return await require_staff_access(current_user)

def get_user_accessible_firms(db: Session, user: AuthenticatedUser) -> list[str]:
    """Get list of firm IDs accessible to the user"""
    if user.role == UserRole.TRENOR_ADMIN:
        # Trenor admins can access all firms
        firms = db.query(CAFirm).filter(CAFirm.is_active == True).all()
        return [firm.firm_id for firm in firms]
    else:
        # Other users can only access their own firm
        return [user.firm_id]

def validate_firm_access(db: Session, user: AuthenticatedUser, firm_id: str) -> bool:
    """Validate if user has access to a specific firm"""
    accessible_firms = get_user_accessible_firms(db, user)
    return firm_id in accessible_firms