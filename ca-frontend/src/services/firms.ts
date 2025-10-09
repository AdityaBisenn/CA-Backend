import { apiClient } from '@/lib/api-client';
import {
  CAFirm,
  CAFirmCreate,
  PaginatedResponse,
} from '@/types/api';

export class FirmService {
  private basePath = '/tenant/firms';

  async createFirm(firmData: CAFirmCreate): Promise<CAFirm> {
    return apiClient.post(`${this.basePath}`, firmData);
  }

  async getFirms(params?: {
    page?: number;
    per_page?: number;
    active_only?: boolean;
    search?: string;
  }): Promise<PaginatedResponse<CAFirm>> {
    return apiClient.get(`${this.basePath}`, { params });
  }

  async getFirm(firmId: string): Promise<CAFirm> {
    return apiClient.get(`${this.basePath}/${firmId}`);
  }

  async updateFirm(firmId: string, updates: Partial<CAFirmCreate>): Promise<CAFirm> {
    return apiClient.put(`${this.basePath}/${firmId}`, updates);
  }

  async deleteFirm(firmId: string): Promise<{ message: string }> {
    return apiClient.delete(`${this.basePath}/${firmId}`);
  }

  async getFirmStats(firmId: string): Promise<{
    total_entities: number;
    active_entities: number;
    total_users: number;
    active_users: number;
  }> {
    return apiClient.get(`${this.basePath}/${firmId}/stats`);
  }
}

export const firmService = new FirmService();