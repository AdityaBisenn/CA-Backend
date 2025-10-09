# app/services/ai_reconciliation.py
"""
AI-Powered Reconciliation Service
Integrates LLM capabilities with the CDM reconciliation engine
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json

from sqlalchemy.orm import Session
from app.core.init_llm import make_llm
from app.core.tenant_context import TenantContext
from app.cdm.models.reconciliation import ReconciliationLog, AIFeedback
from app.cdm.models.transaction import VoucherHeader
from app.cdm.models.external import BankStatement
from app.core.database import get_db


class AIReconciliationService:
    """
    Service for AI-powered financial reconciliation using LLM
    Integrates with existing CDM reconciliation models
    """
    
    def __init__(self, db: Session, context: TenantContext):
        self.db = db
        self.context = context
        self.llm = make_llm(temperature=0.2)  # Low temperature for consistency
    
    async def intelligent_bank_reconciliation(
        self, 
        vouchers: List[VoucherHeader], 
        bank_statements: List[BankStatement]
    ) -> List[Dict]:
        """
        Use AI to intelligently match vouchers with bank statements
        """
        reconciliation_results = []
        
        for voucher in vouchers:
            # Find potential matches using AI analysis
            potential_matches = await self._find_ai_matches(voucher, bank_statements)
            
            if potential_matches:
                best_match = potential_matches[0]  # Highest confidence
                
                # Create reconciliation log entry
                recon_log = ReconciliationLog(
                    company_id=self.context.company_id,
                    source_table="vouchers",
                    target_table="bank_statements", 
                    source_record_id=voucher.voucher_id,
                    target_record_id=best_match['bank_record_id'],
                    match_score=best_match['confidence_score'],
                    match_rule="AI_LLM_Analysis",
                    rule_details={
                        "ai_reasoning": best_match['reasoning'],
                        "amount_variance": best_match.get('amount_variance', 0),
                        "date_variance_days": best_match.get('date_variance', 0),
                        "description_similarity": best_match.get('description_similarity', 0)
                    },
                    status="Matched" if best_match['confidence_score'] > 0.85 else "Manual_Review",
                    ai_reasoning=best_match['reasoning']
                )
                
                self.db.add(recon_log)
                reconciliation_results.append({
                    "voucher_id": voucher.voucher_id,
                    "matched": True,
                    "confidence": float(best_match['confidence_score']),
                    "requires_review": best_match['confidence_score'] <= 0.85
                })
        
        self.db.commit()
        return reconciliation_results
    
    async def _find_ai_matches(
        self, 
        voucher: VoucherHeader, 
        bank_statements: List[BankStatement]
    ) -> List[Dict]:
        """
        Use LLM to analyze and find potential matches for a voucher
        """
        
        # Prepare data for AI analysis
        voucher_data = {
            "date": voucher.voucher_date.isoformat(),
            "amount": float(voucher.total_amount),
            "description": voucher.narration or "",
            "type": voucher.voucher_type,
            "party": voucher.party_ledger_id
        }
        
        bank_data = []
        for stmt in bank_statements:
            bank_data.append({
                "id": stmt.statement_id,
                "date": stmt.transaction_date.isoformat(),
                "amount": float(stmt.amount),
                "description": stmt.description or "",
                "reference": stmt.reference_number or "",
                "type": stmt.transaction_type
            })
        
        # Create AI prompt for reconciliation analysis
        prompt = f"""
        You are a financial reconciliation expert. Analyze the following voucher and find the best matching bank statement(s).
        
        VOUCHER TO MATCH:
        {json.dumps(voucher_data, indent=2)}
        
        BANK STATEMENTS:
        {json.dumps(bank_data, indent=2)}
        
        For each potential match, provide:
        1. Confidence score (0.0 to 1.0)
        2. Detailed reasoning for the match
        3. Amount variance (if any)
        4. Date variance in days (if any) 
        5. Description similarity assessment
        
        Return ONLY a JSON array of matches, ordered by confidence score (highest first).
        Format: [{{"bank_record_id": "id", "confidence_score": 0.95, "reasoning": "explanation", "amount_variance": 0.0, "date_variance": 0, "description_similarity": 0.9}}]
        """
        
        try:
            response = self.llm.invoke(prompt)
            
            # Parse AI response
            matches = json.loads(response.content)
            
            # Validate and filter matches
            valid_matches = []
            for match in matches:
                if (isinstance(match.get('confidence_score'), (int, float)) and 
                    0.0 <= match['confidence_score'] <= 1.0):
                    
                    # Convert confidence to Decimal for database storage
                    match['confidence_score'] = Decimal(str(match['confidence_score']))
                    valid_matches.append(match)
            
            return valid_matches
            
        except (json.JSONDecodeError, Exception) as e:
            # Log error and return empty matches
            print(f"AI reconciliation error: {e}")
            return []
    
    async def analyze_financial_anomalies(
        self, 
        vouchers: List[VoucherHeader]
    ) -> Dict:
        """
        Use AI to detect potential anomalies in financial data
        """
        
        # Prepare voucher data for analysis
        voucher_data = []
        for v in vouchers:
            voucher_data.append({
                "id": v.voucher_id,
                "date": v.voucher_date.isoformat(),
                "amount": float(v.total_amount),
                "type": v.voucher_type,
                "description": v.narration or ""
            })
        
        prompt = f"""
        You are a financial auditor analyzing transactions for anomalies. 
        Review these vouchers and identify any suspicious patterns, unusual amounts, or data inconsistencies.
        
        VOUCHERS TO ANALYZE:
        {json.dumps(voucher_data, indent=2)}
        
        Look for:
        1. Unusual amount patterns (round numbers, duplicates)
        2. Frequency anomalies (too many transactions on specific dates)
        3. Description inconsistencies
        4. Amount outliers compared to typical transaction ranges
        
        Return analysis as JSON: {{"anomalies_found": true/false, "suspicious_vouchers": [], "summary": "explanation", "risk_level": "low/medium/high"}}
        """
        
        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response.content)
            return analysis
            
        except Exception as e:
            return {
                "anomalies_found": False,
                "error": str(e),
                "summary": "AI analysis failed"
            }
    
    async def generate_reconciliation_report(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> str:
        """
        Generate AI-powered reconciliation insights report
        """
        
        # Get reconciliation data from database
        recon_logs = self.db.query(ReconciliationLog).filter(
            ReconciliationLog.company_id == self.context.company_id,
            ReconciliationLog.created_at >= start_date,
            ReconciliationLog.created_at <= end_date
        ).all()
        
        # Prepare data for AI report generation
        recon_data = []
        for log in recon_logs:
            recon_data.append({
                "status": log.status,
                "match_score": float(log.match_score) if log.match_score else 0,
                "source_table": log.source_table,
                "target_table": log.target_table,
                "ai_reasoning": log.ai_reasoning
            })
        
        prompt = f"""
        Generate a comprehensive reconciliation report based on this data:
        
        RECONCILIATION DATA:
        {json.dumps(recon_data, indent=2)}
        
        Report Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
        
        Include:
        1. Executive Summary
        2. Reconciliation Statistics
        3. Key Insights and Patterns
        4. Areas of Concern
        5. Recommendations for Improvement
        
        Format as professional markdown report.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"# Reconciliation Report\n\nError generating AI report: {str(e)}"
    
    def record_ai_feedback(
        self,
        voucher_id: str,
        original_prediction: Dict,
        user_correction: Dict,
        feedback_type: str,
        user_id: str
    ):
        """
        Record user feedback on AI predictions for model improvement
        """
        
        feedback = AIFeedback(
            company_id=self.context.company_id,
            voucher_id=voucher_id,
            original_prediction=original_prediction,
            user_correction=user_correction,
            feedback_type=feedback_type,
            confidence_before=Decimal(str(original_prediction.get('confidence', 0))),
            confidence_after=Decimal('1.0'),  # User correction is assumed correct
            model_version="gpt-4",  # Track which model version
            user_id=user_id
        )
        
        self.db.add(feedback)
        self.db.commit()
        
        return feedback.feedback_id