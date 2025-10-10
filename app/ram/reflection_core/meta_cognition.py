# app/ram/reflection_core/meta_cognition.py
"""
RAM Layer 3: Reflection & Meta-Cognition
Implements self-assessment, performance tracking, and strategy refinement
"""

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from app.core.database import Base
from sqlalchemy import Column, String, Numeric, DateTime, JSON, Text, Boolean, Index
from sqlalchemy.sql import func
import uuid


class ReflectionType(Enum):
    PERFORMANCE_ANALYSIS = "performance_analysis"
    STRATEGY_ASSESSMENT = "strategy_assessment"
    ERROR_ANALYSIS = "error_analysis"
    EFFICIENCY_REVIEW = "efficiency_review"
    QUALITY_AUDIT = "quality_audit"


class ReflectionLog(Base):
    """Database model for storing reflection sessions"""
    __tablename__ = "reflection_log"
    
    reflection_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, nullable=False)
    reflection_type = Column(String, nullable=False)  # ReflectionType enum
    trigger_event = Column(String, nullable=False)  # What triggered this reflection
    performance_metrics = Column(JSON)  # Quantitative performance data
    analysis_results = Column(JSON)  # Analysis outcomes
    improvement_strategies = Column(JSON)  # Identified improvements
    confidence_score = Column(Numeric(5,4), nullable=False)
    meta_insights = Column(Text)  # Higher-level insights
    action_items = Column(JSON)  # Concrete next steps
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_reflection_company_type', 'company_id', 'reflection_type'),
        Index('idx_reflection_date', 'created_at'),
        Index('idx_reflection_confidence', 'confidence_score'),
    )


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    accuracy_rate: Decimal
    processing_time: Decimal
    success_rate: Decimal
    user_satisfaction: Decimal
    confidence_score: Decimal
    error_rate: Decimal
    throughput: Decimal


class MetaCognitionEngine:
    """Engine for meta-cognitive reflection and self-improvement"""
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_threshold = Decimal('0.8')
        self.reflection_frequency = timedelta(days=7)  # Weekly reflection
        self.improvement_threshold = Decimal('0.1')  # 10% improvement target
    
    def trigger_reflection(
        self,
        reflection_type: ReflectionType,
        trigger_event: str,
        performance_data: Dict[str, Any],
        company_id: str
    ) -> Dict[str, Any]:
        """Trigger a reflection session"""
        
        # Perform reflection analysis
        reflection_result = self._perform_reflection_analysis(
            reflection_type, performance_data, company_id
        )
        
        # Store reflection in database
        reflection_log = ReflectionLog(
            company_id=company_id,
            reflection_type=reflection_type.value,
            trigger_event=trigger_event,
            performance_metrics=performance_data,
            analysis_results=reflection_result["analysis"],
            improvement_strategies=reflection_result["strategies"],
            confidence_score=reflection_result["confidence"],
            meta_insights=reflection_result["insights"],
            action_items=reflection_result["actions"]
        )
        
        self.db.add(reflection_log)
        self.db.commit()
        
        return {
            "reflection_id": reflection_log.reflection_id,
            "analysis": reflection_result["analysis"],
            "strategies": reflection_result["strategies"],
            "insights": reflection_result["insights"],
            "actions": reflection_result["actions"],
            "confidence": float(reflection_result["confidence"])
        }
    
    def _perform_reflection_analysis(
        self,
        reflection_type: ReflectionType,
        performance_data: Dict[str, Any],
        company_id: str
    ) -> Dict[str, Any]:
        """Perform deep reflection analysis"""
        
        if reflection_type == ReflectionType.PERFORMANCE_ANALYSIS:
            return self._analyze_performance(performance_data, company_id)
        elif reflection_type == ReflectionType.STRATEGY_ASSESSMENT:
            return self._assess_strategies(performance_data, company_id)
        elif reflection_type == ReflectionType.ERROR_ANALYSIS:
            return self._analyze_errors(performance_data, company_id)
        elif reflection_type == ReflectionType.EFFICIENCY_REVIEW:
            return self._review_efficiency(performance_data, company_id)
        elif reflection_type == ReflectionType.QUALITY_AUDIT:
            return self._audit_quality(performance_data, company_id)
        else:
            return self._general_reflection(performance_data, company_id)
    
    def _analyze_performance(self, data: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Analyze overall performance metrics"""
        
        # Extract metrics
        metrics = PerformanceMetrics(
            accuracy_rate=Decimal(str(data.get("accuracy_rate", 0.0))),
            processing_time=Decimal(str(data.get("processing_time", 0.0))),
            success_rate=Decimal(str(data.get("success_rate", 0.0))),
            user_satisfaction=Decimal(str(data.get("user_satisfaction", 0.0))),
            confidence_score=Decimal(str(data.get("confidence_score", 0.0))),
            error_rate=Decimal(str(data.get("error_rate", 0.0))),
            throughput=Decimal(str(data.get("throughput", 0.0)))
        )
        
        # Compare with historical performance
        historical_data = self._get_historical_performance(company_id)
        
        analysis = {
            "current_metrics": {
                "accuracy": float(metrics.accuracy_rate),
                "speed": float(metrics.processing_time),
                "success": float(metrics.success_rate),
                "satisfaction": float(metrics.user_satisfaction)
            },
            "trends": self._analyze_trends(metrics, historical_data),
            "strengths": self._identify_strengths(metrics),
            "weaknesses": self._identify_weaknesses(metrics),
            "improvement_potential": self._calculate_improvement_potential(metrics)
        }
        
        strategies = self._generate_improvement_strategies(analysis)
        insights = self._generate_meta_insights(analysis, "performance")
        actions = self._generate_action_items(strategies)
        confidence = self._calculate_reflection_confidence(analysis)
        
        return {
            "analysis": analysis,
            "strategies": strategies,
            "insights": insights,
            "actions": actions,
            "confidence": confidence
        }
    
    def _assess_strategies(self, data: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Assess effectiveness of current strategies"""
        
        current_strategies = data.get("strategies", [])
        strategy_performance = data.get("strategy_performance", {})
        
        analysis = {
            "strategy_effectiveness": {},
            "resource_allocation": {},
            "opportunity_cost": {},
            "strategic_alignment": {}
        }
        
        for strategy in current_strategies:
            strategy_name = strategy.get("name", "unknown")
            performance = strategy_performance.get(strategy_name, {})
            
            analysis["strategy_effectiveness"][strategy_name] = {
                "success_rate": performance.get("success_rate", 0.0),
                "resource_efficiency": performance.get("resource_efficiency", 0.0),
                "user_impact": performance.get("user_impact", 0.0),
                "scalability": performance.get("scalability", 0.0),
                "recommendation": self._assess_strategy_performance(performance)
            }
        
        strategies = self._optimize_strategy_mix(analysis)
        insights = self._generate_meta_insights(analysis, "strategy")
        actions = self._generate_strategic_actions(strategies)
        confidence = self._calculate_reflection_confidence(analysis)
        
        return {
            "analysis": analysis,
            "strategies": strategies,
            "insights": insights,
            "actions": actions,
            "confidence": confidence
        }
    
    def _analyze_errors(self, data: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Analyze error patterns and root causes"""
        
        errors = data.get("errors", [])
        error_categories = {}
        
        for error in errors:
            category = error.get("category", "unknown")
            if category not in error_categories:
                error_categories[category] = {
                    "count": 0,
                    "severity_sum": 0,
                    "examples": []
                }
            
            error_categories[category]["count"] += 1
            error_categories[category]["severity_sum"] += error.get("severity", 1)
            error_categories[category]["examples"].append(error.get("description", ""))
        
        analysis = {
            "error_distribution": error_categories,
            "critical_patterns": self._identify_critical_error_patterns(error_categories),
            "root_causes": self._analyze_root_causes(errors),
            "prevention_opportunities": self._identify_prevention_opportunities(errors)
        }
        
        strategies = self._generate_error_prevention_strategies(analysis)
        insights = self._generate_meta_insights(analysis, "error")
        actions = self._generate_error_actions(strategies)
        confidence = self._calculate_reflection_confidence(analysis)
        
        return {
            "analysis": analysis,
            "strategies": strategies,
            "insights": insights,
            "actions": actions,
            "confidence": confidence
        }
    
    def _review_efficiency(self, data: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Review operational efficiency"""
        
        processes = data.get("processes", {})
        resource_usage = data.get("resource_usage", {})
        
        analysis = {
            "process_efficiency": {},
            "resource_utilization": resource_usage,
            "bottlenecks": self._identify_bottlenecks(processes),
            "optimization_opportunities": self._identify_optimizations(processes, resource_usage)
        }
        
        for process_name, process_data in processes.items():
            analysis["process_efficiency"][process_name] = {
                "throughput": process_data.get("throughput", 0),
                "latency": process_data.get("latency", 0),
                "resource_intensity": process_data.get("resource_intensity", 0),
                "efficiency_score": self._calculate_efficiency_score(process_data)
            }
        
        strategies = self._generate_efficiency_strategies(analysis)
        insights = self._generate_meta_insights(analysis, "efficiency")
        actions = self._generate_efficiency_actions(strategies)
        confidence = self._calculate_reflection_confidence(analysis)
        
        return {
            "analysis": analysis,
            "strategies": strategies,
            "insights": insights,
            "actions": actions,
            "confidence": confidence
        }
    
    def _audit_quality(self, data: Dict[str, Any], company_id: str) -> Dict[str, Any]:
        """Audit output quality"""
        
        quality_metrics = data.get("quality_metrics", {})
        user_feedback = data.get("user_feedback", [])
        
        analysis = {
            "quality_scores": quality_metrics,
            "user_satisfaction_analysis": self._analyze_user_feedback(user_feedback),
            "quality_trends": self._analyze_quality_trends(quality_metrics, company_id),
            "improvement_areas": self._identify_quality_improvements(quality_metrics, user_feedback)
        }
        
        strategies = self._generate_quality_strategies(analysis)
        insights = self._generate_meta_insights(analysis, "quality")
        actions = self._generate_quality_actions(strategies)
        confidence = self._calculate_reflection_confidence(analysis)
        
        return {
            "analysis": analysis,
            "strategies": strategies,
            "insights": insights,
            "actions": actions,
            "confidence": confidence
        }
    
    def get_reflection_summary(self, company_id: str, days: int = 30) -> Dict[str, Any]:
        """Get reflection summary for past period"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        reflections = self.db.query(ReflectionLog).filter(
            ReflectionLog.company_id == company_id,
            ReflectionLog.created_at >= cutoff_date
        ).all()
        
        summary = {
            "total_reflections": len(reflections),
            "reflection_types": {},
            "average_confidence": 0.0,
            "implemented_actions": 0,
            "key_insights": [],
            "improvement_trajectory": [],
            "meta_learning": {}
        }
        
        if not reflections:
            return summary
        
        # Aggregate by type
        for reflection in reflections:
            ref_type = reflection.reflection_type
            if ref_type not in summary["reflection_types"]:
                summary["reflection_types"][ref_type] = 0
            summary["reflection_types"][ref_type] += 1
        
        # Calculate averages
        total_confidence = sum(float(r.confidence_score) for r in reflections)
        summary["average_confidence"] = total_confidence / len(reflections)
        
        # Count implemented actions
        summary["implemented_actions"] = sum(1 for r in reflections if r.is_implemented)
        
        # Extract key insights
        for reflection in reflections[-5:]:  # Last 5 reflections
            if reflection.meta_insights:
                summary["key_insights"].append({
                    "insight": reflection.meta_insights,
                    "type": reflection.reflection_type,
                    "date": reflection.created_at.isoformat(),
                    "confidence": float(reflection.confidence_score)
                })
        
        # Meta-learning analysis
        summary["meta_learning"] = self._analyze_meta_learning_progress(reflections)
        
        return summary
    
    def _generate_improvement_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement strategies based on analysis"""
        strategies = []
        
        weaknesses = analysis.get("weaknesses", [])
        for weakness in weaknesses:
            strategies.append({
                "area": weakness,
                "strategy": f"Implement targeted improvement for {weakness}",
                "priority": "high" if weakness in ["accuracy", "reliability"] else "medium",
                "effort": "medium",
                "impact": "high"
            })
        
        return strategies
    
    def _generate_meta_insights(self, analysis: Dict[str, Any], domain: str) -> str:
        """Generate higher-level meta insights"""
        insights = []
        
        if domain == "performance":
            trends = analysis.get("trends", {})
            if trends.get("improving", False):
                insights.append("System shows consistent improvement trajectory")
            else:
                insights.append("Performance plateau reached, need strategic intervention")
        
        elif domain == "strategy":
            effectiveness = analysis.get("strategy_effectiveness", {})
            high_performers = [k for k, v in effectiveness.items() 
                             if v.get("success_rate", 0) > 0.8]
            if high_performers:
                insights.append(f"High-performing strategies: {', '.join(high_performers)}")
        
        elif domain == "error":
            critical_patterns = analysis.get("critical_patterns", [])
            if critical_patterns:
                insights.append(f"Critical error patterns identified: {len(critical_patterns)} categories")
        
        return " | ".join(insights) if insights else "No significant meta-insights identified"
    
    def _calculate_reflection_confidence(self, analysis: Dict[str, Any]) -> Decimal:
        """Calculate confidence in reflection analysis"""
        
        # Base confidence on data completeness and consistency
        data_completeness = len([k for k, v in analysis.items() if v]) / len(analysis)
        
        # Adjust based on data quality indicators
        confidence = Decimal(str(data_completeness * 0.8))  # Base confidence
        
        # Boost confidence if we have historical context
        if "trends" in analysis:
            confidence += Decimal('0.1')
        
        return min(Decimal('1.0'), confidence)
    
    # Helper methods for specific analyses
    def _get_historical_performance(self, company_id: str) -> Dict[str, Any]:
        """Get historical performance data"""
        # Placeholder - would query historical performance metrics
        return {}
    
    def _analyze_trends(self, current: PerformanceMetrics, historical: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends"""
        return {"improving": True, "declining_areas": [], "stable_areas": []}
    
    def _identify_strengths(self, metrics: PerformanceMetrics) -> List[str]:
        """Identify performance strengths"""
        strengths = []
        if metrics.accuracy_rate > Decimal('0.9'):
            strengths.append("accuracy")
        if metrics.success_rate > Decimal('0.85'):
            strengths.append("reliability")
        return strengths
    
    def _identify_weaknesses(self, metrics: PerformanceMetrics) -> List[str]:
        """Identify performance weaknesses"""
        weaknesses = []
        if metrics.accuracy_rate < Decimal('0.7'):
            weaknesses.append("accuracy")
        if metrics.processing_time > Decimal('5.0'):
            weaknesses.append("speed")
        return weaknesses
    
    def _calculate_improvement_potential(self, metrics: PerformanceMetrics) -> Dict[str, float]:
        """Calculate improvement potential"""
        return {
            "accuracy": max(0, float(Decimal('1.0') - metrics.accuracy_rate)),
            "speed": max(0, float(metrics.processing_time - Decimal('1.0'))),
            "overall": 0.2  # 20% overall improvement potential
        }
    
    def _generate_action_items(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate concrete action items"""
        actions = []
        for strategy in strategies:
            actions.append({
                "action": f"Implement {strategy.get('strategy', 'improvement strategy')}",
                "priority": strategy.get("priority", "medium"),
                "timeline": "2 weeks",
                "owner": "system",
                "success_metric": f"Improve {strategy.get('area', 'performance')} by 10%"
            })
        return actions
    
    # Additional helper methods would be implemented here...
    def _assess_strategy_performance(self, performance: Dict[str, Any]) -> str:
        """Assess individual strategy performance"""
        success_rate = performance.get("success_rate", 0.0)
        if success_rate > 0.8:
            return "continue"
        elif success_rate > 0.6:
            return "optimize"
        else:
            return "reconsider"
    
    def _optimize_strategy_mix(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize strategy mix"""
        return [{"strategy": "balance_resource_allocation", "impact": "medium"}]
    
    def _analyze_meta_learning_progress(self, reflections: List[ReflectionLog]) -> Dict[str, Any]:
        """Analyze meta-learning progress"""
        return {
            "learning_velocity": "steady",
            "insight_quality": "improving",
            "implementation_rate": 0.7
        }