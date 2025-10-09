import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthTokens, UserRole } from '@/types/api';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  selectedCompanyId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  setAuth: (authData: AuthTokens) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  setSelectedCompany: (companyId: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      selectedCompanyId: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      setAuth: (authData: AuthTokens) => {
        set({
          user: authData.user,
          token: authData.access_token,
          refreshToken: authData.refresh_token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        set({
          token: accessToken,
          refreshToken: refreshToken,
          isAuthenticated: true,
        });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setSelectedCompany: (companyId: string) => {
        set({ selectedCompanyId: companyId });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          selectedCompanyId: null,
          isAuthenticated: false,
          isLoading: false,
        });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'ca-auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        selectedCompanyId: state.selectedCompanyId,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Utility functions
export const hasRole = (user: User | null, requiredRoles: UserRole[]): boolean => {
  if (!user) return false;
  return requiredRoles.includes(user.role);
};

export const isTrenorAdmin = (user: User | null): boolean => {
  return hasRole(user, [UserRole.TRENOR_ADMIN]);
};

export const isFirmAdmin = (user: User | null): boolean => {
  return hasRole(user, [UserRole.TRENOR_ADMIN, UserRole.CA_FIRM_ADMIN]);
};

export const hasStaffAccess = (user: User | null): boolean => {
  return hasRole(user, [UserRole.TRENOR_ADMIN, UserRole.CA_FIRM_ADMIN, UserRole.CA_STAFF]);
};