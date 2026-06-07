import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  // 🔧 Demo user if not authenticated
  const user = currentUser || {
    id: 'demo-user',
    nome: 'Visitante',
    email: 'demo@fretebr.com',
    tipo: 'motorista' as const,
  };

  const getTipoLabel = (tipo: string) => {
    return tipo === 'motorista' ? '🚚 Motorista' : '📦 Shipper';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">🚚 FreteBR</h1>
            <p className="text-sm text-gray-600 mt-1">Marketplace de fretes inteligente</p>
          </div>
          {currentUser && (
            <button
              onClick={() => {
                localStorage.removeItem('jwt_token');
                window.location.reload();
              }}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200"
            >
              Logout
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-2">
            Bem-vindo, {user.nome}! 👋
          </h2>
          <p className="text-lg text-gray-600">
            {currentUser
              ? 'Você está autenticado. Aqui está seu painel.'
              : 'Você está visitando sem fazer login. Aqui está um preview do dashboard.'}
          </p>
        </div>

        {/* User Info Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-md p-8 border border-gray-100">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6">📋 Suas Informações</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-medium text-gray-600">Email</label>
                <p className="text-lg font-semibold text-gray-900 mt-1">{user.email}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Nome</label>
                <p className="text-lg font-semibold text-gray-900 mt-1">{user.nome}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Tipo de Usuário</label>
                <p className="text-lg font-semibold text-gray-900 mt-1">{getTipoLabel(user.tipo)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-600">Status</label>
                <p className="text-lg font-semibold text-green-600 mt-1">✅ Ativo</p>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-md p-8 text-white">
            <h3 className="text-xl font-semibold mb-6">📊 Resumo</h3>
            <div className="space-y-4">
              <div>
                <p className="text-blue-100 text-sm">Fretes Ativos</p>
                <p className="text-3xl font-bold">0</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm">Ganhos Totais</p>
                <p className="text-3xl font-bold">R$ 0,00</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="bg-white rounded-xl shadow-md p-8 border border-gray-100 mb-8">
          <h3 className="text-2xl font-semibold text-gray-900 mb-6">🎯 Ações Rápidas</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/procurar-fretes')}
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 shadow-md"
            >
              🔍 Procurar Fretes
            </button>
            <button
              onClick={() => navigate('/postar-frete')}
              className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 shadow-md"
            >
              📝 Postar Frete
            </button>
            <button
              onClick={() => navigate('/meus-fretes')}
              className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 shadow-md"
            >
              📦 Meus Fretes
            </button>
            <button
              onClick={() => navigate('/meus-matches')}
              className="bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-semibold py-4 px-6 rounded-lg transition transform hover:scale-105 shadow-md"
            >
              🤝 Meus Matches
            </button>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-4xl mb-3">⚡</div>
            <h4 className="font-bold text-gray-900 mb-2">Rápido</h4>
            <p className="text-gray-600 text-sm">Encontre fretes em segundos</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-4xl mb-3">🔒</div>
            <h4 className="font-bold text-gray-900 mb-2">Seguro</h4>
            <p className="text-gray-600 text-sm">Plataforma confiável e segura</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
            <div className="text-4xl mb-3">💰</div>
            <h4 className="font-bold text-gray-900 mb-2">Lucrativo</h4>
            <p className="text-gray-600 text-sm">Maximize seus ganhos</p>
          </div>
        </div>
      </main>
    </div>
  );
};
