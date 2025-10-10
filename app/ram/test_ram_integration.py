# app/ram/test_ram_integration.py
"""
Comprehensive test suite for RAM cognitive framework integration
Tests database connectivity, CDM model integration, and authentication
"""

import asyncio
import json
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.tenant_context import TenantContext

# RAM Components
from app.ram.ram_service import RAMOrchestrationService
from app.ram.cognitive_core.reasoning_engine import RAMCognitiveEngine
from app.ram.adaptive_core.heuristic_memory import AdaptiveMemoryService
from app.ram.reflection_core.meta_cognition import MetaCognitionEngine, ReflectionType

# CDM Models (existing architecture)
from app.cdm.models.entity import Entity
from app.cdm.models.master import Ledger
from app.cdm.models.transaction import VoucherHeader, VoucherLine
from app.cdm.models.external import BankStatement, GSTSales
from app.cdm.models.reconciliation import ReconciliationLog

# Authentication
from app.tenant.models.firm import CAFirm
from app.tenant.models.user import User


class RAMIntegrationTester:
    """Comprehensive tester for RAM-CA architecture integration"""
    
    def __init__(self):
        self.db = next(get_db())
        self.test_company_id = None
        self.test_firm_id = None
        self.test_results = []
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests"""
        
        print("🧪 Starting RAM Architecture Integration Tests...")
        print("=" * 60)
        
        # Test 1: Database connectivity and schema
        await self._test_database_connectivity()
        
        # Test 2: CDM model integration
        await self._test_cdm_integration()
        
        # Test 3: RAM components initialization
        await self._test_ram_components()
        
        # Test 4: Data flow integration
        await self._test_data_flow_integration()
        
        # Test 5: Reconciliation with real data
        await self._test_reconciliation_with_real_data()
        
        # Test 6: Learning and adaptation
        await self._test_learning_adaptation()
        
        # Test 7: API endpoints
        await self._test_api_endpoints()
        
        # Summary
        return self._generate_test_summary()
    
    async def _test_database_connectivity(self):
        """Test database connectivity and RAM table creation"""
        
        print("\n1️⃣ Testing Database Connectivity & Schema...")
        
        try:
            # Test basic database connection
            result = self.db.execute("SELECT 1").scalar()
            self._log_success("Database connection", "Connected successfully")
            
            # Check if RAM tables exist
            tables_to_check = ['heuristic_memory', 'reflection_log']
            for table in tables_to_check:
                try:
                    self.db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                    self._log_success(f"Table {table}", "Exists and accessible")
                except Exception as e:
                    self._log_error(f"Table {table}", f"Missing or inaccessible: {e}")
            
            # Check CDM tables
            cdm_tables = ['entities', 'ledgers', 'vouchers', 'bank_statements', 'reconciliation_logs']
            for table in cdm_tables:
                try:
                    count = self.db.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                    self._log_success(f"CDM Table {table}", f"Exists with {count} records")
                except Exception as e:
                    self._log_error(f"CDM Table {table}", f"Issue: {e}")
                    
        except Exception as e:
            self._log_error("Database connectivity", f"Failed: {e}")
    
    async def _test_cdm_integration(self):
        """Test integration with existing CDM models"""
        
        print("\n2️⃣ Testing CDM Model Integration...")
        
        try:
            # Get or create test company
            test_entity = self.db.query(Entity).first()
            if not test_entity:
                # Create test entity
                from datetime import date
                test_entity = Entity(
                    company_id="test-company-" + str(int(datetime.now().timestamp())),
                    company_name="Test Company for RAM",
                    financial_year_start=date(2023, 4, 1),
                    financial_year_end=date(2024, 3, 31)
                )
                self.db.add(test_entity)
                self.db.commit()
                self._log_success("Test entity creation", f"Created: {test_entity.company_name}")
            else:
                self._log_success("Existing entity found", f"Using: {test_entity.company_name}")
            
            self.test_company_id = test_entity.company_id
            
            # Check existing vouchers
            voucher_count = self.db.query(VoucherHeader).filter(
                VoucherHeader.company_id == self.test_company_id
            ).count()
            self._log_success("Vouchers for company", f"Found {voucher_count} vouchers")
            
            # Check existing bank statements
            bank_stmt_count = self.db.query(BankStatement).filter(
                BankStatement.company_id == self.test_company_id
            ).count()
            self._log_success("Bank statements for company", f"Found {bank_stmt_count} statements")
            
            # Check reconciliation logs
            recon_count = self.db.query(ReconciliationLog).filter(
                ReconciliationLog.company_id == self.test_company_id
            ).count()
            self._log_success("Reconciliation logs", f"Found {recon_count} existing logs")
            
        except Exception as e:
            self._log_error("CDM integration", f"Failed: {e}")
    
    async def _test_ram_components(self):
        """Test RAM component initialization and functionality"""
        
        print("\n3️⃣ Testing RAM Component Initialization...")
        
        try:
            # Test Cognitive Engine
            cognitive_engine = RAMCognitiveEngine(self.db)
            self._log_success("RAMCognitiveEngine", "Initialized successfully")
            
            # Test perceptual interface
            test_data = {"test": "data"}
            perceptual_result = cognitive_engine.perceptual_interface.process_contextual_data(
                test_data, self.test_company_id or "test-company"
            )
            self._log_success("Perceptual interface", f"Processed data: {len(str(perceptual_result))} chars")
            
            # Test Adaptive Memory
            adaptive_memory = AdaptiveMemoryService(self.db)
            learning_stats = adaptive_memory.get_learning_statistics(
                self.test_company_id or "test-company"
            )
            self._log_success("AdaptiveMemoryService", f"Learning stats: {learning_stats['total_patterns_learned']} patterns")
            
            # Test Meta-Cognition
            meta_cognition = MetaCognitionEngine(self.db)
            reflection_summary = meta_cognition.get_reflection_summary(
                self.test_company_id or "test-company"
            )
            self._log_success("MetaCognitionEngine", f"Reflections: {reflection_summary['total_reflections']}")
            
            # Test Main Orchestration Service
            ram_service = RAMOrchestrationService(self.db)
            system_status = await ram_service.get_system_status(
                self.test_company_id or "test-company"
            )
            self._log_success("RAMOrchestrationService", f"System health: {system_status['system_health']['database_connectivity']}")
            
        except Exception as e:
            self._log_error("RAM components", f"Failed: {e}")
    
    async def _test_data_flow_integration(self):
        """Test data flow from CDM models to RAM processing"""
        
        print("\n4️⃣ Testing Data Flow Integration...")
        
        try:
            if not self.test_company_id:
                self._log_error("Data flow test", "No test company ID available")
                return
            
            # Create RAM service
            ram_service = RAMOrchestrationService(self.db)
            
            # Test perceptual data gathering
            test_request = {
                "batch_size": 10,
                "financial_year": "2023-24",
                "priority": "high"
            }
            
            perceptual_data = await ram_service._gather_perceptual_data(
                self.test_company_id, test_request
            )
            
            self._log_success("Perceptual data gathering", 
                f"Gathered {len(perceptual_data.get('vouchers', []))} vouchers, "
                f"{len(perceptual_data.get('bank_statements', []))} statements, "
                f"{len(perceptual_data.get('historical_patterns', []))} patterns"
            )
            
            # Test cognitive processing
            if perceptual_data.get('vouchers') or perceptual_data.get('bank_statements'):
                reasoning_result = await ram_service.cognitive_engine.process_reconciliation_request(
                    perceptual_data, self.test_company_id
                )
                
                self._log_success("Cognitive processing", 
                    f"Generated strategy with {len(reasoning_result.get('reconciliation_strategy', {}).get('matching_rules', []))} rules"
                )
            else:
                self._log_warning("Cognitive processing", "No data available for processing")
                
        except Exception as e:
            self._log_error("Data flow integration", f"Failed: {e}")
    
    async def _test_reconciliation_with_real_data(self):
        """Test reconciliation processing with real database data"""
        
        print("\n5️⃣ Testing Reconciliation with Real Data...")
        
        try:
            if not self.test_company_id:
                self._log_error("Reconciliation test", "No test company ID available")
                return
            
            # Create test context
            context = TenantContext(company_id=self.test_company_id, user_id="test-user")
            
            # Create RAM service
            ram_service = RAMOrchestrationService(self.db)
            
            # Check available data
            unmatched_vouchers = self.db.query(VoucherHeader).filter(
                VoucherHeader.company_id == self.test_company_id,
                VoucherHeader.reconciliation_status == "Unmatched"
            ).count()
            
            unmatched_statements = self.db.query(BankStatement).filter(
                BankStatement.company_id == self.test_company_id,
                BankStatement.reconciliation_status == "Unmatched"
            ).count()
            
            self._log_success("Available data", 
                f"{unmatched_vouchers} unmatched vouchers, {unmatched_statements} unmatched statements"
            )
            
            if unmatched_vouchers > 0 and unmatched_statements > 0:
                # Process small batch
                reconciliation_request = {
                    "batch_size": 5,
                    "financial_year": "2023-24",
                    "mode": "automatic",
                    "confidence_threshold": 0.7
                }
                
                result = await ram_service.process_reconciliation_batch(
                    context, reconciliation_request
                )
                
                summary = result.get('ram_processing_summary', {})
                self._log_success("Reconciliation processing", 
                    f"Processed {summary.get('total_items_processed', 0)} items, "
                    f"{summary.get('successful_matches', 0)} matches, "
                    f"avg confidence {summary.get('average_confidence', 0):.2f}"
                )
                
                # Check if data was actually written to database
                new_recon_count = self.db.query(ReconciliationLog).filter(
                    ReconciliationLog.company_id == self.test_company_id
                ).count()
                self._log_success("Database persistence", f"Reconciliation logs in DB: {new_recon_count}")
                
            else:
                self._log_warning("Reconciliation test", "Insufficient data for reconciliation test")
                
        except Exception as e:
            self._log_error("Reconciliation with real data", f"Failed: {e}")
    
    async def _test_learning_adaptation(self):
        """Test learning and adaptation capabilities"""
        
        print("\n6️⃣ Testing Learning & Adaptation...")
        
        try:
            if not self.test_company_id:
                self._log_error("Learning test", "No test company ID available")
                return
            
            # Test adaptive memory
            adaptive_memory = AdaptiveMemoryService(self.db)
            
            # Record a successful pattern
            pattern_hash = adaptive_memory.evolver.record_successful_pattern(
                idea="Test reconciliation pattern for integration test",
                function_name="test_matching_function",
                success_score=Decimal('0.95'),
                context={
                    "domain": "reconciliation",
                    "financial_year": "2023-24",
                    "task_type": "integration_test"
                },
                company_id=self.test_company_id
            )
            
            self._log_success("Pattern recording", f"Recorded pattern: {pattern_hash[:16]}...")
            
            # Test pattern retrieval
            similar_patterns = adaptive_memory.evolver.fetch_similar_patterns(
                context={"domain": "reconciliation", "task_type": "integration_test"},
                company_id=self.test_company_id,
                min_score=Decimal('0.8')
            )
            
            self._log_success("Pattern retrieval", f"Found {len(similar_patterns)} similar patterns")
            
            # Test meta-cognition reflection
            meta_cognition = MetaCognitionEngine(self.db)
            
            performance_data = {
                "accuracy_rate": 0.92,
                "processing_time": 2.5,
                "success_rate": 0.88,
                "confidence_score": 0.85
            }
            
            reflection_result = meta_cognition.trigger_reflection(
                ReflectionType.PERFORMANCE_ANALYSIS,
                "integration_test_triggered",
                performance_data,
                self.test_company_id
            )
            
            self._log_success("Meta-cognitive reflection", 
                f"Reflection confidence: {reflection_result['confidence']:.2f}"
            )
            
        except Exception as e:
            self._log_error("Learning & adaptation", f"Failed: {e}")
    
    async def _test_api_endpoints(self):
        """Test API endpoint accessibility (without actual HTTP calls)"""
        
        print("\n7️⃣ Testing API Endpoint Integration...")
        
        try:
            # Import routes to verify they're properly configured
            from app.ram.routes import router
            
            # Count available routes
            route_count = len(router.routes)
            self._log_success("RAM API routes", f"{route_count} routes registered")
            
            # Check if routes are properly tagged
            ram_routes = [route for route in router.routes if hasattr(route, 'tags') and 'RAM Cognitive Framework' in route.tags]
            self._log_success("RAM tagged routes", f"{len(ram_routes)} RAM-specific routes")
            
            # Verify main app integration
            from app.main import app
            all_routes = []
            for route in app.routes:
                if hasattr(route, 'path'):
                    all_routes.append(route.path)
            
            ram_api_routes = [path for path in all_routes if '/ram' in path]
            self._log_success("Main app integration", f"{len(ram_api_routes)} RAM routes in main app")
            
            # Check authentication dependency
            from app.ram.routes import get_current_user, get_tenant_context
            self._log_success("Authentication integration", "JWT and tenant context dependencies available")
            
        except Exception as e:
            self._log_error("API endpoints", f"Failed: {e}")
    
    def _log_success(self, test_name: str, message: str):
        """Log successful test result"""
        print(f"   ✅ {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "status": "SUCCESS",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _log_warning(self, test_name: str, message: str):
        """Log warning test result"""
        print(f"   ⚠️  {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "status": "WARNING",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _log_error(self, test_name: str, message: str):
        """Log error test result"""
        print(f"   ❌ {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "status": "ERROR",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "SUCCESS"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARNING"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"🧪 RAM INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"❌ Errors: {error_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*60}")
        
        if success_rate >= 80:
            print("🎉 RAM ARCHITECTURE INTEGRATION: EXCELLENT")
        elif success_rate >= 60:
            print("👍 RAM ARCHITECTURE INTEGRATION: GOOD")
        else:
            print("⚠️  RAM ARCHITECTURE INTEGRATION: NEEDS ATTENTION")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "warning_tests": warning_tests,
                "error_tests": error_tests,
                "success_rate": success_rate,
                "test_company_id": self.test_company_id,
                "timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results,
            "integration_status": "EXCELLENT" if success_rate >= 80 else "GOOD" if success_rate >= 60 else "NEEDS_ATTENTION",
            "database_integration": successful_tests > 0,
            "cdm_integration": any("CDM" in r["test"] for r in self.test_results if r["status"] == "SUCCESS"),
            "ram_components_working": any("RAM" in r["test"] for r in self.test_results if r["status"] == "SUCCESS")
        }


# Main test execution function
async def run_integration_tests():
    """Run all RAM integration tests"""
    tester = RAMIntegrationTester()
    return await tester.run_all_tests()


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(run_integration_tests())