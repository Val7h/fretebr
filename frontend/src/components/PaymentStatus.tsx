import React, { useState, useEffect } from 'react';

export interface Payment {
  id: string;
  match_id: string;
  amount: number;
  status: 'pending' | 'paid' | 'expired';
  qr_code_url?: string;
  pix_key: string;
  created_at: string;
  expires_at: string;
}

interface PaymentStatusProps {
  payment: Payment;
  onPaid?: () => void;
  onExpired?: () => void;
}

export const PaymentStatus: React.FC<PaymentStatusProps> = ({
  payment,
  onPaid,
  onExpired,
}) => {
  const [timeLeft, setTimeLeft] = useState<number>(0);

  // Calculate remaining time
  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const expiresAt = new Date(payment.expires_at).getTime();
      const difference = expiresAt - now;

      if (difference <= 0) {
        setTimeLeft(0);
        if (onExpired) {
          onExpired();
        }
      } else {
        setTimeLeft(Math.floor(difference / 1000));
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, [payment, onExpired]);

  // Poll for payment status
  useEffect(() => {
    if (payment.status === 'paid' || payment.status === 'expired') {
      return;
    }

    const pollPaymentStatus = async () => {
      try {
        // Mock polling - in production, call actual API
        if (Math.random() > 0.95) {
          if (onPaid) {
            onPaid();
          }
        }
      } catch (err) {
        console.error('Error polling payment status:', err);
      }
    };

    const interval = setInterval(pollPaymentStatus, 2000);

    return () => clearInterval(interval);
  }, [payment.status, onPaid]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (payment.status === 'paid') {
    return (
      <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
        <div className="text-5xl mb-3 animate-bounce">✅</div>
        <h2 className="text-2xl font-bold text-green-600 mb-2">Pagamento Confirmado!</h2>
        <p className="text-gray-600">Sua transação foi processada com sucesso.</p>
      </div>
    );
  }

  if (payment.status === 'expired') {
    return (
      <div className="bg-red-50 border-2 border-red-500 rounded-lg p-6 text-center">
        <div className="text-5xl mb-3">❌</div>
        <h2 className="text-2xl font-bold text-red-600 mb-2">Pagamento Expirou</h2>
        <p className="text-gray-600">O código QR expirou. Crie um novo pagamento para continuar.</p>
      </div>
    );
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Status do Pagamento</h2>
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

        {/* Status Indicator */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full border border-blue-200">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            <span className="text-blue-700 font-medium">Aguardando pagamento...</span>
          </div>
        </div>

        {/* Info Text */}
        <p className="text-xs text-gray-500 text-center">
          Verificando status automaticamente a cada 2 segundos
        </p>
      </div>
    </div>
  );
};
