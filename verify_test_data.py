#!/usr/bin/env python3
"""
Verification script to check the generated reconciliation test data
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.cdm.models.transaction import VoucherHeader
from app.cdm.models.external import BankStatement, GSTSales, GSTPurchases
from app.cdm.models.entity import Entity

# Import all models to ensure proper relationship setup
import app.tenant.models.firm
import app.tenant.models.user
import app.cdm.models.entity
import app.cdm.models.master
import app.cdm.models.transaction
import app.cdm.models.external
import app.cdm.models.reconciliation

def verify_test_data():
    session = Session(bind=engine)
    try:
        # Get basic counts
        entity = session.query(Entity).first()
        print(f"🏢 Entity: {entity.company_name}")
        print("=" * 60)
        
        # Count vouchers
        sales_count = session.query(VoucherHeader).filter_by(voucher_type="Sales").count()
        purchase_count = session.query(VoucherHeader).filter_by(voucher_type="Purchase").count()
        total_vouchers = sales_count + purchase_count
        
        print(f"📄 VOUCHERS:")
        print(f"   • Sales: {sales_count}")
        print(f"   • Purchases: {purchase_count}")
        print(f"   • Total: {total_vouchers}")
        
        # Count bank statements by reconciliation status
        bank_total = session.query(BankStatement).count()
        bank_matched = session.query(BankStatement).filter_by(reconciliation_status="Matched").count()
        bank_near = session.query(BankStatement).filter_by(reconciliation_status="Near_Match").count()
        bank_unmatched = session.query(BankStatement).filter_by(reconciliation_status="Unmatched").count()
        
        print(f"\n🏦 BANK STATEMENTS:")
        print(f"   • Total: {bank_total}")
        print(f"   • Matched: {bank_matched} ({bank_matched/bank_total*100:.1f}%)")
        print(f"   • Near Match: {bank_near} ({bank_near/bank_total*100:.1f}%)")
        print(f"   • Unmatched: {bank_unmatched} ({bank_unmatched/bank_total*100:.1f}%)")
        
        # Count GST data
        gst_sales_count = session.query(GSTSales).count()
        gst_purchase_count = session.query(GSTPurchases).count()
        
        print(f"\n📋 GST RECORDS:")
        print(f"   • Sales: {gst_sales_count}")
        print(f"   • Purchases: {gst_purchase_count}")
        
        # Sample data analysis
        print(f"\n💡 SAMPLE ANALYSIS:")
        
        # Show some sample sales vouchers
        sample_sales = session.query(VoucherHeader).filter_by(voucher_type="Sales").limit(3).all()
        print(f"   Sample Sales Vouchers:")
        for voucher in sample_sales:
            print(f"     - {voucher.voucher_number}: ₹{voucher.total_amount} ({voucher.voucher_date})")
        
        # Show some sample bank transactions
        sample_bank = session.query(BankStatement).limit(3).all()
        print(f"   Sample Bank Transactions:")
        for txn in sample_bank:
            status_emoji = {"Matched": "✅", "Near_Match": "⚠️", "Unmatched": "❌"}.get(txn.reconciliation_status, "❓")
            print(f"     - {status_emoji} ₹{txn.amount} {txn.dr_cr} ({txn.txn_date}) - {txn.narration[:50]}...")
        
        # Show reconciliation opportunities
        linked_bank_txns = session.query(BankStatement).filter(BankStatement.linked_voucher_id.isnot(None)).count()
        print(f"\n🔗 RECONCILIATION OPPORTUNITIES:")
        print(f"   • Directly linked bank transactions: {linked_bank_txns}")
        print(f"   • Need reconciliation: {bank_total - linked_bank_txns}")
        
        print("\n" + "=" * 60)
        print("✅ Test data verification completed successfully!")
        print("🚀 Your database is ready for reconciliation testing!")
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verify_test_data()