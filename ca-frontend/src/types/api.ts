// API Types based on CA Backend Models

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Auth Types
export enum UserRole {
  TRENOR_ADMIN = 'trenor_admin',
  CA_FIRM_ADMIN = 'ca_firm_admin', 
  CA_STAFF = 'ca_staff',
  CA_VIEWER = 'ca_viewer',
  CLIENT_USER = 'client_user'
}

export interface User {
  user_id: string;
  firm_id: string | null;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  firm_id?: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  role?: UserRole;
}

// CA Firm Types
export interface CAFirm {
  firm_id: string;
  firm_name: string;
  contact_email?: string;
  phone?: string;
  address?: string;
  gstin?: string;
  pan?: string;
  firm_registration_no?: string;
  city?: string;
  state?: string;
  pincode?: string;
  subscription_tier: 'basic' | 'premium' | 'enterprise';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CAFirmCreate {
  firm_name: string;
  contact_email?: string;
  phone?: string;
  address?: string;
  gstin?: string;
  pan?: string;
  firm_registration_no?: string;
  city?: string;
  state?: string;
  pincode?: string;
  subscription_tier?: 'basic' | 'premium' | 'enterprise';
}

// Entity (Company) Types
export enum GSTType {
  REGULAR = 'Regular',
  COMPOSITION = 'Composition'
}

export interface Entity {
  company_id: string;
  firm_id: string;
  company_name: string;
  financial_year_start: string; // ISO date
  financial_year_end: string; // ISO date
  books_begin_from?: string; // ISO date
  gst_registration_type?: GSTType;
  state?: string;
  gstin?: string;
  currency: string;
  pan?: string;
  cin?: string;
  registration_type?: string;
  tan?: string;
  ifsc_default_bank?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface EntityCreate {
  company_name: string;
  financial_year_start: string;
  financial_year_end: string;
  books_begin_from?: string;
  gst_registration_type?: GSTType;
  state?: string;
  gstin?: string;
  currency?: string;
  pan?: string;
  cin?: string;
  registration_type?: string;
  tan?: string;
  ifsc_default_bank?: string;
}

// Ledger Types
export interface Group {
  group_id: string;
  company_id: string;
  group_name: string;
  parent_group_id?: string;
  group_type: 'Assets' | 'Liabilities' | 'Income' | 'Expenses';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Ledger {
  ledger_id: string;
  company_id: string;
  ledger_name: string;
  group_id: string;
  opening_balance: number;
  balance_type: 'Dr' | 'Cr';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  group?: Group;
}

// Transaction Types
export enum VoucherStatus {
  DRAFT = 'Draft',
  POSTED = 'Posted', 
  VERIFIED = 'Verified'
}

export enum ReconciliationStatus {
  UNMATCHED = 'Unmatched',
  AUTO_MATCHED = 'AutoMatched',
  MANUALLY_VERIFIED = 'ManuallyVerified',
  DISPUTED = 'Disputed'
}

export interface VoucherHeader {
  voucher_id: string;
  company_id: string;
  voucher_type: string;
  voucher_date: string; // ISO date
  voucher_number: string;
  party_ledger_id?: string;
  narration?: string;
  ref_document?: string;
  total_amount: number;
  status: VoucherStatus;
  is_gst_applicable: boolean;
  place_of_supply?: string;
  source_system?: string;
  external_match_key?: string;
  reconciliation_status: ReconciliationStatus;
  reconciliation_source?: string;
  reconciliation_confidence?: number;
  created_at: string;
  updated_at?: string;
  party_ledger?: Ledger;
  lines?: VoucherLine[];
}

export interface VoucherLine {
  line_id: string;
  voucher_id: string;
  company_id: string;
  ledger_id: string;
  debit: number;
  credit: number;
  item_id?: string;
  quantity?: number;
  rate?: number;
  tax_id?: string;
  tax_amount: number;
  discount: number;
  round_off: number;
  narration?: string;
  created_at: string;
  updated_at?: string;
  ledger?: Ledger;
}

export interface VoucherCreate {
  voucher_type: string;
  voucher_date: string;
  voucher_number: string;
  party_ledger_id?: string;
  narration?: string;
  ref_document?: string;
  total_amount: number;
  is_gst_applicable?: boolean;
  place_of_supply?: string;
  lines: VoucherLineCreate[];
}

export interface VoucherLineCreate {
  ledger_id: string;
  debit?: number;
  credit?: number;
  item_id?: string;
  quantity?: number;
  rate?: number;
  tax_id?: string;
  tax_amount?: number;
  discount?: number;
  round_off?: number;
  narration?: string;
}

// External Data Types
export interface BankStatement {
  bank_txn_id: string;
  company_id: string;
  bank_id: string;
  txn_date: string; // ISO date
  value_date?: string; // ISO date
  narration?: string;
  amount: number;
  dr_cr: 'Dr' | 'Cr';
  cheque_ref?: string;
  balance_after_txn?: number;
  linked_voucher_id?: string;
  reconciliation_status: 'Matched' | 'Near_Match' | 'Unmatched' | 'Disputed';
  created_at: string;
  updated_at?: string;
  linked_voucher?: VoucherHeader;
}

export interface GSTSales {
  gst_invoice_id: string;
  company_id: string;
  gstin_customer?: string;
  invoice_number: string;
  invoice_date: string; // ISO date
  taxable_value: number;
  tax_amount: number;
  total_value: number;
  status: string;
  linked_voucher_id?: string;
  reconciliation_status: 'Matched' | 'Near_Match' | 'Unmatched' | 'Disputed';
  created_at: string;
  updated_at?: string;
  linked_voucher?: VoucherHeader;
}

export interface GSTPurchases {
  purchase_id: string;
  company_id: string;
  supplier_gstin?: string;
  invoice_number: string;
  invoice_date: string; // ISO date
  taxable_value: number;
  igst_amount: number;
  cgst_amount: number;
  sgst_amount: number;
  itc_available: boolean;
  linked_voucher_id?: string;
  reconciliation_status: 'Matched' | 'Near_Match' | 'Unmatched' | 'Disputed';
  created_at: string;
  updated_at?: string;
  linked_voucher?: VoucherHeader;
}

// Reconciliation Types
export interface ReconciliationSummary {
  total_vouchers: number;
  matched_vouchers: number;
  unmatched_vouchers: number;
  disputed_vouchers: number;
  match_percentage: number;
  total_bank_statements: number;
  matched_bank_statements: number;
  total_gst_sales: number;
  matched_gst_sales: number;
  total_gst_purchases: number;
  matched_gst_purchases: number;
}

export interface ReconciliationLog {
  log_id: string;
  company_id: string;
  voucher_id?: string;
  external_ref_id?: string;
  external_ref_type: 'bank_statement' | 'gst_sales' | 'gst_purchases';
  match_score: number;
  match_rules?: string;
  ai_reasoning?: string;
  human_verified: boolean;
  verified_by?: string;
  created_at: string;
}

// Dashboard Types  
export interface DashboardStats {
  total_entities: number;
  total_vouchers: number;
  total_amount: number;
  pending_reconciliation: number;
  reconciliation_summary: ReconciliationSummary;
  recent_vouchers: VoucherHeader[];
  recent_bank_statements: BankStatement[];
}

// File Ingestion Types
export interface FileIngestionResult {
  status: 'success' | 'error';
  file_name: string;
  records_processed: number;
  records_created: number;
  records_updated: number;
  errors: string[];
  warnings: string[];
}