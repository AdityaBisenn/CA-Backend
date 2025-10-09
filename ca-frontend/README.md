# CA Management System - Frontend

Modern React/TypeScript frontend for the multi-tenant CA (Chartered Accountant) management system with AI-powered reconciliation capabilities.

## 🏗️ Architecture

### **Tech Stack**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for global state, React Query for server state
- **UI Components**: Radix UI primitives with custom styling
- **Icons**: Heroicons
- **HTTP Client**: Axios with automatic token refresh

### **Key Features**
- 🔐 **JWT Authentication** with automatic token refresh
- 🏢 **Multi-tenant Architecture** with company context switching  
- 📊 **Real-time Dashboard** with financial KPIs and reconciliation metrics
- 🔄 **AI-Powered Reconciliation** management interface
- 📈 **Entity Management** for CA firm clients
- 📋 **Voucher Management** with GST integration
- 👥 **Role-based Access Control** (Trenor Admin, CA Firm Admin, CA Staff, CA Viewer)
- 📱 **Responsive Design** optimized for desktop and tablet

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- CA Backend API running on `http://127.0.0.1:8001`

### Installation

```bash
# Navigate to frontend directory
cd ca-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api/v1
```

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Protected dashboard pages
│   ├── login/            # Authentication page
│   ├── globals.css       # Global styles and CSS variables
│   ├── layout.tsx        # Root layout with providers
│   └── page.tsx          # Home redirect page
├── components/            # Reusable UI components
│   ├── ui/               # Base UI components (Button, Toast, etc.)
│   └── dashboard/        # Dashboard-specific components
├── lib/                  # Utilities and configurations
│   ├── api-client.ts     # Axios client with interceptors
│   └── utils.ts          # Shared utility functions
├── services/             # API service layer
│   ├── auth.ts           # Authentication endpoints
│   ├── cdm.ts            # CDM (Common Data Model) endpoints
│   └── firms.ts          # CA firm management endpoints
├── store/                # Zustand global state
│   └── auth.ts           # Authentication state management
└── types/                # TypeScript type definitions
    └── api.ts            # API response/request types
```

## 🔐 Authentication Flow

1. **Login**: User enters credentials → JWT tokens stored in Zustand + localStorage
2. **Token Refresh**: Automatic refresh on 401 responses via Axios interceptor
3. **Company Context**: Required `X-Company-ID` header for tenant isolation
4. **Route Protection**: Dashboard layout checks authentication state
5. **Role-based Access**: Navigation and features filtered by user role

## 🏢 Multi-Tenant Architecture

### **Company Context System**
- **Company Selector**: Dropdown to switch between client companies
- **Header Injection**: `X-Company-ID` automatically added to API requests
- **Data Isolation**: All API responses filtered by selected company
- **Persistent Selection**: Company choice persisted in auth store

### **User Roles**
1. **Trenor Admin**: Platform-level access to all firms
2. **CA Firm Admin**: Full access to firm's data and settings
3. **CA Staff**: Access to financial data and reconciliation
4. **CA Viewer**: Read-only access to reports and data

## 📊 Key Pages

### **Dashboard (`/dashboard`)**
- Financial KPIs and metrics
- Recent vouchers overview
- Reconciliation status summary
- Company-specific data filtering

### **Companies (`/dashboard/entities`)**
- CRUD operations for client companies
- Financial year management
- GST and PAN details
- State and registration information

### **Reconciliation (`/dashboard/reconciliation`)**
- Bank statement reconciliation
- GST sales/purchase matching
- AI-powered match confidence scores
- Manual reconciliation controls
- Real-time match rate metrics

### **Vouchers (`/dashboard/vouchers`)**
- Accounting voucher management
- GST-compliant entries
- Multi-line voucher support
- Party ledger integration

## 🎨 Design System

### **Color Palette**
- **Primary**: Blue (#3B82F6) for navigation and CTAs
- **Success**: Green (#10B981) for matched transactions
- **Warning**: Yellow (#F59E0B) for near-matches
- **Destructive**: Red (#EF4444) for unmatched/errors
- **Muted**: Gray tones for secondary information

### **Typography**
- **Headings**: Inter font with semibold weights
- **Body**: Inter regular for readability
- **Code/Data**: Monospace for financial figures

### **Components**
- **Consistent spacing** using Tailwind's spacing scale
- **Rounded corners** (0.5rem) for modern feel
- **Subtle shadows** for depth and hierarchy
- **Hover states** for interactive elements

## 🔄 State Management

### **Zustand Auth Store**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;  
  refreshToken: string | null;
  selectedCompanyId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

### **React Query**
- **Server state caching** with 5-minute stale time
- **Automatic retries** except for auth errors (401/403)
- **Background refetching** for real-time data
- **Optimistic updates** for better UX

## 📡 API Integration

### **Request Flow**
1. **Authentication**: JWT token in Authorization header
2. **Tenant Context**: X-Company-ID header for data isolation
3. **Error Handling**: Automatic retry with exponential backoff
4. **Token Refresh**: Seamless token renewal on expiration

### **Key Services**
- `authService`: Login, logout, token refresh
- `cdmService`: Entities, vouchers, ledgers, reconciliation
- `firmService`: CA firm management and user operations

## 🚀 Deployment

### **Build for Production**
```bash
npm run build
npm start
```

### **Environment Configuration**
- Set `NEXT_PUBLIC_API_URL` to production backend URL
- Configure CORS settings in backend for frontend domain
- Set up proper JWT secret and token expiration

## 🔧 Development

### **Available Scripts**
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server  
- `npm run lint`: Run ESLint
- `npm run type-check`: TypeScript type checking

### **Code Quality**
- **TypeScript**: Strict type checking enabled
- **ESLint**: Next.js recommended configuration
- **Prettier**: Code formatting (recommended)
- **Tailwind**: Consistent styling patterns

## 🧪 Testing Recommendations

- **Unit Tests**: Jest + React Testing Library
- **Integration Tests**: Test API service layer
- **E2E Tests**: Playwright for critical user flows
- **Accessibility**: axe-core for WCAG compliance

## 📈 Performance Optimizations

- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js built-in image optimization
- **API Caching**: React Query with strategic cache invalidation
- **Bundle Analysis**: `@next/bundle-analyzer` for size monitoring

This frontend provides a comprehensive, user-friendly interface for CA firms to manage their clients' financial data with AI-powered reconciliation capabilities, built with modern React patterns and enterprise-grade architecture.