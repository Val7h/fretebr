import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

interface Receipt {
  transaction_id: number;
  match_id: number;
  amount: number;
  status: string;
  payment_date: string;
  motorista_id: number;
  shipper_id: number;
}

export const ReceiptPage = () => {
  const { id: matchId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [match, setMatch] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) return;
    (async () => {
      try {
        setIsLoading(true);
        setErro(null);
        const [r, m] = await Promise.all([
          apiService.getReceipt(parseInt(matchId)).catch(() => null),
          apiService.getMatch(parseInt(matchId)).catch(() => null),
        ]);
        setReceipt(r);
        setMatch(m);
      } catch (e: any) {
        setErro(e?.response?.data?.detail || 'Erro ao carregar recibo');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [matchId]);

  if (isLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Carregando recibo...</p>
      </div>
    );
  }

  if (erro || !receipt) {
    return (
      <div style={{ padding: 40, maxWidth: 700, margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <button onClick={() => navigate(-1)} style={btnBack}>← Voltar</button>
        <div style={{ color: '#c62828', padding: 16, background: '#fff0f0', borderRadius: 8, marginTop: 16 }}>
          {erro || 'Recibo nao disponivel (pagamento ainda nao confirmado?)'}
        </div>
      </div>
    );
  }

  const dataFormatada = new Date(receipt.payment_date).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div style={{ padding: 32, maxWidth: 720, margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <button onClick={() => navigate('/')} style={btnBack}>← Dashboard</button>

      {/* Header de sucesso */}
      <div style={{
        background: 'linear-gradient(135deg, #2e7d32 0%, #43a047 100%)',
        color: 'white', padding: 28, borderRadius: 12,
        textAlign: 'center', marginTop: 16, marginBottom: 24,
      }}>
        <div style={{ fontSize: 48 }}>✅</div>
        <h1 style={{ margin: '8px 0', fontSize: 24 }}>Pagamento confirmado!</h1>
        <p style={{ margin: 0, opacity: 0.9 }}>Obrigado pela transacao via FreteBR</p>
      </div>

      {/* Card do recibo */}
      <div style={card}>
        <h3 style={{ marginTop: 0, color: '#333', borderBottom: '1px solid #eee', paddingBottom: 10 }}>
          🧾 Recibo de Pagamento
        </h3>

        <Row label="Numero da transacao" value={`#${receipt.transaction_id}`} mono />
        <Row label="Match" value={`#${receipt.match_id}`} mono />
        <Row label="Status" value={receipt.status.toUpperCase()} highlight />
        <Row label="Data e hora" value={dataFormatada} />
        <Row label="Valor pago" value={`R$ ${receipt.amount.toFixed(2)}`} big />

        {match?.frete && (
          <>
            <div style={{ borderTop: '1px solid #eee', margin: '16px 0', paddingTop: 16 }}>
              <h4 style={{ margin: '0 0 12px', color: '#666', fontSize: 13, textTransform: 'uppercase' }}>
                Detalhes do Frete
              </h4>
              <Row label="Origem" value={match.frete.origem || '—'} />
              <Row label="Destino" value={match.frete.destino || '—'} />
              <Row label="Peso" value={`${match.frete.peso_kg ?? '—'} kg`} />
            </div>
          </>
        )}
      </div>

      {/* Acoes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <button
          onClick={() => navigate(`/match/${matchId}/rating`)}
          style={{ ...btnPrimary, background: '#f59e0b' }}
        >
          ⭐ Avaliar agora
        </button>
        <button
          onClick={() => navigate('/transacoes')}
          style={btnPrimary}
        >
          📊 Ver transacoes
        </button>
      </div>

      <p style={{ color: '#999', fontSize: 12, textAlign: 'center', marginTop: 20 }}>
        Recibo gerado automaticamente. Guarde este numero para suporte: #{receipt.transaction_id}
      </p>
    </div>
  );
};

function Row({ label, value, mono, highlight, big }: {
  label: string; value: string; mono?: boolean; highlight?: boolean; big?: boolean;
}) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between',
      padding: '8px 0', borderBottom: '1px solid #f5f5f5',
    }}>
      <span style={{ color: '#666', fontSize: 14 }}>{label}</span>
      <span style={{
        fontWeight: big ? 700 : 600,
        color: highlight ? '#2e7d32' : (big ? '#667eea' : '#333'),
        fontFamily: mono ? 'monospace' : 'inherit',
        fontSize: big ? 18 : 14,
      }}>
        {value}
      </span>
    </div>
  );
}

const btnBack: React.CSSProperties = {
  padding: '8px 16px', background: '#f0f0f0',
  border: 'none', borderRadius: 6, cursor: 'pointer', fontWeight: 600,
};

const btnPrimary: React.CSSProperties = {
  padding: 14, background: '#667eea', color: 'white',
  border: 'none', borderRadius: 8, cursor: 'pointer',
  fontWeight: 600, fontSize: 15,
};

const card: React.CSSProperties = {
  background: 'white', borderRadius: 12, padding: 24,
  boxShadow: '0 2px 12px rgba(0,0,0,0.06)', marginBottom: 16,
};
