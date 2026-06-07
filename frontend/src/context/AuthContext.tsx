import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService, COOKIE_MODE } from '../services/api';
import type { User, SignupPayload } from '../services/api';

interface AuthContextType {
  currentUser: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    // Em COOKIE_MODE o navegador envia cookie httpOnly automaticamente
    // em /auth/me - se 200, esta logado; se 401, nao esta.
    const hasLocalToken = !COOKIE_MODE && localStorage.getItem('jwt_token');
    if (COOKIE_MODE || hasLocalToken) {
      apiService
        .getMe()
        .then(setCurrentUser)
        .catch(() => {
          if (!COOKIE_MODE) {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('refresh_token');
          }
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiService.login({ email, password });
      // Em COOKIE_MODE o backend ja setou cookies httpOnly via Set-Cookie
      if (!COOKIE_MODE) {
        localStorage.setItem('jwt_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
      }
      setCurrentUser(response.user);
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      if (!COOKIE_MODE) {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
      }
      throw error;
    }
  };

  const signup = async (payload: SignupPayload) => {
    try {
      const response = await apiService.signup(payload);
      if (!COOKIE_MODE) {
        localStorage.setItem('jwt_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
      }
      setCurrentUser(response.user);
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      if (!COOKIE_MODE) {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
      }
      throw error;
    }
  };

  const logout = async () => {
    // Em COOKIE_MODE precisamos chamar /auth/logout pra limpar cookies httpOnly
    if (COOKIE_MODE) {
      try { await apiService.logout(); } catch {}
    } else {
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('refresh_token');
    }
    setCurrentUser(null);
  };

  const value: AuthContextType = {
    currentUser,
    isLoading,
    login,
    signup,
    logout,
    isAuthenticated: !!currentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
