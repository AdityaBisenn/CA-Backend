# app/cdm/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.auth import (
    get_current_active_user,
    require_staff_access,
    require_firm_admin,
    AuthenticatedUser,
    UserRole
)
from app.cdm.models.entity import Entity
from app.cdm.models.master import Group, Ledger, StockItem, TaxLedger
from app.cdm.models.transaction import VoucherHeader, VoucherLine
from app.cdm.models.external import BankStatement, GSTSales, GSTPurchases
from app.cdm.models.reconciliation import ReconciliationLog

from app.cdm.schemas.entity import EntityCreate, EntityUpdate, EntityResponse
from app.cdm.schemas.transaction import VoucherHeaderCreate, VoucherHeaderResponse, VoucherLineCreate

def get_user_accessible_firms(db: Session, user: AuthenticatedUser) -> List[str]:
    """Get list of firm IDs that user has access to"""
    if user.role == UserRole.TRENOR_ADMIN:
        # Admin has access to all firms
        return []  # Empty list means no restriction
    elif user.firm_id:
        return [user.firm_id]
    else:
        return []

from app.cdm.schemas.master import (
    GroupCreate, GroupUpdate, GroupResponse,
    LedgerCreate, LedgerUpdate, LedgerResponse,
    StockItemCreate, StockItemUpdate, StockItemResponse,
    TaxLedgerCreate, TaxLedgerUpdate, TaxLedgerResponse
)
from app.cdm.schemas.transaction import (
    VoucherHeaderCreate, VoucherHeaderUpdate, VoucherHeaderResponse
)

router = APIRouter(prefix="/cdm", tags=["CDM - Common Data Model"])


def get_user_accessible_firms(db: Session, user: AuthenticatedUser) -> List[str]:
    """Get list of firm IDs that the user has access to"""
    if user.role == UserRole.TRENOR_ADMIN:
        # Trenor admins can access all firms
        from app.tenant.models.firm import CAFirm
        firms = db.query(CAFirm.firm_id).all()
        return [firm.firm_id for firm in firms]
    elif user.firm_id:
        # Other users can only access their own firm
        return [user.firm_id]
    else:
        return []


def apply_tenant_filter(query, model, current_user: AuthenticatedUser, db: Session):
    """Apply tenant filtering to a query based on user's accessible firms"""
    accessible_firms = get_user_accessible_firms(db, current_user)
    return query.filter(model.firm_id.in_(accessible_firms))

# ==================== ENTITY ROUTES ====================

@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    entity: EntityCreate, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Create a new company entity within current CA firm"""
    entity_data = entity.model_dump()
    entity_data['firm_id'] = current_user.firm_id  # Ensure entity belongs to current firm
    
    db_entity = Entity(**entity_data)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.get("/entities", response_model=List[EntityResponse])
def get_entities(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get all entities for current CA firm"""
    query = db.query(Entity)
    query = apply_tenant_filter(query, Entity, current_user, db)
    entities = query.offset(skip).limit(limit).all()
    return entities

@router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(
    entity_id: str, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get specific entity by ID"""
    query = db.query(Entity).filter(Entity.company_id == entity_id)
    query = apply_tenant_filter(query, Entity, current_user, db)
    entity = query.first()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity

@router.put("/entities/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: str,
    entity: EntityUpdate, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Update specific entity"""
    query = db.query(Entity).filter(Entity.company_id == entity_id)
    query = apply_tenant_filter(query, Entity, current_user, db)
    db_entity = query.first()

# ==================== GROUP ROUTES ====================

@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(
    group: GroupCreate, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Create a new group within current company context"""
    group_data = group.model_dump()
    # Note: company_id should be provided in the request body and validated against user's accessible entities
    
    db_group = Group(**group_data)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/groups", response_model=List[GroupResponse])
def get_groups(
    company_id: str,  # Required parameter for company context
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get groups within specified company context"""
    # Validate user has access to this company
    accessible_firms = get_user_accessible_firms(db, current_user)
    entity = db.query(Entity).filter(
        Entity.company_id == company_id,
        Entity.firm_id.in_(accessible_firms)
    ).first()
    if not entity:
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    query = db.query(Group).filter(
        Group.is_active == True,
        Group.company_id == company_id
    )
    groups = query.offset(skip).limit(limit).all()
    return groups

# ==================== LEDGER ROUTES ====================

@router.post("/ledgers", response_model=LedgerResponse, status_code=status.HTTP_201_CREATED)
def create_ledger(
    ledger: LedgerCreate, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_firm_admin)
):
    """Create a new ledger within current company context"""
    # Validate user has access to the specified company
    accessible_firms = get_user_accessible_firms(db, current_user)
    entity = db.query(Entity).filter(
        Entity.company_id == ledger.company_id,
        Entity.firm_id.in_(accessible_firms)
    ).first()
    if not entity:
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    ledger_data = ledger.model_dump()
    
    db_ledger = Ledger(**ledger_data)
    db.add(db_ledger)
    db.commit()
    db.refresh(db_ledger)
    return db_ledger

@router.get("/ledgers", response_model=List[LedgerResponse])
def get_ledgers(company_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get ledgers, optionally filtered by company"""
    query = db.query(Ledger).filter(Ledger.is_active == True)
    if company_id:
        query = query.filter(Ledger.company_id == company_id)
    ledgers = query.offset(skip).limit(limit).all()
    return ledgers

# ==================== STOCK ITEM ROUTES ====================

@router.post("/stock-items", response_model=StockItemResponse, status_code=status.HTTP_201_CREATED)
def create_stock_item(item: StockItemCreate, db: Session = Depends(get_db)):
    """Create a new stock item"""
    db_item = StockItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/stock-items", response_model=List[StockItemResponse])
def get_stock_items(company_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get stock items, optionally filtered by company"""
    query = db.query(StockItem).filter(StockItem.is_active == True)
    if company_id:
        query = query.filter(StockItem.company_id == company_id)
    items = query.offset(skip).limit(limit).all()
    return items

# ==================== TAX LEDGER ROUTES ====================

@router.post("/tax-ledgers", response_model=TaxLedgerResponse, status_code=status.HTTP_201_CREATED)
def create_tax_ledger(tax: TaxLedgerCreate, db: Session = Depends(get_db)):
    """Create a new tax ledger"""
    db_tax = TaxLedger(**tax.dict())
    db.add(db_tax)
    db.commit()
    db.refresh(db_tax)
    return db_tax

@router.get("/tax-ledgers", response_model=List[TaxLedgerResponse])
def get_tax_ledgers(company_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get tax ledgers, optionally filtered by company"""
    query = db.query(TaxLedger).filter(TaxLedger.is_active == True)
    if company_id:
        query = query.filter(TaxLedger.company_id == company_id)
    taxes = query.offset(skip).limit(limit).all()
    return taxes

# ==================== VOUCHER ROUTES ====================

@router.post("/vouchers", response_model=VoucherHeaderResponse, status_code=status.HTTP_201_CREATED)
def create_voucher(
    voucher: VoucherHeaderCreate, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Create a new voucher"""
    
    # Verify user has access to the company
    if current_user.role != UserRole.TRENOR_ADMIN:
        accessible_firms = get_user_accessible_firms(db, current_user)
        company = db.query(Entity).filter(Entity.company_id == voucher.company_id).first()
        if not company or company.firm_id not in accessible_firms:
            raise HTTPException(status_code=403, detail="Access denied to this company")
    
    # Create voucher header
    db_voucher = VoucherHeader(
        company_id=voucher.company_id,
        voucher_number=voucher.voucher_number,
        voucher_type=voucher.voucher_type,
        voucher_date=voucher.voucher_date,
        party_ledger_id=voucher.party_ledger_id,
        total_amount=voucher.total_amount,
        narration=voucher.narration,
        status=voucher.status
    )
    
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    
    # Create voucher lines
    for line_data in voucher.lines:
        db_line = VoucherLine(
            voucher_id=db_voucher.voucher_id,
            ledger_id=line_data.ledger_id,
            debit_amount=line_data.debit_amount,
            credit_amount=line_data.credit_amount,
            line_narration=line_data.line_narration
        )
        db.add(db_line)
    
    db.commit()
    return db_voucher

@router.get("/vouchers", response_model=List[VoucherHeaderResponse])
def get_vouchers(
    skip: int = 0, 
    limit: int = 100,
    voucher_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
    company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get vouchers for current CA firm with filtering"""
    
    query = db.query(VoucherHeader)
    
    # Apply tenant filtering based on user access
    accessible_firms = get_user_accessible_firms(db, current_user)
    if current_user.role != UserRole.TRENOR_ADMIN and accessible_firms:
        query = query.join(Entity).filter(Entity.firm_id.in_(accessible_firms))
    
    # Apply company filter if provided
    if company_id:
        query = query.filter(VoucherHeader.company_id == company_id)
    
    # Apply additional filters
    if voucher_type:
        query = query.filter(VoucherHeader.voucher_type == voucher_type)
    if status:
        query = query.filter(VoucherHeader.status == status)
    if from_date:
        query = query.filter(VoucherHeader.voucher_date >= from_date)  
    if to_date:
        query = query.filter(VoucherHeader.voucher_date <= to_date)
    
    vouchers = query.offset(skip).limit(limit).all()
    return vouchers

@router.get("/vouchers/{voucher_id}", response_model=VoucherHeaderResponse)
def get_voucher(
    voucher_id: str, 
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_staff_access)
):
    """Get voucher by ID with lines"""
    voucher = db.query(VoucherHeader).filter(VoucherHeader.voucher_id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    # Verify user has access to this voucher's company
    if current_user.role != UserRole.TRENOR_ADMIN:
        accessible_firms = get_user_accessible_firms(db, current_user)
        company = db.query(Entity).filter(Entity.company_id == voucher.company_id).first()
        if not company or (accessible_firms and company.firm_id not in accessible_firms):
            raise HTTPException(status_code=403, detail="Access denied to this voucher")
    
    return voucher

# ==================== RECONCILIATION ROUTES ====================

@router.get("/reconciliation/unmatched")
def get_unmatched_records(company_id: str, table_name: Optional[str] = None, db: Session = Depends(get_db)):
    """Get unmatched records for reconciliation"""
    # This would implement logic to find unmatched bank statements, GST records, etc.
    return {"message": "Reconciliation logic to be implemented"}

@router.post("/reconciliation/match")
def trigger_reconciliation(company_id: str, db: Session = Depends(get_db)):
    """Trigger AI-powered reconciliation for a company"""
    # This would implement the AI matching logic
    return {"message": "AI reconciliation triggered", "company_id": company_id}

# ==================== EXTERNAL DATA ROUTES ====================

@router.get("/bank-statements")
def get_bank_statements(
    skip: int = 0,
    limit: int = 100,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    reconciliation_status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    """Get bank statements for a company"""
    # Verify access to company
    accessible_firms = get_user_accessible_firms(db, current_user)
    company = db.query(Entity).filter(Entity.company_id == x_company_id).first()
    if not company or (accessible_firms and company.firm_id not in accessible_firms):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    query = db.query(BankStatement).filter(BankStatement.company_id == x_company_id)
    
    if from_date:
        query = query.filter(BankStatement.transaction_date >= from_date)
    if to_date:
        query = query.filter(BankStatement.transaction_date <= to_date)
    if reconciliation_status:
        query = query.filter(BankStatement.reconciliation_status == reconciliation_status)
    
    statements = query.offset(skip).limit(limit).all()
    return statements

@router.get("/gst-sales")
def get_gst_sales(
    skip: int = 0,
    limit: int = 100,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    reconciliation_status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    """Get GST sales records for a company"""
    # Verify access to company
    accessible_firms = get_user_accessible_firms(db, current_user)
    company = db.query(Entity).filter(Entity.company_id == x_company_id).first()
    if not company or (accessible_firms and company.firm_id not in accessible_firms):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    query = db.query(GSTSales).filter(GSTSales.company_id == x_company_id)
    
    if from_date:
        query = query.filter(GSTSales.invoice_date >= from_date)
    if to_date:
        query = query.filter(GSTSales.invoice_date <= to_date)
    if reconciliation_status:
        query = query.filter(GSTSales.reconciliation_status == reconciliation_status)
    
    sales = query.offset(skip).limit(limit).all()
    return sales

@router.get("/gst-purchases")
def get_gst_purchases(
    skip: int = 0,
    limit: int = 100,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    reconciliation_status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    """Get GST purchases records for a company"""
    # Verify access to company
    accessible_firms = get_user_accessible_firms(db, current_user)
    company = db.query(Entity).filter(Entity.company_id == x_company_id).first()
    if not company or (accessible_firms and company.firm_id not in accessible_firms):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    query = db.query(GSTPurchases).filter(GSTPurchases.company_id == x_company_id)
    
    if from_date:
        query = query.filter(GSTPurchases.invoice_date >= from_date)
    if to_date:
        query = query.filter(GSTPurchases.invoice_date <= to_date)
    if reconciliation_status:
        query = query.filter(GSTPurchases.reconciliation_status == reconciliation_status)
    
    purchases = query.offset(skip).limit(limit).all()
    return purchases

# ==================== DASHBOARD ROUTES ====================

@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    """Get dashboard statistics for a company"""
    # Verify access to company
    accessible_firms = get_user_accessible_firms(db, current_user)
    company = db.query(Entity).filter(Entity.company_id == x_company_id).first()
    if not company or (accessible_firms and company.firm_id not in accessible_firms):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    # Get counts
    total_vouchers = db.query(VoucherHeader).filter(VoucherHeader.company_id == x_company_id).count()
    total_bank_statements = db.query(BankStatement).filter(BankStatement.company_id == x_company_id).count()
    matched_bank = db.query(BankStatement).filter(
        BankStatement.company_id == x_company_id,
        BankStatement.reconciliation_status == "Matched"
    ).count()
    
    # Calculate totals
    voucher_sum = db.query(VoucherHeader).filter(VoucherHeader.company_id == x_company_id).all()
    total_amount = sum(v.total_amount or 0 for v in voucher_sum)
    
    # Recent records
    recent_vouchers = db.query(VoucherHeader).filter(
        VoucherHeader.company_id == x_company_id
    ).order_by(VoucherHeader.voucher_date.desc()).limit(5).all()
    
    recent_bank_statements = db.query(BankStatement).filter(
        BankStatement.company_id == x_company_id
    ).order_by(BankStatement.transaction_date.desc()).limit(5).all()
    
    return {
        "total_entities": 1,  # For now, single entity per company
        "total_vouchers": total_vouchers,
        "total_amount": float(total_amount),
        "pending_reconciliation": total_bank_statements - matched_bank,
        "reconciliation_summary": {
            "matched": matched_bank,
            "unmatched": total_bank_statements - matched_bank,
            "total": total_bank_statements
        },
        "recent_vouchers": recent_vouchers,
        "recent_bank_statements": recent_bank_statements
    }

@router.get("/reconciliation/summary")
def get_reconciliation_summary(
    current_user: AuthenticatedUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    x_company_id: str = Header(..., alias="X-Company-ID")
):
    """Get reconciliation summary for a company"""
    # Verify access to company
    accessible_firms = get_user_accessible_firms(db, current_user)
    company = db.query(Entity).filter(Entity.company_id == x_company_id).first()
    if not company or (accessible_firms and company.firm_id not in accessible_firms):
        raise HTTPException(status_code=403, detail="Access denied to this company")
    
    # Bank statements reconciliation
    total_bank = db.query(BankStatement).filter(BankStatement.company_id == x_company_id).count()
    matched_bank = db.query(BankStatement).filter(
        BankStatement.company_id == x_company_id,
        BankStatement.reconciliation_status == "Matched"
    ).count()
    
    # GST reconciliation
    total_gst_sales = db.query(GSTSales).filter(GSTSales.company_id == x_company_id).count()
    matched_gst_sales = db.query(GSTSales).filter(
        GSTSales.company_id == x_company_id,
        GSTSales.reconciliation_status == "Matched"
    ).count()
    
    total_gst_purchases = db.query(GSTPurchases).filter(GSTPurchases.company_id == x_company_id).count()
    matched_gst_purchases = db.query(GSTPurchases).filter(
        GSTPurchases.company_id == x_company_id,
        GSTPurchases.reconciliation_status == "Matched"
    ).count()
    
    return {
        "bank_statements": {
            "total": total_bank,
            "matched": matched_bank,
            "unmatched": total_bank - matched_bank,
            "reconciliation_rate": (matched_bank / total_bank * 100) if total_bank > 0 else 0
        },
        "gst_sales": {
            "total": total_gst_sales,
            "matched": matched_gst_sales,
            "unmatched": total_gst_sales - matched_gst_sales,
            "reconciliation_rate": (matched_gst_sales / total_gst_sales * 100) if total_gst_sales > 0 else 0
        },
        "gst_purchases": {
            "total": total_gst_purchases,
            "matched": matched_gst_purchases,
            "unmatched": total_gst_purchases - matched_gst_purchases,
            "reconciliation_rate": (matched_gst_purchases / total_gst_purchases * 100) if total_gst_purchases > 0 else 0
        }
    }