# app/cdm/models/master.py
from sqlalchemy import Column, String, Numeric, Boolean, Enum, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid

class GroupNature(enum.Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    INCOME = "Income"
    EXPENSE = "Expense"

class Group(Base):
    __tablename__ = "groups"
    
    group_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    group_name = Column(String, nullable=False)
    parent_group_id = Column(String, ForeignKey("groups.group_id"), nullable=True)
    nature = Column(Enum(GroupNature))
    is_primary = Column(Boolean, default=False)
    behaves_like_subledger = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    entity = relationship("Entity", back_populates="groups")
    parent_group = relationship("Group", remote_side=[group_id])
    ledgers = relationship("Ledger", back_populates="group")

    # Indexes for performance
    __table_args__ = (
        Index('idx_group_company_name', 'company_id', 'group_name'),
    )

class Ledger(Base):
    __tablename__ = "ledgers"
    
    ledger_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    ledger_name = Column(String, nullable=False)
    group_id = Column(String, ForeignKey("groups.group_id"))
    opening_balance = Column(Numeric(18,2), default=0.0)
    dr_cr = Column(String)
    gst_registration_no = Column(String)
    gst_applicable = Column(Boolean, default=False)
    default_credit_period = Column(Integer, default=0)
    address = Column(String)
    type = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    entity = relationship("Entity", back_populates="ledgers")
    group = relationship("Group", back_populates="ledgers")
    voucher_headers = relationship("VoucherHeader", back_populates="party_ledger")
    voucher_lines = relationship("VoucherLine", back_populates="ledger")

    # Indexes
    __table_args__ = (
        Index('idx_ledger_company_name', 'company_id', 'ledger_name'),
        Index('idx_ledger_group', 'group_id'),
    )

class StockItem(Base):
    __tablename__ = "stock_items"
    
    item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    item_name = Column(String, nullable=False)
    stock_group = Column(String)
    unit = Column(String)
    hsn_code = Column(String)
    tax_rate = Column(Numeric(5,2))
    valuation_method = Column(String)
    is_nil_rated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    voucher_lines = relationship("VoucherLine", back_populates="stock_item")

    # Indexes
    __table_args__ = (
        Index('idx_stock_company_name', 'company_id', 'item_name'),
        Index('idx_stock_hsn', 'hsn_code'),
    )

class TaxLedger(Base):
    __tablename__ = "tax_ledgers"
    
    tax_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    tax_name = Column(String, nullable=False)
    rate = Column(Numeric(5,2), nullable=False)
    type = Column(String)
    ledger_ref = Column(String, ForeignKey("ledgers.ledger_id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ledger = relationship("Ledger")
    voucher_lines = relationship("VoucherLine", back_populates="tax_ledger")

    # Indexes
    __table_args__ = (
        Index('idx_tax_company_type', 'company_id', 'type'),
    )