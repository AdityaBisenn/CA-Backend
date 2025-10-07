# app/cdm/schemas/entity.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from enum import Enum

class GSTType(str, Enum):
    REGULAR = "Regular"
    COMPOSITION = "Composition"

class EntityBase(BaseModel):
    company_name: str
    financial_year_start: date
    financial_year_end: date
    books_begin_from: Optional[date] = None
    gst_registration_type: Optional[GSTType] = None
    state: Optional[str] = None
    gstin: Optional[str] = None
    currency: Optional[str] = "INR"
    pan: Optional[str] = None
    cin: Optional[str] = None
    registration_type: Optional[str] = None
    tan: Optional[str] = None
    ifsc_default_bank: Optional[str] = None
    is_active: bool = True

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    company_name: Optional[str] = None
    financial_year_start: Optional[date] = None
    financial_year_end: Optional[date] = None
    books_begin_from: Optional[date] = None
    gst_registration_type: Optional[GSTType] = None
    state: Optional[str] = None
    gstin: Optional[str] = None
    currency: Optional[str] = None
    pan: Optional[str] = None
    cin: Optional[str] = None
    registration_type: Optional[str] = None
    tan: Optional[str] = None
    ifsc_default_bank: Optional[str] = None
    is_active: Optional[bool] = None

class EntityResponse(EntityBase):
    company_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True