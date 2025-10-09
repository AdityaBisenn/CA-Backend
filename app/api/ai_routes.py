# app/api/ai_routes.py
"""
AI-powered API endpoints for reconciliation and financial analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.tenant_context import get_tenant_context, TenantContext
from app.core.auth import require_staff_access, get_current_user
from app.services.ai_reconciliation import AIReconciliationService
from app.cdm.models.transaction import VoucherHeader
from app.cdm.models.external import BankStatement

router = APIRouter(prefix="/ai", tags=["AI Analytics"])

# Request/Response Models
class ReconciliationRequest(BaseModel):
    start_date: date
    end_date: date
    auto_match_threshold: Optional[float] = Field(default=0.85, ge=0.0, le=1.0)

class AnomalyAnalysisRequest(BaseModel):
    voucher_ids: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class AIFeedbackRequest(BaseModel):
    voucher_id: str
    original_prediction: Dict
    user_correction: Dict
    feedback_type: str = Field(..., pattern="^(classification|reconciliation|validation)$")

class ReconciliationResult(BaseModel):
    total_vouchers: int
    matched_count: int
    requires_review_count: int
    unmatched_count: int
    average_confidence: float
    processing_time_seconds: float

@router.post("/reconcile/bank-statements", response_model=ReconciliationResult)
async def ai_bank_reconciliation(
    request: ReconciliationRequest,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(require_staff_access),
    db: Session = Depends(get_db)
):
    """
    Perform AI-powered bank reconciliation for the specified date range
    """
    try:
        start_time = datetime.now()
        
        # Initialize AI service
        ai_service = AIReconciliationService(db, context)
        
        # Get vouchers for the date range
        vouchers = db.query(VoucherHeader).filter(
            VoucherHeader.company_id == context.company_id,
            VoucherHeader.voucher_date >= request.start_date,
            VoucherHeader.voucher_date <= request.end_date,
            VoucherHeader.is_active == True
        ).all()
        
        if not vouchers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No vouchers found for the specified date range"
            )
        
        # Get unmatched bank statements
        bank_statements = db.query(BankStatement).filter(
            BankStatement.company_id == context.company_id,
            BankStatement.transaction_date >= request.start_date,
            BankStatement.transaction_date <= request.end_date,
            BankStatement.reconciliation_status == "Unmatched"
        ).all()
        
        # Perform AI reconciliation
        results = await ai_service.intelligent_bank_reconciliation(vouchers, bank_statements)
        
        # Calculate statistics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        matched_count = sum(1 for r in results if r['matched'] and not r['requires_review'])
        review_count = sum(1 for r in results if r['matched'] and r['requires_review'])
        unmatched_count = len(vouchers) - len(results)
        
        avg_confidence = (
            sum(r['confidence'] for r in results if r['matched']) / 
            len([r for r in results if r['matched']])
        ) if results else 0.0
        
        return ReconciliationResult(
            total_vouchers=len(vouchers),
            matched_count=matched_count,
            requires_review_count=review_count,
            unmatched_count=unmatched_count,
            average_confidence=round(avg_confidence, 4),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI reconciliation failed: {str(e)}"
        )

@router.post("/analyze/anomalies")
async def detect_financial_anomalies(
    request: AnomalyAnalysisRequest,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(require_staff_access),
    db: Session = Depends(get_db)
):
    """
    Use AI to detect potential anomalies in financial transactions
    """
    try:
        ai_service = AIReconciliationService(db, context)
        
        # Build query based on request
        query = db.query(VoucherHeader).filter(
            VoucherHeader.company_id == context.company_id,
            VoucherHeader.is_active == True
        )
        
        if request.voucher_ids:
            query = query.filter(VoucherHeader.voucher_id.in_(request.voucher_ids))
        
        if request.start_date:
            query = query.filter(VoucherHeader.voucher_date >= request.start_date)
            
        if request.end_date:
            query = query.filter(VoucherHeader.voucher_date <= request.end_date)
        
        vouchers = query.limit(100).all()  # Limit for performance
        
        if not vouchers:
            return {
                "anomalies_found": False,
                "summary": "No vouchers found for analysis",
                "risk_level": "none"
            }
        
        # Perform AI anomaly detection
        analysis = await ai_service.analyze_financial_anomalies(vouchers)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}"
        )

@router.get("/reports/reconciliation-insights")
async def generate_reconciliation_insights(
    start_date: date,
    end_date: date,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(require_staff_access),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered reconciliation insights report
    """
    try:
        ai_service = AIReconciliationService(db, context)
        
        # Convert dates to datetime for service
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        report = await ai_service.generate_reconciliation_report(
            start_datetime, 
            end_datetime
        )
        
        return {
            "report_period": f"{start_date} to {end_date}",
            "generated_at": datetime.now().isoformat(),
            "report_content": report,
            "format": "markdown"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )

@router.post("/feedback")
async def submit_ai_feedback(
    request: AIFeedbackRequest,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(require_staff_access),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on AI predictions for model improvement
    """
    try:
        ai_service = AIReconciliationService(db, context)
        
        feedback_id = ai_service.record_ai_feedback(
            voucher_id=request.voucher_id,
            original_prediction=request.original_prediction,
            user_correction=request.user_correction,
            feedback_type=request.feedback_type,
            user_id=current_user.user_id
        )
        
        return {
            "feedback_id": feedback_id,
            "status": "recorded",
            "message": "Thank you for your feedback. This will help improve AI accuracy."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )

@router.get("/health")
async def ai_service_health():
    """
    Check AI service health and LLM connectivity
    """
    try:
        from app.core.init_llm import make_llm
        
        # Test LLM connectivity
        llm = make_llm()
        test_response = llm.invoke("Test connection. Respond with 'OK'.")
        
        return {
            "status": "healthy",
            "llm_connected": "OK" in test_response.content,
            "model": "gpt-4",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }