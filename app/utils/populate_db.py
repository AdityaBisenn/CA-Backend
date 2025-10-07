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
import random
import hashlib
from decimal import Decimal
from faker import Faker

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

def populate_db_with_test_data(session: Session, entity: Entity, bank_ledger: Ledger, 
                               sales_group: Group, purchase_group: Group):
    """
    Generate realistic reconciliation test data with statistical accuracy.
    
    🎯 Goal: Create data patterns for reconciliation testing:
    ✅ 80% perfectly reconcilable (exact matches)
    ⚠️ 15% near matches (date/amount off by small delta)
    ❌ 5% unreconciled (missing invoice or unmatched entry)
    """
    
    # Initialize Faker for Indian locale
    fake = Faker('en_IN')
    
    # Configuration
    num_sales = 150
    num_purchases = 120
    num_bank_txns_base = 280  # Will be adjusted based on reconciliation logic
    
    # Generate realistic party names (customers and suppliers)
    customers = [fake.company() for _ in range(15)]
    suppliers = [fake.company() for _ in range(12)]
    
    # Financial year start date
    fy_start = datetime.date(2024, 4, 1)
    
    print("🧮 Generating realistic reconciliation test data...")
    
    # ===============================
    # 1. GENERATE SALES VOUCHERS
    # ===============================
    print("📊 Creating sales vouchers...")
    sales_vouchers = []
    
    for i in range(num_sales):
        customer = random.choice(customers)
        
        # Normal distribution around ₹10,000 ± ₹3,000
        base_amount = max(1000, random.normalvariate(10000, 3000))
        base_amount = round(base_amount, 2)
        
        # Calculate GST (18%)
        gst_rate = 0.18
        taxable_value = round(base_amount / (1 + gst_rate), 2)
        gst_amount = round(base_amount - taxable_value, 2)
        total_amount = taxable_value + gst_amount
        
        # Random date within financial year
        random_days = random.randint(0, 300)  # 10 months of data
        voucher_date = fy_start + datetime.timedelta(days=random_days)
        
        # Create sales voucher
        voucher = VoucherHeader(
            company_id=entity.company_id,
            voucher_type="Sales",
            voucher_date=voucher_date,
            voucher_number=f"INV-{i+1:04d}",
            party_ledger_id=sales_group.group_id,
            narration=f"Sale to {customer}",
            total_amount=total_amount,
            status=VoucherStatus.POSTED,
            is_gst_applicable=True
        )
        session.add(voucher)
        
        sales_vouchers.append({
            'voucher': voucher,
            'customer': customer,
            'total_amount': total_amount,
            'taxable_value': taxable_value,
            'gst_amount': gst_amount,
            'date': voucher_date
        })
    
    session.flush()  # Get voucher IDs
    
    # ===============================
    # 2. GENERATE PURCHASE VOUCHERS
    # ===============================
    print("📈 Creating purchase vouchers...")
    purchase_vouchers = []
    
    for i in range(num_purchases):
        supplier = random.choice(suppliers)
        
        # Normal distribution around ₹8,000 ± ₹2,500
        base_amount = max(500, random.normalvariate(8000, 2500))
        base_amount = round(base_amount, 2)
        
        # Calculate GST (18%)
        taxable_value = round(base_amount / (1 + gst_rate), 2)
        gst_amount = round(base_amount - taxable_value, 2)
        total_amount = taxable_value + gst_amount
        
        # Random date within financial year
        random_days = random.randint(0, 300)
        voucher_date = fy_start + datetime.timedelta(days=random_days)
        
        # Create purchase voucher
        voucher = VoucherHeader(
            company_id=entity.company_id,
            voucher_type="Purchase",
            voucher_date=voucher_date,
            voucher_number=f"PUR-{i+1:04d}",
            party_ledger_id=purchase_group.group_id,
            narration=f"Purchase from {supplier}",
            total_amount=total_amount,
            status=VoucherStatus.POSTED,
            is_gst_applicable=True
        )
        session.add(voucher)
        
        purchase_vouchers.append({
            'voucher': voucher,
            'supplier': supplier,
            'total_amount': total_amount,
            'taxable_value': taxable_value,
            'gst_amount': gst_amount,
            'date': voucher_date
        })
    
    session.flush()  # Get voucher IDs
    
    # ===============================
    # 3. GENERATE BANK STATEMENTS WITH RECONCILIATION LOGIC
    # ===============================
    print("🏦 Creating bank statements with reconciliation patterns...")
    
    all_vouchers = sales_vouchers + purchase_vouchers
    bank_transactions = []
    running_balance = Decimal('500000.00')  # Starting bank balance
    
    # Shuffle vouchers for realistic banking sequence
    voucher_pool = all_vouchers.copy()
    random.shuffle(voucher_pool)
    
    # Calculate how many vouchers to process for different reconciliation types
    total_vouchers = len(voucher_pool)
    perfect_match_count = int(total_vouchers * 0.80)  # 80%
    near_match_count = int(total_vouchers * 0.15)     # 15%
    unmatched_count = total_vouchers - perfect_match_count - near_match_count  # 5%
    
    voucher_index = 0
    
    # 80% Perfect matches
    for i in range(perfect_match_count):
        voucher_data = voucher_pool[voucher_index]
        voucher = voucher_data['voucher']
        amount = voucher_data['total_amount']
        
        # Date variance: ±0-2 days from invoice date
        bank_date = voucher_data['date'] + datetime.timedelta(days=random.randint(-2, 2))
        
        # Determine Dr/Cr based on voucher type
        if voucher.voucher_type == "Sales":
            dr_cr = "Cr"
            running_balance += Decimal(str(amount))
            narration = f"Collection from {voucher_data['customer']} - {voucher.voucher_number}"
        else:
            dr_cr = "Dr"
            running_balance -= Decimal(str(amount))
            narration = f"Payment to {voucher_data['supplier']} - {voucher.voucher_number}"
        
        # Create bank transaction
        bank_txn = BankStatement(
            company_id=entity.company_id,
            bank_id=bank_ledger.ledger_id,
            txn_date=bank_date,
            narration=narration,
            amount=Decimal(str(abs(amount))),
            dr_cr=dr_cr,
            balance_after_txn=running_balance,
            linked_voucher_id=voucher.voucher_id,  # Perfect link
            reconciliation_status="Matched",
            txn_hash=hashlib.sha256(f"{voucher.voucher_number}{amount}{bank_date}".encode()).hexdigest()
        )
        session.add(bank_txn)
        bank_transactions.append(bank_txn)
        voucher_index += 1
    
    # 15% Near matches (amount/date variance)
    for i in range(near_match_count):
        voucher_data = voucher_pool[voucher_index]
        voucher = voucher_data['voucher']
        base_amount = voucher_data['total_amount']
        
        # Add noise to amount (±₹1-₹10 for round-offs, bank charges)
        amount_variance = random.uniform(-10, 10)
        amount = round(base_amount + amount_variance, 2)
        
        # Date variance: ±3-7 days from invoice date
        date_variance = random.randint(-7, 7)
        if abs(date_variance) <= 2:  # Avoid perfect date match
            date_variance = random.choice([-5, -4, -3, 3, 4, 5])
        bank_date = voucher_data['date'] + datetime.timedelta(days=date_variance)
        
        # Determine Dr/Cr
        if voucher.voucher_type == "Sales":
            dr_cr = "Cr"
            running_balance += Decimal(str(amount))
            narration = f"Collection {voucher_data['customer']} ref {voucher.voucher_number[:6]}"
        else:
            dr_cr = "Dr"
            running_balance -= Decimal(str(amount))
            narration = f"Payment {voucher_data['supplier']} ref {voucher.voucher_number[:6]}"
        
        bank_txn = BankStatement(
            company_id=entity.company_id,
            bank_id=bank_ledger.ledger_id,
            txn_date=bank_date,
            narration=narration,
            amount=Decimal(str(abs(amount))),
            dr_cr=dr_cr,
            balance_after_txn=running_balance,
            linked_voucher_id=None,  # No direct link - needs reconciliation
            reconciliation_status="Near_Match",
            txn_hash=hashlib.sha256(f"near{voucher.voucher_number}{amount}{bank_date}".encode()).hexdigest()
        )
        session.add(bank_txn)
        bank_transactions.append(bank_txn)
        voucher_index += 1
    
    # 5% Completely unmatched entries
    for i in range(unmatched_count):
        # Create orphaned bank entries
        amount = round(random.uniform(1000, 25000), 2)
        random_date = fy_start + datetime.timedelta(days=random.randint(0, 300))
        
        dr_cr = random.choice(["Dr", "Cr"])
        if dr_cr == "Cr":
            running_balance += Decimal(str(amount))
            narration = f"Misc Receipt - {fake.company()}"
        else:
            running_balance -= Decimal(str(amount))
            narration = f"Bank Charges / {fake.company()}"
        
        bank_txn = BankStatement(
            company_id=entity.company_id,
            bank_id=bank_ledger.ledger_id,
            txn_date=random_date,
            narration=narration,
            amount=Decimal(str(amount)),
            dr_cr=dr_cr,
            balance_after_txn=running_balance,
            linked_voucher_id=None,
            reconciliation_status="Unmatched",
            txn_hash=hashlib.sha256(f"unmatched{i}{amount}{random_date}".encode()).hexdigest()
        )
        session.add(bank_txn)
        bank_transactions.append(bank_txn)
        voucher_index += 1
    
    # Add some additional random bank transactions (internal transfers, etc.)
    for i in range(20):
        amount = round(random.uniform(500, 5000), 2)
        random_date = fy_start + datetime.timedelta(days=random.randint(0, 300))
        
        dr_cr = random.choice(["Dr", "Cr"])
        if dr_cr == "Cr":
            running_balance += Decimal(str(amount))
            narration = random.choice([
                f"Interest Credit",
                f"Refund from {fake.company()}",
                f"Internal Transfer Credit"
            ])
        else:
            running_balance -= Decimal(str(amount))
            narration = random.choice([
                f"ATM Withdrawal",
                f"Bank Charges - Service Fee",
                f"Internal Transfer Debit"
            ])
        
        bank_txn = BankStatement(
            company_id=entity.company_id,
            bank_id=bank_ledger.ledger_id,
            txn_date=random_date,
            narration=narration,
            amount=Decimal(str(amount)),
            dr_cr=dr_cr,
            balance_after_txn=running_balance,
            reconciliation_status="Unmatched",
            txn_hash=hashlib.sha256(f"misc{i}{amount}{random_date}".encode()).hexdigest()
        )
        session.add(bank_txn)
        bank_transactions.append(bank_txn)
    
    session.flush()
    
    # ===============================
    # 4. GENERATE GST SALES DATA
    # ===============================
    print("📋 Creating GST sales records...")
    
    for voucher_data in sales_vouchers:
        voucher = voucher_data['voucher']
        
        # 95% of vouchers have matching GST entries
        if random.random() < 0.95:
            # Small variance in GST data (±₹0-₹3 for rounding differences)
            gst_variance = random.uniform(-3, 3)
            gst_total = voucher_data['total_amount'] + gst_variance
            gst_taxable = voucher_data['taxable_value'] + (gst_variance * 0.85)
            gst_tax = gst_total - gst_taxable
            
            gst_sales = GSTSales(
                company_id=entity.company_id,
                gstin_customer=fake.random_int(min=10000000000000000, max=99999999999999999),  # Fake GSTIN
                invoice_number=voucher.voucher_number,
                invoice_date=voucher_data['date'],
                taxable_value=Decimal(str(round(gst_taxable, 2))),
                tax_amount=Decimal(str(round(gst_tax, 2))),
                total_value=Decimal(str(round(gst_total, 2))),
                linked_voucher_id=voucher.voucher_id,
                reconciliation_status="Matched" if abs(gst_variance) < 1 else "Near_Match",
                invoice_hash=hashlib.sha256(f"{voucher.voucher_number}{gst_total}".encode()).hexdigest()
            )
            session.add(gst_sales)
    
    # ===============================
    # 5. GENERATE GST PURCHASE DATA
    # ===============================
    print("📝 Creating GST purchase records...")
    
    for voucher_data in purchase_vouchers:
        voucher = voucher_data['voucher']
        
        # 93% of vouchers have matching GST entries (slightly less than sales)
        if random.random() < 0.93:
            # Small variance in GST data
            gst_variance = random.uniform(-2, 2)
            gst_total = voucher_data['total_amount'] + gst_variance
            gst_taxable = voucher_data['taxable_value'] + (gst_variance * 0.85)
            gst_tax = gst_total - gst_taxable
            
            gst_purchase = GSTPurchases(
                company_id=entity.company_id,
                supplier_gstin=f"{random.randint(10,35)}{fake.bothify('?????#####?#?#')}",
                invoice_number=voucher.voucher_number,
                invoice_date=voucher_data['date'],
                taxable_value=Decimal(str(round(gst_taxable, 2))),
                igst_amount=Decimal(str(round(gst_tax, 2))),
                cgst_amount=Decimal('0.00'),
                sgst_amount=Decimal('0.00'),
                linked_voucher_id=voucher.voucher_id,
                reconciliation_status="Matched" if abs(gst_variance) < 1 else "Near_Match",
                invoice_hash=hashlib.sha256(f"{voucher.voucher_number}{gst_total}supplier".encode()).hexdigest()
            )
            session.add(gst_purchase)
    
    # ===============================
    # 6. ADD SOME DUPLICATE ENTRIES (1-2%)
    # ===============================
    print("🔄 Adding duplicate entries...")
    
    # Create a few duplicate vouchers
    duplicate_sales = random.sample(sales_vouchers, min(3, len(sales_vouchers)))
    for dup_data in duplicate_sales:
        original_voucher = dup_data['voucher']
        
        dup_voucher = VoucherHeader(
            company_id=entity.company_id,
            voucher_type="Sales",
            voucher_date=original_voucher.voucher_date,
            voucher_number=f"{original_voucher.voucher_number}-DUP",
            party_ledger_id=original_voucher.party_ledger_id,
            narration=f"DUPLICATE: {original_voucher.narration}",
            total_amount=original_voucher.total_amount,
            status=VoucherStatus.POSTED,
            is_gst_applicable=True
        )
        session.add(dup_voucher)
    
    session.commit()
    
    # ===============================
    # 7. SUMMARY STATISTICS
    # ===============================
    total_vouchers = len(sales_vouchers) + len(purchase_vouchers)
    total_bank_txns = len(bank_transactions)
    
    print(f"\n🎉 RECONCILIATION TEST DATA GENERATED SUCCESSFULLY!")
    print(f"=" * 60)
    print(f"📊 SUMMARY STATISTICS:")
    print(f"   • Sales Vouchers: {len(sales_vouchers)}")
    print(f"   • Purchase Vouchers: {len(purchase_vouchers)}")
    print(f"   • Total Vouchers: {total_vouchers}")
    print(f"   • Bank Transactions: {total_bank_txns}")
    print(f"   • GST Sales Records: ~{int(len(sales_vouchers) * 0.95)}")
    print(f"   • GST Purchase Records: ~{int(len(purchase_vouchers) * 0.93)}")
    print(f"\n🎯 RECONCILIATION PATTERNS:")
    print(f"   ✅ Perfect Matches: {perfect_match_count} ({perfect_match_count/total_vouchers*100:.1f}%)")
    print(f"   ⚠️  Near Matches: {near_match_count} ({near_match_count/total_vouchers*100:.1f}%)")
    print(f"   ❌ Unmatched: {unmatched_count} ({unmatched_count/total_vouchers*100:.1f}%)")
    print(f"   🔄 Duplicates: 3-5 entries")
    print(f"   💰 Amount Range: ₹500 - ₹25,000")
    print(f"   📅 Date Range: Apr 2024 - Jan 2025")
    print(f"=" * 60)

def populate_db():
    session = Session(bind=engine)
    try:
        # Check if data already exists
        existing_admin = session.query(User).filter_by(email="admin@trenor.ai").first()
        if existing_admin:
            print("📋 Database already contains basic user data.")
            print("🧹 Cleaning up existing test data to avoid duplicates...")
            
            # Clean up old test data but keep users and firms
            session.query(BankStatement).delete()
            session.query(GSTSales).delete()
            session.query(GSTPurchases).delete()
            session.query(VoucherLine).delete()
            session.query(VoucherHeader).delete()
            session.commit()
            
            # Use existing entities
            firm = session.query(CAFirm).first()
            entity = session.query(Entity).first()
            bank_ledger = session.query(Ledger).filter_by(ledger_name="Bank").first()
            
            print(f"Using existing firm: {firm.firm_name}")
            print(f"Using existing entity: {entity.company_name}")
            
        else:
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
            
            # Create all the original basic data
            firm, entity, bank_ledger = create_basic_data(session)
        
        # ===============================
        # GENERATE COMPREHENSIVE TEST DATA FOR RECONCILIATION
        # ===============================
        print("\n🚀 Starting comprehensive test data generation...")
        
        # Create or get additional groups needed for realistic data
        sales_group = session.query(Group).filter_by(group_name="Sales Accounts").first()
        if not sales_group:
            sales_group = Group(
                company_id=entity.company_id,
                group_name="Sales Accounts",
                nature=GroupNature.INCOME,
                is_primary=False,
                is_active=True
            )
            session.add(sales_group)
        
        purchase_group = session.query(Group).filter_by(group_name="Purchase Accounts").first()
        if not purchase_group:
            purchase_group = Group(
                company_id=entity.company_id,
                group_name="Purchase Accounts",
                nature=GroupNature.EXPENSE,
                is_primary=False,
                is_active=True
            )
            session.add(purchase_group)
        session.flush()
        
        # Generate comprehensive test data
        populate_db_with_test_data(session, entity, bank_ledger, sales_group, purchase_group)
        
    except Exception as e:
        session.rollback()
        print(f"Error populating database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def create_basic_data(session: Session):
    """Create the basic firm, users, entity, and ledger data"""
    
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
    print("\n=== Database populated successfully with basic data ===")
    print(f"Super Admin: admin@trenor.ai (password: admin123)")
    print(f"CA Firm Admin: admin@testcafirm.com (password: cafirm123)")
    print(f"CA Staff: staff@testcafirm.com (password: staff123)")
    print(f"Company: {entity.company_name}")
    print(f"Firm: {firm.firm_name}")
    print("Sample vouchers and ledgers created.")
    
    return firm, entity, bank_ledger

if __name__ == "__main__":
    populate_db()

if __name__ == "__main__":
    populate_db()
