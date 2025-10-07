# app/tenant/schemas/firm.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CAFirmBase(BaseModel):
    """Base schema for CA Firm"""
    firm_name: str = Field(..., description="Name of the CA firm")
    firm_code: str = Field(..., description="Unique code for the CA firm")
    email: str = Field(..., description="Primary email address")
    phone: Optional[str] = Field(None, description="Primary phone number")
    address: Optional[str] = Field(None, description="Office address")
    gst_number: Optional[str] = Field(None, description="GST registration number")
    pan_number: Optional[str] = Field(None, description="PAN number")
    registration_number: Optional[str] = Field(None, description="CA registration number")
    is_active: bool = Field(True, description="Whether firm is active")

class CAFirmCreate(CAFirmBase):
    """Schema for creating a new CA firm"""
    pass

class CAFirmUpdate(BaseModel):
    """Schema for updating CA firm details"""
    firm_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    registration_number: Optional[str] = None
    is_active: Optional[bool] = None

class CAFirmResponse(CAFirmBase):
    """Schema for CA firm response"""
    firm_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class CAFirmList(BaseModel):
    """Schema for listing CA firms"""
    firms: List[CAFirmResponse]
    total: int
    page: int
    per_page: int

class CAFirmSummary(BaseModel):
    """Schema for CA firm summary statistics"""
    firm_id: str
    firm_name: str
    firm_code: str
    total_clients: int
    active_clients: int
    total_users: int
    active_users: int
    created_at: datetime

    model_config = {"from_attributes": True}