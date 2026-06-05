import axios from 'axios';
import type { AxiosInstance } from 'axios';

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

export type MatchStatus = 'pendente' | 'aceito' | 'em_entrega' | 'finalizado';

export interface Match {
  id: string;
  frete_id: string;
  shipper_id: string;
  motorista_id: string;
  status: MatchStatus;
  created_at: string;
  updated_at: string;
  frete?: {
    id: string;
    origem: string;
    destino: string;
    peso_kg: number;
    valor_r: number;
    descricao?: string;
    motorista_id: string;
  };
  shipper?: {
    id: string;
    nome: string;
    email: string;
  };
  motorista?: {
    id: string;
    nome: string;
    email: string;
  };
}

export interface Message {
  id: string;
  match_id: string;
  sender_id: string;
  sender_nome: string;
  content: string;
  created_at: string;
}

export interface AcceptFretePayload {
  frete_id: string;
}

export interface UpdateMatchStatusPayload {
  status: MatchStatus;
}

export const matchesApi = {
  async getMatches(): Promise<Match[]> {
    const response = await api.get<Match[]>('/matches');
    return response.data;
  },

  async getMatchById(id: string): Promise<Match> {
    const response = await api.get<Match>(`/matches/${id}`);
    return response.data;
  },

  async acceptFrete(payload: AcceptFretePayload): Promise<Match> {
    const response = await api.post<Match>('/matches', payload);
    return response.data;
  },

  async updateMatchStatus(id: string, payload: UpdateMatchStatusPayload): Promise<Match> {
    const response = await api.put<Match>(`/matches/${id}/status`, payload);
    return response.data;
  },

  async getMessages(matchId: string): Promise<Message[]> {
    const response = await api.get<Message[]>(`/matches/${matchId}/messages`);
    return response.data;
  },

  async sendMessage(matchId: string, content: string): Promise<Message> {
    const response = await api.post<Message>(`/matches/${matchId}/messages`, { content });
    return response.data;
  },
};

export default api;
