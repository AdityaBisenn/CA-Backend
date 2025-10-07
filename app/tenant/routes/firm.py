# app/tenant/routes/firm.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.auth import (
    get_current_active_user, 
    require_trenor_admin, 
    require_firm_admin,
    AuthenticatedUser,
    get_user_accessible_firms
)
from app.tenant.models.firm import CAFirm
from app.tenant.models.user import User, UserRole
from app.cdm.models.entity import Entity
from app.tenant.schemas.firm import (
    CAFirmCreate,
    CAFirmUpdate,
    CAFirmResponse,
    CAFirmList,
    CAFirmSummary
)

router = APIRouter(prefix="/firms", tags=["CA Firms"])


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

@router.post("/", response_model=CAFirmResponse)
async def create_firm(
    firm_data: CAFirmCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_trenor_admin)
):
    """Create a new CA firm"""
    # Check if firm code already exists
    existing_firm = db.query(CAFirm).filter(CAFirm.firm_code == firm_data.firm_code).first()
    if existing_firm:
        raise HTTPException(
            status_code=400,
            detail="Firm code already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(CAFirm).filter(CAFirm.email == firm_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    firm = CAFirm(**firm_data.model_dump())
    db.add(firm)
    db.commit()
    db.refresh(firm)
    
    return firm

@router.get("/", response_model=CAFirmList)
async def list_firms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """List CA firms with pagination and filtering"""
    query = db.query(CAFirm)
    
    if active_only:
        query = query.filter(CAFirm.is_active == True)
    
    if search:
        query = query.filter(
            CAFirm.firm_name.ilike(f"%{search}%") |
            CAFirm.firm_code.ilike(f"%{search}%") |
            CAFirm.email.ilike(f"%{search}%")
        )
    
    # Filter firms based on user role and permissions
    accessible_firms = get_user_accessible_firms(db, current_user)
    if current_user.role != UserRole.TRENOR_ADMIN:
        query = query.filter(CAFirm.firm_id.in_(accessible_firms))
    
    total = query.count()
    firms = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return CAFirmList(
        firms=firms,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{firm_id}", response_model=CAFirmResponse)
async def get_firm(
    firm_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """Get CA firm by ID"""
    # Check if user has access to this firm
    accessible_firms = get_user_accessible_firms(db, current_user)
    if firm_id not in accessible_firms:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this firm"
        )
    
    query = db.query(CAFirm).filter(CAFirm.firm_id == firm_id)
    
    firm = query.first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    return firm

@router.put("/{firm_id}", response_model=CAFirmResponse)
async def update_firm(
    firm_id: str,
    firm_data: CAFirmUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Update CA firm details"""
    # Check if user has access to this firm (only firm admins and trenor admins)
    if current_user.role != UserRole.TRENOR_ADMIN and current_user.firm_id != firm_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to update this firm"
        )
    
    query = db.query(CAFirm).filter(CAFirm.firm_id == firm_id)
    
    firm = query.first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    # Update only provided fields
    update_data = firm_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(firm, field, value)
    
    db.commit()
    db.refresh(firm)
    
    return firm

@router.delete("/{firm_id}")
async def delete_firm(
    firm_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Soft delete CA firm (set inactive)"""
    # Check if user has access to this firm (only firm admins and trenor admins)
    if current_user.role != UserRole.TRENOR_ADMIN and current_user.firm_id != firm_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to delete this firm"
        )
    
    query = db.query(CAFirm).filter(CAFirm.firm_id == firm_id)
    
    firm = query.first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    firm.is_active = False
    db.commit()
    
    return {"message": "Firm deleted successfully"}

@router.get("/{firm_id}/summary", response_model=CAFirmSummary)
async def get_firm_summary(
    firm_id: str,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_active_user)
):
    """Get CA firm summary with statistics"""
    # Check if user has access to this firm
    accessible_firms = get_user_accessible_firms(db, current_user)
    if firm_id not in accessible_firms:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this firm"
        )
    
    firm = db.query(CAFirm).filter(CAFirm.firm_id == firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
    
    # Get client statistics
    total_clients = db.query(Entity).filter(Entity.firm_id == firm_id).count()
    active_clients = db.query(Entity).filter(
        Entity.firm_id == firm_id,
        Entity.is_active == True
    ).count()
    
    # Get user statistics
    total_users = db.query(User).filter(User.firm_id == firm_id).count()
    active_users = db.query(User).filter(
        User.firm_id == firm_id,
        User.is_active == True
    ).count()
    
    return CAFirmSummary(
        firm_id=firm.firm_id,
        firm_name=firm.firm_name,
        firm_code=firm.firm_code,
        total_clients=total_clients,
        active_clients=active_clients,
        total_users=total_users,
        active_users=active_users,
        created_at=firm.created_at
    )