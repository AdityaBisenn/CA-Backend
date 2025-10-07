# Database Population for Frontend Testing

This document explains how to populate the database with test data for frontend development and testing.

## Quick Start

To populate the database with test data, run:

```bash
./populate_test_data.sh
```

Or manually:

```bash
source .venv/bin/activate
python -m app.utils.populate_db
```

## Test User Credentials

After running the population script, you'll have the following test users:

### 1. Super Admin (Platform Admin)
- **Email**: `admin@trenor.ai`
- **Password**: `admin123`
- **Role**: `TRENOR_ADMIN`
- **Description**: Platform-level administrator with full access. Not associated with any CA firm.

### 2. CA Firm Admin
- **Email**: `admin@testcafirm.com`
- **Password**: `cafirm123`
- **Role**: `CA_FIRM_ADMIN`
- **Firm**: Test CA Firm
- **Description**: CA firm owner/partner with full access to firm's entities and users.

### 3. CA Staff Member
- **Email**: `staff@testcafirm.com`
- **Password**: `staff123`
- **Role**: `CA_STAFF`
- **Firm**: Test CA Firm
- **Description**: CA firm staff member with read/write access to assigned entities.

## Sample Data Created

### CA Firm
- **Name**: Test CA Firm
- **GSTIN**: 22AAAAA0000A1Z5
- **Registration**: CA12345
- **Subscription**: Premium

### Company/Entity
- **Name**: Test Company Pvt Ltd
- **GSTIN**: 22BBBBB1111B2Z6
- **PAN**: BBBBB1111B
- **CIN**: U12345MH2024PTC123456
- **Financial Year**: 2024-25 (Apr 1, 2024 to Mar 31, 2025)

### Sample Ledgers
- **Cash**: ₹1,00,000 (Dr opening balance)
- **Bank**: ₹50,000 (Dr opening balance)
- **Loan Account**: ₹20,000 (Cr opening balance)

### Sample Transaction
- **Type**: Payment voucher
- **Number**: PAY-001
- **Date**: April 10, 2024
- **Amount**: ₹20,000
- **Description**: Bank payment to loan account

## Database Verification

To verify the populated data:

```bash
source .venv/bin/activate
python -m app.utils.verify_db
```

## Data Structure

The populated database includes:

1. **Multi-tenant structure**: CA firms can have multiple users and entities
2. **Role-based access**: Different user roles with appropriate permissions
3. **Entity assignments**: Users are mapped to specific entities with permissions
4. **Chart of accounts**: Groups and ledgers for accounting structure
5. **Sample transactions**: Basic vouchers with double-entry bookkeeping

## User Permissions

### User-Entity Mapping
- **CA Admin**: `read,write,admin` permissions on all firm entities
- **CA Staff**: `read,write` permissions on assigned entities
- **Super Admin**: Platform-level access (not entity-specific)

## Authentication Flow Testing

You can test different authentication scenarios:

1. **Platform Admin Login**: Use `admin@trenor.ai` for platform-level features
2. **Firm Admin Login**: Use `admin@testcafirm.com` for firm management features
3. **Staff Login**: Use `staff@testcafirm.com` for day-to-day operations

## API Testing

With this populated data, you can test:

- User authentication and authorization
- Multi-tenant data isolation
- Entity-based data access
- Role-based permissions
- Accounting workflows (vouchers, ledgers, groups)

## Reset Database

To clear all data and start fresh:

```bash
rm agentic_ai_data.db
source .venv/bin/activate
alembic upgrade head
./populate_test_data.sh
```

## Customization

To modify the test data, edit `app/utils/populate_db.py` and change:

- User credentials and roles
- Company information
- Sample transactions
- Opening balances
- Additional ledgers or groups

## Production Notes

⚠️ **Important**: This population script is for development/testing only. Do not run in production environments.