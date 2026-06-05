import api from './api';
import { Frete, CreateFretePayload } from './api';

export const fretesApi = {
  async getFretes(): Promise<Frete[]> {
    const response = await api.get<Frete[]>('/fretes');
    return response.data;
  },

  async getFreteById(id: string): Promise<Frete> {
    const response = await api.get<Frete>(`/fretes/${id}`);
    return response.data;
  },

  async createFrete(payload: CreateFretePayload): Promise<Frete> {
    const response = await api.post<Frete>('/fretes', payload);
    return response.data;
  },

  async updateFrete(id: string, payload: Partial<CreateFretePayload>): Promise<Frete> {
    const response = await api.put<Frete>(`/fretes/${id}`, payload);
    return response.data;
  },

  async deleteFrete(id: string): Promise<void> {
    await api.delete(`/fretes/${id}`);
  },

  async getMyFretes(): Promise<Frete[]> {
    const response = await api.get<Frete[]>('/meus-fretes');
    return response.data;
  },
};

export default fretesApi;
