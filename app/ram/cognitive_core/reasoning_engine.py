# app/ram/cognitive_core/reasoning_engine.py
"""
RAM Cognitive Framework - Layer 1 Reasoning Engine
Implements the core cognitive architecture for CA audit automation
"""

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.core.init_llm import make_llm
from app.core.logger import log_request
from app.cdm.models.reconciliation import ReconciliationLog, AIFeedback
from app.cdm.models.transaction import VoucherHeader
from app.cdm.models.external import BankStatement


class CognitiveStage(Enum):
    """Cognitive processing stages"""
    PERCEPTION = "perception"
    REASONING = "reasoning"  
    META_REASONING = "meta_reasoning"
    REFLECTION = "reflection"


class ReasoningPrimitive(Enum):
    """Core reasoning primitives for CA operations"""
    PATTERN_MATCH = "pattern_match"
    VARIANCE_ANALYSIS = "variance_analysis"
    RULE_APPLICATION = "rule_application"
    EVIDENCE_SYNTHESIS = "evidence_synthesis"
    ANOMALY_DETECTION = "anomaly_detection"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class ReasoningTrace:
    """Trace of reasoning process"""
    trace_id: str
    timestamp: datetime
    stage: CognitiveStage
    primitive: ReasoningPrimitive
    input_data: Dict[str, Any]
    output_result: Any
    confidence_score: Decimal
    reasoning_steps: List[str]
    meta_observations: Dict[str, Any]


@dataclass
class CognitiveContext:
    """Context for cognitive processing"""
    company_id: str
    domain: str  # reconciliation, audit, compliance
    task_type: str
    financial_year: str
    materiality_threshold: Decimal
    user_preferences: Dict[str, Any]


class PerceptualInterface:
    """RAM Layer 1: Perception (Ψ) - Data ingestion and pattern recognition"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = make_llm(temperature=0.2)
    
    def perceive_reconciliation_patterns(
        self, 
        vouchers: List[VoucherHeader], 
        bank_statements: List[BankStatement],
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Extract patterns from reconciliation data"""
        
        # Analyze amount patterns
        amount_patterns = self._analyze_amount_patterns(vouchers, bank_statements)
        
        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(vouchers, bank_statements)
        
        # Analyze textual patterns in narrations
        textual_patterns = self._analyze_textual_patterns(vouchers, bank_statements)
        
        return {
            "amount_patterns": amount_patterns,
            "temporal_patterns": temporal_patterns,
            "textual_patterns": textual_patterns,
            "context": context.__dict__,
            "perception_quality": self._assess_perception_quality()
        }
    
    def _analyze_amount_patterns(self, vouchers: List[VoucherHeader], bank_statements: List[BankStatement]) -> Dict:
        """Analyze amount-based patterns"""
        voucher_amounts = [float(v.total_amount) for v in vouchers]
        bank_amounts = [float(bs.amount) for bs in bank_statements]
        
        return {
            "exact_matches": self._find_exact_amount_matches(voucher_amounts, bank_amounts),
            "variance_clusters": self._cluster_amount_variances(voucher_amounts, bank_amounts),
            "amount_distribution": self._analyze_amount_distribution(voucher_amounts + bank_amounts)
        }
    
    def _analyze_temporal_patterns(self, vouchers: List[VoucherHeader], bank_statements: List[BankStatement]) -> Dict:
        """Analyze time-based patterns"""
        return {
            "date_variance_patterns": self._find_date_patterns(vouchers, bank_statements),
            "seasonal_trends": self._identify_seasonal_patterns(vouchers),
            "processing_delays": self._calculate_processing_delays(vouchers, bank_statements)
        }
    
    def _analyze_textual_patterns(self, vouchers: List[VoucherHeader], bank_statements: List[BankStatement]) -> Dict:
        """Analyze textual patterns in narrations"""
        voucher_texts = [v.narration or "" for v in vouchers]
        bank_texts = [bs.narration or "" for bs in bank_statements]
        
        return {
            "common_phrases": self._extract_common_phrases(voucher_texts + bank_texts),
            "entity_references": self._extract_entity_references(voucher_texts + bank_texts),
            "reference_patterns": self._extract_reference_patterns(bank_texts)
        }
    
    def _assess_perception_quality(self) -> Decimal:
        """Assess quality of perception"""
        # TODO: Implement perception quality metrics
        return Decimal('0.85')
    
    def _find_exact_amount_matches(self, voucher_amounts: List[float], bank_amounts: List[float]) -> List[Tuple]:
        """Find exact amount matches"""
        matches = []
        for i, v_amt in enumerate(voucher_amounts):
            for j, b_amt in enumerate(bank_amounts):
                if abs(v_amt - b_amt) < 0.01:  # Exact match within 1 paisa
                    matches.append((i, j, v_amt, b_amt))
        return matches
    
    def _cluster_amount_variances(self, voucher_amounts: List[float], bank_amounts: List[float]) -> Dict:
        """Cluster amounts by variance patterns"""
        # TODO: Implement clustering algorithm
        return {"variance_clusters": [], "cluster_count": 0}
    
    def _analyze_amount_distribution(self, amounts: List[float]) -> Dict:
        """Analyze distribution of amounts"""
        if not amounts:
            return {"mean": 0, "median": 0, "std_dev": 0}
        
        amounts.sort()
        n = len(amounts)
        mean = sum(amounts) / n
        median = amounts[n//2] if n % 2 == 1 else (amounts[n//2-1] + amounts[n//2]) / 2
        
        variance = sum((x - mean) ** 2 for x in amounts) / n
        std_dev = variance ** 0.5
        
        return {
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "min": min(amounts),
            "max": max(amounts),
            "count": n
        }
    
    def _find_date_patterns(self, vouchers: List[VoucherHeader], bank_statements: List[BankStatement]) -> Dict:
        """Find date-based patterns"""
        # TODO: Implement date pattern analysis
        return {"common_delays": [], "date_clusters": []}
    
    def _identify_seasonal_patterns(self, vouchers: List[VoucherHeader]) -> Dict:
        """Identify seasonal patterns in vouchers"""
        # TODO: Implement seasonal analysis
        return {"seasonal_trends": [], "peak_periods": []}
    
    def _calculate_processing_delays(self, vouchers: List[VoucherHeader], bank_statements: List[BankStatement]) -> Dict:
        """Calculate typical processing delays"""
        # TODO: Implement delay calculation
        return {"avg_delay_days": 0, "delay_distribution": []}
    
    def _extract_common_phrases(self, texts: List[str]) -> List[str]:
        """Extract common phrases from texts"""
        # TODO: Implement phrase extraction
        return []
    
    def _extract_entity_references(self, texts: List[str]) -> List[str]:
        """Extract entity references from texts"""
        # TODO: Implement entity extraction
        return []
    
    def _extract_reference_patterns(self, texts: List[str]) -> List[str]:
        """Extract reference number patterns"""
        # TODO: Implement reference pattern extraction
        return []


class ReasoningLayer:
    """RAM Layer 1: Reasoning (R) - Core reasoning operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = make_llm(temperature=0.1)
    
    def compose_reconciliation_strategy(
        self, 
        perception_data: Dict[str, Any],
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Compose reconciliation strategy based on perceived patterns"""
        
        # Apply reasoning primitives
        pattern_matches = self._apply_pattern_matching(perception_data)
        variance_analysis = self._apply_variance_analysis(perception_data)  
        rule_applications = self._apply_compliance_rules(perception_data, context)
        
        # Synthesize evidence
        evidence_synthesis = self._synthesize_evidence([
            pattern_matches,
            variance_analysis, 
            rule_applications
        ])
        
        # Generate reasoning strategy
        strategy = {
            "approach": self._determine_reconciliation_approach(evidence_synthesis),
            "confidence_threshold": self._calculate_confidence_threshold(context),
            "matching_rules": self._generate_matching_rules(evidence_synthesis),
            "exception_handling": self._define_exception_rules(evidence_synthesis),
            "quality_metrics": self._define_quality_metrics(context)
        }
        
        return strategy
    
    def _apply_pattern_matching(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply pattern matching primitive"""
        amount_patterns = perception_data.get("amount_patterns", {})
        
        # Analyze exact matches
        exact_matches = amount_patterns.get("exact_matches", [])
        
        # Analyze near matches (within tolerance)
        variance_clusters = amount_patterns.get("variance_clusters", {})
        
        return {
            "primitive": ReasoningPrimitive.PATTERN_MATCH,
            "exact_match_count": len(exact_matches),
            "near_match_clusters": len(variance_clusters.get("variance_clusters", [])),
            "pattern_confidence": Decimal('0.90') if exact_matches else Decimal('0.60')
        }
    
    def _apply_variance_analysis(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply variance analysis primitive"""
        amount_patterns = perception_data.get("amount_patterns", {})
        distribution = amount_patterns.get("amount_distribution", {})
        
        # Calculate variance metrics
        std_dev = distribution.get("std_dev", 0)
        mean = distribution.get("mean", 0)
        
        coefficient_of_variation = (std_dev / mean) if mean > 0 else 0
        
        return {
            "primitive": ReasoningPrimitive.VARIANCE_ANALYSIS,
            "coefficient_of_variation": coefficient_of_variation,
            "variance_level": "high" if coefficient_of_variation > 0.5 else "low",
            "analysis_confidence": Decimal('0.85')
        }
    
    def _apply_compliance_rules(self, perception_data: Dict[str, Any], context: CognitiveContext) -> Dict[str, Any]:
        """Apply compliance rules primitive"""
        
        # Check materiality thresholds
        materiality_check = self._check_materiality_compliance(perception_data, context)
        
        # Check temporal compliance (banking days, etc.)
        temporal_check = self._check_temporal_compliance(perception_data)
        
        # Check regulatory compliance
        regulatory_check = self._check_regulatory_compliance(perception_data, context)
        
        return {
            "primitive": ReasoningPrimitive.COMPLIANCE_CHECK,
            "materiality_compliance": materiality_check,
            "temporal_compliance": temporal_check,
            "regulatory_compliance": regulatory_check,
            "overall_compliance_score": Decimal('0.88')
        }
    
    def _synthesize_evidence(self, reasoning_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize evidence from multiple reasoning primitives"""
        
        # Combine confidence scores
        confidence_scores = []
        for result in reasoning_results:
            if "pattern_confidence" in result:
                confidence_scores.append(result["pattern_confidence"])
            if "analysis_confidence" in result:
                confidence_scores.append(result["analysis_confidence"])
            if "overall_compliance_score" in result:
                confidence_scores.append(result["overall_compliance_score"])
        
        # Calculate weighted average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else Decimal('0.5')
        
        return {
            "primitive": ReasoningPrimitive.EVIDENCE_SYNTHESIS,
            "evidence_count": len(reasoning_results),
            "synthesized_confidence": avg_confidence,
            "evidence_quality": "high" if avg_confidence > Decimal('0.8') else "medium"
        }
    
    def _determine_reconciliation_approach(self, evidence: Dict[str, Any]) -> str:
        """Determine best reconciliation approach"""
        confidence = evidence.get("synthesized_confidence", Decimal('0.5'))
        
        if confidence > Decimal('0.9'):
            return "automated_high_confidence"
        elif confidence > Decimal('0.7'):
            return "automated_with_review"
        else:
            return "manual_review_required"
    
    def _calculate_confidence_threshold(self, context: CognitiveContext) -> Decimal:
        """Calculate appropriate confidence threshold"""
        base_threshold = Decimal('0.8')
        
        # Adjust based on materiality
        if context.materiality_threshold < Decimal('1000'):
            return base_threshold + Decimal('0.1')  # Higher threshold for low materiality
        
        return base_threshold
    
    def _generate_matching_rules(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate matching rules based on evidence"""
        rules = []
        
        # Exact amount match rule
        rules.append({
            "rule_type": "exact_amount_match",
            "weight": Decimal('1.0'),
            "tolerance": Decimal('0.01')
        })
        
        # Near amount match rule
        rules.append({
            "rule_type": "near_amount_match", 
            "weight": Decimal('0.8'),
            "tolerance": Decimal('10.00')  # ₹10 tolerance
        })
        
        # Date proximity rule
        rules.append({
            "rule_type": "date_proximity",
            "weight": Decimal('0.6'),
            "max_days_difference": 7
        })
        
        return rules
    
    def _define_exception_rules(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define exception handling rules"""
        return [
            {
                "exception_type": "amount_variance_high",
                "threshold": Decimal('1000.00'),
                "action": "manual_review"
            },
            {
                "exception_type": "date_variance_high", 
                "threshold": 30,  # days
                "action": "escalate_to_supervisor"
            }
        ]
    
    def _define_quality_metrics(self, context: CognitiveContext) -> Dict[str, Any]:
        """Define quality metrics for reconciliation"""
        return {
            "min_confidence_score": Decimal('0.7'),
            "max_processing_time_seconds": 300,
            "required_evidence_count": 2,
            "materiality_threshold": context.materiality_threshold
        }
    
    def _check_materiality_compliance(self, perception_data: Dict[str, Any], context: CognitiveContext) -> Dict[str, Any]:
        """Check materiality compliance"""
        # TODO: Implement materiality checks
        return {"status": "compliant", "variance_amount": Decimal('0.00')}
    
    def _check_temporal_compliance(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check temporal compliance"""
        # TODO: Implement temporal compliance checks
        return {"status": "compliant", "max_delay_days": 0}
    
    def _check_regulatory_compliance(self, perception_data: Dict[str, Any], context: CognitiveContext) -> Dict[str, Any]:
        """Check regulatory compliance"""
        # TODO: Implement regulatory compliance checks
        return {"status": "compliant", "violations": []}


class MetaReasoningLayer:
    """RAM Layer 1: Meta-Reasoning (Θ) - Quality control and evaluation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = make_llm(temperature=0.0)  # Deterministic for evaluation
    
    def evaluate_reasoning_quality(
        self, 
        reasoning_strategy: Dict[str, Any],
        perception_data: Dict[str, Any],
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Evaluate quality of reasoning strategy"""
        
        # Calculate U(θ) score components
        coherence = self._evaluate_coherence(reasoning_strategy, perception_data)
        problem_solving = self._evaluate_problem_solving(reasoning_strategy, context)
        novelty = self._evaluate_novelty(reasoning_strategy)
        eye_catch = self._evaluate_eye_catch(reasoning_strategy)
        
        # Calculate composite U(θ) score
        u_theta = self._calculate_u_theta(coherence, problem_solving, novelty, eye_catch)
        
        # Generate meta-observations
        meta_observations = self._generate_meta_observations(
            u_theta, coherence, problem_solving, novelty, eye_catch
        )
        
        return {
            "u_theta_score": u_theta,
            "component_scores": {
                "coherence": coherence,
                "problem_solving": problem_solving,
                "novelty": novelty,
                "eye_catch": eye_catch
            },
            "meta_observations": meta_observations,
            "quality_assessment": self._assess_overall_quality(u_theta),
            "improvement_suggestions": self._generate_improvement_suggestions(reasoning_strategy, u_theta)
        }
    
    def _evaluate_coherence(self, strategy: Dict[str, Any], perception: Dict[str, Any]) -> Decimal:
        """Evaluate coherence between strategy and perception"""
        # Check if strategy aligns with perceived patterns
        approach = strategy.get("approach", "")
        perception_quality = perception.get("perception_quality", Decimal('0.5'))
        
        # High perception quality should lead to high-confidence approach
        if perception_quality > Decimal('0.8') and "high_confidence" in approach:
            return Decimal('0.9')
        elif perception_quality > Decimal('0.6') and "review" in approach:
            return Decimal('0.8')
        else:
            return Decimal('0.6')
    
    def _evaluate_problem_solving(self, strategy: Dict[str, Any], context: CognitiveContext) -> Decimal:
        """Evaluate problem-solving effectiveness"""
        # Check if strategy addresses the specific reconciliation challenges
        matching_rules = strategy.get("matching_rules", [])
        exception_rules = strategy.get("exception_handling", [])
        
        # More comprehensive rules indicate better problem-solving
        rule_score = min(len(matching_rules) * Decimal('0.2'), Decimal('0.6'))
        exception_score = min(len(exception_rules) * Decimal('0.2'), Decimal('0.4'))
        
        return rule_score + exception_score
    
    def _evaluate_novelty(self, strategy: Dict[str, Any]) -> Decimal:
        """Evaluate novelty of approach"""
        # Check for innovative or non-standard approaches
        approach = strategy.get("approach", "")
        
        # Standard approaches get lower novelty scores
        if approach in ["automated_high_confidence", "manual_review_required"]:
            return Decimal('0.3')
        else:
            return Decimal('0.7')  # Assume some novelty for mixed approaches
    
    def _evaluate_eye_catch(self, strategy: Dict[str, Any]) -> Decimal:
        """Evaluate eye-catching or notable aspects"""
        # Check for interesting or attention-worthy features
        quality_metrics = strategy.get("quality_metrics", {})
        
        # Stringent quality metrics are eye-catching
        min_confidence = quality_metrics.get("min_confidence_score", Decimal('0.5'))
        
        if min_confidence > Decimal('0.8'):
            return Decimal('0.8')
        elif min_confidence > Decimal('0.6'):
            return Decimal('0.6')
        else:
            return Decimal('0.4')
    
    def _calculate_u_theta(self, coherence: Decimal, problem_solving: Decimal, 
                          novelty: Decimal, eye_catch: Decimal) -> Decimal:
        """Calculate composite U(θ) score"""
        # Weighted average with emphasis on coherence and problem-solving
        weights = {
            "coherence": Decimal('0.4'),
            "problem_solving": Decimal('0.3'),
            "novelty": Decimal('0.15'),
            "eye_catch": Decimal('0.15')
        }
        
        u_theta = (
            coherence * weights["coherence"] +
            problem_solving * weights["problem_solving"] +
            novelty * weights["novelty"] +
            eye_catch * weights["eye_catch"]
        )
        
        return round(u_theta, 4)
    
    def _generate_meta_observations(self, u_theta: Decimal, coherence: Decimal, 
                                   problem_solving: Decimal, novelty: Decimal, 
                                   eye_catch: Decimal) -> List[str]:
        """Generate meta-observations about reasoning quality"""
        observations = []
        
        if u_theta > Decimal('0.8'):
            observations.append("High-quality reasoning strategy with strong coherence")
        elif u_theta < Decimal('0.6'):
            observations.append("Strategy requires improvement in multiple dimensions")
        
        if coherence < Decimal('0.6'):
            observations.append("Strategy-perception alignment needs improvement")
        
        if problem_solving < Decimal('0.6'):
            observations.append("Problem-solving approach could be more comprehensive")
        
        if novelty < Decimal('0.4'):
            observations.append("Consider more innovative approaches")
        
        return observations
    
    def _assess_overall_quality(self, u_theta: Decimal) -> str:
        """Assess overall quality level"""
        if u_theta >= Decimal('0.9'):
            return "excellent"
        elif u_theta >= Decimal('0.8'):
            return "good"
        elif u_theta >= Decimal('0.6'):
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _generate_improvement_suggestions(self, strategy: Dict[str, Any], u_theta: Decimal) -> List[str]:
        """Generate suggestions for improving reasoning strategy"""
        suggestions = []
        
        if u_theta < Decimal('0.8'):
            suggestions.append("Consider adding more sophisticated matching rules")
            suggestions.append("Implement adaptive confidence thresholds")
        
        if u_theta < Decimal('0.6'):
            suggestions.append("Review evidence synthesis methodology")
            suggestions.append("Add more comprehensive exception handling")
        
        return suggestions


class RAMCognitiveEngine:
    """Main cognitive engine integrating all RAM layers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.perception = PerceptualInterface(db)
        self.reasoning = ReasoningLayer(db)
        self.meta_reasoning = MetaReasoningLayer(db)
        self.traces: List[ReasoningTrace] = []
    
    def run_cognitive_cycle(
        self, 
        vouchers: List[VoucherHeader],
        bank_statements: List[BankStatement], 
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Run complete cognitive cycle for reconciliation"""
        
        cycle_start = datetime.now()
        trace_id = f"ram_cycle_{int(cycle_start.timestamp())}"
        
        try:
            # Stage 1: Perception (Ψ)
            perception_data = self.perception.perceive_reconciliation_patterns(
                vouchers, bank_statements, context
            )
            self._log_trace(trace_id, CognitiveStage.PERCEPTION, perception_data)
            
            # Stage 2: Reasoning (R)
            reasoning_strategy = self.reasoning.compose_reconciliation_strategy(
                perception_data, context
            )
            self._log_trace(trace_id, CognitiveStage.REASONING, reasoning_strategy)
            
            # Stage 3: Meta-Reasoning (Θ)
            quality_evaluation = self.meta_reasoning.evaluate_reasoning_quality(
                reasoning_strategy, perception_data, context
            )
            self._log_trace(trace_id, CognitiveStage.META_REASONING, quality_evaluation)
            
            # Compile results
            cycle_result = {
                "cycle_id": trace_id,
                "timestamp": cycle_start.isoformat(),
                "context": context.__dict__,
                "perception_data": perception_data,
                "reasoning_strategy": reasoning_strategy,
                "quality_evaluation": quality_evaluation,
                "processing_time_ms": int((datetime.now() - cycle_start).total_seconds() * 1000),
                "u_theta_score": quality_evaluation["u_theta_score"]
            }
            
            # Store cognitive cycle results
            self._store_cognitive_cycle(cycle_result)
            
            return cycle_result
            
        except Exception as e:
            # Log error and return failure result
            error_result = {
                "cycle_id": trace_id,
                "timestamp": cycle_start.isoformat(),
                "error": str(e),
                "status": "failed"
            }
            
            log_request(
                method="RAM_COGNITIVE_CYCLE",
                path="/cognitive/cycle",
                status_code=500,
                duration_ms=int((datetime.now() - cycle_start).total_seconds() * 1000),
                extra={"error": str(e), "context": context.__dict__}
            )
            
            return error_result
    
    def _log_trace(self, trace_id: str, stage: CognitiveStage, result_data: Dict[str, Any]):
        """Log reasoning trace"""
        trace = ReasoningTrace(
            trace_id=trace_id,
            timestamp=datetime.now(),
            stage=stage,
            primitive=ReasoningPrimitive.EVIDENCE_SYNTHESIS,  # Default primitive
            input_data={},
            output_result=result_data,
            confidence_score=result_data.get("u_theta_score", Decimal('0.0')),
            reasoning_steps=[],
            meta_observations=result_data.get("meta_observations", {})
        )
        
        self.traces.append(trace)
    
    def _store_cognitive_cycle(self, cycle_result: Dict[str, Any]):
        """Store cognitive cycle results in database"""
        try:
            # Create reconciliation log entry
            recon_log = ReconciliationLog(
                company_id=cycle_result["context"]["company_id"],
                source_table="cognitive_engine",
                target_table="ram_cycles",
                source_record_id=cycle_result["cycle_id"],
                match_score=cycle_result["u_theta_score"],
                match_rule="RAM_COGNITIVE_CYCLE",
                rule_details=json.dumps({
                    "perception_quality": cycle_result["perception_data"].get("perception_quality"),
                    "reasoning_approach": cycle_result["reasoning_strategy"].get("approach"),
                    "quality_assessment": cycle_result["quality_evaluation"].get("quality_assessment")
                }),
                status="Completed",
                ai_reasoning=json.dumps(cycle_result["quality_evaluation"].get("meta_observations", []))
            )
            
            self.db.add(recon_log)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            # Log error but don't fail the cycle
            log_request(
                method="STORE_COGNITIVE_CYCLE",
                path="/cognitive/store",
                status_code=500,
                duration_ms=0,
                extra={"error": str(e)}
            )
    
    def get_reasoning_history(self, company_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get reasoning history for analysis"""
        logs = self.db.query(ReconciliationLog).filter(
            ReconciliationLog.company_id == company_id,
            ReconciliationLog.match_rule == "RAM_COGNITIVE_CYCLE"
        ).order_by(ReconciliationLog.created_at.desc()).limit(limit).all()
        
        return [
            {
                "log_id": log.log_id,
                "timestamp": log.created_at.isoformat(),
                "u_theta_score": float(log.match_score),
                "rule_details": json.loads(log.rule_details or "{}"),
                "ai_reasoning": json.loads(log.ai_reasoning or "[]")
            }
            for log in logs
        ]