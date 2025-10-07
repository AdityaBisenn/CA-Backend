# app/core/tenant_context.py
from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional, TYPE_CHECKING
from app.core.database import get_db
from app.tenant.models.firm import CAFirm
from app.cdm.models.entity import Entity

if TYPE_CHECKING:
    from app.core.auth import AuthenticatedUser

class TenantContext:
    def __init__(self, firm_id: str, company_id: str, user_id: str):
        self.firm_id = firm_id
        self.company_id = company_id
        self.user_id = user_id

async def get_tenant_context(
    x_company_id: str = Header(..., alias="X-Company-ID"),
    db: Session = Depends(get_db)
) -> TenantContext:
    """
    Extract tenant context from headers and authenticated user.
    This ensures data isolation between CA firms and their clients.
    """
    # Import here to avoid circular imports
    from app.core.auth import get_current_active_user
    
    # Get authenticated user
    current_user = await get_current_active_user()
    
    if not x_company_id:
        raise HTTPException(
            status_code=400, 
            detail="Missing X-Company-ID header. Client context required."
        )

    # Validate that the company belongs to this user's firm
    entity = db.query(Entity).filter(
        Entity.company_id == x_company_id,
        Entity.firm_id == current_user.firm_id,
        Entity.is_active == True
    ).first()
    
    if not entity:
        raise HTTPException(
            status_code=404,
            detail="Company not found or not accessible by your firm"
        )

    return TenantContext(
        firm_id=current_user.firm_id,
        company_id=x_company_id,
        user_id=current_user.user_id
    )

async def get_optional_tenant_context(
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db)
) -> Optional[TenantContext]:
    """
    Optional tenant context for endpoints that can work with or without tenant context.
    Useful for admin/system-level endpoints.
    """
    from app.core.auth import get_current_active_user
    
    try:
        current_user = await get_current_active_user()
        if x_company_id:
            # Validate that the company belongs to this user's firm
            entity = db.query(Entity).filter(
                Entity.company_id == x_company_id,
                Entity.firm_id == current_user.firm_id,
                Entity.is_active == True
            ).first()
            
            if entity:
                return TenantContext(
                    firm_id=current_user.firm_id,
                    company_id=x_company_id,
                    user_id=current_user.user_id
                )
    except:
        pass
    
    return None

def apply_tenant_filter(query, model, context: TenantContext):
    """
    Apply tenant filtering to SQLAlchemy queries.
    Ensures data isolation at both firm and company level.
    """
    if hasattr(model, 'firm_id') and hasattr(model, 'company_id'):
        # Model has both firm_id and company_id (like some audit tables)
        return query.filter(
            model.firm_id == context.firm_id,
            model.company_id == context.company_id
        )
    elif hasattr(model, 'company_id'):
        # Model has company_id (most CDM tables)
        return query.filter(model.company_id == context.company_id)
    elif hasattr(model, 'firm_id'):
        # Model has only firm_id (like CAFirm, User)
        return query.filter(model.firm_id == context.firm_id)
    else:
        # Model has no tenant fields (should be rare)
        return query