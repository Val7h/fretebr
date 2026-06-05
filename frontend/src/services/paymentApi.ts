import api from './api';

export interface Payment {
  id: string;
  match_id: string;
  amount: number;
  status: 'pending' | 'paid' | 'expired';
  qr_code_url?: string;
  pix_key: string;
  created_at: string;
  expires_at: string;
}

export interface Receipt {
  id: string;
  match_id: string;
  transaction_id: string;
  amount: number;
  payment_method: string;
  paid_at: string;
  shipper_name: string;
  motorista_name: string;
  frete_origem: string;
  frete_destino: string;
  frete_peso_kg: number;
  frete_status: string;
}

export interface Rating {
  id?: string;
  match_id: string;
  rating: number; // 1-5
  feedback?: string;
  created_at?: string;
}

export const paymentApi = {
  async createPayment(match_id: string, amount: number): Promise<Payment> {
    const response = await api.post<Payment>('/payments', {
      match_id,
      amount,
    });
    return response.data;
  },

  async getPaymentStatus(payment_id: string): Promise<Payment> {
    const response = await api.get<Payment>(`/payments/${payment_id}`);
    return response.data;
  },

  async getReceipt(match_id: string): Promise<Receipt> {
    const response = await api.get<Receipt>(`/matches/${match_id}/receipt`);
    return response.data;
  },

  async submitRating(match_id: string, rating: number, feedback?: string): Promise<Rating> {
    const response = await api.post<Rating>('/ratings', {
      match_id,
      rating,
      feedback,
    });
    return response.data;
  },

  async getRating(match_id: string): Promise<Rating | null> {
    try {
      const response = await api.get<Rating>(`/ratings/match/${match_id}`);
      return response.data;
    } catch {
      return null;
    }
  },
};
