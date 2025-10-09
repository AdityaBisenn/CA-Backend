import { apiClient } from '@/lib/api-client';
import {
  Entity,
  EntityCreate,
  Group,
  Ledger,
  VoucherHeader,
  VoucherCreate,
  BankStatement,
  GSTSales,
  GSTPurchases,
  DashboardStats,
  ReconciliationSummary,
} from '@/types/api';

export class CDMService {
  private basePath = '/cdm';

  // Entities
  async createEntity(entityData: EntityCreate): Promise<Entity> {
    return apiClient.post(`${this.basePath}/entities`, entityData);
  }

  async getEntities(params?: {
    skip?: number;
    limit?: number;
  }): Promise<Entity[]> {
    return apiClient.get(`${this.basePath}/entities`, { params });
  }

  async getEntity(entityId: string): Promise<Entity> {
    return apiClient.get(`${this.basePath}/entities/${entityId}`);
  }

  async updateEntity(entityId: string, updates: Partial<EntityCreate>): Promise<Entity> {
    return apiClient.put(`${this.basePath}/entities/${entityId}`, updates);
  }

  async deleteEntity(entityId: string): Promise<{ message: string }> {
    return apiClient.delete(`${this.basePath}/entities/${entityId}`);
  }

  // Groups
  async getGroups(params?: {
    skip?: number;
    limit?: number;
  }): Promise<Group[]> {
    return apiClient.get(`${this.basePath}/groups`, { params });
  }

  async createGroup(groupData: {
    group_name: string;
    parent_group_id?: string;
    group_type: 'Assets' | 'Liabilities' | 'Income' | 'Expenses';
  }): Promise<Group> {
    return apiClient.post(`${this.basePath}/groups`, groupData);
  }

  // Ledgers
  async getLedgers(params?: {
    skip?: number;
    limit?: number;
    group_id?: string;
  }): Promise<Ledger[]> {
    return apiClient.get(`${this.basePath}/ledgers`, { params });
  }

  async createLedger(ledgerData: {
    ledger_name: string;
    group_id: string;
    opening_balance?: number;
    balance_type?: 'Dr' | 'Cr';
  }): Promise<Ledger> {
    return apiClient.post(`${this.basePath}/ledgers`, ledgerData);
  }

  async getLedger(ledgerId: string): Promise<Ledger> {
    return apiClient.get(`${this.basePath}/ledgers/${ledgerId}`);
  }

  // Vouchers
  async getVouchers(params?: {
    skip?: number;
    limit?: number;
    voucher_type?: string;
    from_date?: string;
    to_date?: string;
    status?: string;
  }): Promise<VoucherHeader[]> {
    return apiClient.get(`${this.basePath}/vouchers`, { params });
  }

  async createVoucher(voucherData: VoucherCreate): Promise<VoucherHeader> {
    return apiClient.post(`${this.basePath}/vouchers`, voucherData);
  }

  async getVoucher(voucherId: string): Promise<VoucherHeader> {
    return apiClient.get(`${this.basePath}/vouchers/${voucherId}`);
  }

  async updateVoucher(voucherId: string, updates: Partial<VoucherCreate>): Promise<VoucherHeader> {
    return apiClient.put(`${this.basePath}/vouchers/${voucherId}`, updates);
  }

  async deleteVoucher(voucherId: string): Promise<{ message: string }> {
    return apiClient.delete(`${this.basePath}/vouchers/${voucherId}`);
  }

  // External Data - Bank Statements
  async getBankStatements(params?: {
    skip?: number;
    limit?: number;
    from_date?: string;
    to_date?: string;
    reconciliation_status?: string;
  }): Promise<BankStatement[]> {
    return apiClient.get(`${this.basePath}/bank-statements`, { params });
  }

  async getBankStatement(bankTxnId: string): Promise<BankStatement> {
    return apiClient.get(`${this.basePath}/bank-statements/${bankTxnId}`);
  }

  // External Data - GST Sales
  async getGSTSales(params?: {
    skip?: number;
    limit?: number;
    from_date?: string;
    to_date?: string;
    reconciliation_status?: string;
  }): Promise<GSTSales[]> {
    return apiClient.get(`${this.basePath}/gst-sales`, { params });
  }

  // External Data - GST Purchases
  async getGSTPurchases(params?: {
    skip?: number;
    limit?: number;
    from_date?: string;
    to_date?: string;
    reconciliation_status?: string;
  }): Promise<GSTPurchases[]> {
    return apiClient.get(`${this.basePath}/gst-purchases`, { params });
  }

  // Dashboard & Analytics
  async getDashboardStats(): Promise<DashboardStats> {
    return apiClient.get(`${this.basePath}/dashboard/stats`);
  }

  async getReconciliationSummary(): Promise<ReconciliationSummary> {
    return apiClient.get(`${this.basePath}/reconciliation/summary`);
  }

  // Reconciliation Actions
  async runReconciliation(): Promise<{
    status: string;
    matches_found: number;
    processing_time: number;
  }> {
    return apiClient.post(`${this.basePath}/reconciliation/run`);
  }

  async markReconciled(voucherId: string, externalId: string, externalType: string): Promise<{
    message: string;
  }> {
    return apiClient.post(`${this.basePath}/reconciliation/mark-reconciled`, {
      voucher_id: voucherId,
      external_id: externalId,
      external_type: externalType,
    });
  }

  async markDisputed(voucherId: string, reason: string): Promise<{
    message: string;
  }> {
    return apiClient.post(`${this.basePath}/reconciliation/mark-disputed`, {
      voucher_id: voucherId,
      reason,
    });
  }
}

export const cdmService = new CDMService();