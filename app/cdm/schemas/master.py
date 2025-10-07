# app/cdm/schemas/master.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal

class GroupNature(str, Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    INCOME = "Income"
    EXPENSE = "Expense"

class GroupBase(BaseModel):
    company_id: str
    group_name: str
    parent_group_id: Optional[str] = None
    nature: Optional[GroupNature] = None
    is_primary: bool = False
    behaves_like_subledger: bool = False
    is_active: bool = True

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    group_name: Optional[str] = None
    parent_group_id: Optional[str] = None
    nature: Optional[GroupNature] = None
    is_primary: Optional[bool] = None
    behaves_like_subledger: Optional[bool] = None
    is_active: Optional[bool] = None

class GroupResponse(GroupBase):
    group_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LedgerBase(BaseModel):
    company_id: str
    ledger_name: str
    group_id: str
    opening_balance: Decimal = Decimal('0.00')
    dr_cr: Optional[str] = None
    gst_registration_no: Optional[str] = None
    gst_applicable: bool = False
    default_credit_period: int = 0
    address: Optional[str] = None
    type: Optional[str] = None
    is_active: bool = True

class LedgerCreate(LedgerBase):
    pass

class LedgerUpdate(BaseModel):
    ledger_name: Optional[str] = None
    group_id: Optional[str] = None
    opening_balance: Optional[Decimal] = None
    dr_cr: Optional[str] = None
    gst_registration_no: Optional[str] = None
    gst_applicable: Optional[bool] = None
    default_credit_period: Optional[int] = None
    address: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None

class LedgerResponse(LedgerBase):
    ledger_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StockItemBase(BaseModel):
    company_id: str
    item_name: str
    stock_group: Optional[str] = None
    unit: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    valuation_method: Optional[str] = None
    is_nil_rated: bool = False
    is_active: bool = True

class StockItemCreate(StockItemBase):
    pass

class StockItemUpdate(BaseModel):
    item_name: Optional[str] = None
    stock_group: Optional[str] = None
    unit: Optional[str] = None
    hsn_code: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    valuation_method: Optional[str] = None
    is_nil_rated: Optional[bool] = None
    is_active: Optional[bool] = None

class StockItemResponse(StockItemBase):
    item_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaxLedgerBase(BaseModel):
    company_id: str
    tax_name: str
    rate: Decimal
    type: str
    ledger_ref: Optional[str] = None
    is_active: bool = True

class TaxLedgerCreate(TaxLedgerBase):
    pass

class TaxLedgerUpdate(BaseModel):
    tax_name: Optional[str] = None
    rate: Optional[Decimal] = None
    type: Optional[str] = None
    ledger_ref: Optional[str] = None
    is_active: Optional[bool] = None

class TaxLedgerResponse(TaxLedgerBase):
    tax_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True