import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, type Frete } from '../services/api';
import { FreteCard } from '../components/FreteCard';
import { useAuth } from '../context/AuthContext';

export const FindFretePage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [fretes, setFretes] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('disponível');
  const [filterCity, setFilterCity] = useState<string>('');

  useEffect(() => {
    fetchFretes();
  }, []);

  const fetchFretes = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await apiService.getFretes();
      setFretes(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar fretes';
      setError(errorMessage);
      console.error('Error fetching fretes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Filter fretes based on selected criteria
  const filteredFretes = fretes.filter(frete => {
    if (filterStatus !== 'all' && frete.status !== filterStatus) {
      return false;
    }
    if (filterCity && !frete.destino.includes(filterCity)) {
      return false;
    }
    return true;
  });

  // Get unique destination cities for filter
  const destinyCities = Array.from(
    new Set(fretes.map(f => f.destino.split('(')[1]?.replace(')', '') || ''))
  ).filter(Boolean);

  // Check if user is shipper
  if (currentUser?.tipo !== 'shipper') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Acesso Negado</h1>
          <p className="text-gray-700 mb-6">
            Apenas shippers podem procurar fretes. Você está logado como {currentUser?.tipo}.
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Procurar Fretes</h2>
          <p className="text-gray-600 mb-8">
            Encontre fretes disponíveis e aceite os que lhe interessam.
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
              {error}
            </div>
          )}

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 pb-8 border-b border-gray-200">
            <div>
              <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                id="status-filter"
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Todos</option>
                <option value="disponível">Disponível</option>
                <option value="aceito">Aceito</option>
                <option value="entregue">Entregue</option>
              </select>
            </div>
            <div>
              <label htmlFor="city-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Destino
              </label>
              <select
                id="city-filter"
                value={filterCity}
                onChange={e => setFilterCity(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Qualquer destino</option>
                {destinyCities.map(city => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-600">Carregando fretes...</div>
            </div>
          ) : filteredFretes.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  {fretes.length === 0
                    ? 'Nenhum frete disponível no momento'
                    : 'Nenhum frete encontrado com esses filtros'}
                </p>
                {fretes.length > 0 && (
                  <button
                    onClick={() => {
                      setFilterStatus('all');
                      setFilterCity('');
                    }}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Limpar filtros
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredFretes.map(frete => (
                <FreteCard key={frete.id} frete={frete} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
