# app/tenant/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import (
    get_current_active_user, 
    require_firm_admin, 
    require_staff_access,
    AuthenticatedUser,
    UserRole
)
from app.tenant.models.user import User, UserEntityMap
from app.tenant.models.firm import CAFirm
from app.cdm.models.entity import Entity
from app.tenant.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserList,
    UserEntityMapCreate,
    UserEntityMapUpdate,
    UserEntityMapResponse,
    UserEntityAccess,
    ChangePassword
)

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_accessible_firms(db: Session, user: AuthenticatedUser) -> List[str]:
    """Get list of firm IDs that the user has access to"""
    if user.role == UserRole.TRENOR_ADMIN:
        # Trenor admins can access all firms
        firms = db.query(CAFirm.firm_id).all()
        return [firm.firm_id for firm in firms]
    elif user.firm_id:
        # Other users can only access their own firm
        return [user.firm_id]
    else:
        return []

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Create a new user within a CA firm"""
    # Ensure user is being created in the current firm context
    if user_data.firm_id != current_user.firm_id and current_user.role != UserRole.TRENOR_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot create user for different firm"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password (in production, use proper password hashing)
    user_dict = user_data.model_dump(exclude={'password'})
    user = User(**user_dict)
    user.set_password(user_data.password)  # Assuming we implement this method
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/", response_model=UserList)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """List users within the current CA firm"""
    # Filter by user's accessible firms
    accessible_firms = get_user_accessible_firms(db, current_user)
    query = db.query(User).filter(User.firm_id.in_(accessible_firms))
    
    if active_only:
        query = query.filter(User.is_active == True)
    
    if role:
        query = query.filter(User.role == role)
    
    if search:
        query = query.filter(
            User.first_name.ilike(f"%{search}%") |
            User.last_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return UserList(
        users=users,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get user by ID within current firm"""
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Update user details"""
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Soft delete user (set inactive)"""
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/change-password")
async def change_password(
    user_id: str,
    password_data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """Change user password"""
    # Users can only change their own password unless they're admin
    if user_id != current_user.user_id and current_user.role not in [UserRole.TRENOR_ADMIN, UserRole.CA_FIRM_ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="You can only change your own password"
        )
    
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password (implement proper verification)
    if not user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    user.set_password(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

# User-Entity mapping endpoints

@router.post("/{user_id}/entities", response_model=UserEntityMapResponse)
async def grant_entity_access(
    user_id: str,
    mapping_data: UserEntityMapCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Grant user access to a specific entity"""
    # Verify user exists in accessible firms
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify entity exists in accessible firms
    entity = db.query(Entity).filter(
        Entity.company_id == mapping_data.company_id,
        Entity.firm_id.in_(accessible_firms)
    ).first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Check if mapping already exists
    existing_mapping = db.query(UserEntityMap).filter(
        UserEntityMap.user_id == user_id,
        UserEntityMap.company_id == mapping_data.company_id
    ).first()
    
    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="User already has access to this entity"
        )
    
    mapping = UserEntityMap(**mapping_data.model_dump())
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    
    return mapping

@router.get("/{user_id}/entities", response_model=List[UserEntityAccess])
async def list_user_entities(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """List all entities a user has access to"""
    # Verify user exists in accessible firms
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()

@router.put("/{user_id}/entities/{entity_id}", response_model=UserEntityMapResponse)
async def update_entity_access(
    user_id: str,
    entity_id: str,
    mapping_data: UserEntityMapUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Update user's access level for a specific entity"""
    # Verify user exists in accessible firms
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()

@router.delete("/{user_id}/entities/{entity_id}")
async def revoke_entity_access(
    user_id: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Revoke user's access to a specific entity"""
    # Verify user exists in accessible firms
    accessible_firms = get_user_accessible_firms(db, current_user)
    user = db.query(User).filter(
        User.user_id == user_id,
        User.firm_id.in_(accessible_firms)
    ).first()