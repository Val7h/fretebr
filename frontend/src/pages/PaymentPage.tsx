import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { apiService } from '../services/api';

interface PaymentData {
  transaction_id: number;
  qr_code_data: string;
  payment_id?: string;
  expires_in_seconds?: number;
  expires_at?: string;
}

export const PaymentPage = () => {
  const { id: matchId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [match, setMatch] = useState<any>(null);
  const [payment, setPayment] = useState<PaymentData | null>(null);
  const [status, setStatus] = useState<string>('aguardando');
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [secondsLeft, setSecondsLeft] = useState<number>(0);
  const [copiado, setCopiado] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const pollRef = useRef<number | null>(null);

  // Inicializa: busca match e cria pagamento
  useEffect(() => {
    if (!matchId) return;
    (async () => {
      try {
        setIsLoading(true);
        setErro(null);
        const m = await apiService.getMatch(parseInt(matchId));
        setMatch(m);
        const amount = m?.valor_proposta || m?.frete?.valor_r;
        if (!amount) {
          setErro('Valor do frete nao encontrado');
          return;
        }
        const p = await apiService.createPayment(parseInt(matchId), amount);
        setPayment(p);
        if (p.expires_in_seconds) setSecondsLeft(p.expires_in_seconds);
      } catch (e: any) {
        setErro(e?.response?.data?.detail || 'Erro ao iniciar pagamento');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [matchId]);

  // Timer regressivo
  useEffect(() => {
    if (!payment || secondsLeft <= 0) return;
    const t = window.setInterval(() => setSecondsLeft((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [payment, secondsLeft > 0]);

  // Polling de status a cada 5s
  useEffect(() => {
    if (!payment) return;
    const poll = async () => {
      try {
        const s = await apiService.getPaymentStatus(payment.transaction_id);
        setStatus(s.status);
        if (s.status === 'pago') {
          // Sucesso: redireciona para receipt
          window.setTimeout(() => navigate(`/match/${matchId}/receipt`), 800);
        }
      } catch {
        // silencioso, continua polling
      }
    };
    poll();
    pollRef.current = window.setInterval(poll, 5000);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [payment, matchId, navigate]);

  const handleCopy = async () => {
    if (!payment?.qr_code_data) return;
    try {
      await navigator.clipboard.writeText(payment.qr_code_data);
      setCopiado(true);
      window.setTimeout(() => setCopiado(false), 2000);
    } catch {
      setErro('Falha ao copiar');
    }
  };

  const handleSimulate = async () => {
    if (!payment) return;
    try {
      setSimulating(true);
      await apiService.simulatePaymentPaid(payment.transaction_id);
      // O polling vai pegar o "pago" em <=5s, mas força rápida:
      const s = await apiService.getPaymentStatus(payment.transaction_id);
      setStatus(s.status);
      if (s.status === 'pago') navigate(`/match/${matchId}/receipt`);
    } catch (e: any) {
      setErro(e?.response?.data?.detail || 'Falha ao simular pagamento');
    } finally {
      setSimulating(false);
    }
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const ss = (s % 60).toString().padStart(2, '0');
    return `${m}:${ss}`;
  };

  if (isLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Iniciando pagamento Pix...</p>
      </div>
    );
  }

  if (erro || !payment) {
    return (
      <div style={{ padding: 40, maxWidth: 700, margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <button onClick={() => navigate(-1)} style={btnBack}>← Voltar</button>
        <div style={{ color: '#c62828', padding: 16, background: '#fff0f0', borderRadius: 8, marginTop: 16 }}>
          {erro || 'Erro ao gerar pagamento'}
        </div>
      </div>
    );
  }

  const isPaid = status === 'pago';
  const isExpired = secondsLeft === 0 && payment.expires_in_seconds && payment.expires_in_seconds > 0;

  return (
    <div style={{ padding: 32, maxWidth: 720, margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <button onClick={() => navigate(-1)} style={btnBack}>← Voltar</button>

      <h1 style={{ color: '#333', marginTop: 16, marginBottom: 8 }}>💳 Pagamento Pix</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>
        Match #{matchId} — Transacao #{payment.transaction_id}
      </p>

      {/* Resumo */}
      {match && (
        <div style={card}>
          <p style={{ margin: 0, color: '#666', fontSize: 14 }}>Rota</p>
          <p style={{ margin: '4px 0 12px', fontWeight: 600, fontSize: 16 }}>
            {match?.frete?.origem || '—'} → {match?.frete?.destino || '—'}
          </p>
          <p style={{ margin: 0, color: '#666', fontSize: 14 }}>Valor a pagar</p>
          <p style={{ margin: '4px 0 0', fontWeight: 700, fontSize: 28, color: '#667eea' }}>
            R$ {(match?.valor_proposta ?? match?.frete?.valor_r ?? 0).toFixed(2)}
          </p>
        </div>
      )}

      {/* Status badge */}
      <div style={{ ...statusBadge(status), marginBottom: 20 }}>
        {isPaid ? '✅ Pago — redirecionando...' :
         isExpired ? '⏰ Pix expirado' :
         status === 'pendente' || status === 'aguardando' ? '⏳ Aguardando pagamento' :
         status}
      </div>

      {/* QR + Código */}
      <div style={card}>
        <h3 style={{ marginTop: 0, color: '#333' }}>QR Code Pix</h3>
        <div style={{
          display: 'flex', justifyContent: 'center',
          padding: 16, background: 'white', borderRadius: 8,
          border: '1px solid #eee', marginBottom: 16,
        }}>
          <QRCodeSVG
            value={payment.qr_code_data}
            size={220}
            level="M"
            includeMargin={true}
            bgColor="#FFFFFF"
            fgColor="#000000"
          />
        </div>
        <p style={{ margin: '0 0 10px', textAlign: 'center', color: '#666', fontSize: 12 }}>
          Escaneie com o app do seu banco
        </p>

        <p style={{ margin: '12px 0 6px', color: '#666', fontSize: 13 }}>
          Ou copie e cole o codigo:
        </p>
        <textarea
          readOnly
          value={payment.qr_code_data}
          style={{
            width: '100%', minHeight: 80, padding: 10,
            border: '1px solid #ddd', borderRadius: 6,
            fontFamily: 'monospace', fontSize: 12,
            boxSizing: 'border-box',
          }}
        />
        <button onClick={handleCopy} style={{
          ...btnPrimary, marginTop: 10, width: '100%',
          background: copiado ? '#2e7d32' : '#667eea',
        }}>
          {copiado ? '✓ Copiado!' : '📋 Copiar codigo Pix'}
        </button>
      </div>

      {/* Timer */}
      {payment.expires_in_seconds && payment.expires_in_seconds > 0 && (
        <div style={{ ...card, textAlign: 'center' }}>
          <p style={{ margin: 0, color: '#666', fontSize: 13 }}>Tempo restante</p>
          <p style={{
            margin: '6px 0 0', fontSize: 28, fontWeight: 700,
            color: secondsLeft < 60 ? '#c62828' : '#333',
            fontFamily: 'monospace',
          }}>
            {formatTime(secondsLeft)}
          </p>
        </div>
      )}

      {/* DEV: botao de simular pagamento */}
      {!isPaid && !isExpired && (
        <div style={{ ...card, background: '#fff3e0', border: '1px dashed #e65100' }}>
          <p style={{ margin: '0 0 8px', color: '#e65100', fontWeight: 600, fontSize: 13 }}>
            ⚠ Modo DEV (MOCK MP)
          </p>
          <button onClick={handleSimulate} disabled={simulating} style={{
            ...btnPrimary, background: '#e65100', width: '100%',
            opacity: simulating ? 0.6 : 1,
          }}>
            {simulating ? 'Processando...' : '🧪 Simular pagamento concluido'}
          </button>
        </div>
      )}
    </div>
  );
};

const btnBack: React.CSSProperties = {
  padding: '8px 16px', background: '#f0f0f0',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 600,
};

const btnPrimary: React.CSSProperties = {
  padding: '12px 18px', background: '#667eea', color: 'white',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 600, fontSize: 15,
};

const card: React.CSSProperties = {
  background: 'white', borderRadius: 12, padding: 20,
  boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 16,
};

function statusBadge(status: string): React.CSSProperties {
  const map: Record<string, [string, string]> = {
    pago: ['#e8f5e9', '#2e7d32'],
    pendente: ['#fff3e0', '#e65100'],
    aguardando: ['#fff3e0', '#e65100'],
    falhou: ['#ffebee', '#c62828'],
    expirado: ['#f5f5f5', '#666'],
  };
  const [bg, color] = map[status] || ['#f5f5f5', '#666'];
  return {
    padding: '10px 16px', background: bg, color,
    borderRadius: 8, fontWeight: 600, textAlign: 'center' as const,
  };
}
