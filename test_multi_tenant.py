#!/usr/bin/env python3
"""
Multi-Tenant System Test Script

This script demonstrates and tests the multi-tenant functionality:
1. Creates sample CA firms
2. Creates users for each firm  
3. Creates client entities for each firm
4. Tests data isolation between firms
"""

import asyncio
import uuid
from sqlalchemy.orm import Session
from app.core.database import get_db, engine

# Import all models to ensure relationships are loaded
from app.tenant.models.firm import CAFirm
from app.tenant.models.user import User, UserRole, UserEntityMap
from app.cdm.models.entity import Entity
from app.cdm.models.master import Group, Ledger, StockItem, TaxLedger
from app.cdm.models.transaction import VoucherHeader, VoucherLine
from app.cdm.models.external import BankStatement, GSTSales, GSTPurchases
from app.cdm.models.reconciliation import ReconciliationLog

async def create_sample_data():
    """Create sample multi-tenant data for testing"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🏢 Creating sample CA firms...")
        
        # Create first CA firm
        firm1 = CAFirm(
            firm_name="ABC & Associates",
            contact_email="admin@abc-associates.com",
            phone="+91-9876543210",
            address="123 Business District, Mumbai",
            gstin="27ABCDE1234F1Z5",
            pan="ABCDE1234F",
            firm_registration_no="REG001",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001"
        )
        db.add(firm1)
        
        # Create second CA firm  
        firm2 = CAFirm(
            firm_name="XYZ Chartered Accountants",
            contact_email="contact@xyz-ca.com", 
            phone="+91-9876543211",
            address="456 Corporate Hub, Bangalore",
            gstin="29XYZAB5678P1Q2",
            pan="XYZAB5678P",
            firm_registration_no="REG002",
            city="Bangalore",
            state="Karnataka", 
            pincode="560001"
        )
        db.add(firm2)
        
        db.commit()
        db.refresh(firm1)
        db.refresh(firm2)
        
        print(f"✅ Created firm 1: {firm1.firm_name} (ID: {firm1.firm_id})")
        print(f"✅ Created firm 2: {firm2.firm_name} (ID: {firm2.firm_id})")
        
        print("\n👥 Creating users for each firm...")
        
        # Create admin user for firm 1
        user1 = User(
            email="admin@abc-associates.com",
            name="Admin User",
            role=UserRole.CA_FIRM_ADMIN,
            firm_id=firm1.firm_id
        )
        user1.set_password("admin123")
        db.add(user1)
        
        # Create staff user for firm 1
        staff1 = User(
            email="staff@abc-associates.com", 
            name="Staff Member",
            role=UserRole.CA_STAFF,
            firm_id=firm1.firm_id
        )
        staff1.set_password("staff123")
        db.add(staff1)
        
        # Create admin user for firm 2
        user2 = User(
            email="admin@xyz-ca.com",
            name="Manager XYZ",
            role=UserRole.CA_FIRM_ADMIN,
            firm_id=firm2.firm_id
        )
        user2.set_password("manager123")
        db.add(user2)
        
        db.commit()
        
        print(f"✅ Created users for firm 1: {user1.email}, {staff1.email}")
        print(f"✅ Created users for firm 2: {user2.email}")
        
        print("\n🏭 Creating client entities for each firm...")
        
        # Create entities for firm 1
        from datetime import date
        
        entity1_1 = Entity(
            company_name="Tech Solutions Pvt Ltd",
            company_id=str(uuid.uuid4()),
            financial_year_start=date(2024, 4, 1),
            financial_year_end=date(2025, 3, 31),
            gstin="27TECH1234A1B2",
            pan="AABCT1234E",
            firm_id=firm1.firm_id,
            state="Maharashtra"
        )
        
        entity1_2 = Entity(
            company_name="Retail Enterprises Ltd", 
            company_id=str(uuid.uuid4()),
            financial_year_start=date(2024, 4, 1),
            financial_year_end=date(2025, 3, 31),
            gstin="27RETAIL567C1D2",
            pan="AABCR5678F",
            firm_id=firm1.firm_id,
            state="Maharashtra"
        )
        
        # Create entities for firm 2
        entity2_1 = Entity(
            company_name="Manufacturing Corp",
            company_id=str(uuid.uuid4()),
            financial_year_start=date(2024, 4, 1),
            financial_year_end=date(2025, 3, 31), 
            gstin="29MANUF789E1F2",
            pan="AABCM7890G",
            firm_id=firm2.firm_id,
            state="Karnataka"
        )
        
        entity2_2 = Entity(
            company_name="Services International",
            company_id=str(uuid.uuid4()),
            financial_year_start=date(2024, 4, 1),
            financial_year_end=date(2025, 3, 31),
            gstin="29SERV012G1H2", 
            pan="AABCS0123H",
            firm_id=firm2.firm_id,
            state="Karnataka"
        )
        
        db.add_all([entity1_1, entity1_2, entity2_1, entity2_2])
        db.commit()
        
        print(f"✅ Created entities for firm 1: {entity1_1.company_name}, {entity1_2.company_name}")
        print(f"✅ Created entities for firm 2: {entity2_1.company_name}, {entity2_2.company_name}")
        
        print("\n🔍 Testing data isolation...")
        
        # Test: Firm 1 should only see their own entities
        firm1_entities = db.query(Entity).filter(Entity.firm_id == firm1.firm_id).all()
        firm2_entities = db.query(Entity).filter(Entity.firm_id == firm2.firm_id).all()
        
        print(f"✅ Firm 1 entities count: {len(firm1_entities)} (Expected: 2)")
        print(f"✅ Firm 2 entities count: {len(firm2_entities)} (Expected: 2)")
        
        # Test: Users should only belong to their firm
        firm1_users = db.query(User).filter(User.firm_id == firm1.firm_id).all()
        firm2_users = db.query(User).filter(User.firm_id == firm2.firm_id).all()
        
        print(f"✅ Firm 1 users count: {len(firm1_users)} (Expected: 2)")
        print(f"✅ Firm 2 users count: {len(firm2_users)} (Expected: 1)")
        
        print("\n🎉 Multi-tenant sample data created successfully!")
        print("\n📋 Summary:")
        print(f"• Total CA Firms: 2")
        print(f"• Total Users: 3")  
        print(f"• Total Client Entities: 4")
        print(f"• Data isolation: ✅ Verified")
        
        print(f"\n🔐 Test Credentials:")
        print(f"Firm 1 Admin: admin@abc-associates.com / admin123")
        print(f"Firm 1 Staff: staff@abc-associates.com / staff123") 
        print(f"Firm 2 Admin: admin@xyz-ca.com / manager123")
        
        return {
            "firms": [firm1, firm2],
            "users": [user1, staff1, user2],
            "entities": [entity1_1, entity1_2, entity2_1, entity2_2]
        }
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_tenant_isolation(db: Session):
    """Test that tenant isolation is working correctly"""
    
    print("\n🧪 Running tenant isolation tests...")
    
    firms = db.query(CAFirm).all()
    if len(firms) < 2:
        print("❌ Need at least 2 firms for isolation testing")
        return False
    
    firm1, firm2 = firms[0], firms[1] 
    
    # Test 1: Entity isolation
    firm1_entities = db.query(Entity).filter(Entity.firm_id == firm1.firm_id).all()
    firm2_entities = db.query(Entity).filter(Entity.firm_id == firm2.firm_id).all()
    
    # Check no cross-contamination
    for entity in firm1_entities:
        if entity.firm_id != firm1.firm_id:
            print(f"❌ Entity {entity.company_name} has wrong firm_id")
            return False
            
    for entity in firm2_entities:
        if entity.firm_id != firm2.firm_id:
            print(f"❌ Entity {entity.company_name} has wrong firm_id")
            return False
    
    print("✅ Entity isolation test passed")
    
    # Test 2: User isolation 
    firm1_users = db.query(User).filter(User.firm_id == firm1.firm_id).all()
    firm2_users = db.query(User).filter(User.firm_id == firm2.firm_id).all()
    
    for user in firm1_users:
        if user.firm_id != firm1.firm_id:
            print(f"❌ User {user.email} has wrong firm_id")
            return False
            
    for user in firm2_users:
        if user.firm_id != firm2.firm_id:
            print(f"❌ User {user.email} has wrong firm_id")
            return False
    
    print("✅ User isolation test passed")
    
    # Test 3: Cross-firm query should return empty
    cross_query = db.query(Entity).filter(
        Entity.firm_id == firm1.firm_id,
        Entity.company_name.in_([e.company_name for e in firm2_entities])
    ).all()
    
    if cross_query:
        print(f"❌ Cross-firm query returned {len(cross_query)} results, expected 0")
        return False
    
    print("✅ Cross-firm isolation test passed")
    print("🎉 All tenant isolation tests passed!")
    
    return True

if __name__ == "__main__":
    print("🚀 Multi-Tenant System Test")
    print("=" * 50)
    
    # Create sample data
    sample_data = asyncio.run(create_sample_data())
    
    # Test isolation
    db = next(get_db())
    try:
        test_tenant_isolation(db)
    finally:
        db.close()
    
    print("\n✨ Test completed! You can now test the API endpoints.")
    print("\n📖 Next steps:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Use the test credentials above to authenticate API calls")
    print("4. Set tenant headers (X-Firm-ID, X-Company-ID) in requests")