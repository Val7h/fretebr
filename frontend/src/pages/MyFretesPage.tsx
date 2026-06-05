import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, Frete } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const MyFretesPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [fretes, setFretes] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchMyFretes();
  }, []);

  const fetchMyFretes = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await apiService.getMyFretes();
      setFretes(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar seus fretes';
      setError(errorMessage);
      console.error('Error fetching my fretes:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredFretes =
    filterStatus === 'all' ? fretes : fretes.filter(f => f.status === filterStatus);

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja cancelar este frete?')) {
      try {
        await apiService.deleteFrete(id);
        setFretes(fretes.filter(f => f.id !== id));
      } catch (err) {
        setError('Erro ao cancelar frete');
        console.error('Error deleting frete:', err);
      }
    }
  };

  // Check if user is motorista
  if (currentUser?.tipo !== 'motorista') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Acesso Negado</h1>
          <p className="text-gray-700 mb-6">
            Apenas motoristas podem visualizar seus fretes.
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
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Meus Fretes</h2>
              <p className="text-gray-600 mt-2">
                Gerencie os fretes que você postou
              </p>
            </div>
            <button
              onClick={() => navigate('/postar-frete')}
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Postar Novo Frete
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
              {error}
            </div>
          )}

          {/* Filter */}
          <div className="mb-6">
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
              Filtrar por Status
            </label>
            <select
              id="status-filter"
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Todos</option>
              <option value="disponível">Disponível</option>
              <option value="aceito">Aceito</option>
              <option value="entregue">Entregue</option>
              <option value="cancelado">Cancelado</option>
            </select>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-600">Carregando fretes...</div>
            </div>
          ) : filteredFretes.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-gray-600 mb-6">
                {filterStatus === 'all'
                  ? 'Você ainda não postou nenhum frete'
                  : `Nenhum frete com status "${filterStatus}"`}
              </p>
              {filterStatus === 'all' && (
                <button
                  onClick={() => navigate('/postar-frete')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
                >
                  Postar Seu Primeiro Frete
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredFretes.map(frete => (
                <div
                  key={frete.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {frete.origem} → {frete.destino}
                        </h3>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
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
                      <p className="text-sm text-gray-600">
                        Postado em {new Date(frete.created_at).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">
                        R$ {frete.valor_r.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-600">{frete.peso_kg} kg</p>
                    </div>
                  </div>

                  {frete.descricao && (
                    <p className="text-gray-700 mb-4 text-sm">{frete.descricao}</p>
                  )}

                  <div className="flex gap-3">
                    <button
                      onClick={() => navigate(`/frete/${frete.id}`)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
                    >
                      Ver Detalhes
                    </button>
                    {frete.status === 'disponível' && (
                      <>
                        <button
                          onClick={() => navigate(`/frete/${frete.id}`)}
                          className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded-lg transition"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(frete.id)}
                          className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition"
                        >
                          Cancelar
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
