import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import type { Match, MatchStatus } from '../services/matchesApi';
import { useAuth } from '../context/AuthContext';

export const MyMatchesPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [matches, setMatches] = useState<Match[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<MatchStatus | 'all'>('all');

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await matchesApi.getMatches();
      setMatches(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar matches';
      setError(errorMessage);
      console.error('Error fetching matches:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredMatches = matches.filter((match) => {
    if (selectedFilter === 'all') return true;
    return match.status === selectedFilter;
  });

  const getStatusColor = (status: MatchStatus) => {
    switch (status) {
      case 'pendente':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'aceito':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'em_entrega':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'finalizado':
        return 'bg-gray-50 border-gray-200 text-gray-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getStatusBadge = (status: MatchStatus) => {
    const badges: Record<MatchStatus, { emoji: string; label: string }> = {
      pendente: { emoji: '🔴', label: 'Pendente' },
      aceito: { emoji: '🟢', label: 'Aceito' },
      em_entrega: { emoji: '🔵', label: 'Em Entrega' },
      finalizado: { emoji: '⚪', label: 'Finalizado' },
    };
    return badges[status];
  };

  const getOtherUserName = (match: Match) => {
    if (currentUser?.tipo === 'motorista') {
      return match.shipper?.nome || 'Shipper Desconhecido';
    } else {
      return match.motorista?.nome || 'Motorista Desconhecido';
    }
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
            Voltar
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Meus Matches</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
              {error}
            </div>
          )}

          {/* Filter Buttons */}
          <div className="flex flex-wrap gap-2 mb-8">
            <button
              onClick={() => setSelectedFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFilter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setSelectedFilter('pendente')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFilter === 'pendente'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              Pendentes
            </button>
            <button
              onClick={() => setSelectedFilter('aceito')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFilter === 'aceito'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              Aceito
            </button>
            <button
              onClick={() => setSelectedFilter('em_entrega')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFilter === 'em_entrega'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              Em Entrega
            </button>
            <button
              onClick={() => setSelectedFilter('finalizado')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedFilter === 'finalizado'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              Finalizado
            </button>
          </div>

          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-600">Carregando matches...</div>
            </div>
          ) : filteredMatches.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-600 mb-4">Nenhum match encontrado</p>
              <button
                onClick={() => navigate('/procurar-fretes')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
              >
                {currentUser?.tipo === 'shipper' ? 'Procurar Fretes' : 'Voltar ao Dashboard'}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMatches.map((match) => {
                const badge = getStatusBadge(match.status);
                const otherUserName = getOtherUserName(match);

                return (
                  <div
                    key={match.id}
                    className={`border rounded-lg p-6 hover:shadow-lg transition ${getStatusColor(
                      match.status
                    )}`}
                  >
                    {/* Route */}
                    <div className="mb-4">
                      <h3 className="text-lg font-bold text-gray-900">
                        {match.frete?.origem} → {match.frete?.destino}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {match.frete?.peso_kg} kg • R$ {match.frete?.valor_r.toFixed(2)}
                      </p>
                    </div>

                    {/* Other User Info */}
                    <div className="mb-4 py-4 border-t border-current border-opacity-20">
                      <p className="text-sm text-gray-600 mb-1">
                        {currentUser?.tipo === 'motorista' ? 'Shipper' : 'Motorista'}
                      </p>
                      <p className="font-semibold text-gray-900">{otherUserName}</p>
                    </div>

                    {/* Status Badge */}
                    <div className="mb-4 flex items-center gap-2">
                      <span className="text-xl">{badge.emoji}</span>
                      <span className="text-sm font-medium">{badge.label}</span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/match/${match.id}/chat`)}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-3 rounded-lg transition text-sm"
                      >
                        Ir para Chat
                      </button>
                      <button
                        onClick={() => navigate(`/match/${match.id}`)}
                        className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-3 rounded-lg transition text-sm"
                      >
                        Ver Detalhes
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
