import axios, { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
});

// Add JWT token to request headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface SignupPayload {
  email: string;
  password: string;
  tipo: 'motorista' | 'shipper';
  nome: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  nome: string;
  tipo: 'motorista' | 'shipper';
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export const apiService = {
  async signup(payload: SignupPayload): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/signup', payload);
    return response.data;
  },

  async login(payload: LoginPayload): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', payload);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

export default api;
