import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface MatchData {
  id: number;
  frete_id: number;
  motorista_id: number;
  valor_proposta: number;
  status: string;
  mensagem: string;
  created_at: string;
  motorista?: {
    id: number;
    nome: string;
    email: string;
    telefone?: string;
  };
  frete?: {
    id: number;
    origem: string;
    destino: string;
    peso_kg: number;
    valor_r: number;
    descricao?: string;
  };
}

export const MatchDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [match, setMatch] = useState<MatchData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    loadMatch();
  }, [id]);

  const loadMatch = async () => {
    try {
      setIsLoading(true);
      setErro(null);
      if (!id) return;
      const data = await apiService.getMatch(parseInt(id));
      setMatch(data);
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao carregar match');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Carregando detalhes...</p>
      </div>
    );
  }

  if (erro || !match) {
    return (
      <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            marginBottom: '20px',
            padding: '8px 16px',
            background: '#f0f0f0',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
          }}
        >
          ← Voltar
        </button>
        <div style={{ color: 'red', padding: '20px', background: '#fff0f0', borderRadius: '8px' }}>
          {erro || 'Match não encontrado'}
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'aceito':
        return { bg: '#e8f5e9', color: '#2e7d32' };
      case 'pendente':
        return { bg: '#fff3e0', color: '#e65100' };
      case 'rejeitado':
        return { bg: '#ffebee', color: '#c62828' };
      case 'em_entrega':
        return { bg: '#e3f2fd', color: '#1565c0' };
      case 'finalizado':
        return { bg: '#f3e5f5', color: '#6a1b9a' };
      default:
        return { bg: '#f5f5f5', color: '#666' };
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'aceito':
        return '✅ Aceito';
      case 'pendente':
        return '⏳ Pendente';
      case 'rejeitado':
        return '❌ Rejeitado';
      case 'em_entrega':
        return '🚚 Em Entrega';
      case 'finalizado':
        return '🎉 Finalizado';
      default:
        return status;
    }
  };

  const statusColors = getStatusColor(match.status);
  const dataCriado = new Date(match.created_at).toLocaleDateString('pt-BR');

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <button
        onClick={() => navigate(-1)}
        style={{
          marginBottom: '20px',
          padding: '8px 16px',
          background: '#f0f0f0',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontWeight: '600',
        }}
      >
        ← Voltar
      </button>

      <div
        style={{
          background: 'white',
          borderRadius: '12px',
          padding: '30px',
          boxShadow: '0 2px 16px rgba(0,0,0,0.08)',
          marginBottom: '30px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
          <h1 style={{ margin: 0, color: '#333', fontSize: '2rem' }}>
            🤝 Detalhes do Match
          </h1>
          <span
            style={{
              padding: '8px 16px',
              background: statusColors.bg,
              color: statusColors.color,
              borderRadius: '20px',
              fontWeight: '600',
            }}
          >
            {getStatusLabel(match.status)}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '30px' }}>
          {/* Informações do Frete */}
          <div>
            <h3 style={{ margin: '0 0 15px 0', color: '#666', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Informações do Frete
            </h3>
            <div style={{ display: 'grid', gap: '15px' }}>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Origem</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>
                  📍 {match.frete?.origem || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Destino</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>
                  📍 {match.frete?.destino || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Peso</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333' }}>
                  {match.frete?.peso_kg || 'N/A'} kg
                </p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Valor Base</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#667eea', fontSize: '1.2rem' }}>
                  R$ {match.frete?.valor_r.toFixed(2) || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Informações da Proposta */}
          <div>
            <h3 style={{ margin: '0 0 15px 0', color: '#666', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Proposta Aceita
            </h3>
            <div style={{ display: 'grid', gap: '15px' }}>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Motorista</p>
                <p style={{ margin: '0 0 2px 0', fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>
                  {match.motorista?.nome || 'N/A'}
                </p>
                <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                  📧 {match.motorista?.email || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Valor Proposto</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#2e7d32', fontSize: '1.2rem' }}>
                  R$ {match.valor_proposta.toFixed(2)}
                </p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Aceito em</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333' }}>
                  {dataCriado}
                </p>
              </div>
            </div>
          </div>
        </div>

        {match.mensagem && (
          <div style={{ marginTop: '30px', paddingTop: '30px', borderTop: '1px solid #f0f0f0' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Mensagem da Proposta
            </h3>
            <p style={{ margin: 0, color: '#333', fontSize: '0.95rem', lineHeight: '1.6', background: '#f5f5f5', padding: '15px', borderRadius: '6px' }}>
              "{match.mensagem}"
            </p>
          </div>
        )}

        {(match.status === 'aceito' || match.status === 'em_entrega' || match.status === 'finalizado') && (
          <div style={{ marginTop: '30px', paddingTop: '30px', borderTop: '1px solid #f0f0f0', display: 'grid', gap: 12 }}>
            <button
              onClick={() => navigate(`/match/${match.id}/chat`)}
              style={{
                width: '100%',
                padding: '14px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '1rem',
              }}
            >
              💬 Conversar
            </button>
            <button
              onClick={() => navigate(`/match/${match.id}/payment`)}
              style={{
                width: '100%',
                padding: '14px',
                background: '#2e7d32',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '1rem',
              }}
            >
              💳 Pagar via Pix
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
