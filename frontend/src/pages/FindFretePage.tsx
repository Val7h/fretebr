import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService, Frete } from '../services/api';

export const FindFretePage: React.FC = () => {
  const navigate = useNavigate();
  const [fretes, setFretes] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

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

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-600">Carregando fretes...</div>
            </div>
          ) : fretes.length === 0 ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-600">Nenhum frete disponível no momento</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {fretes.map(frete => (
                <div
                  key={frete.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition cursor-pointer"
                  onClick={() => navigate(`/frete/${frete.id}`)}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Origem</p>
                      <p className="text-lg font-semibold text-gray-900">{frete.origem}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        frete.status === 'disponível'
                          ? 'bg-green-100 text-green-800'
                          : frete.status === 'aceito'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {frete.status}
                    </span>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-600">Destino</p>
                    <p className="text-lg font-semibold text-gray-900">{frete.destino}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4 py-4 border-t border-gray-200">
                    <div>
                      <p className="text-xs text-gray-600">Peso</p>
                      <p className="text-sm font-semibold text-gray-900">{frete.peso_kg} kg</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Valor</p>
                      <p className="text-sm font-semibold text-gray-900">
                        R$ {frete.valor_r.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  <button
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
                    onClick={e => {
                      e.stopPropagation();
                      navigate(`/frete/${frete.id}`);
                    }}
                  >
                    Ver Detalhes
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
