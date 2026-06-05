import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import type { Match } from '../services/matchesApi';
import { MatchTimeline } from '../components/MatchTimeline';
import { useAuth } from '../context/AuthContext';

export const MatchDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [match, setMatch] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    if (id) {
      fetchMatch(id);
    }
  }, [id]);

  const fetchMatch = async (matchId: string) => {
    setIsLoading(true);
    setError('');
    try {
      const data = await matchesApi.getMatchById(matchId);
      setMatch(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar match';
      setError(errorMessage);
      console.error('Error fetching match:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateStatus = async (newStatus: 'aceito' | 'em_entrega' | 'finalizado') => {
    if (!match) return;
    setIsUpdating(true);
    try {
      const updated = await matchesApi.updateMatchStatus(match.id, { status: newStatus });
      setMatch(updated);
      if (newStatus === 'finalizado') {
        setTimeout(() => {
          navigate('/meus-matches');
        }, 2000);
      }
    } catch (err) {
      setError('Erro ao atualizar status do match');
      console.error('Error updating match status:', err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancelMatch = async () => {
    if (!match) return;
    if (window.confirm('Tem certeza que deseja cancelar este match?')) {
      setIsUpdating(true);
      try {
        await matchesApi.updateMatchStatus(match.id, { status: 'finalizado' });
        navigate('/meus-matches');
      } catch (err) {
        setError('Erro ao cancelar match');
        console.error('Error canceling match:', err);
        setIsUpdating(false);
      }
    }
  };

  const isMotoristaUser = currentUser?.tipo === 'motorista';
  const isMotoristaOwner = isMotoristaUser && match?.motorista_id === currentUser?.id;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
          <button
            onClick={() => navigate('/meus-matches')}
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

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-600">Carregando detalhes do match...</div>
          </div>
        ) : !match ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Match não encontrado</h2>
            <button
              onClick={() => navigate('/meus-matches')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Voltar
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8">
            {/* Frete Info Header */}
            <div className="mb-8 pb-8 border-b border-gray-200">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {match.frete?.origem} → {match.frete?.destino}
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Peso</p>
                  <p className="text-2xl font-bold text-blue-600">{match.frete?.peso_kg} kg</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Valor</p>
                  <p className="text-2xl font-bold text-green-600">
                    R$ {match.frete?.valor_r.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Data da Criação</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date(match.created_at).toLocaleDateString('pt-BR')}
                  </p>
                </div>
              </div>
            </div>

            {/* Timeline Section */}
            <div className="mb-8 pb-8 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">
                Status do Transporte
              </h3>
              <MatchTimeline currentStatus={match.status} />
            </div>

            {/* Other User Info */}
            <div className="mb-8 pb-8 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {isMotoristaUser ? 'Informações do Shipper' : 'Informações do Motorista'}
              </h3>
              <div className="bg-gray-50 rounded-lg p-6">
                <p className="text-sm text-gray-600 mb-2">Nome</p>
                <p className="text-lg font-semibold text-gray-900 mb-4">
                  {isMotoristaUser ? match.shipper?.nome : match.motorista?.nome}
                </p>
                <p className="text-sm text-gray-600 mb-2">Email</p>
                <p className="text-lg text-gray-900">
                  {isMotoristaUser ? match.shipper?.email : match.motorista?.email}
                </p>
              </div>
            </div>

            {/* Actions Section */}
            <div className="flex flex-col gap-3">
              <button
                onClick={() => navigate(`/match/${match.id}/chat`)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition"
                disabled={isUpdating}
              >
                Ir para Chat
              </button>

              {match.status === 'pendente' && (
                <>
                  <button
                    onClick={handleCancelMatch}
                    disabled={isUpdating}
                    className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition"
                  >
                    {isUpdating ? 'Cancelando...' : 'Cancelar Match'}
                  </button>
                </>
              )}

              {match.status === 'aceito' && isMotoristaOwner && (
                <button
                  onClick={() => handleUpdateStatus('em_entrega')}
                  disabled={isUpdating}
                  className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition"
                >
                  {isUpdating ? 'Atualizando...' : 'Marcar como Em Entrega'}
                </button>
              )}

              {match.status === 'em_entrega' && isMotoristaOwner && (
                <button
                  onClick={() => handleUpdateStatus('finalizado')}
                  disabled={isUpdating}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition"
                >
                  {isUpdating ? 'Finalizando...' : 'Marcar como Entregue'}
                </button>
              )}

              <button
                onClick={() => navigate('/meus-matches')}
                disabled={isUpdating}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition"
              >
                Voltar aos Matches
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
