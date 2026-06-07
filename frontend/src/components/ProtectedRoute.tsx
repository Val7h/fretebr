import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'motorista' | 'shipper';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { isAuthenticated, isLoading, currentUser } = useAuth();

  // 🔧 FIX: Check if token exists but currentUser not yet set (handles race condition)
  const hasToken = !!localStorage.getItem('jwt_token');
  const isAuthenticating = hasToken && !currentUser;

  if (isLoading || isAuthenticating) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600">
        <div className="text-white text-center">
          <div className="inline-block">
            <svg className="animate-spin h-8 w-8 text-white mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && currentUser?.tipo !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};
