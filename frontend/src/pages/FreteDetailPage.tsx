import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import type { Frete } from '../services/api';
import { matchesApi } from '../services/matchesApi';
import { useAuth } from '../context/AuthContext';

export const FreteDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [frete, setFrete] = useState<Frete | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (id) {
      fetchFrete(id);
    }
  }, [id]);

  const fetchFrete = async (freteId: string) => {
    setIsLoading(true);
    setError('');
    try {
      const data = await apiService.getFreteById(freteId);
      setFrete(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar frete';
      setError(errorMessage);
      console.error('Error fetching frete:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!frete) return;
    if (window.confirm('Tem certeza que deseja cancelar este frete?')) {
      setIsDeleting(true);
      try {
        await apiService.deleteFrete(frete.id);
        navigate('/meus-fretes');
      } catch (err) {
        setError('Erro ao cancelar frete');
        console.error('Error deleting frete:', err);
        setIsDeleting(false);
      }
    }
  };

  const handleAcceptFrete = async () => {
    if (!frete) return;
    setIsAccepting(true);
    setError('');
    try {
      await matchesApi.acceptFrete({ frete_id: frete.id });
      setSuccessMessage('Frete aceito com sucesso! Redirecionando para Meus Matches...');
      setTimeout(() => {
        navigate('/meus-matches');
      }, 2000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao aceitar frete';
      setError(errorMessage);
      console.error('Error accepting frete:', err);
      setIsAccepting(false);
    }
  };

  const isMotoristaOwner = currentUser?.tipo === 'motorista' && currentUser?.id === frete?.motorista_id;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
          <button
            onClick={() => navigate(-1)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Voltar
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700 mb-6">
            {successMessage}
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-600">Carregando frete...</div>
          </div>
        ) : !frete ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Frete não encontrado</h2>
            <button
              onClick={() => navigate(-1)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Voltar
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8">
            {/* Route Info */}
            <div className="mb-8 pb-8 border-b border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-4xl font-bold text-gray-900">
                  {frete.origem} → {frete.destino}
                </h1>
                <span
                  className={`px-4 py-2 rounded-full text-lg font-medium ${
                    frete.status === 'disponível'
                      ? 'bg-green-100 text-green-800'
                      : frete.status === 'aceito'
                      ? 'bg-blue-100 text-blue-800'
                      : frete.status === 'entregue'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {frete.status}
                </span>
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-blue-50 rounded-lg p-6">
                <p className="text-sm text-gray-600 mb-2">Peso</p>
                <p className="text-3xl font-bold text-blue-600">{frete.peso_kg} kg</p>
              </div>
              <div className="bg-green-50 rounded-lg p-6">
                <p className="text-sm text-gray-600 mb-2">Valor</p>
                <p className="text-3xl font-bold text-green-600">
                  R$ {frete.valor_r.toFixed(2)}
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-6">
                <p className="text-sm text-gray-600 mb-2">Postado em</p>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(frete.created_at).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>

            {/* Description */}
            {frete.descricao && (
              <div className="mb-8 pb-8 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Descrição</h3>
                <p className="text-gray-700 leading-relaxed">{frete.descricao}</p>
              </div>
            )}

            {/* Driver Info - Placeholder */}
            <div className="mb-8 pb-8 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações do Motorista</h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <p className="text-gray-600">Motorista: (será implementado)</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => navigate(-1)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition"
              >
                Voltar
              </button>

              {currentUser?.tipo === 'shipper' && frete.status === 'disponível' && (
                <button
                  onClick={handleAcceptFrete}
                  disabled={isAccepting}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
                >
                  {isAccepting ? 'Aceitando...' : 'Quero Este Frete'}
                </button>
              )}

              {isMotoristaOwner && frete.status === 'disponível' && (
                <>
                  <button
                    onClick={() => navigate(`/frete/${frete.id}/edit`)}
                    className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg transition"
                  >
                    Editar
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
                  >
                    {isDeleting ? 'Cancelando...' : 'Cancelar Frete'}
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
