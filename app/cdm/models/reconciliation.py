# app/cdm/models/reconciliation.py
from sqlalchemy import Column, String, Numeric, Text, DateTime, JSON, Index, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class ReconciliationLog(Base):
    __tablename__ = "reconciliation_log"

    recon_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    source_table = Column(String, nullable=False)
    target_table = Column(String, nullable=False)
    source_record_id = Column(String, nullable=False)
    target_record_id = Column(String)
    match_score = Column(Numeric(5,4))  # AI confidence score (0.0000 to 1.0000)
    match_rule = Column(String)  # Rule that triggered the match
    rule_details = Column(JSON)  # Store AI reasoning, parameters, etc.
    status = Column(String, default="Pending")  # Pending, Matched, Rejected, Manual_Review
    remarks = Column(Text)
    ai_reasoning = Column(Text)  # Store model explanations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_recon_company_source', 'company_id', 'source_table'),
        Index('idx_recon_status_score', 'status', 'match_score'),
        Index('idx_recon_source_record', 'source_record_id'),
        Index('idx_recon_target_record', 'target_record_id'),
    )

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # csv, xlsx, pdf, etc.
    file_size = Column(Numeric(15,0))  # bytes
    file_hash = Column(String)  # SHA256 of file content
    status = Column(String, default="Started")  # Started, Processing, Completed, Failed
    records_processed = Column(Numeric(10,0), default=0)
    records_failed = Column(Numeric(10,0), default=0)
    error_details = Column(JSON)  # Store errors and warnings
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    processing_duration = Column(Numeric(10,3))  # seconds

    # Indexes
    __table_args__ = (
        Index('idx_job_company_status', 'company_id', 'status'),
        Index('idx_job_file_hash', 'file_hash'),
    )

class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    table_name = Column(String, nullable=False)
    record_id = Column(String, nullable=False)
    operation = Column(String, nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)  # Before state
    new_values = Column(JSON)  # After state
    user_id = Column(String)  # Who made the change
    session_id = Column(String)  # Session/request identifier
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_audit_company_table', 'company_id', 'table_name'),
        Index('idx_audit_record', 'record_id'),
        Index('idx_audit_timestamp', 'timestamp'),
    )

class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    feedback_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)
    voucher_id = Column(String, ForeignKey("vouchers.voucher_id"))
    original_prediction = Column(JSON)  # What AI originally suggested
    user_correction = Column(JSON)  # What user actually did
    feedback_type = Column(String)  # classification, reconciliation, validation
    confidence_before = Column(Numeric(5,4))
    confidence_after = Column(Numeric(5,4))
    model_version = Column(String)  # Track which AI model version
    user_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_feedback_company_type', 'company_id', 'feedback_type'),
        Index('idx_feedback_voucher', 'voucher_id'),
    )