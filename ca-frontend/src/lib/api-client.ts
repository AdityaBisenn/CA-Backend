import axios from 'axios'

// Simple axios instance used across the frontend services
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Add request interceptor to include auth token and company ID
apiClient.interceptors.request.use(
  (config) => {
    // Get auth data from localStorage if available
    const authData = typeof window !== 'undefined' ? localStorage.getItem('ca-auth-storage') : null;
    if (authData) {
      try {
        const parsedAuth = JSON.parse(authData);
        if (parsedAuth.state?.token) {
          config.headers.Authorization = `Bearer ${parsedAuth.state.token}`;
        }
        if (parsedAuth.state?.selectedCompanyId) {
          config.headers['X-Company-ID'] = parsedAuth.state.selectedCompanyId;
        }
      } catch (e) {
        console.warn('Failed to parse auth data:', e);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle data extraction
apiClient.interceptors.response.use(
  (response) => {
    // Return just the data portion of the response
    return response.data;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient
