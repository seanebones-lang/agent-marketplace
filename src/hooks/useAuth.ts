/**
 * Authentication Hook
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Customer, AuthTokens } from '@/types';

export function useAuth() {
  const [user, setUser] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        apiClient.setToken(token);
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      apiClient.clearAuth();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setError(null);
      setLoading(true);
      await apiClient.login(email, password);
      await checkAuth();
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: {
    name: string;
    email: string;
    password: string;
    tier?: string;
  }): Promise<void> => {
    try {
      setError(null);
      setLoading(true);
      const response = await apiClient.register(data);
      
      // Auto-login after registration
      if (response.api_key) {
        apiClient.setApiKey(response.api_key);
      }
      
      await login(data.email, data.password);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    apiClient.clearAuth();
    setUser(null);
  };

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };
}

