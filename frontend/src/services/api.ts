import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8001/api';

// Cookie mode: backend seta cookies httpOnly em /auth/login + /auth/signup.
// Frontend NAO precisa ler/gravar tokens no localStorage.
// Ativado quando VITE_AUTH_COOKIE_MODE=true.
export const COOKIE_MODE = ((import.meta as any).env?.VITE_AUTH_COOKIE_MODE || 'false')
  .toLowerCase() === 'true';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // CORS: envia cookies cross-origin (backend precisa allow_credentials=True)
  withCredentials: COOKIE_MODE,
});

// Request interceptor
api.interceptors.request.use((config) => {
  if (!COOKIE_MODE) {
    // Modo legacy: anexa Authorization Bearer do localStorage
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  // Em COOKIE_MODE o navegador anexa fretebr_access automaticamente
  return config;
});

// Response interceptor: 401 -> tentar refresh uma vez
let _isRefreshing = false;
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest: any = error.config;
    const has401 = error.response?.status === 401;
    const canRetry =
      has401 &&
      !originalRequest._retried &&
      !originalRequest.url?.includes('/auth/refresh') &&
      !originalRequest.url?.includes('/auth/login');

    if (!canRetry) return Promise.reject(error);
    if (_isRefreshing) return Promise.reject(error);

    originalRequest._retried = true;
    _isRefreshing = true;

    try {
      let refreshPayload: any = {};
      if (!COOKIE_MODE) {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) throw new Error('no refresh');
        refreshPayload = { refresh_token: refresh };
      }
      // Em COOKIE_MODE o cookie fretebr_refresh acompanha automaticamente
      const r = await axios.post(`${API_BASE_URL}/auth/refresh`, refreshPayload, {
        withCredentials: COOKIE_MODE,
      });
      if (!COOKIE_MODE) {
        const newAccess = r.data.access_token;
        const newRefresh = r.data.refresh_token;
        if (newAccess) localStorage.setItem('jwt_token', newAccess);
        if (newRefresh) localStorage.setItem('refresh_token', newRefresh);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      }
      return api(originalRequest);
    } catch (e) {
      if (!COOKIE_MODE) {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
      }
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      return Promise.reject(e);
    } finally {
      _isRefreshing = false;
    }
  }
);

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
  motorista_id: number;
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
  password: string;
  tipo: 'motorista' | 'shipper';
  nome: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Extend API with auth and frete methods
export const apiService = {
  ...api,
  // Auth endpoints
  getMe: () => api.get('/auth/me').then(res => res.data),
  login: (payload: { email: string; password: string }) =>
    api.post('/auth/login', payload).then(res => res.data),
  signup: (user: SignupPayload) => api.post('/auth/signup', user).then(res => res.data),
  logout: () => api.post('/auth/logout').then(res => res.data).catch(() => null),

  // Frete endpoints
  createFrete: (payload: CreateFretePayload) =>
    api.post('/fretes', payload).then(res => res.data),
  getMyFretes: () =>
    api.get('/fretes/meus-fretes').then(res => res.data),
  getAvailableFretes: () =>
    api.get('/fretes').then(res => res.data),
  getFrete: (id: number) =>
    api.get(`/fretes/${id}`).then(res => res.data),
  updateFrete: (id: number, payload: Partial<CreateFretePayload>) =>
    api.put(`/fretes/${id}`, payload).then(res => res.data),
  deleteFrete: (id: number) =>
    api.delete(`/fretes/${id}`),

  // Match/Proposal endpoints
  createProposal: (freteId: number, valorProposta: number, mensagem: string = '') =>
    api.post(`/matches/?frete_id=${freteId}&valor_proposta=${valorProposta}&mensagem=${mensagem}`).then(res => res.data),
  getFreteProposals: (freteId: number) =>
    api.get(`/matches/frete/${freteId}`).then(res => res.data),
  getMyProposals: () =>
    api.get('/matches/my-proposals').then(res => res.data),
  acceptProposal: (matchId: number) =>
    api.put(`/matches/${matchId}/accept`).then(res => res.data),
  rejectProposal: (matchId: number) =>
    api.put(`/matches/${matchId}/reject`).then(res => res.data),
  getMatch: (matchId: number) =>
    api.get(`/matches/${matchId}`).then(res => res.data),

  // Message endpoints
  getMatchMessages: (matchId: number) =>
    api.get(`/messages/match/${matchId}`).then(res => res.data),
  sendMessage: (matchId: number, conteudo: string) =>
    api.post(`/messages/match/${matchId}`, { conteudo }).then(res => res.data),
  deleteMessage: (messageId: number) =>
    api.delete(`/messages/${messageId}`).then(res => res.data),

  // Rating endpoints
  rateMotorista: (motorista_id: number, stars: number, review_text: string = '', frete_id?: number, match_id?: number) =>
    api.post('/ratings/motorista', { rated_user_id: motorista_id, stars, review_text, frete_id, match_id }).then(res => res.data),
  rateShipper: (shipper_id: number, stars: number, review_text: string = '', frete_id?: number, match_id?: number) =>
    api.post('/ratings/shipper', { rated_user_id: shipper_id, stars, review_text, frete_id, match_id }).then(res => res.data),
  getMotoristaRatings: (motorista_id: number) =>
    api.get(`/ratings/motorista/${motorista_id}/ratings`).then(res => res.data),
  getShipperRatings: (shipper_id: number) =>
    api.get(`/ratings/shipper/${shipper_id}/ratings`).then(res => res.data),
  getMotoristaReviews: (motorista_id: number, limit: number = 10, offset: number = 0) =>
    api.get(`/ratings/motorista/${motorista_id}/reviews?limit=${limit}&offset=${offset}`).then(res => res.data),
  getShipperReviews: (shipper_id: number, limit: number = 10, offset: number = 0) =>
    api.get(`/ratings/shipper/${shipper_id}/reviews?limit=${limit}&offset=${offset}`).then(res => res.data),
  getUserProfile: (user_id: number) =>
    api.get(`/ratings/user/${user_id}/profile`).then(res => res.data),

  // Notification endpoints
  getNotifications: (limit: number = 20, offset: number = 0, unreadOnly: boolean = false) =>
    api.get(`/notifications?limit=${limit}&offset=${offset}&unread_only=${unreadOnly}`).then(res => res.data),
  markAsRead: (notificationId: number) =>
    api.put(`/notifications/${notificationId}/read`).then(res => res.data),
  markAllAsRead: () =>
    api.put('/notifications/read-all').then(res => res.data),
  deleteNotification: (notificationId: number) =>
    api.delete(`/notifications/${notificationId}`).then(res => res.data),
  getUnreadCount: () =>
    api.get('/notifications/count/unread').then(res => res.data),

  // Transaction endpoints
  getTransactions: (limit: number = 20, offset: number = 0, status?: string) =>
    api.get(`/transactions?limit=${limit}&offset=${offset}${status ? `&status=${status}` : ''}`).then(res => res.data),
  getTransaction: (transactionId: number) =>
    api.get(`/transactions/${transactionId}`).then(res => res.data),
  getTransactionStatistics: () =>
    api.get('/transactions/statistics/summary').then(res => res.data),

  // Payment endpoints (Pix MP)
  createPayment: (matchId: number, amount: number) =>
    api.post('/payments', { match_id: matchId, amount }).then(res => res.data),
  getPaymentStatus: (transactionId: number) =>
    api.get(`/payments/${transactionId}`).then(res => res.data),
  simulatePaymentPaid: (transactionId: number) =>
    api.post(`/payments/${transactionId}/simulate-paid`).then(res => res.data),
  getReceipt: (matchId: number) =>
    api.get(`/payments/${matchId}/receipt`).then(res => res.data),
};

export default api;
