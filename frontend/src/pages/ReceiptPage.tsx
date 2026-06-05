import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import type { Match } from '../services/matchesApi';

export const ReceiptPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [match, setMatch] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

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
        err instanceof Error ? err.message : 'Erro ao carregar recibo';
      setError(errorMessage);
      console.error('Error fetching match:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadReceipt = () => {
    // Generate PDF receipt (optional - can be enhanced with jsPDF library)
    const receiptContent = generateReceiptHTML();
    const blob = new Blob([receiptContent], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `recibo-${match?.id}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const generateReceiptHTML = () => {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .receipt { max-width: 600px; margin: 0 auto; border: 1px solid #ccc; padding: 20px; }
            .header { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
            .section { margin-bottom: 20px; }
            .label { color: #666; font-size: 12px; margin-bottom: 4px; }
            .value { font-weight: bold; font-size: 14px; }
            .footer { text-align: center; color: #999; font-size: 11px; margin-top: 30px; }
          </style>
        </head>
        <body>
          <div class="receipt">
            <div class="header">
              <h1>FreteBR</h1>
              <p>Recibo de Pagamento</p>
            </div>
            <div class="section">
              <div class="label">Transaction ID</div>
              <div class="value">${match?.id}</div>
            </div>
            <div class="section">
              <div class="label">Valor Pago</div>
              <div class="value">R$ ${match?.frete?.valor_r.toFixed(2)}</div>
            </div>
            <div class="section">
              <div class="label">Método de Pagamento</div>
              <div class="value">Pix</div>
            </div>
            <div class="section">
              <div class="label">Data e Hora</div>
              <div class="value">${new Date().toLocaleDateString('pt-BR')} ${new Date().toLocaleTimeString('pt-BR')}</div>
            </div>
            <div class="footer">
              <p>Este recibo foi gerado automaticamente pelo sistema FreteBR</p>
            </div>
          </div>
        </body>
      </html>
    `;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando recibo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
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
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
            {error}
          </div>
        )}

        {!match ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Recibo não encontrado</h2>
            <button
              onClick={() => navigate('/meus-matches')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Voltar aos Matches
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="bg-white rounded-lg shadow-md p-8 text-center border-4 border-green-500">
              <div className="text-6xl mb-4">✅</div>
              <h1 className="text-3xl font-bold text-green-600 mb-2">Pagamento Confirmado</h1>
              <p className="text-gray-600">Seu pagamento foi recebido com sucesso</p>
            </div>

            {/* Receipt - Invoice Style */}
            <div className="bg-white rounded-lg shadow-md p-8 border-2 border-gray-200">
              {/* Receipt Header */}
              <div className="text-center mb-8 pb-8 border-b-2 border-gray-300">
                <h2 className="text-2xl font-bold text-gray-900">FreteBR</h2>
                <p className="text-sm text-gray-600">Recibo de Pagamento</p>
              </div>

              {/* Transaction Details */}
              <div className="space-y-6">
                {/* Transaction ID */}
                <div className="flex justify-between border-b border-gray-200 pb-3">
                  <span className="text-gray-600">Transaction ID</span>
                  <span className="font-mono font-semibold text-gray-900">{match.id}</span>
                </div>

                {/* Amount */}
                <div className="flex justify-between border-b border-gray-200 pb-3">
                  <span className="text-gray-600">Valor Pago</span>
                  <span className="text-2xl font-bold text-green-600">
                    R$ {match.frete?.valor_r.toFixed(2)}
                  </span>
                </div>

                {/* Payment Method */}
                <div className="flex justify-between border-b border-gray-200 pb-3">
                  <span className="text-gray-600">Método de Pagamento</span>
                  <span className="font-semibold text-gray-900">Pix</span>
                </div>

                {/* Date and Time */}
                <div className="flex justify-between border-b border-gray-200 pb-3">
                  <span className="text-gray-600">Data e Hora</span>
                  <span className="font-semibold text-gray-900">
                    {new Date().toLocaleDateString('pt-BR')} {new Date().toLocaleTimeString('pt-BR', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>

                {/* Separator */}
                <div className="border-t-2 border-gray-300 pt-6"></div>

                {/* Frete Details */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Detalhes do Frete</h3>
                  <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600">Origem</p>
                      <p className="font-semibold text-gray-900">{match.frete?.origem}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Destino</p>
                      <p className="font-semibold text-gray-900">{match.frete?.destino}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Peso</p>
                      <p className="font-semibold text-gray-900">{match.frete?.peso_kg} kg</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="font-semibold text-green-600 flex items-center gap-1">
                        <span>Entregue</span>
                        <span>✅</span>
                      </p>
                    </div>
                  </div>
                </div>

                {/* Participants */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-xs text-blue-600 font-semibold mb-2">REMETENTE (Shipper)</p>
                    <p className="font-semibold text-gray-900">{match.shipper?.nome}</p>
                    <p className="text-sm text-gray-600">{match.shipper?.email}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-xs text-green-600 font-semibold mb-2">TRANSPORTISTA (Motorista)</p>
                    <p className="font-semibold text-gray-900">{match.motorista?.nome}</p>
                    <p className="text-sm text-gray-600">{match.motorista?.email}</p>
                  </div>
                </div>
              </div>

              {/* Footer Note */}
              <div className="mt-8 pt-6 border-t border-gray-200 text-center">
                <p className="text-xs text-gray-500">
                  Este é um recibo oficial do sistema FreteBR. Mantém uma cópia para seus registros.
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                onClick={() => navigate(`/match/${match.id}/rating`)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition"
              >
                Ir para Avaliação ⭐
              </button>
              <button
                onClick={handleDownloadReceipt}
                className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition"
              >
                Baixar Recibo 📄
              </button>
            </div>

            <button
              onClick={() => navigate('/meus-matches')}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-3 px-4 rounded-lg transition"
            >
              Voltar aos Matches
            </button>
          </div>
        )}
      </main>
    </div>
  );
};
