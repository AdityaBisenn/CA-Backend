#!/usr/bin/env python3

"""
Test script to validate the Pydantic v2 compatibility fix
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    """Test that all modules can be imported without errors"""
    
    print("🧪 Testing import compatibility...")
    
    try:
        # Test core modules
        from app.core.init_llm import make_llm
        print("✅ LLM initialization module imported successfully")
        
        # Test AI service
        from app.services.ai_reconciliation import AIReconciliationService
        print("✅ AI reconciliation service imported successfully")
        
        # Test AI routes (this was causing the Pydantic error)
        from app.api.ai_routes import router as ai_router
        print("✅ AI routes imported successfully")
        
        # Test main app
        from app.main import app
        print("✅ FastAPI main app imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_pydantic_models():
    """Test that Pydantic models work correctly"""
    
    print("\n🧪 Testing Pydantic model validation...")
    
    try:
        from app.api.ai_routes import AIFeedbackRequest, ReconciliationRequest
        
        # Test valid feedback request
        feedback_data = {
            "voucher_id": "test-123",
            "original_prediction": {"confidence": 0.95},
            "user_correction": {"status": "matched"},
            "feedback_type": "reconciliation"  # Should match pattern
        }
        
        feedback_request = AIFeedbackRequest(**feedback_data)
        print(f"✅ Valid feedback request created: {feedback_request.feedback_type}")
        
        # Test invalid feedback type (should raise validation error)
        try:
            invalid_feedback = AIFeedbackRequest(
                voucher_id="test-123",
                original_prediction={},
                user_correction={},
                feedback_type="invalid_type"  # Should fail pattern validation
            )
            print("❌ Pattern validation is not working - invalid type accepted")
            return False
        except Exception:
            print("✅ Pattern validation working - invalid type rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 Starting Pydantic v2 compatibility validation...\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test Pydantic models
    models_ok = test_pydantic_models()
    
    print(f"\n📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Models:  {'✅ PASS' if models_ok else '❌ FAIL'}")
    
    if imports_ok and models_ok:
        print(f"\n🎉 All tests passed! The Pydantic v2 compatibility fix is working correctly.")
        return 0
    else:
        print(f"\n💥 Some tests failed. Check the error messages above.")
        return 1

if __name__ == "__main__":
    exit(main())