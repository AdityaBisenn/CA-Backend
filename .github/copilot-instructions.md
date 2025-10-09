# CA Verified AI Layer Backend - AI Coding Agent Instructions

## 🏗️ Architecture Overview

This is a **multi-tenant FastAPI backend** for CA (Chartered Accountant) firms managing multiple client entities with complete data isolation. The system implements a comprehensive **Common Data Model (CDM)** for accounting data with AI-powered reconciliation capabilities.

### Core Architecture Principles
- **Multi-tenant isolation**: Every table includes `company_id`/`firm_id` for data segregation
- **Header-based tenant context**: All API requests require `X-Company-ID` header for tenant identification
- **Financial precision**: Use `Decimal(18,2)` for monetary amounts, `Decimal(15,4)` for quantities
- **UUID primary keys**: All models use string UUIDs for distributed scalability
- **Soft deletion**: Models use `is_active` boolean instead of hard deletes

## 🔑 Critical Development Patterns

### Tenant Context Pattern (MANDATORY)
All CDM routes must use tenant context dependency injection:

```python
from app.core.tenant_context import get_tenant_context, TenantContext

@router.get("/entities")
async def list_entities(
    context: TenantContext = Depends(get_tenant_context),
    db: Session = Depends(get_db)
):
    # Query automatically filtered by context.company_id
    entities = db.query(Entity).filter(Entity.company_id == context.company_id).all()
```

**Never** write direct queries without tenant filtering - use `apply_tenant_filter()` helper.

### Database Model Conventions
- **Primary keys**: `{model}_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))`
- **Monetary fields**: `Decimal(18,2)` with proper imports: `from decimal import Decimal`
- **Timestamps**: `created_at = Column(DateTime(timezone=True), server_default=func.now())`
- **Foreign keys**: Always include tenant isolation fields (`company_id`, `firm_id`)
- **Indexes**: Add composite indexes for `(company_id, date)` patterns

### API Response Pattern
All endpoints return consistent structured responses:

```python
# Use Pydantic schemas from app/cdm/schemas/
from app.cdm.schemas.entity import EntityResponse

@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(entity_data: EntityCreate, ...):
    # Implementation
```

## 🛠️ Essential Commands & Workflows

### Database Operations
```bash
# Create migration
./migrate.sh create "descriptive_migration_name"

# Apply migrations
./migrate.sh upgrade

# Rollback migrations  
./migrate.sh downgrade

# Reset database (development)
rm agentic_ai_data.db && alembic upgrade head
```

### Development Server
```bash
# Start with auto-reload
./run.sh
# OR
uvicorn app.main:app --reload --port 8001

# API Documentation: http://127.0.0.1:8001/docs
```

### Test Data Generation
```bash
# Generate comprehensive reconciliation test data (270+ vouchers, 290+ bank statements)
python -m app.utils.populate_db

# Verify generated data patterns
python verify_test_data.py
```

## 📊 Data Layer Patterns

### Multi-Tenant Model Structure
```python
class ExampleModel(Base):
    __tablename__ = "example_table"
    
    example_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("entities.company_id"), nullable=False)  # REQUIRED
    firm_id = Column(String, ForeignKey("ca_firms.firm_id"), nullable=True)  # Optional
    
    # Business logic fields
    amount = Column(Numeric(18,2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_example_company_date', 'company_id', 'created_at'),
        Index('idx_example_active', 'is_active'),
    )
```

### Reconciliation Status Pattern
External data models use string-based reconciliation status:
- `"Matched"` - Perfect algorithmic match
- `"Near_Match"` - Requires human review (amount/date variance)
- `"Unmatched"` - No corresponding internal record
- `"Disputed"` - Human-flagged discrepancy

## 🧮 Financial Data Precision

### Amount Handling
```python
from decimal import Decimal

# Always use Decimal for financial calculations
amount = Decimal('10000.50')
gst_rate = Decimal('0.18')
total = amount * (1 + gst_rate)

# Database storage
Column('amount', Numeric(18,2), nullable=False)  # Monetary amounts
Column('quantity', Numeric(15,4), nullable=False)  # Quantities
Column('confidence_score', Numeric(5,4), nullable=False)  # AI scores (0.0000-1.0000)
```

### GST Calculation Pattern
```python
# Standard 18% GST calculation
taxable_value = total_amount / Decimal('1.18')
gst_amount = total_amount - taxable_value
```

## 🔐 Authentication & Authorization

### User Role Hierarchy
1. `TRENOR_ADMIN` - Platform administrators (no firm_id)
2. `CA_FIRM_ADMIN` - CA firm owners/partners  
3. `CA_STAFF` - CA firm employees
4. `CA_VIEWER` - Read-only access
5. `CLIENT_USER` - Client portal users (future)

### Request Headers (Required)
```
Authorization: Bearer <jwt_token>
X-Company-ID: <uuid>  # Required for all CDM operations
Content-Type: application/json
```

## 🔄 AI Integration Points

### Reconciliation Engine Pattern
```python
# AI confidence scoring and feedback loop
reconciliation_log = ReconciliationLog(
    company_id=context.company_id,
    match_score=Decimal('0.9500'),  # AI confidence (0.0000-1.0000)
    match_rules='{"amount_variance": 0.02, "date_variance": 2}',
    ai_reasoning="High confidence: exact amount match, 1-day date variance within tolerance"
)
```

### File Ingestion Pipeline
Located in `app/ingestion/`:
- `file_parser.py` - Multi-format parsing (CSV, Excel, XML, PDF)
- `schema_detector.py` - Automatic column mapping detection
- `service.py` - Processing orchestration with error handling

## 📁 Module Structure & Boundaries

```
app/
├── tenant/          # Multi-tenancy (firms, users, permissions)
├── auth/           # JWT authentication & authorization  
├── cdm/            # Common Data Model (core accounting entities)
├── ingestion/      # File processing pipeline
├── core/           # Shared utilities (database, tenant context, auth)
└── utils/          # Database population, verification scripts
```

### Cross-Module Dependencies
- **CDM routes** depend on `tenant_context` for data isolation
- **Auth** provides JWT tokens consumed by all protected routes
- **Ingestion** writes to CDM models after processing
- **Utils** contain test data generators matching CDM schema patterns

## ⚡ Performance Considerations

### Query Optimization Patterns
```python
# Always use strategic indexing for tenant + date filtering
__table_args__ = (
    Index('idx_voucher_company_date', 'company_id', 'voucher_date'),
    Index('idx_voucher_type_status', 'voucher_type', 'status'),
    Index('idx_voucher_party', 'party_ledger_id'),
)

# Use joins instead of N+1 queries
vouchers = db.query(VoucherHeader).options(
    joinedload(VoucherHeader.voucher_lines)
).filter(VoucherHeader.company_id == context.company_id).all()
```

### Hash-Based Deduplication
External data models use SHA256 hashing:
```python
def generate_hash(self):
    hash_string = f"{self.company_id}{self.invoice_number}{self.invoice_date}{self.total_value}"
    return hashlib.sha256(hash_string.encode()).hexdigest()
```

## 🧪 Testing Patterns

### Test Data Generation
The system includes a sophisticated test data generator (`app/utils/populate_db.py`) that creates:
- 150 sales + 120 purchase vouchers with realistic amounts
- 290+ bank statements with reconciliation patterns (80% matched, 15% near-match, 5% unmatched)
- GST records with minor variances for testing reconciliation algorithms
- Multi-tenant data isolation verification

### API Testing Headers
```python
headers = {
    "Authorization": "Bearer <jwt_token>",
    "X-Company-ID": "<company_uuid>",
    "Content-Type": "application/json"
}
```

## 🚨 Common Pitfalls to Avoid

1. **Never bypass tenant context** - All CDM queries must be tenant-aware
2. **Don't use float for money** - Always use `Decimal` for financial calculations  
3. **Avoid direct model queries** - Use tenant filtering helpers
4. **Don't hardcode UUIDs** - Generate dynamically with `str(uuid.uuid4())`
5. **Missing indexes** - Add composite indexes for `(company_id, date)` patterns
6. **Circular imports** - Use `TYPE_CHECKING` for type hints in shared modules

This architecture supports enterprise-scale CA firm operations with complete data isolation, AI-powered reconciliation, and financial precision suitable for regulatory compliance.