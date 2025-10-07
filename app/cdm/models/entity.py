# app/cdm/models/entity.py
from sqlalchemy import Column, String, Date, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
import uuid

class GSTType(enum.Enum):
    REGULAR = "Regular"
    COMPOSITION = "Composition"

class Entity(Base):
    __tablename__ = "entities"

    company_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    firm_id = Column(String, ForeignKey("ca_firms.firm_id"), nullable=True, index=True)  # Temporarily nullable for migration
    company_name = Column(String, nullable=False)
    financial_year_start = Column(Date, nullable=False)
    financial_year_end = Column(Date, nullable=False)
    books_begin_from = Column(Date)
    gst_registration_type = Column(Enum(GSTType))
    state = Column(String)
    gstin = Column(String, unique=True)
    currency = Column(String, default="INR")
    pan = Column(String)
    cin = Column(String)
    registration_type = Column(String)
    tan = Column(String)
    ifsc_default_bank = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    firm = relationship("CAFirm", back_populates="entities")
    groups = relationship("Group", back_populates="entity", cascade="all, delete-orphan", lazy="select")
    ledgers = relationship("Ledger", back_populates="entity", cascade="all, delete-orphan", lazy="select")
    vouchers = relationship("VoucherHeader", back_populates="entity", cascade="all, delete-orphan", lazy="select")
    user_assignments = relationship("UserEntityMap", back_populates="entity", cascade="all, delete-orphan", lazy="select")