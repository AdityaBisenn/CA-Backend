# app/ram/ram_service.py
"""
RAM Cognitive Framework Service Integration
Main service orchestrator for CA firm automation with cognitive capabilities
"""

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.database import get_db
from app.core.tenant_context import TenantContext
from app.core.logger import log_request

# RAM Core Components
from app.ram.cognitive_core.reasoning_engine import RAMCognitiveEngine
from app.ram.adaptive_core.heuristic_memory import AdaptiveMemoryService
from app.ram.reflection_core.meta_cognition import MetaCognitionEngine, ReflectionType

# CDM Models
from app.cdm.models.reconciliation import ReconciliationLog, AIFeedback
from app.cdm.models.transaction import VoucherHeader, VoucherLine
from app.cdm.models.external import BankStatement, GSTSales, GSTPurchases

# AI Services
from app.services.ai_reconciliation import AIReconciliationService


class RAMOrchestrationService:
    """
    Main RAM service orchestrator that integrates all cognitive layers
    for CA firm automation and reconciliation processing
    """
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize RAM components
        self.cognitive_engine = RAMCognitiveEngine(db)
        self.adaptive_memory = AdaptiveMemoryService(db)
        self.meta_cognition = MetaCognitionEngine(db)
        
        # Initialize existing services (will be initialized with context when needed)
        self.ai_reconciliation_service = None
        
        # Processing metrics
        self.session_metrics = {
            "processed_items": 0,
            "successful_matches": 0,
            "near_matches": 0,
            "unmatched_items": 0,
            "processing_time": 0.0,
            "confidence_scores": []
        }
    
    async def process_reconciliation_batch(
        self,
        context: TenantContext,
        reconciliation_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for batch reconciliation processing with full RAM cognition
        """
        
        start_time = datetime.now()
        company_id = context.company_id
        
        # Log the request
        await log_request("ram_reconciliation", {
            "company_id": company_id,
            "request_type": "batch_processing",
            "items_count": reconciliation_request.get("items_count", 0)
        })
        
        try:
            # Phase 1: Perceptual Analysis & Data Gathering
            perceptual_data = await self._gather_perceptual_data(
                company_id, reconciliation_request
            )
            
            # Phase 2: Cognitive Reasoning
            reasoning_result = await self.cognitive_engine.process_reconciliation_request(
                perceptual_data, company_id
            )
            
            # Phase 3: Execute Reconciliation with Cognitive Insights
            execution_result = await self._execute_reconciliation_with_cognition(
                reasoning_result, company_id
            )
            
            # Phase 4: Adaptive Learning
            await self._learn_from_execution(execution_result, company_id)
            
            # Phase 5: Meta-Cognitive Reflection
            reflection_result = await self._reflect_on_performance(
                execution_result, company_id
            )
            
            # Calculate final metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            final_result = {
                "ram_processing_summary": {
                    "total_items_processed": execution_result.get("total_processed", 0),
                    "successful_matches": execution_result.get("successful_matches", 0),
                    "near_matches": execution_result.get("near_matches", 0),
                    "unmatched_items": execution_result.get("unmatched_items", 0),
                    "processing_time_seconds": processing_time,
                    "average_confidence": execution_result.get("average_confidence", 0.0)
                },
                "cognitive_insights": reasoning_result.get("insights", {}),
                "adaptive_learning": execution_result.get("learning_summary", {}),
                "reflection_outcomes": reflection_result,
                "recommendations": await self._generate_recommendations(
                    execution_result, company_id
                ),
                "detailed_results": execution_result.get("detailed_results", [])
            }
            
            return final_result
            
        except Exception as e:
            # Error reflection and learning
            error_context = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_stage": "unknown",
                "company_id": company_id
            }
            
            await self._handle_processing_error(error_context)
            raise
    
    async def _gather_perceptual_data(
        self,
        company_id: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather and structure perceptual data for cognitive processing"""
        
        # Get unreconciled vouchers
        vouchers = self.db.query(VoucherHeader).filter(
            VoucherHeader.company_id == company_id,
            VoucherHeader.reconciliation_status == "Unmatched"
        ).limit(request.get("batch_size", 100)).all()
        
        # Get unmatched bank statements
        bank_statements = self.db.query(BankStatement).filter(
            BankStatement.company_id == company_id,
            BankStatement.reconciliation_status == "Unmatched"
        ).limit(request.get("batch_size", 100)).all()
        
        # Get historical reconciliation patterns
        recent_reconciliations = self.db.query(ReconciliationLog).filter(
            ReconciliationLog.company_id == company_id
        ).order_by(ReconciliationLog.created_at.desc()).limit(50).all()
        
        # Structure perceptual data
        perceptual_data = {
            "context": {
                "company_id": company_id,
                "financial_year": request.get("financial_year", "2023-24"),
                "domain": "reconciliation",
                "task_type": "batch_processing",
                "priority": request.get("priority", "medium")
            },
            "vouchers": [
                {
                    "voucher_id": v.voucher_id,
                    "voucher_type": v.voucher_type,
                    "voucher_date": v.voucher_date.isoformat(),
                    "total_amount": float(v.total_amount),
                    "party_name": v.party_name,
                    "narration": v.narration
                }
                for v in vouchers
            ],
            "bank_statements": [
                {
                    "statement_id": bs.bank_txn_id,
                    "transaction_date": bs.txn_date.isoformat(),
                    "amount": float(bs.amount),
                    "description": bs.narration,
                    "reference_number": bs.cheque_ref
                }
                for bs in bank_statements
            ],
            "historical_patterns": [
                {
                    "match_score": float(rl.match_score),
                    "match_rules": rl.match_rules,
                    "voucher_type": rl.voucher_type,
                    "success": rl.human_verified
                }
                for rl in recent_reconciliations
            ],
            "batch_metadata": {
                "requested_batch_size": request.get("batch_size", 100),
                "actual_vouchers": len(vouchers),
                "actual_statements": len(bank_statements),
                "processing_mode": request.get("mode", "automatic")
            }
        }
        
        return perceptual_data
    
    async def _execute_reconciliation_with_cognition(
        self,
        reasoning_result: Dict[str, Any],
        company_id: str
    ) -> Dict[str, Any]:
        """Execute reconciliation using cognitive insights"""
        
        cognitive_strategy = reasoning_result.get("reconciliation_strategy", {})
        matching_rules = cognitive_strategy.get("matching_rules", [])
        confidence_threshold = cognitive_strategy.get("confidence_threshold", 0.8)
        
        detailed_results = []
        successful_matches = 0
        near_matches = 0
        unmatched_items = 0
        confidence_scores = []
        
        # Process each voucher with cognitive strategy
        vouchers_to_process = reasoning_result.get("vouchers", [])
        
        for voucher_data in vouchers_to_process:
            voucher_id = voucher_data.get("voucher_id")
            
            # Apply cognitive matching strategy
            match_result = await self._apply_cognitive_matching(
                voucher_data, reasoning_result, company_id
            )
            
            # Record result in database
            reconciliation_log = ReconciliationLog(
                company_id=company_id,
                voucher_id=voucher_id,
                bank_statement_id=match_result.get("bank_statement_id"),
                match_score=Decimal(str(match_result.get("confidence", 0.0))),
                match_rules=cognitive_strategy,
                ai_reasoning=match_result.get("reasoning", ""),
                confidence_score=Decimal(str(match_result.get("confidence", 0.0))),
                human_verified=False
            )
            
            self.db.add(reconciliation_log)
            
            # Update counters
            if match_result.get("match_type") == "exact":
                successful_matches += 1
            elif match_result.get("match_type") == "near":
                near_matches += 1
            else:
                unmatched_items += 1
            
            confidence_scores.append(match_result.get("confidence", 0.0))
            detailed_results.append(match_result)
        
        self.db.commit()
        
        # Calculate U(θ) score
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        u_theta_score = self._calculate_u_theta_score(
            successful_matches, near_matches, unmatched_items, average_confidence
        )
        
        execution_result = {
            "total_processed": len(vouchers_to_process),
            "successful_matches": successful_matches,
            "near_matches": near_matches,
            "unmatched_items": unmatched_items,
            "average_confidence": average_confidence,
            "u_theta_score": float(u_theta_score),
            "detailed_results": detailed_results,
            "cognitive_strategy_used": cognitive_strategy
        }
        
        return execution_result
    
    async def _apply_cognitive_matching(
        self,
        voucher_data: Dict[str, Any],
        reasoning_result: Dict[str, Any],
        company_id: str
    ) -> Dict[str, Any]:
        """Apply cognitive matching strategy to individual voucher"""
        
        # Get matching strategy from reasoning
        strategy = reasoning_result.get("reconciliation_strategy", {})
        matching_rules = strategy.get("matching_rules", [])
        
        # Get candidate bank statements
        candidates = self.db.query(BankStatement).filter(
            BankStatement.company_id == company_id,
            BankStatement.reconciliation_status == "Unmatched"
        ).all()
        
        best_match = None
        best_confidence = 0.0
        best_reasoning = ""
        
        voucher_amount = Decimal(str(voucher_data.get("total_amount", 0)))
        voucher_date = datetime.fromisoformat(voucher_data.get("voucher_date"))
        
        for candidate in candidates:
            confidence = 0.0
            reasoning_parts = []
            
            # Apply each matching rule
            for rule in matching_rules:
                rule_type = rule.get("rule_type")
                rule_weight = Decimal(str(rule.get("weight", 1.0)))
                
                if rule_type == "amount_exact":
                    if abs(candidate.amount - voucher_amount) < Decimal('0.01'):
                        confidence += float(rule_weight * Decimal('1.0'))
                        reasoning_parts.append("Exact amount match")
                
                elif rule_type == "amount_tolerance":
                    tolerance = Decimal(str(rule.get("tolerance", 0.02)))
                    amount_diff = abs(candidate.amount - voucher_amount)
                    if amount_diff <= voucher_amount * tolerance:
                        match_strength = 1.0 - float(amount_diff / (voucher_amount * tolerance))
                        confidence += float(rule_weight * Decimal(str(match_strength)))
                        reasoning_parts.append(f"Amount within {tolerance*100}% tolerance")
                
                elif rule_type == "date_proximity":
                    date_diff = abs((candidate.txn_date - voucher_date.date()).days)
                    max_days = rule.get("max_days", 3)
                    if date_diff <= max_days:
                        date_strength = 1.0 - (date_diff / max_days)
                        confidence += float(rule_weight * Decimal(str(date_strength)))
                        reasoning_parts.append(f"Date within {max_days} days")
                
                elif rule_type == "reference_match":
                    if (voucher_data.get("reference_number") and 
                        candidate.cheque_ref and
                        voucher_data.get("reference_number") in candidate.cheque_ref):
                        confidence += float(rule_weight * Decimal('1.0'))
                        reasoning_parts.append("Reference number match")
            
            # Normalize confidence by total possible weight
            total_weight = sum(Decimal(str(rule.get("weight", 1.0))) for rule in matching_rules)
            if total_weight > 0:
                confidence = confidence / float(total_weight)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = candidate
                best_reasoning = " | ".join(reasoning_parts)
        
        # Determine match type
        confidence_threshold = strategy.get("confidence_threshold", 0.8)
        near_match_threshold = strategy.get("near_match_threshold", 0.6)
        
        if best_confidence >= confidence_threshold:
            match_type = "exact"
            status = "Matched"
        elif best_confidence >= near_match_threshold:
            match_type = "near"
            status = "Near_Match"
        else:
            match_type = "unmatched"
            status = "Unmatched"
        
        return {
            "voucher_id": voucher_data.get("voucher_id"),
            "bank_statement_id": best_match.bank_txn_id if best_match else None,
            "confidence": best_confidence,
            "match_type": match_type,
            "status": status,
            "reasoning": best_reasoning,
            "amount_difference": float(abs(best_match.amount - voucher_amount)) if best_match else None,
            "date_difference_days": abs((best_match.txn_date - voucher_date.date()).days) if best_match else None
        }
    
    async def _learn_from_execution(
        self,
        execution_result: Dict[str, Any],
        company_id: str
    ):
        """Learn from execution results using adaptive memory"""
        
        # Record learning from successful reconciliation
        if execution_result.get("u_theta_score", 0.0) > 0.7:
            await self.adaptive_memory.learn_from_reconciliation_success(
                execution_result, company_id
            )
    
    async def _reflect_on_performance(
        self,
        execution_result: Dict[str, Any],
        company_id: str
    ) -> Dict[str, Any]:
        """Perform meta-cognitive reflection on performance"""
        
        performance_data = {
            "accuracy_rate": execution_result.get("u_theta_score", 0.0),
            "processing_time": 0.0,  # Would be calculated from actual timing
            "success_rate": execution_result.get("successful_matches", 0) / max(1, execution_result.get("total_processed", 1)),
            "confidence_score": execution_result.get("average_confidence", 0.0),
            "error_rate": execution_result.get("unmatched_items", 0) / max(1, execution_result.get("total_processed", 1))
        }
        
        # Trigger performance reflection
        reflection_result = self.meta_cognition.trigger_reflection(
            ReflectionType.PERFORMANCE_ANALYSIS,
            "batch_reconciliation_completed",
            performance_data,
            company_id
        )
        
        return reflection_result
    
    async def _generate_recommendations(
        self,
        execution_result: Dict[str, Any],
        company_id: str
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Performance-based recommendations
        u_theta_score = execution_result.get("u_theta_score", 0.0)
        if u_theta_score < 0.7:
            recommendations.append({
                "type": "performance_improvement",
                "priority": "high",
                "description": "Consider adjusting matching rules to improve accuracy",
                "suggested_action": "Review and optimize confidence thresholds"
            })
        
        # Volume-based recommendations
        unmatched_items = execution_result.get("unmatched_items", 0)
        total_processed = execution_result.get("total_processed", 1)
        unmatched_rate = unmatched_items / total_processed
        
        if unmatched_rate > 0.3:
            recommendations.append({
                "type": "matching_strategy",
                "priority": "medium",
                "description": f"High unmatched rate ({unmatched_rate:.1%})",
                "suggested_action": "Consider additional matching rules or manual review"
            })
        
        # Get adaptive memory recommendations
        context = execution_result.get("context", {})
        memory_recommendations = self.adaptive_memory.get_recommendations_for_context(
            context, company_id
        )
        
        for rec in memory_recommendations:
            recommendations.append({
                "type": "learned_pattern",
                "priority": "low",
                "description": rec["recommendation"],
                "confidence": rec["confidence"],
                "suggested_action": f"Apply {rec['function']} pattern"
            })
        
        return recommendations
    
    async def _handle_processing_error(self, error_context: Dict[str, Any]):
        """Handle processing errors with reflection"""
        
        company_id = error_context.get("company_id")
        if company_id:
            self.meta_cognition.trigger_reflection(
                ReflectionType.ERROR_ANALYSIS,
                "processing_error_occurred",
                error_context,
                company_id
            )
    
    def _calculate_u_theta_score(
        self,
        successful_matches: int,
        near_matches: int,
        unmatched_items: int,
        average_confidence: float
    ) -> Decimal:
        """Calculate U(θ) utility score"""
        
        total_items = successful_matches + near_matches + unmatched_items
        if total_items == 0:
            return Decimal('0.0')
        
        # Weighted scoring
        success_weight = Decimal('1.0')
        near_weight = Decimal('0.7')
        unmatched_weight = Decimal('0.0')
        
        weighted_score = (
            (successful_matches * success_weight) +
            (near_matches * near_weight) +
            (unmatched_items * unmatched_weight)
        ) / total_items
        
        # Apply confidence adjustment
        confidence_factor = Decimal(str(average_confidence))
        u_theta = weighted_score * confidence_factor
        
        return min(Decimal('1.0'), u_theta)
    
    async def get_system_status(self, company_id: str) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Get learning statistics
        learning_stats = self.adaptive_memory.get_learning_statistics(company_id)
        
        # Get reflection summary
        reflection_summary = self.meta_cognition.get_reflection_summary(company_id)
        
        # Get recent performance metrics
        recent_reconciliations = self.db.query(ReconciliationLog).filter(
            ReconciliationLog.company_id == company_id
        ).order_by(ReconciliationLog.created_at.desc()).limit(100).all()
        
        if recent_reconciliations:
            avg_confidence = sum(float(r.confidence_score) for r in recent_reconciliations) / len(recent_reconciliations)
            success_rate = sum(1 for r in recent_reconciliations if r.human_verified) / len(recent_reconciliations)
        else:
            avg_confidence = 0.0
            success_rate = 0.0
        
        return {
            "cognitive_status": {
                "cognitive_engine_active": True,
                "adaptive_learning_active": True,
                "meta_cognition_active": True,
                "average_processing_confidence": avg_confidence,
                "success_rate": success_rate
            },
            "learning_progress": learning_stats,
            "reflection_insights": reflection_summary,
            "system_health": {
                "database_connectivity": True,
                "ai_services_available": True,
                "last_updated": datetime.now().isoformat()
            }
        }


# Factory function for dependency injection
def get_ram_service(db: Session = Depends(get_db)) -> RAMOrchestrationService:
    """Factory function to create RAM service instance"""
    return RAMOrchestrationService(db)