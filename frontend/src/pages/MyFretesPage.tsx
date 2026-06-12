import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import type { Frete } from '../services/api';
import { Loading, EmptyState, ErrorState, PageContainer, PageHeader } from '../components/UIStates';

export const MyFretesPage = () => {
  const navigate = useNavigate();
  const [fretes, setFretes] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { loadFretes(); }, []);

  const loadFretes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.getMyFretes();
      setFretes(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Não foi possível carregar seus fretes.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <Loading message="Carregando seus fretes..." />;

  return (
    <PageContainer>
      <PageHeader
        title="📦 Meus Fretes"
        subtitle="Fretes que você postou e seu status atual."
        action={
          fretes.length > 0 ? (
            <button onClick={() => navigate('/postar-frete')} style={{
              padding: '10px 18px', background: '#667eea', color: 'white',
              border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer',
              fontSize: '0.9rem', boxShadow: '0 2px 6px rgba(102,126,234,0.3)',
            }}>
              + Novo frete
            </button>
          ) : null
        }
      />

      {error ? (
        <ErrorState message={error} onRetry={loadFretes} />
      ) : fretes.length === 0 ? (
        <EmptyState
          icon="📭"
          title="Você ainda não postou nenhum frete"
          description="Crie sua primeira solicitação em menos de 1 minuto. Motoristas próximos da sua rota receberão a oportunidade automaticamente."
          ctaLabel="Postar meu primeiro frete"
          ctaHref="/postar-frete"
        />
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 280px), 1fr))',
          gap: 16,
        }}>
          {fretes.map(frete => {
            const corStatus = frete.status === 'disponível' || frete.status === 'disponivel'
              ? { bg: '#e8f5e9', text: '#2e7d32' }
              : frete.status === 'aceito'
                ? { bg: '#e3f2fd', text: '#1565c0' }
                : { bg: '#fff3e0', text: '#e65100' };
            return (
              <div
                key={frete.id}
                onClick={() => navigate(`/frete/${frete.id}`)}
                style={{
                  background: 'white', borderRadius: 12, padding: 20,
                  boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
                  border: '1px solid #f0f0f0', cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(102,126,234,0.15)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.06)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ marginBottom: 12 }}>
                  <span style={{
                    display: 'inline-block', padding: '4px 12px',
                    background: corStatus.bg, color: corStatus.text,
                    borderRadius: 20, fontSize: '0.8rem', fontWeight: 600,
                  }}>
                    {frete.status.charAt(0).toUpperCase() + frete.status.slice(1)}
                  </span>
                </div>

                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                    📍 {frete.origem}
                  </div>
                  <div style={{ color: '#999', fontSize: '0.9rem', margin: '4px 0 0 22px' }}>↓</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                    🏁 {frete.destino}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, padding: '12px 0', borderTop: '1px solid #f0f0f0' }}>
                  <div>
                    <div style={{ color: '#999', fontSize: '0.75rem', textTransform: 'uppercase' }}>Peso</div>
                    <div style={{ color: '#333', fontWeight: 600 }}>{frete.peso_kg} kg</div>
                  </div>
                  <div>
                    <div style={{ color: '#999', fontSize: '0.75rem', textTransform: 'uppercase' }}>Valor</div>
                    <div style={{ color: '#667eea', fontWeight: 700, fontSize: '1.05rem' }}>
                      R$ {frete.valor_r.toFixed(2).replace('.', ',')}
                    </div>
                  </div>
                </div>

                {frete.descricao && (
                  <p style={{
                    margin: 0, color: '#666', fontSize: '0.88rem',
                    lineHeight: 1.4,
                    overflow: 'hidden', textOverflow: 'ellipsis',
                    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                  }}>
                    {frete.descricao}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </PageContainer>
  );
};
