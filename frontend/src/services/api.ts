import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types
export interface Frete {
  id: number;
  motorista_id: number;
  origem: string;
  destino: string;
  peso_kg: number;
  valor_r: number;
  descricao?: string;
  status: 'disponível' | 'aceito' | 'entregue' | 'cancelado';
  created_at: string;
  updated_at: string;
}

export interface CreateFretePayload {
  origem: string;
  destino: string;
  peso_kg: number;
  valor_r: number;
  descricao?: string;
  urgencia?: string;
  data_entrega?: string;
}

export interface Match {
  id: number;
  frete_id: number;
  transportador_id: number;
  status: 'pendente' | 'aceito' | 'rejeitado';
  valor_proposta?: number;
  created_at: string;
}

export interface CreateMatchPayload {
  frete_id: number;
  valor_proposta?: number;
  mensagem?: string;
}

export interface Payment {
  id: number;
  match_id: number;
  valor: number;
  status: 'pendente' | 'pago' | 'expirado';
  qr_code_url?: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  tipo: 'motorista' | 'shipper';
  nome: string;
}

export interface SignupPayload {
  email: string;
  senha: string;
  tipo: 'motorista' | 'shipper';
  nome: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Extend API with auth methods
export const apiService = {
  ...api,
  getMe: () => api.get('/auth/me'),
  login: (email: string, senha: string) =>
    api.post('/auth/login', { username: email, password: senha }),
  signup: (user: SignupPayload) => api.post('/auth/register', user),
};

export default api;
