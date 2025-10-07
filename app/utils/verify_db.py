import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine

# Import all models to ensure proper relationship setup
import app.tenant.models.firm
import app.tenant.models.user
import app.cdm.models.entity
import app.cdm.models.master
import app.cdm.models.transaction
import app.cdm.models.external
import app.cdm.models.reconciliation

from app.tenant.models.user import User
from app.tenant.models.firm import CAFirm
from app.cdm.models.entity import Entity

def verify_data():
    session = Session(bind=engine)
    try:
        # Count users
        user_count = session.query(User).count()
        firm_count = session.query(CAFirm).count()
        entity_count = session.query(Entity).count()
        
        print(f"=== Database Verification ===")
        print(f"Users: {user_count}")
        print(f"CA Firms: {firm_count}")
        print(f"Entities/Companies: {entity_count}")
        
        # Show user details
        users = session.query(User).all()
        print("\n=== User Details ===")
        for user in users:
            firm_name = user.firm.firm_name if user.firm else "No Firm (Platform Admin)"
            print(f"- {user.name} ({user.email}) - Role: {user.role.value} - Firm: {firm_name}")
        
        print("\n=== Verification Complete ===")
        
    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_data()