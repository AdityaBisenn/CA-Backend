# app/cdm/models/transaction.py
from sqlalchemy import Column, String, Numeric, Date, Boolean, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid

class VoucherStatus(enum.Enum):
    DRAFT = "Draft"
    POSTED = "Posted"
    VERIFIED = "Verified"

class ReconciliationStatus(enum.Enum):
    UNMATCHED = "Unmatched"
    AUTO_MATCHED = "AutoMatched"
    MANUALLY_VERIFIED = "ManuallyVerified"
    DISPUTED = "Disputed"

class VoucherHeader(Base):
    __tablename__ = "vouchers"

    voucher_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    voucher_type = Column(String, nullable=False)
    voucher_date = Column(Date, nullable=False)
    voucher_number = Column(String, nullable=False)
    party_ledger_id = Column(String, ForeignKey("ledgers.ledger_id"))
    narration = Column(String)
    ref_document = Column(String)
    total_amount = Column(Numeric(18,2), nullable=False)
    status = Column(Enum(VoucherStatus), default=VoucherStatus.DRAFT)
    is_gst_applicable = Column(Boolean, default=False)
    place_of_supply = Column(String)
    source_system = Column(String)
    external_match_key = Column(String)
    reconciliation_status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.UNMATCHED)
    reconciliation_source = Column(String)
    reconciliation_confidence = Column(Numeric(5,4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    entity = relationship("Entity", back_populates="vouchers")
    party_ledger = relationship("Ledger", back_populates="voucher_headers")
    lines = relationship("VoucherLine", back_populates="voucher", cascade="all, delete-orphan")
    bank_statements = relationship("BankStatement", back_populates="linked_voucher")
    gst_sales = relationship("GSTSales", back_populates="linked_voucher")
    gst_purchases = relationship("GSTPurchases", back_populates="linked_voucher")

    # Indexes for performance
    __table_args__ = (
        Index('idx_voucher_company_date', 'company_id', 'voucher_date'),
        Index('idx_voucher_type_status', 'voucher_type', 'status'),
        Index('idx_voucher_external_key', 'external_match_key'),
    )

class VoucherLine(Base):
    __tablename__ = "voucher_lines"

    line_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voucher_id = Column(String, ForeignKey("vouchers.voucher_id"), nullable=False)
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    ledger_id = Column(String, ForeignKey("ledgers.ledger_id"), nullable=False)
    debit = Column(Numeric(18,2), default=0.0)
    credit = Column(Numeric(18,2), default=0.0)
    item_id = Column(String, ForeignKey("stock_items.item_id"))
    quantity = Column(Numeric(15,4))
    rate = Column(Numeric(18,4))
    tax_id = Column(String, ForeignKey("tax_ledgers.tax_id"))
    tax_amount = Column(Numeric(18,2), default=0.0)
    discount = Column(Numeric(18,2), default=0.0)
    round_off = Column(Numeric(18,2), default=0.0)
    narration = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    voucher = relationship("VoucherHeader", back_populates="lines")
    ledger = relationship("Ledger", back_populates="voucher_lines")
    stock_item = relationship("StockItem", back_populates="voucher_lines")
    tax_ledger = relationship("TaxLedger", back_populates="voucher_lines")

    # Indexes
    __table_args__ = (
        Index('idx_vline_voucher_ledger', 'voucher_id', 'ledger_id'),
        Index('idx_vline_company_date', 'company_id'),
    )