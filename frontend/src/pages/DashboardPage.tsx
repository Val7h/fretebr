import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const DashboardPage: React.FC = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getTipoLabel = (tipo: string) => {
    return tipo === 'motorista' ? 'Motorista' : 'Shipper';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Bem-vindo, {currentUser?.nome}!
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            {/* User Info Card */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Informações da Conta
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="text-lg font-medium text-gray-900">
                    {currentUser?.email}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Nome</p>
                  <p className="text-lg font-medium text-gray-900">
                    {currentUser?.nome}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tipo de Usuário</p>
                  <div className="flex items-center mt-1">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                        currentUser?.tipo === 'motorista'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {getTipoLabel(currentUser?.tipo || '')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Role-based Actions Card */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Ações Rápidas
              </h3>
              <div className="space-y-3">
                {currentUser?.tipo === 'motorista' ? (
                  <>
                    <button
                      onClick={() => navigate('/postar-frete')}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition text-left"
                    >
                      Postar Novo Frete
                    </button>
                    <button
                      onClick={() => navigate('/meus-fretes')}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition text-left"
                    >
                      Meus Fretes
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => navigate('/procurar-fretes')}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition text-left"
                  >
                    Procurar Fretes
                  </button>
                )}
                <button
                  onClick={() => navigate('/meus-matches')}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition text-left"
                >
                  Meus Matches
                </button>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <p className="text-4xl font-bold text-blue-600">0</p>
              <p className="text-gray-600 mt-2">Fretes Ativos</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <p className="text-4xl font-bold text-green-600">R$ 0,00</p>
              <p className="text-gray-600 mt-2">Ganhos Totais</p>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
              <p className="text-4xl font-bold text-orange-600">0</p>
              <p className="text-gray-600 mt-2">Entregas Concluídas</p>
            </div>
          </div>

          {/* Payment History Card */}
          <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Histórico de Pagamentos</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Nenhum pagamento realizado</p>
                  <p className="text-sm text-gray-600">Seus pagamentos aparecerão aqui</p>
                </div>
                <span className="text-gray-400">📋</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
