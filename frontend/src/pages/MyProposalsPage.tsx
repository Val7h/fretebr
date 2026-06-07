import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface Proposal {
  id: number;
  frete_id: number;
  frete_origem: string;
  frete_destino: string;
  valor_proposta: number;
  status: string;
  created_at: string;
}

export const MyProposalsPage = () => {
  const [propostas, setPropostas] = useState<Proposal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    loadPropostas();
  }, []);

  const loadPropostas = async () => {
    try {
      setIsLoading(true);
      setErro(null);
      const data = await apiService.getMyProposals();
      setPropostas(data);
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao carregar propostas');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'aceito':
        return { bg: '#e8f5e9', color: '#2e7d32' };
      case 'pendente':
        return { bg: '#fff3e0', color: '#e65100' };
      case 'rejeitado':
        return { bg: '#ffebee', color: '#c62828' };
      default:
        return { bg: '#f5f5f5', color: '#666' };
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'aceito':
        return '✅ Aceita';
      case 'pendente':
        return '⏳ Pendente';
      case 'rejeitado':
        return '❌ Rejeitada';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Carregando propostas...</p>
      </div>
    );
  }

  if (erro) {
    return (
      <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <h1 style={{ color: '#333', fontSize: '2rem' }}>📝 Minhas Propostas</h1>
        <div style={{ color: 'red', padding: '20px', background: '#fff0f0', borderRadius: '8px' }}>
          {erro}
        </div>
        <button
          onClick={loadPropostas}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
          }}
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h1 style={{ color: '#333', fontSize: '2rem', marginBottom: '30px' }}>
        📝 Minhas Propostas
      </h1>

      {propostas.length === 0 ? (
        <div
          style={{
            padding: '60px 40px',
            textAlign: 'center',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
          }}
        >
          <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '20px' }}>
            Você ainda não fez nenhuma proposta.
          </p>
          <a
            href="/procurar-fretes"
            style={{
              padding: '12px 24px',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '6px',
              fontWeight: '600',
              display: 'inline-block',
            }}
          >
            Procurar Fretes
          </a>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px',
          }}
        >
          {propostas.map((proposta) => {
            const statusColors = getStatusColor(proposta.status);
            const data = new Date(proposta.created_at);
            const dataFormatada = data.toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            });

            return (
              <div
                key={proposta.id}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '20px',
                  boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                  border: '1px solid #f0f0f0',
                  transition: 'all 0.3s',
                  cursor: 'pointer',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.12)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.08)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ marginBottom: '12px' }}>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      background: statusColors.bg,
                      color: statusColors.color,
                      borderRadius: '20px',
                      fontSize: '0.85rem',
                      fontWeight: '600',
                    }}
                  >
                    {getStatusLabel(proposta.status)}
                  </span>
                </div>

                <h3 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '1.1rem' }}>
                  📍 {proposta.frete_origem}
                </h3>
                <p style={{ margin: '0 0 12px 0', color: '#666', fontSize: '0.95rem' }}>
                  ➜ {proposta.frete_destino}
                </p>

                <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '12px', marginTop: '12px' }}>
                  <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>
                    Seu Valor
                  </p>
                  <p style={{ margin: '0 0 12px 0', fontWeight: '600', color: '#667eea', fontSize: '1.2rem' }}>
                    R$ {proposta.valor_proposta.toFixed(2)}
                  </p>

                  <p style={{ margin: '8px 0', color: '#999', fontSize: '0.85rem' }}>
                    Data: {dataFormatada}
                  </p>
                </div>

                <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #f0f0f0' }}>
                  <a
                    href={`/frete/${proposta.frete_id}`}
                    style={{
                      display: 'block',
                      padding: '8px',
                      background: '#667eea',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '6px',
                      textAlign: 'center',
                      fontSize: '0.9rem',
                      fontWeight: '600',
                    }}
                  >
                    Ver Detalhes
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
