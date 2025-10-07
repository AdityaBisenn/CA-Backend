# Agentic AI Layer - Verified Accounting Backend

## 🏗️ Complete CDM (Common Data Model) Implementation

This is a production-ready FastAPI backend for the **Agentic AI Layer project**, featuring a comprehensive Common Data Model for accounting and financial data management.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Apply database migrations
./migrate.sh upgrade

# Run the server
bash run.sh
```

Visit: **http://127.0.0.1:8001/docs** for interactive API documentation

## 📋 Project Structure

```
verified_ai_layer_backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py             # Global configuration
│   │   └── logger.py             # Error logging utilities
│   ├── ingestion/                # Data ingestion pipeline
│   │   ├── routes.py            # File upload endpoints
│   │   ├── service.py           # Processing orchestration
│   │   ├── file_parser.py       # Multi-format parsing
│   │   ├── schema_detector.py   # Auto schema detection
│   │   └── error_logger.py      # Module logging
│   ├── cdm/                     # Common Data Model
│   │   ├── database.py          # SQLAlchemy configuration
│   │   ├── routes.py            # CDM API endpoints
│   │   ├── models/              # Database models
│   │   │   ├── entity.py        # Company entities
│   │   │   ├── master.py        # Groups, Ledgers, Items
│   │   │   ├── transaction.py   # Vouchers & Lines
│   │   │   ├── external.py      # Bank, GST data
│   │   │   └── reconciliation.py # AI matching logs
│   │   └── schemas/             # Pydantic schemas
│   │       ├── entity.py
│   │       ├── master.py
│   │       └── transaction.py
│   └── utils/
│       └── helpers.py           # Utility functions
├── tests/                       # Test files
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                # Migration environment
│   └── alembic.ini           # Migration configuration
├── requirements.txt            # Python dependencies
├── run.sh                     # Server launcher
├── migrate.sh                 # Database migration manager
├── MIGRATIONS.md              # Migration documentation
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🏦 CDM Architecture Overview

### **Entity Layer** - Company Management
- **Company/Entity**: Multi-company support with GST, PAN, financial year configuration
- **Audit trails**: Created/updated timestamps for all entities
- **Status management**: Active/inactive entity tracking

### **Master Layer** - Chart of Accounts
- **Groups**: Hierarchical account structure (Asset, Liability, Income, Expense)
- **Ledgers**: Individual accounts with opening balances, GST settings
- **Stock Items**: Inventory management with HSN codes, tax rates
- **Tax Ledgers**: Tax configuration for GST, TDS, etc.

### **Transaction Layer** - Financial Vouchers
- **Voucher Headers**: Sales, purchase, payment, receipt vouchers
- **Voucher Lines**: Double-entry accounting with debit/credit entries
- **Financial precision**: Decimal(18,2) for amounts, proper rounding
- **Status workflow**: Draft → Posted → Verified

### **External Data Layer** - Third-party Integration  
- **Bank Statements**: Auto-reconciliation with hash-based deduplication
- **GST Sales/Purchases**: GSTR-1, GSTR-2A integration ready
- **Raw JSON storage**: Preserve original data for audit trails

### **Reconciliation Layer** - AI-Powered Matching
- **Reconciliation Logs**: AI confidence scores, match rules, reasoning
- **Ingestion Jobs**: File processing tracking with success/failure metrics
- **Audit Events**: Complete CRUD operation logging
- **AI Feedback**: Machine learning improvement through user corrections

## 🔌 API Endpoints

### **Ingestion APIs**
- `POST /api/v1/ingest` - Upload files (CSV, Excel, XML, PDF)

### **Entity Management** 
- `POST /api/v1/cdm/entities` - Create company
- `GET /api/v1/cdm/entities` - List companies
- `GET /api/v1/cdm/entities/{id}` - Get company details
- `PUT /api/v1/cdm/entities/{id}` - Update company

### **Master Data APIs**
- `POST/GET /api/v1/cdm/groups` - Account groups
- `POST/GET /api/v1/cdm/ledgers` - Chart of accounts  
- `POST/GET /api/v1/cdm/stock-items` - Inventory items
- `POST/GET /api/v1/cdm/tax-ledgers` - Tax configuration

### **Transaction APIs**
- `POST /api/v1/cdm/vouchers` - Create vouchers with lines
- `GET /api/v1/cdm/vouchers` - List vouchers (filterable by company)
- `GET /api/v1/cdm/vouchers/{id}` - Get voucher details

### **Reconciliation APIs**
- `GET /api/v1/cdm/reconciliation/unmatched` - Find unmatched records
- `POST /api/v1/cdm/reconciliation/match` - Trigger AI matching

## 🗄️ Database Features

### **Multi-Company Architecture**
Every table includes `company_id` foreign key for proper data isolation

### **Financial Precision** 
- `Numeric(18,2)` for monetary amounts
- `Numeric(15,4)` for quantities  
- `Numeric(5,4)` for AI confidence scores

### **Performance Optimization**
- Strategic indexing on frequently queried columns
- Composite indexes for company + date filtering
- Hash-based deduplication for external data

### **Audit & Compliance**
- `created_at`, `updated_at` timestamps on all entities
- `is_active` soft deletion
- Complete reconciliation audit trails

## 🤖 AI Integration Ready

### **Reconciliation Engine**
- Confidence scoring (0.0000 to 1.0000)
- Rule-based matching with JSON metadata storage
- Human-in-the-loop feedback collection

### **Data Ingestion Pipeline**
- Multi-format parsing with error handling
- Schema auto-detection for CSV/Excel files
- Provenance tracking with SHA256 checksums

### **Machine Learning Support**
- Model version tracking
- Prediction vs. correction logging
- Confidence score analytics

## 🔧 Production Features

### **Database Support**
- **Development**: SQLite (auto-configured)
- **Production**: PostgreSQL with connection pooling
- **Migration system**: Alembic for schema versioning

### **Migration Management**
- Automated migration generation with `./migrate.sh create "message"`
- Safe database upgrades with `./migrate.sh upgrade`  
- Version control for database schema changes
- Rollback support with `./migrate.sh downgrade`

### **Security & Monitoring**
- CORS middleware for frontend integration
- Environment-based configuration
- Comprehensive error logging to JSONL format

### **Scalability Design**
- Modular architecture for microservice splitting
- Async FastAPI with proper session management
- Background task integration points

## 🧩 Extension Points for Your Team

### **Immediate Next Steps**
1. **Authentication Layer**: JWT middleware integration
2. **Background Jobs**: Celery + Redis for heavy processing
3. **Report Generation**: PDF/Excel export endpoints
4. **Dashboard APIs**: Analytics and summary endpoints

### **AI Reasoning Module**
1. **ReAct Agents**: Rule-based validation agents
2. **Anomaly Detection**: Outlier identification in transactions
3. **Predictive Analytics**: Cash flow and trend analysis

### **Integration Layer**
1. **Tally Connector**: XML import/export to Tally
2. **Banking APIs**: Direct bank statement fetching
3. **GST APIs**: Real-time GSTN integration

## 🧪 Testing

```bash
# Run basic API tests
python -m pytest tests/

# Test database connection
python -c "from app.cdm.database import engine; print('DB Connected:', engine.url)"

# Test data ingestion
curl -X POST "http://localhost:8000/api/v1/ingest" -H "Content-Type: multipart/form-data" -F "file=@sample.csv"
```

## 🎯 Key Improvements Implemented

✅ **UUID-based primary keys** for distributed scalability  
✅ **Company-scoped data** with proper foreign key relationships  
✅ **Financial precision** with proper decimal handling  
✅ **Comprehensive indexing** for query performance  
✅ **Audit trail support** with timestamps and soft deletion  
✅ **Hash-based deduplication** for external data sources  
✅ **AI integration points** with confidence scoring and feedback loops  
✅ **Production-ready configuration** with environment variables  
✅ **Modular architecture** ready for team development  

This CDM implementation provides a **solid foundation** for your Agentic AI Layer project, supporting everything from basic accounting operations to advanced AI-powered reconciliation and verification workflows.

## 🤝 Team Development

The modular structure allows your interns to work on independent modules:

- **Intern A**: Ingestion pipeline enhancements
- **Intern B**: CDM API extensions  
- **Intern C**: AI reconciliation algorithms
- **Intern D**: Frontend dashboard integration

Each module has clear interfaces and can be developed, tested, and deployed independently.