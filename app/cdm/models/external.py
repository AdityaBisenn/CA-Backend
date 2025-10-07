# app/cdm/models/external.py
from sqlalchemy import Column, String, Numeric, Date, Boolean, ForeignKey, DateTime, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import hashlib

class BankStatement(Base):
    __tablename__ = "bank_statements"

    bank_txn_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    bank_id = Column(String, ForeignKey("ledgers.ledger_id"), nullable=False)
    txn_date = Column(Date, nullable=False)
    value_date = Column(Date)
    narration = Column(String)
    amount = Column(Numeric(18,2), nullable=False)
    dr_cr = Column(String, nullable=False)
    cheque_ref = Column(String)
    balance_after_txn = Column(Numeric(18,2))
    txn_hash = Column(String, unique=True)  # SHA256 hash for duplicate prevention
    linked_voucher_id = Column(String, ForeignKey("vouchers.voucher_id"))
    reconciliation_status = Column(String, default="Unmatched")
    raw_json = Column(JSON)  # Store original extracted data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bank_ledger = relationship("Ledger")
    linked_voucher = relationship("VoucherHeader", back_populates="bank_statements")

    # Indexes
    __table_args__ = (
        Index('idx_bank_company_date', 'company_id', 'txn_date'),
        Index('idx_bank_reconciliation', 'reconciliation_status'),
        Index('idx_bank_hash', 'txn_hash'),
    )

    def generate_hash(self):
        """Generate SHA256 hash for duplicate detection"""
        hash_string = f"{self.bank_id}{self.txn_date}{self.amount}{self.dr_cr}{self.narration}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

class GSTSales(Base):
    __tablename__ = "gst_sales"

    gst_invoice_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    gstin_customer = Column(String)
    invoice_number = Column(String, nullable=False)
    invoice_date = Column(Date, nullable=False)
    taxable_value = Column(Numeric(18,2), nullable=False)
    tax_amount = Column(Numeric(18,2), default=0.0)
    total_value = Column(Numeric(18,2), nullable=False)
    status = Column(String, default="Active")
    invoice_hash = Column(String, unique=True)  # For deduplication
    linked_voucher_id = Column(String, ForeignKey("vouchers.voucher_id"))
    reconciliation_status = Column(String, default="Unmatched")
    raw_json = Column(JSON)  # Store GSTR data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    linked_voucher = relationship("VoucherHeader", back_populates="gst_sales")

    # Indexes
    __table_args__ = (
        Index('idx_gst_sales_company_date', 'company_id', 'invoice_date'),
        Index('idx_gst_sales_invoice', 'invoice_number'),
        Index('idx_gst_sales_hash', 'invoice_hash'),
    )

    def generate_hash(self):
        """Generate hash for invoice deduplication"""
        hash_string = f"{self.company_id}{self.invoice_number}{self.invoice_date}{self.total_value}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

class GSTPurchases(Base):
    __tablename__ = "gst_purchases"

    purchase_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    supplier_gstin = Column(String)
    invoice_number = Column(String, nullable=False)
    invoice_date = Column(Date, nullable=False)
    taxable_value = Column(Numeric(18,2), nullable=False)
    igst_amount = Column(Numeric(18,2), default=0.0)
    cgst_amount = Column(Numeric(18,2), default=0.0)
    sgst_amount = Column(Numeric(18,2), default=0.0)
    itc_available = Column(Boolean, default=True)
    invoice_hash = Column(String, unique=True)
    linked_voucher_id = Column(String, ForeignKey("vouchers.voucher_id"))
    reconciliation_status = Column(String, default="Unmatched")
    raw_json = Column(JSON)  # Store GSTR-2A data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    linked_voucher = relationship("VoucherHeader", back_populates="gst_purchases")

    # Indexes
    __table_args__ = (
        Index('idx_gst_purchase_company_date', 'company_id', 'invoice_date'),
        Index('idx_gst_purchase_supplier', 'supplier_gstin'),
        Index('idx_gst_purchase_hash', 'invoice_hash'),
    )

    def generate_hash(self):
        """Generate hash for invoice deduplication"""
        hash_string = f"{self.company_id}{self.supplier_gstin}{self.invoice_number}{self.invoice_date}"
        return hashlib.sha256(hash_string.encode()).hexdigest()