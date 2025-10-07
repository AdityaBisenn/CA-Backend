# app/cdm/schemas/transaction.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

class VoucherStatus(str, Enum):
    DRAFT = "Draft"
    POSTED = "Posted"
    VERIFIED = "Verified"

class ReconciliationStatus(str, Enum):
    UNMATCHED = "Unmatched"
    AUTO_MATCHED = "AutoMatched"
    MANUALLY_VERIFIED = "ManuallyVerified"
    DISPUTED = "Disputed"

class VoucherLineBase(BaseModel):
    ledger_id: str
    debit: Decimal = Decimal('0.00')
    credit: Decimal = Decimal('0.00')
    item_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    rate: Optional[Decimal] = None
    tax_id: Optional[str] = None
    tax_amount: Decimal = Decimal('0.00')
    discount: Decimal = Decimal('0.00')
    round_off: Decimal = Decimal('0.00')
    narration: Optional[str] = None

class VoucherLineCreate(VoucherLineBase):
    pass

class VoucherLineUpdate(BaseModel):
    ledger_id: Optional[str] = None
    debit: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    item_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    rate: Optional[Decimal] = None
    tax_id: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    narration: Optional[str] = None

class VoucherLineResponse(VoucherLineBase):
    line_id: str
    voucher_id: str
    company_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VoucherHeaderBase(BaseModel):
    company_id: str
    voucher_type: str
    voucher_date: date
    voucher_number: str
    party_ledger_id: Optional[str] = None
    narration: Optional[str] = None
    ref_document: Optional[str] = None
    total_amount: Decimal
    status: VoucherStatus = VoucherStatus.DRAFT
    is_gst_applicable: bool = False
    place_of_supply: Optional[str] = None
    source_system: Optional[str] = None
    external_match_key: Optional[str] = None
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.UNMATCHED
    reconciliation_source: Optional[str] = None
    reconciliation_confidence: Optional[Decimal] = None

class VoucherHeaderCreate(VoucherHeaderBase):
    lines: List[VoucherLineCreate] = []

class VoucherHeaderUpdate(BaseModel):
    voucher_type: Optional[str] = None
    voucher_date: Optional[date] = None
    voucher_number: Optional[str] = None
    party_ledger_id: Optional[str] = None
    narration: Optional[str] = None
    ref_document: Optional[str] = None
    total_amount: Optional[Decimal] = None
    status: Optional[VoucherStatus] = None
    is_gst_applicable: Optional[bool] = None
    place_of_supply: Optional[str] = None
    source_system: Optional[str] = None
    external_match_key: Optional[str] = None
    reconciliation_status: Optional[ReconciliationStatus] = None
    reconciliation_source: Optional[str] = None
    reconciliation_confidence: Optional[Decimal] = None

class VoucherHeaderResponse(VoucherHeaderBase):
    voucher_id: str
    lines: List[VoucherLineResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True