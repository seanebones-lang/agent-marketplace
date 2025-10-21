/**
 * API Client
 * 
 * Centralized API client for backend communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;
  private apiKey: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        
        // Add API key if available
        if (this.apiKey) {
          config.headers['X-API-Key'] = this.apiKey;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          await this.refreshToken();
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_key', apiKey);
    }
  }

  clearAuth() {
    this.token = null;
    this.apiKey = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('api_key');
    }
  }

  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return;

      const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
        refresh_token: refreshToken,
      });

      this.setToken(response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
    } catch (error) {
      this.clearAuth();
      throw error;
    }
  }

  // Agent Packages
  async getPackages(category?: string) {
    const params = category ? { category } : {};
    const response = await this.client.get('/api/v1/packages', { params });
    return response.data;
  }

  async getPackage(packageId: string) {
    const response = await this.client.get(`/api/v1/packages/${packageId}`);
    return response.data;
  }

  async executePackage(packageId: string, task: string, engineType: string = 'crewai') {
    const response = await this.client.post(`/api/v1/packages/${packageId}/execute`, {
      task,
      engine_type: engineType,
    });
    return response.data;
  }

  async getCategories() {
    const response = await this.client.get('/api/v1/categories');
    return response.data;
  }

  // Authentication
  async register(data: {
    name: string;
    email: string;
    password: string;
    tier?: string;
  }) {
    const response = await this.client.post('/api/v1/auth/register', data);
    return response.data;
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await this.client.post('/api/v1/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    this.setToken(response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);

    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async regenerateApiKey() {
    const response = await this.client.post('/api/v1/auth/api-key/regenerate');
    return response.data;
  }

  // Health
  async getHealth() {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }
}

export const apiClient = new APIClient();
export default apiClient;

