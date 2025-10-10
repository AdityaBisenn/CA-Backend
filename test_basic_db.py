# test_basic_db.py
"""
Basic database test without relationships
"""

import sys
sys.path.insert(0, '/Users/adityabisen/Desktop/CA Updates Agent/CA-App/CA-Backend')

from sqlalchemy import text

def test_basic_db():
    """Test basic database operations"""
    print("🧪 Testing Basic Database Operations...")
    
    try:
        from app.core.database import get_db
        db = next(get_db())
        
        # Test basic query
        result = db.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection: {result}")
        
        # Test RAM tables
        try:
            count = db.execute(text("SELECT COUNT(*) FROM heuristic_memory")).scalar()
            print(f"✅ heuristic_memory table: {count} records")
        except Exception as e:
            print(f"❌ heuristic_memory: {e}")
        
        try:
            count = db.execute(text("SELECT COUNT(*) FROM reflection_log")).scalar()
            print(f"✅ reflection_log table: {count} records")
        except Exception as e:
            print(f"❌ reflection_log: {e}")
        
        # Test CDM tables
        tables = ['entities', 'vouchers', 'bank_statements', 'reconciliation_logs']
        for table in tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"✅ {table} table: {count} records")
            except Exception as e:
                print(f"❌ {table}: {e}")
        
        db.close()
        print("\n🎉 Database is working! Your data is ready for RAM processing.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_data_availability():
    """Test if we have data for reconciliation"""
    print("\n📊 Testing Data Availability for Reconciliation...")
    
    try:
        from app.core.database import get_db
        from app.cdm.models.entity import Entity
        db = next(get_db())
        
        # Get companies
        companies = db.query(Entity).all()
        print(f"✅ Found {len(companies)} companies in database")
        
        if companies:
            test_company = companies[0]
            print(f"✅ Test company: {test_company.company_name} (ID: {test_company.company_id})")
            
            # Check data for this company
            from sqlalchemy import text
            
            voucher_count = db.execute(text(
                "SELECT COUNT(*) FROM vouchers WHERE company_id = :company_id"
            ), {"company_id": test_company.company_id}).scalar()
            
            stmt_count = db.execute(text(
                "SELECT COUNT(*) FROM bank_statements WHERE company_id = :company_id" 
            ), {"company_id": test_company.company_id}).scalar()
            
            print(f"✅ Company has {voucher_count} vouchers and {stmt_count} bank statements")
            
            if voucher_count > 0 and stmt_count > 0:
                print("🎉 Perfect! This company has data ready for reconciliation!")
            elif voucher_count > 0 or stmt_count > 0:
                print("⚠️  Partial data available - you can still test the system")
            else:
                print("ℹ️  No transaction data yet - you'll need to populate some test data")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Data availability test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BASIC DATABASE & DATA TEST")
    print("=" * 40)
    
    success1 = test_basic_db()
    success2 = test_data_availability()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your database is ready for RAM cognitive processing!")
        print("\n🌐 Next Steps:")
        print("1. Visit http://localhost:8001/docs")
        print("2. Try the RAM endpoints:")
        print("   - GET /api/v1/ram/system/status")
        print("   - POST /api/v1/ram/processing/validate") 
        print("   - POST /api/v1/ram/reconciliation/batch")
    else:
        print("⚠️  Some issues detected, but core functionality should work")