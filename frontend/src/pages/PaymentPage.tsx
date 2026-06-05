import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import type { Match } from '../services/matchesApi';

interface Payment {
  id: string;
  match_id: string;
  amount: number;
  status: 'pending' | 'paid' | 'expired';
  qr_code_url?: string;
  pix_key: string;
  created_at: string;
  expires_at: string;
}

export const PaymentPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [match, setMatch] = useState<Match | null>(null);
  const [payment, setPayment] = useState<Payment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [pixKeyCopied, setPixKeyCopied] = useState(false);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    if (id) {
      fetchMatchAndCreatePayment(id);
    }
  }, [id]);

  const fetchMatchAndCreatePayment = async (matchId: string) => {
    setIsLoading(true);
    setError('');
    try {
      // Fetch match details
      const matchData = await matchesApi.getMatchById(matchId);
      setMatch(matchData);

      // Create payment
      if (matchData.frete?.valor_r) {
        const paymentData = await createPayment(matchId, matchData.frete.valor_r);
        setPayment(paymentData);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar dados do pagamento';
      setError(errorMessage);
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createPayment = async (matchId: string, amount: number): Promise<Payment> => {
    // Mock payment creation - in production, call backend API
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000); // 5 minutes from now
    return {
      id: `PAY-${Date.now()}`,
      match_id: matchId,
      amount,
      status: 'pending',
      qr_code_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', // Placeholder QR code
      pix_key: '00020126580014br.gov.bcb.pix',
      created_at: new Date().toISOString(),
      expires_at: expiresAt.toISOString(),
    };
  };

  // Calculate remaining time
  useEffect(() => {
    if (!payment) return;

    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const expiresAt = new Date(payment.expires_at).getTime();
      const difference = expiresAt - now;

      if (difference <= 0) {
        setPayment((prev) => (prev ? { ...prev, status: 'expired' } : null));
        setTimeLeft(0);
        setIsPolling(false);
      } else {
        setTimeLeft(Math.floor(difference / 1000)); // Convert to seconds
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [payment]);

  // Poll for payment status every 2 seconds
  useEffect(() => {
    if (!payment || payment.status === 'paid' || payment.status === 'expired') {
      return;
    }

    setIsPolling(true);

    const pollPaymentStatus = async () => {
      try {
        // Mock polling - in production, call: const status = await paymentApi.getPaymentStatus(payment.id);
        // For now, we'll simulate it by checking a flag
        if (Math.random() > 0.95) {
          // Simulate 5% chance payment is confirmed (for demo purposes)
          setPayment((prev) => (prev ? { ...prev, status: 'paid' } : null));
          setIsPolling(false);
        }
      } catch (err) {
        console.error('Error polling payment status:', err);
      }
    };

    const interval = setInterval(pollPaymentStatus, 2000);

    return () => clearInterval(interval);
  }, [payment]);

  // Auto-redirect when payment is completed
  useEffect(() => {
    if (payment?.status === 'paid' && id) {
      setTimeout(() => {
        navigate(`/match/${id}/receipt`);
      }, 1500);
    }
  }, [payment?.status, id, navigate]);

  const handleCopyPixKey = () => {
    if (payment?.pix_key) {
      navigator.clipboard.writeText(payment.pix_key);
      setPixKeyCopied(true);
      setTimeout(() => setPixKeyCopied(false), 2000);
    }
  };

  const handleCreateNewPayment = async () => {
    if (id) {
      setPayment(null);
      await fetchMatchAndCreatePayment(id);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados do pagamento...</p>
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
            onClick={() => navigate(`/match/${id}`)}
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

        {!match || !payment ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Erro ao carregar pagamento</h2>
            <button
              onClick={handleCreateNewPayment}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Tentar novamente
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h1 className="text-3xl font-bold text-gray-900">Confirmar Pagamento</h1>
            </div>

            {/* Frete Details */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Detalhes do Frete</h2>
              <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                <div>
                  <p className="text-gray-600">Origem</p>
                  <p className="font-semibold text-gray-900">{match.frete?.origem}</p>
                </div>
                <div>
                  <p className="text-gray-600">Destino</p>
                  <p className="font-semibold text-gray-900">{match.frete?.destino}</p>
                </div>
                <div>
                  <p className="text-gray-600">Peso</p>
                  <p className="font-semibold text-gray-900">{match.frete?.peso_kg} kg</p>
                </div>
                <div>
                  <p className="text-gray-600">Valor</p>
                  <p className="font-semibold text-green-600">R$ {match.frete?.valor_r.toFixed(2)}</p>
                </div>
              </div>
            </div>

            {/* Payment Status Section */}
            {payment.status === 'expired' ? (
              <div className="bg-white rounded-lg shadow-md p-6 border-2 border-red-500">
                <div className="text-center mb-6">
                  <div className="text-5xl mb-3">❌</div>
                  <h2 className="text-2xl font-bold text-red-600 mb-2">Pagamento Expirou</h2>
                  <p className="text-gray-600">
                    O código QR expirou. Crie um novo pagamento para continuar.
                  </p>
                </div>
                <button
                  onClick={handleCreateNewPayment}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition"
                >
                  Criar Novo Pagamento
                </button>
              </div>
            ) : payment.status === 'paid' ? (
              <div className="bg-white rounded-lg shadow-md p-6 border-2 border-green-500">
                <div className="text-center">
                  <div className="text-5xl mb-3 animate-bounce">✅</div>
                  <h2 className="text-2xl font-bold text-green-600 mb-2">Pagamento Confirmado!</h2>
                  <p className="text-gray-600">Redirecionando para o recibo...</p>
                </div>
              </div>
            ) : (
              <>
                {/* QR Code Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Código QR</h2>
                  <div className="flex flex-col items-center gap-4">
                    {payment.qr_code_url && (
                      <img
                        src={payment.qr_code_url}
                        alt="QR Code Pix"
                        className="w-64 h-64 border-4 border-gray-200 rounded-lg"
                      />
                    )}
                    <p className="text-center text-sm text-gray-600 max-w-sm">
                      Escaneie este código QR com seu banco para pagar via Pix
                    </p>
                  </div>
                </div>

                {/* Pix Key Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Chave Pix</h2>
                  <div className="flex flex-col gap-3">
                    <p className="text-sm text-gray-600">
                      Ou copie a chave Pix abaixo para fazer a transferência manualmente:
                    </p>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        readOnly
                        value={payment.pix_key}
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-sm font-mono select-all"
                      />
                      <button
                        onClick={handleCopyPixKey}
                        className={`px-6 py-3 font-medium rounded-lg transition whitespace-nowrap ${
                          pixKeyCopied
                            ? 'bg-green-600 hover:bg-green-700 text-white'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        }`}
                      >
                        {pixKeyCopied ? '✓ Copiado' : 'Copiar'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Status Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Status do Pagamento</h2>
                  <div className="space-y-4">
                    {/* Countdown Timer */}
                    <div className="text-center">
                      <p className="text-sm text-gray-600 mb-2">Tempo restante</p>
                      <div className="flex items-center justify-center gap-2">
                        <div className="text-4xl font-bold text-blue-600 font-mono">
                          {formatTime(timeLeft)}
                        </div>
                        <div className="text-sm text-gray-600">segundos</div>
                      </div>
                    </div>

                    {/* Status Text */}
                    <div className="text-center">
                      <div className="inline-flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-full">
                        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                        <span className="text-blue-700 font-medium">Aguardando pagamento...</span>
                      </div>
                    </div>

                    {/* Info */}
                    <p className="text-xs text-gray-500 text-center">
                      Verificando status automaticamente a cada 2 segundos
                    </p>
                  </div>
                </div>
              </>
            )}

            {/* Back Button */}
            {payment.status !== 'paid' && (
              <button
                onClick={() => navigate(`/match/${id}`)}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition"
              >
                Voltar aos Detalhes do Match
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
