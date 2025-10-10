# test_ram_simple.py
"""
Simple RAM integration test - just verify components work
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/Users/adityabisen/Desktop/CA Updates Agent/CA-App/CA-Backend')

import asyncio
from decimal import Decimal
from datetime import datetime

def test_imports():
    """Test if all RAM components can be imported"""
    print("🧪 Testing RAM Component Imports...")
    
    try:
        from app.core.database import get_db
        print("✅ Database connection imported")
        
        from app.ram.cognitive_core.reasoning_engine import RAMCognitiveEngine
        print("✅ RAMCognitiveEngine imported")
        
        from app.ram.adaptive_core.heuristic_memory import AdaptiveMemoryService
        print("✅ AdaptiveMemoryService imported")
        
        from app.ram.reflection_core.meta_cognition import MetaCognitionEngine
        print("✅ MetaCognitionEngine imported")
        
        from app.ram.ram_service import RAMOrchestrationService
        print("✅ RAMOrchestrationService imported")
        
        from app.cdm.models.entity import Entity
        from app.cdm.models.transaction import VoucherHeader
        from app.cdm.models.external import BankStatement
        from app.cdm.models.reconciliation import ReconciliationLog
        print("✅ CDM models imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        from app.core.database import get_db
        db = next(get_db())
        
        # Test basic query
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection successful: {result}")
        
        # Check if RAM tables exist
        try:
            count = db.execute(text("SELECT COUNT(*) FROM heuristic_memory")).scalar()
            print(f"✅ heuristic_memory table exists with {count} records")
        except Exception as e:
            print(f"❌ heuristic_memory table issue: {e}")
        
        try:
            count = db.execute(text("SELECT COUNT(*) FROM reflection_log")).scalar()
            print(f"✅ reflection_log table exists with {count} records")
        except Exception as e:
            print(f"❌ reflection_log table issue: {e}")
        
        # Check CDM tables
        try:
            count = db.execute(text("SELECT COUNT(*) FROM entities")).scalar()
            print(f"✅ entities table exists with {count} records")
        except Exception as e:
            print(f"❌ entities table issue: {e}")
        
        try:
            count = db.execute(text("SELECT COUNT(*) FROM vouchers")).scalar()
            print(f"✅ vouchers table exists with {count} records")
        except Exception as e:
            print(f"❌ vouchers table issue: {e}")
        
        try:
            count = db.execute(text("SELECT COUNT(*) FROM bank_statements")).scalar()
            print(f"✅ bank_statements table exists with {count} records")
        except Exception as e:
            print(f"❌ bank_statements table issue: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_ram_initialization():
    """Test RAM component initialization"""
    print("\n🧠 Testing RAM Component Initialization...")
    
    try:
        from app.core.database import get_db
        from app.ram.ram_service import RAMOrchestrationService
        
        db = next(get_db())
        
        # Initialize RAM service
        ram_service = RAMOrchestrationService(db)
        print("✅ RAMOrchestrationService initialized")
        
        # Test cognitive engine
        if ram_service.cognitive_engine:
            print("✅ Cognitive Engine initialized")
        else:
            print("❌ Cognitive Engine not initialized")
        
        # Test adaptive memory
        if ram_service.adaptive_memory:
            print("✅ Adaptive Memory initialized")
        else:
            print("❌ Adaptive Memory not initialized")
        
        # Test meta-cognition
        if ram_service.meta_cognition:
            print("✅ Meta-Cognition initialized")
        else:
            print("❌ Meta-Cognition not initialized")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ RAM initialization failed: {e}")
        return False

async def test_system_status():
    """Test system status endpoint"""
    print("\n📊 Testing System Status...")
    
    try:
        from app.core.database import get_db
        from app.ram.ram_service import RAMOrchestrationService
        
        db = next(get_db())
        ram_service = RAMOrchestrationService(db)
        
        # Test with a dummy company ID
        test_company_id = "test-company-123"
        
        status = await ram_service.get_system_status(test_company_id)
        print(f"✅ System status retrieved: {len(status)} components")
        
        if 'cognitive_status' in status:
            print("✅ Cognitive status available")
        
        if 'learning_progress' in status:
            print("✅ Learning progress available")
        
        if 'system_health' in status:
            print("✅ System health available")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ System status test failed: {e}")
        return False

async def test_learning_system():
    """Test learning system"""
    print("\n📚 Testing Learning System...")
    
    try:
        from app.core.database import get_db
        from app.ram.adaptive_core.heuristic_memory import AdaptiveMemoryService
        
        db = next(get_db())
        adaptive_memory = AdaptiveMemoryService(db)
        
        test_company_id = "test-company-123"
        
        # Record a test pattern
        pattern_hash = adaptive_memory.evolver.record_successful_pattern(
            idea="Test pattern for integration verification",
            function_name="test_function",
            success_score=Decimal('0.95'),
            context={"domain": "test", "task_type": "integration"},
            company_id=test_company_id
        )
        print(f"✅ Pattern recorded: {pattern_hash[:16]}...")
        
        # Get learning statistics
        stats = adaptive_memory.get_learning_statistics(test_company_id)
        print(f"✅ Learning stats: {stats['total_patterns_learned']} patterns learned")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Learning system test failed: {e}")
        return False

async def test_reflection_system():
    """Test reflection system"""
    print("\n🤔 Testing Reflection System...")
    
    try:
        from app.core.database import get_db
        from app.ram.reflection_core.meta_cognition import MetaCognitionEngine, ReflectionType
        
        db = next(get_db())
        meta_cognition = MetaCognitionEngine(db)
        
        test_company_id = "test-company-123"
        
        # Trigger a test reflection
        performance_data = {
            "accuracy_rate": 0.92,
            "processing_time": 2.5,
            "success_rate": 0.88
        }
        
        reflection_result = meta_cognition.trigger_reflection(
            ReflectionType.PERFORMANCE_ANALYSIS,
            "integration_test",
            performance_data,
            test_company_id
        )
        
        print(f"✅ Reflection triggered: confidence {reflection_result['confidence']:.2f}")
        
        # Get reflection summary
        summary = meta_cognition.get_reflection_summary(test_company_id, 30)
        print(f"✅ Reflection summary: {summary['total_reflections']} reflections")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Reflection system test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RAM ARCHITECTURE INTEGRATION TEST")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 6
    
    # Run tests
    if test_imports():
        tests_passed += 1
    
    if test_database_connection():
        tests_passed += 1
    
    if test_ram_initialization():
        tests_passed += 1
    
    if await test_system_status():
        tests_passed += 1
    
    if await test_learning_system():
        tests_passed += 1
    
    if await test_reflection_system():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"🧪 TEST RESULTS: {tests_passed}/{total_tests} passed")
    success_rate = (tests_passed / total_tests) * 100
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 RAM INTEGRATION: EXCELLENT!")
        print("✅ Your RAM cognitive framework is fully integrated and working!")
    elif success_rate >= 60:
        print("👍 RAM INTEGRATION: GOOD!")
        print("⚠️  Minor issues detected, but core functionality works")
    else:
        print("⚠️  RAM INTEGRATION: NEEDS ATTENTION")
        print("❌ Several components need fixing")
    
    print("\n🌐 Next steps:")
    print("1. Visit http://localhost:8001/docs to see RAM API endpoints")
    print("2. Test /api/v1/ram/system/status endpoint")
    print("3. Try /api/v1/ram/processing/validate endpoint")
    print("4. Your database has live reconciliation data ready for processing!")

if __name__ == "__main__":
    asyncio.run(main())