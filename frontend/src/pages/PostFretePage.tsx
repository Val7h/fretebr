import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import type { CreateFretePayload } from '../services/api';
import { FreteForm } from '../components/FreteForm';

export const PostFretePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Check if user is motorista
  if (currentUser?.tipo !== 'motorista') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Acesso Negado</h1>
          <p className="text-gray-700 mb-6">
            Apenas motoristas podem postar fretes. Você está logado como {currentUser?.tipo}.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
          >
            Voltar ao Dashboard
          </button>
        </div>
      </div>
    );
  }

  const handleSubmit = async (data: CreateFretePayload) => {
    setError('');
    setIsLoading(true);

    try {
      await apiService.createFrete(data);
      // Show success message would go here (toast)
      navigate('/meus-fretes');
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao postar frete. Tente novamente.';
      setError(errorMessage);
      console.error('Error posting frete:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Postar Novo Frete</h2>
          <p className="text-gray-600 mb-8">
            Preencha os detalhes do frete que deseja ofertar para os clientes.
          </p>

          <FreteForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
            error={error}
          />
        </div>
      </main>
    </div>
  );
};
