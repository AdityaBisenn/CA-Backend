import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.tenant.models.firm import CAFirm
from app.tenant.models.user import User, UserRole, UserEntityMap
from app.cdm.models.entity import Entity, GSTType
from app.cdm.models.master import Group, GroupNature, Ledger, StockItem, TaxLedger
from app.cdm.models.transaction import VoucherHeader, VoucherStatus, VoucherLine
from app.cdm.models.external import BankStatement, GSTSales, GSTPurchases
from app.cdm.models.reconciliation import ReconciliationLog, IngestionJob, AuditEvent, AIFeedback
import datetime

# Import all models to ensure proper relationship setup
import app.tenant.models.firm
import app.tenant.models.user
import app.cdm.models.entity
import app.cdm.models.master
import app.cdm.models.transaction
import app.cdm.models.external
import app.cdm.models.reconciliation

# Create all tables if not exist
Base.metadata.create_all(bind=engine)

def populate_db():
    session = Session(bind=engine)
    try:
        # Create Super Admin (Trenor Platform Admin)
        super_admin = User(
            firm_id=None,  # No firm association for platform admin
            name="Super Admin",
            email="admin@trenor.ai",
            role=UserRole.TRENOR_ADMIN,
            is_active=True
        )
        super_admin.set_password("admin123")
        session.add(super_admin)
        session.flush()
        print(f"Created Super Admin: {super_admin.email}")

        # Create CA Firm
        firm = CAFirm(
            firm_name="Test CA Firm",
            contact_email="firm@example.com",
            phone="1234567890",
            address="123 Main St, City",
            gstin="22AAAAA0000A1Z5",
            pan="AAAAA0000A",
            firm_registration_no="CA12345",
            city="Metropolis",
            state="State",
            pincode="123456",
            subscription_tier="premium",
            is_active=True
        )
        session.add(firm)
        session.flush()  # Get firm_id
        print(f"Created CA Firm: {firm.firm_name}")

        # Create CA Firm Admin User
        ca_admin = User(
            firm_id=firm.firm_id,
            name="CA Firm Admin",
            email="admin@testcafirm.com",
            role=UserRole.CA_FIRM_ADMIN,
            is_active=True
        )
        ca_admin.set_password("cafirm123")
        session.add(ca_admin)
        session.flush()
        print(f"Created CA Firm Admin: {ca_admin.email}")

        # Create CA Staff User
        ca_staff = User(
            firm_id=firm.firm_id,
            name="CA Staff Member",
            email="staff@testcafirm.com",
            role=UserRole.CA_STAFF,
            is_active=True
        )
        ca_staff.set_password("staff123")
        session.add(ca_staff)
        session.flush()
        print(f"Created CA Staff: {ca_staff.email}")

        # Create Entity (Company)
        entity = Entity(
            firm_id=firm.firm_id,
            company_name="Test Company Pvt Ltd",
            financial_year_start=datetime.date(2024, 4, 1),
            financial_year_end=datetime.date(2025, 3, 31),
            books_begin_from=datetime.date(2024, 4, 1),
            gst_registration_type=GSTType.REGULAR,
            state="State",
            gstin="22BBBBB1111B2Z6",
            currency="INR",
            pan="BBBBB1111B",
            cin="U12345MH2024PTC123456",
            registration_type="Private Limited",
            tan="MUMT12345B",
            ifsc_default_bank="SBIN0001234",
            is_active=True
        )
        session.add(entity)
        session.flush()  # Get company_id

        # Map CA admin to entity
        ca_admin_entity_map = UserEntityMap(
            user_id=ca_admin.user_id,
            company_id=entity.company_id,
            permissions="read,write,admin"
        )
        session.add(ca_admin_entity_map)

        # Map CA staff to entity
        ca_staff_entity_map = UserEntityMap(
            user_id=ca_staff.user_id,
            company_id=entity.company_id,
            permissions="read,write"
        )
        session.add(ca_staff_entity_map)

        # Create Groups
        asset_group = Group(
            company_id=entity.company_id,
            group_name="Assets",
            nature=GroupNature.ASSET,
            is_primary=True,
            is_active=True
        )
        session.add(asset_group)
        session.flush()

        liability_group = Group(
            company_id=entity.company_id,
            group_name="Liabilities",
            nature=GroupNature.LIABILITY,
            is_primary=True,
            is_active=True
        )
        session.add(liability_group)
        session.flush()

        # Create Ledgers
        cash_ledger = Ledger(
            company_id=entity.company_id,
            ledger_name="Cash",
            group_id=asset_group.group_id,
            opening_balance=100000.00,
            dr_cr="Dr",
            is_active=True
        )
        session.add(cash_ledger)
        session.flush()

        bank_ledger = Ledger(
            company_id=entity.company_id,
            ledger_name="Bank",
            group_id=asset_group.group_id,
            opening_balance=50000.00,
            dr_cr="Dr",
            is_active=True
        )
        session.add(bank_ledger)
        session.flush()

        loan_ledger = Ledger(
            company_id=entity.company_id,
            ledger_name="Loan Account",
            group_id=liability_group.group_id,
            opening_balance=20000.00,
            dr_cr="Cr",
            is_active=True
        )
        session.add(loan_ledger)
        session.flush()

        # Create Voucher (Transaction)
        voucher = VoucherHeader(
            company_id=entity.company_id,
            voucher_type="Payment",
            voucher_date=datetime.date(2024, 4, 10),
            voucher_number="PAY-001",
            party_ledger_id=bank_ledger.ledger_id,
            narration="Payment to Loan Account",
            total_amount=20000.00,
            status=VoucherStatus.POSTED,
            is_gst_applicable=False
        )
        session.add(voucher)
        session.flush()

        # Voucher Lines
        line1 = VoucherLine(
            voucher_id=voucher.voucher_id,
            company_id=entity.company_id,
            ledger_id=bank_ledger.ledger_id,
            debit=0.00,
            credit=20000.00,
            narration="Bank payment"
        )
        session.add(line1)

        line2 = VoucherLine(
            voucher_id=voucher.voucher_id,
            company_id=entity.company_id,
            ledger_id=loan_ledger.ledger_id,
            debit=20000.00,
            credit=0.00,
            narration="Loan account receipt"
        )
        session.add(line2)

        session.commit()
        print("\n=== Database populated successfully with test data ===")
        print(f"Super Admin: admin@trenor.ai (password: admin123)")
        print(f"CA Firm Admin: admin@testcafirm.com (password: cafirm123)")
        print(f"CA Staff: staff@testcafirm.com (password: staff123)")
        print(f"Company: {entity.company_name}")
        print(f"Firm: {firm.firm_name}")
        print("Sample vouchers and ledgers created.")
    except Exception as e:
        session.rollback()
        print(f"Error populating database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    populate_db()
