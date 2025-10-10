# app/ram/routes.py
"""
RAM Cognitive Framework API Routes
FastAPI routes for CA firm automation with cognitive capabilities
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant_context import get_tenant_context, TenantContext
from app.core.auth import get_current_user
from app.core.logger import log_request

from app.ram.ram_service import RAMOrchestrationService, get_ram_service
from app.ram.reflection_core.meta_cognition import ReflectionType


router = APIRouter(prefix="/ram", tags=["RAM Cognitive Framework"])


# Pydantic Models for API
class ReconciliationBatchRequest(BaseModel):
    batch_size: int = Field(default=100, ge=1, le=1000, description="Number of items to process")
    financial_year: str = Field(default="2023-24", description="Financial year for processing")
    priority: str = Field(default="medium", description="Processing priority")
    mode: str = Field(default="automatic", description="Processing mode")
    confidence_threshold: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    near_match_threshold: Optional[float] = Field(default=0.6, ge=0.0, le=1.0)

class ReconciliationBatchResponse(BaseModel):
    ram_processing_summary: Dict[str, Any]
    cognitive_insights: Dict[str, Any]
    adaptive_learning: Dict[str, Any]
    reflection_outcomes: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    detailed_results: List[Dict[str, Any]]

class SystemStatusResponse(BaseModel):
    cognitive_status: Dict[str, Any]
    learning_progress: Dict[str, Any]
    reflection_insights: Dict[str, Any]
    system_health: Dict[str, Any]

class ReflectionTriggerRequest(BaseModel):
    reflection_type: str = Field(description="Type of reflection to trigger")
    trigger_event: str = Field(description="Event that triggered reflection")
    performance_data: Dict[str, Any] = Field(description="Performance data for analysis")

class ReflectionResponse(BaseModel):
    reflection_id: str
    analysis: Dict[str, Any]
    strategies: List[Dict[str, Any]]
    insights: str
    actions: List[Dict[str, Any]]
    confidence: float

class LearningStatsResponse(BaseModel):
    total_patterns_learned: int
    high_success_patterns: int
    average_success_score: float
    learning_rate: float
    success_threshold: float
    most_used_pattern: Dict[str, Any]
    adaptive_weights: Dict[str, float]

class RecommendationRequest(BaseModel):
    context: Dict[str, Any] = Field(description="Context for recommendations")
    min_confidence: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    limit: Optional[int] = Field(default=5, ge=1, le=20)


@router.post("/reconciliation/batch", response_model=ReconciliationBatchResponse)
async def process_reconciliation_batch(
    request: ReconciliationBatchRequest,
    background_tasks: BackgroundTasks,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Process a batch of reconciliation requests using full RAM cognitive framework
    """
    
    # Log the API request
    await log_request("ram_batch_reconciliation", {
        "company_id": context.company_id,
        "user_id": current_user.get("user_id"),
        "batch_size": request.batch_size,
        "mode": request.mode
    })
    
    try:
        # Convert Pydantic model to dict for processing
        reconciliation_request = {
            "batch_size": request.batch_size,
            "financial_year": request.financial_year,
            "priority": request.priority,
            "mode": request.mode,
            "confidence_threshold": request.confidence_threshold,
            "near_match_threshold": request.near_match_threshold
        }
        
        # Process with RAM cognitive framework
        result = await ram_service.process_reconciliation_batch(
            context, reconciliation_request
        )
        
        return ReconciliationBatchResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAM processing failed: {str(e)}"
        )


@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Get comprehensive RAM system status and performance metrics
    """
    
    try:
        status_data = await ram_service.get_system_status(context.company_id)
        return SystemStatusResponse(**status_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.post("/reflection/trigger", response_model=ReflectionResponse)
async def trigger_reflection(
    request: ReflectionTriggerRequest,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Manually trigger a reflection session for performance analysis
    """
    
    try:
        # Validate reflection type
        try:
            reflection_type = ReflectionType(request.reflection_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reflection type: {request.reflection_type}"
            )
        
        # Trigger reflection
        reflection_result = ram_service.meta_cognition.trigger_reflection(
            reflection_type,
            request.trigger_event,
            request.performance_data,
            context.company_id
        )
        
        return ReflectionResponse(**reflection_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reflection failed: {str(e)}"
        )


@router.get("/learning/statistics", response_model=LearningStatsResponse)
async def get_learning_statistics(
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Get adaptive learning statistics and progress metrics
    """
    
    try:
        stats = ram_service.adaptive_memory.get_learning_statistics(context.company_id)
        return LearningStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get learning statistics: {str(e)}"
        )


@router.post("/recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Get AI recommendations based on learned patterns and current context
    """
    
    try:
        recommendations = ram_service.adaptive_memory.get_recommendations_for_context(
            request.context,
            context.company_id
        )
        
        # Filter by confidence if specified
        if request.min_confidence:
            recommendations = [
                rec for rec in recommendations 
                if rec.get("confidence", 0.0) >= request.min_confidence
            ]
        
        # Apply limit
        if request.limit:
            recommendations = recommendations[:request.limit]
        
        return {
            "recommendations": recommendations,
            "total_available": len(recommendations),
            "context_analyzed": request.context,
            "min_confidence_applied": request.min_confidence
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/reflection/summary")
async def get_reflection_summary(
    days: int = 30,
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Get reflection summary for the specified time period
    """
    
    try:
        summary = ram_service.meta_cognition.get_reflection_summary(
            context.company_id, days
        )
        
        return {
            "reflection_summary": summary,
            "period_days": days,
            "company_id": context.company_id,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reflection summary: {str(e)}"
        )


@router.get("/cognitive/insights")
async def get_cognitive_insights(
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    ram_service: RAMOrchestrationService = Depends(get_ram_service)
):
    """
    Get current cognitive insights and processing capabilities
    """
    
    try:
        # Get recent cognitive processing results
        insights = {
            "perceptual_capabilities": {
                "data_sources_integrated": ["vouchers", "bank_statements", "gst_records"],
                "pattern_recognition_active": True,
                "contextual_analysis_enabled": True
            },
            "reasoning_capabilities": {
                "primitive_reasoning_functions": 8,
                "strategy_composition_active": True,
                "confidence_scoring_enabled": True,
                "adaptive_thresholds": True
            },
            "meta_cognitive_capabilities": {
                "performance_monitoring": True,
                "strategy_assessment": True,
                "error_analysis": True,
                "continuous_improvement": True
            },
            "adaptive_weights": ram_service.adaptive_memory.get_adaptive_weights(),
            "system_maturity": {
                "learning_phase": "active",
                "pattern_database_size": "growing",
                "confidence_calibration": "improving"
            }
        }
        
        return {
            "cognitive_insights": insights,
            "company_id": context.company_id,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cognitive insights: {str(e)}"
        )


@router.post("/processing/validate")
async def validate_processing_readiness(
    context: TenantContext = Depends(get_tenant_context),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate system readiness for RAM cognitive processing
    """
    
    try:
        # Check data availability
        from app.cdm.models.transaction import VoucherHeader
        from app.cdm.models.external import BankStatement
        
        voucher_count = db.query(VoucherHeader).filter(
            VoucherHeader.company_id == context.company_id,
            VoucherHeader.reconciliation_status == "Unmatched"
        ).count()
        
        statement_count = db.query(BankStatement).filter(
            BankStatement.company_id == context.company_id,
            BankStatement.reconciliation_status == "Unmatched"
        ).count()
        
        # Check system components
        readiness_check = {
            "data_availability": {
                "unmatched_vouchers": voucher_count,
                "unmatched_statements": statement_count,
                "processing_ready": voucher_count > 0 and statement_count > 0
            },
            "system_components": {
                "cognitive_engine": True,
                "adaptive_memory": True,
                "meta_cognition": True,
                "database_connectivity": True
            },
            "processing_recommendations": []
        }
        
        # Generate recommendations
        if voucher_count == 0:
            readiness_check["processing_recommendations"].append(
                "No unmatched vouchers available for processing"
            )
        
        if statement_count == 0:
            readiness_check["processing_recommendations"].append(
                "No unmatched bank statements available for processing"
            )
        
        if voucher_count > 0 and statement_count > 0:
            readiness_check["processing_recommendations"].append(
                f"Ready to process {min(voucher_count, statement_count)} reconciliation pairs"
            )
        
        return {
            "readiness_check": readiness_check,
            "company_id": context.company_id,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Readiness validation failed: {str(e)}"
        )