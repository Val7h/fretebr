import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { User, SignupPayload } from '../services/api';

interface AuthContextType {
  currentUser: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      apiService
        .getMe()
        .then(setCurrentUser)
        .catch(() => {
          localStorage.removeItem('jwt_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await apiService.login({ email, password });
      localStorage.setItem('jwt_token', response.access_token);
      setCurrentUser(response.user);
      // Add small delay to ensure state updates propagate
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      localStorage.removeItem('jwt_token');
      throw error;
    }
  };

  const signup = async (payload: SignupPayload) => {
    try {
      const response = await apiService.signup(payload);
      localStorage.setItem('jwt_token', response.access_token);
      setCurrentUser(response.user);
      // Add small delay to ensure state updates propagate
      await new Promise(resolve => setTimeout(resolve, 100));
    } catch (error) {
      localStorage.removeItem('jwt_token');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
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
