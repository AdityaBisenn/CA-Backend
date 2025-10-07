# Multi-Tenant CA Firm Architecture

## Overview

This system has been upgraded to support multiple CA (Chartered Accountant) firms, each managing multiple client entities with complete data isolation. The architecture ensures that:

1. **Each CA firm** can manage multiple client companies
2. **Data isolation** between different CA firms 
3. **User access control** with role-based permissions
4. **Entity-level permissions** for granular access control

## Architecture Components

### 1. Tenant Models (`app/tenant/models/`)

#### CAFirm Model
- **Purpose**: Represents a CA firm (tenant)
- **Key Fields**: `firm_id`, `firm_name`, `firm_code`, `email`, `gstin`, `pan`
- **Relationships**: Has many users and entities

#### User Model  
- **Purpose**: Users belonging to a CA firm with role-based access
- **Roles**: 
  - `TRENOR_ADMIN`: Platform admin (your team)
  - `CA_FIRM_ADMIN`: CA firm owner/admin
  - `CA_STAFF`: CA firm staff members
  - `CA_VIEWER`: Read-only access to CA firm data
  - `CLIENT_USER`: Client's own user (limited access)
- **Features**: Password hashing with bcrypt, last login tracking

#### UserEntityMap Model
- **Purpose**: Maps users to specific client entities with granular permissions
- **Permissions**: JSON field for flexible permission storage
- **Use Case**: Allow staff to access only specific client companies

### 2. Tenant Context System (`app/core/tenant_context.py`)

#### TenantContext Class
- Extracts tenant information from HTTP headers
- **Headers Required**:
  - `X-Firm-ID`: CA firm identifier  
  - `X-Company-ID`: Client company identifier
  - `X-User-ID`: User identifier (optional)

#### Security Features
- Validates firm exists and is active
- Ensures company belongs to the specified firm
- Provides data isolation at query level

#### Helper Functions
- `apply_tenant_filter()`: Automatically filters queries by tenant context
- `get_optional_tenant_context()`: For admin/system endpoints

### 3. Updated CDM Models

#### Entity Model Changes
- **Added**: `firm_id` foreign key linking to CAFirm
- **Purpose**: Ensures all client entities belong to a specific CA firm
- **Migration**: Uses nullable field initially for smooth migration

### 4. API Routes Structure

#### Tenant Routes (`/api/v1/tenant/`)
- **Firm Management**: 
  - `POST /firms` - Create new CA firm
  - `GET /firms` - List firms (filtered by context)
  - `GET /firms/{firm_id}` - Get firm details
  - `PUT /firms/{firm_id}` - Update firm
  - `GET /firms/{firm_id}/summary` - Firm statistics

- **User Management**:
  - `POST /users` - Create user within firm
  - `GET /users` - List users in firm  
  - `GET /users/{user_id}` - Get user details
  - `PUT /users/{user_id}` - Update user
  - `POST /users/{user_id}/change-password` - Change password
  - `POST /users/{user_id}/entities` - Grant entity access
  - `GET /users/{user_id}/entities` - List user's accessible entities
  - `PUT /users/{user_id}/entities/{company_id}` - Update entity permissions

#### CDM Routes (`/api/v1/cdm/`)
- **Enhanced with tenant context**: All routes now require tenant headers
- **Automatic filtering**: All queries filtered by firm and company context
- **Data isolation**: Users can only access data within their firm and assigned entities

### 5. Database Schema

#### New Tables
1. **ca_firms** - CA firm master data
2. **users** - User accounts with role-based access  
3. **user_entity_map** - User-to-entity permission mapping

#### Modified Tables
1. **entities** - Added `firm_id` foreign key

#### Indexes
- Strategic indexing on tenant fields for performance
- Composite indexes on `(firm_id, role)`, `(firm_id, company_id)` etc.

## Usage Patterns

### 1. Creating a New CA Firm
```json
POST /api/v1/tenant/firms
{
  "firm_name": "ABC & Associates",
  "firm_code": "ABC001", 
  "email": "admin@abc-ca.com",
  "gstin": "29ABCDE1234F1Z5",
  "pan": "ABCDE1234F"
}
```

### 2. Creating Firm Admin User
```json  
POST /api/v1/tenant/users
Headers: X-Firm-ID: <firm_id>
{
  "email": "admin@abc-ca.com",
  "first_name": "Admin",
  "last_name": "User", 
  "role": "CA_FIRM_ADMIN",
  "password": "secure_password",
  "firm_id": "<firm_id>"
}
```

### 3. Adding Client Entity
```json
POST /api/v1/cdm/entities  
Headers: 
  X-Firm-ID: <firm_id>
  X-Company-ID: <company_id>
{
  "company_name": "Client Company Ltd",
  "company_id": "<company_id>",
  "gstin": "29XYZAB5678P1Q2"
}
```

### 4. Granting Entity Access to Staff
```json
POST /api/v1/tenant/users/{user_id}/entities
Headers: X-Firm-ID: <firm_id>, X-Company-ID: <company_id>
{
  "user_id": "<user_id>",
  "company_id": "<company_id>", 
  "permissions": {"read": true, "write": true, "delete": false}
}
```

## Security Model

### 1. Multi-Level Data Isolation
- **Firm Level**: CA firms cannot see each other's data
- **Entity Level**: Users can only access assigned client entities  
- **Role Level**: Permissions based on user roles

### 2. Request Flow
1. Client sends request with tenant headers
2. `get_tenant_context()` validates headers and permissions
3. Routes use context to filter queries automatically
4. Data returned only for authorized firm/entities

### 3. Permission Matrix
| Role | Firm Admin | User Mgmt | Client Data | System Config |
|------|------------|-----------|-------------|---------------|
| TRENOR_ADMIN | ✅ All | ✅ All | ✅ All | ✅ Yes |
| CA_FIRM_ADMIN | ✅ Own | ✅ Own Firm | ✅ Own Clients | ❌ No |
| CA_STAFF | ❌ No | ❌ No | ✅ Assigned Only | ❌ No |
| CA_VIEWER | ❌ No | ❌ No | 👁️ Read Only | ❌ No |
| CLIENT_USER | ❌ No | ❌ No | 👁️ Own Data Only | ❌ No |

## Migration Notes

### Database Migration
- Migration `7fae4977ee93` adds all tenant tables
- Uses batch mode for SQLite compatibility  
- Entity.firm_id initially nullable for smooth migration

### Code Migration
- All CDM routes updated with tenant context dependencies
- Automatic query filtering via `apply_tenant_filter()`
- Pydantic schemas updated for v2 compatibility

## Development Workflow

### 1. Local Development Setup
```bash
# Apply migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# API Documentation  
http://localhost:8000/docs
```

### 2. Testing Multi-Tenancy
1. Create a CA firm via `/api/v1/tenant/firms`
2. Create admin user for the firm  
3. Set tenant headers in requests
4. Verify data isolation between firms

### 3. Adding New Features
- Always use `get_tenant_context()` dependency
- Apply tenant filtering to all queries
- Test with multiple firms to ensure isolation

## Monitoring & Observability

### Key Metrics to Track
- **Tenant Isolation**: Verify no cross-tenant data leakage
- **Performance**: Query performance with tenant filtering  
- **User Activity**: Login patterns, entity access patterns
- **Data Growth**: Per-firm data volumes and growth rates

### Security Auditing
- Log all tenant context switches
- Monitor failed authorization attempts  
- Track user permission changes
- Audit entity access grants/revokes

## Future Enhancements

### 1. Enhanced Authentication
- JWT token-based authentication
- Multi-factor authentication for admin users
- Single sign-on (SSO) integration

### 2. Advanced Multi-Tenancy
- Database per tenant for larger firms
- Geographic data residency requirements
- Advanced backup/restore per tenant

### 3. Business Features  
- Subscription management and billing
- Firm-level feature toggles
- Advanced reporting across entities
- Audit trails and compliance reports

This architecture provides the foundation for a scalable, secure multi-tenant CA firm management system while maintaining complete data isolation and flexible permission controls.