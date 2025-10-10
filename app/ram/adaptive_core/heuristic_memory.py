# app/ram/adaptive_core/heuristic_memory.py
"""
RAM Layer 2: Adaptive Learning & Heuristic Memory
Implements pattern learning and weight evolution for CA operations
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime
import json
import hashlib
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.core.database import Base
from sqlalchemy import Column, String, Numeric, DateTime, JSON, Text, Index
from sqlalchemy.sql import func
import uuid


class HeuristicMemory(Base):
    """Database model for storing successful heuristics"""
    __tablename__ = "heuristic_memory"
    
    heuristic_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, nullable=False)
    idea = Column(Text, nullable=False)  # Description of successful pattern
    function_name = Column(String, nullable=False)  # Implementation function
    success_score = Column(Numeric(5,4), nullable=False)  # U(θ) score
    context_meta = Column(JSON)  # Context: client, FY, domain
    pattern_hash = Column(String, nullable=False)  # Deterministic hash
    usage_count = Column(Numeric(10,0), default=0)  # How often used
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_heuristic_company_score', 'company_id', 'success_score'),
        Index('idx_heuristic_hash', 'pattern_hash'),
        Index('idx_heuristic_function', 'function_name'),
    )


@dataclass 
class AdaptiveWeight:
    """Represents adaptive weight for reasoning primitives"""
    primitive_name: str
    weight: Decimal
    confidence: Decimal
    last_updated: datetime
    update_count: int


class HeuristicEvolver:
    """Evolves heuristic weights based on success feedback"""
    
    def __init__(self, db: Session):
        self.db = db
        self.learning_rate = Decimal('0.1')
        self.success_threshold = Decimal('0.8')
        self.weights: Dict[str, AdaptiveWeight] = {}
    
    def record_successful_pattern(
        self, 
        idea: str,
        function_name: str,
        success_score: Decimal,
        context: Dict[str, Any],
        company_id: str
    ) -> str:
        """Record successful reasoning pattern"""
        
        # Generate deterministic hash
        pattern_hash = self._generate_pattern_hash(idea, function_name, success_score)
        
        # Check if pattern already exists
        existing = self.db.query(HeuristicMemory).filter(
            HeuristicMemory.pattern_hash == pattern_hash,
            HeuristicMemory.company_id == company_id
        ).first()
        
        if existing:
            # Update usage statistics
            existing.usage_count += 1
            existing.last_used = datetime.now()
            # Update success score (running average)
            existing.success_score = (existing.success_score + success_score) / 2
        else:
            # Create new heuristic record
            heuristic = HeuristicMemory(
                company_id=company_id,
                idea=idea,
                function_name=function_name,
                success_score=success_score,
                context_meta=context,
                pattern_hash=pattern_hash,
                usage_count=1,
                last_used=datetime.now()
            )
            self.db.add(heuristic)
        
        self.db.commit()
        return pattern_hash
    
    def fetch_similar_patterns(
        self, 
        context: Dict[str, Any],
        company_id: str,
        min_score: Decimal = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch similar successful patterns"""
        
        min_score = min_score or self.success_threshold
        
        query = self.db.query(HeuristicMemory).filter(
            HeuristicMemory.company_id == company_id,
            HeuristicMemory.success_score >= min_score
        ).order_by(
            HeuristicMemory.success_score.desc(),
            HeuristicMemory.usage_count.desc()
        ).limit(limit)
        
        patterns = []
        for heuristic in query.all():
            patterns.append({
                "heuristic_id": heuristic.heuristic_id,
                "idea": heuristic.idea,
                "function_name": heuristic.function_name,
                "success_score": float(heuristic.success_score),
                "context_meta": heuristic.context_meta,
                "usage_count": int(heuristic.usage_count),
                "last_used": heuristic.last_used.isoformat() if heuristic.last_used else None,
                "relevance_score": self._calculate_relevance(heuristic.context_meta, context)
            })
        
        # Sort by relevance score
        patterns.sort(key=lambda x: x["relevance_score"], reverse=True)
        return patterns
    
    def evolve_weights(
        self, 
        primitive_results: Dict[str, Dict[str, Any]],
        overall_success_score: Decimal
    ) -> Dict[str, AdaptiveWeight]:
        """Evolve primitive weights based on results"""
        
        updated_weights = {}
        
        for primitive_name, result in primitive_results.items():
            primitive_score = result.get("confidence", Decimal('0.5'))
            
            # Get current weight or initialize
            current_weight = self.weights.get(primitive_name, AdaptiveWeight(
                primitive_name=primitive_name,
                weight=Decimal('1.0'),
                confidence=Decimal('0.5'),
                last_updated=datetime.now(),
                update_count=0
            ))
            
            # Calculate weight adjustment based on success
            if overall_success_score > self.success_threshold:
                # Positive reinforcement
                weight_delta = self.learning_rate * (primitive_score - current_weight.weight)
            else:
                # Negative reinforcement
                weight_delta = -self.learning_rate * (current_weight.weight - primitive_score)
            
            # Update weight with bounds
            new_weight = max(Decimal('0.1'), min(Decimal('2.0'), 
                           current_weight.weight + weight_delta))
            
            updated_weight = AdaptiveWeight(
                primitive_name=primitive_name,
                weight=new_weight,
                confidence=primitive_score,
                last_updated=datetime.now(),
                update_count=current_weight.update_count + 1
            )
            
            updated_weights[primitive_name] = updated_weight
        
        self.weights.update(updated_weights)
        return updated_weights
    
    def get_primitive_weight(self, primitive_name: str) -> Decimal:
        """Get current weight for a primitive"""
        weight = self.weights.get(primitive_name)
        return weight.weight if weight else Decimal('1.0')
    
    def _generate_pattern_hash(self, idea: str, function_name: str, success_score: Decimal) -> str:
        """Generate deterministic hash for pattern"""
        hash_input = f"{idea}|{function_name}|{success_score}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _calculate_relevance(self, stored_context: Dict[str, Any], current_context: Dict[str, Any]) -> float:
        """Calculate relevance score between contexts"""
        if not stored_context or not current_context:
            return 0.0
        
        relevance_score = 0.0
        max_score = 0.0
        
        # Compare domain
        if stored_context.get("domain") == current_context.get("domain"):
            relevance_score += 0.4
        max_score += 0.4
        
        # Compare financial year (closer years are more relevant)
        stored_fy = stored_context.get("financial_year", "")
        current_fy = current_context.get("financial_year", "")
        if stored_fy and current_fy:
            try:
                fy_diff = abs(int(stored_fy[:4]) - int(current_fy[:4]))
                fy_relevance = max(0, 1 - (fy_diff * 0.2))  # Decay by 20% per year
                relevance_score += fy_relevance * 0.3
            except:
                pass
        max_score += 0.3
        
        # Compare task type
        if stored_context.get("task_type") == current_context.get("task_type"):
            relevance_score += 0.3
        max_score += 0.3
        
        return relevance_score / max_score if max_score > 0 else 0.0


class AdaptiveMemoryService:
    """Service for managing adaptive memory across the system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.evolver = HeuristicEvolver(db)
    
    def learn_from_reconciliation_success(
        self,
        reconciliation_result: Dict[str, Any],
        company_id: str
    ):
        """Learn from successful reconciliation"""
        
        success_score = reconciliation_result.get("u_theta_score", Decimal('0.0'))
        
        if success_score >= self.evolver.success_threshold:
            # Extract successful patterns
            reasoning_strategy = reconciliation_result.get("reasoning_strategy", {})
            
            # Record successful approach
            approach = reasoning_strategy.get("approach", "unknown")
            self.evolver.record_successful_pattern(
                idea=f"Reconciliation approach: {approach}",
                function_name="compose_reconciliation_strategy",
                success_score=success_score,
                context=reconciliation_result.get("context", {}),
                company_id=company_id
            )
            
            # Record successful matching rules
            matching_rules = reasoning_strategy.get("matching_rules", [])
            for rule in matching_rules:
                rule_type = rule.get("rule_type", "unknown")
                self.evolver.record_successful_pattern(
                    idea=f"Matching rule: {rule_type} with weight {rule.get('weight')}",
                    function_name="generate_matching_rules",
                    success_score=success_score,
                    context=reconciliation_result.get("context", {}),
                    company_id=company_id
                )
    
    def get_recommendations_for_context(
        self,
        context: Dict[str, Any],
        company_id: str
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on learned patterns"""
        
        similar_patterns = self.evolver.fetch_similar_patterns(
            context=context,
            company_id=company_id,
            min_score=Decimal('0.7'),
            limit=5
        )
        
        recommendations = []
        for pattern in similar_patterns:
            recommendations.append({
                "recommendation": pattern["idea"],
                "confidence": pattern["success_score"],
                "relevance": pattern["relevance_score"],
                "usage_frequency": pattern["usage_count"],
                "function": pattern["function_name"]
            })
        
        return recommendations
    
    def get_adaptive_weights(self) -> Dict[str, float]:
        """Get current adaptive weights"""
        return {
            name: float(weight.weight) 
            for name, weight in self.evolver.weights.items()
        }
    
    def get_learning_statistics(self, company_id: str) -> Dict[str, Any]:
        """Get learning statistics"""
        
        total_patterns = self.db.query(HeuristicMemory).filter(
            HeuristicMemory.company_id == company_id
        ).count()
        
        high_success_patterns = self.db.query(HeuristicMemory).filter(
            HeuristicMemory.company_id == company_id,
            HeuristicMemory.success_score >= Decimal('0.8')
        ).count()
        
        avg_success_score = self.db.query(func.avg(HeuristicMemory.success_score)).filter(
            HeuristicMemory.company_id == company_id
        ).scalar() or 0
        
        most_used_pattern = self.db.query(HeuristicMemory).filter(
            HeuristicMemory.company_id == company_id
        ).order_by(HeuristicMemory.usage_count.desc()).first()
        
        return {
            "total_patterns_learned": total_patterns,
            "high_success_patterns": high_success_patterns,
            "average_success_score": float(avg_success_score),
            "learning_rate": float(self.evolver.learning_rate),
            "success_threshold": float(self.evolver.success_threshold),
            "most_used_pattern": {
                "idea": most_used_pattern.idea if most_used_pattern else None,
                "usage_count": int(most_used_pattern.usage_count) if most_used_pattern else 0,
                "success_score": float(most_used_pattern.success_score) if most_used_pattern else 0
            },
            "adaptive_weights": self.get_adaptive_weights()
        }