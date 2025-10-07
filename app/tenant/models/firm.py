# app/tenant/models/firm.py
from sqlalchemy import Column, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class CAFirm(Base):
    __tablename__ = "ca_firms"

    firm_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    firm_name = Column(String, nullable=False)
    contact_email = Column(String)
    phone = Column(String)
    address = Column(Text)
    gstin = Column(String)
    pan = Column(String)
    firm_registration_no = Column(String)  # CA firm registration
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    subscription_tier = Column(String, default="basic")  # basic, premium, enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    entities = relationship("Entity", back_populates="firm", cascade="all, delete-orphan")
    users = relationship("User", back_populates="firm", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_firm_name', 'firm_name'),
        Index('idx_firm_gstin', 'gstin'),
        Index('idx_firm_active', 'is_active'),
    )