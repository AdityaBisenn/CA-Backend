import { apiClient } from '@/lib/api-client';
import {
  LoginRequest,
  RegisterRequest,
  AuthTokens,
  User,
} from '@/types/api';

export class AuthService {
  private basePath = '/auth';

  async login(credentials: LoginRequest): Promise<AuthTokens> {
    return apiClient.post(`${this.basePath}/login`, credentials);
  }

  async register(userData: RegisterRequest): Promise<{ message: string; user_id: string }> {
    return apiClient.post(`${this.basePath}/register`, userData);
  }

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return apiClient.post(`${this.basePath}/refresh`, {
      refresh_token: refreshToken,
    });
  }

  async logout(): Promise<void> {
    return apiClient.post(`${this.basePath}/logout`);
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  async getProfile(): Promise<User> {
    return apiClient.get(`${this.basePath}/profile`);
  }

  async requestPasswordReset(email: string): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/reset-password`, { email });
  }

  async confirmPasswordReset(token: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post(`${this.basePath}/reset-password/confirm`, {
      token,
      new_password: newPassword,
    });
  }
}

export const authService = new AuthService();