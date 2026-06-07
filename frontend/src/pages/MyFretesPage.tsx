import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Frete } from '../services/api';

export const MyFretesPage = () => {
  const [fretes, setFretes] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFretes();
  }, []);

  const loadFretes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.getMyFretes();
      setFretes(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao carregar fretes');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <p>Carregando fretes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
        <h1>📦 Meus Fretes</h1>
        <div style={{ color: 'red', padding: '20px', background: '#fff0f0', borderRadius: '8px' }}>
          {error}
        </div>
        <button
          onClick={loadFretes}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <h1 style={{ color: '#333', fontSize: '2rem', marginBottom: '30px' }}>📦 Meus Fretes</h1>

      {fretes.length === 0 ? (
        <div style={{
          padding: '60px 40px',
          textAlign: 'center',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
        }}>
          <p style={{ fontSize: '1.1rem', color: '#666', marginBottom: '20px' }}>
            Você ainda não postou nenhum frete.
          </p>
          <a
            href="/postar-frete"
            style={{
              padding: '12px 24px',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '6px',
              fontWeight: '600',
              display: 'inline-block'
            }}
          >
            Postar Novo Frete
          </a>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {fretes.map(frete => (
            <div
              key={frete.id}
              style={{
                background: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                border: '1px solid #f0f0f0',
                transition: 'all 0.3s',
                cursor: 'pointer'
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
                <span style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  background: frete.status === 'disponível' ? '#e8f5e9' : '#fff3e0',
                  color: frete.status === 'disponível' ? '#2e7d32' : '#e65100',
                  borderRadius: '20px',
                  fontSize: '0.85rem',
                  fontWeight: '600'
                }}>
                  {frete.status.charAt(0).toUpperCase() + frete.status.slice(1)}
                </span>
              </div>

              <h3 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '1.1rem' }}>
                📍 {frete.origem}
              </h3>
              <p style={{ margin: '0 0 12px 0', color: '#666', fontSize: '0.95rem' }}>
                ➜ {frete.destino}
              </p>

              <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '12px', marginTop: '12px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <p style={{ margin: '0 0 4px 0', color: '#999', fontSize: '0.85rem' }}>Peso</p>
                    <p style={{ margin: 0, fontWeight: '600', color: '#333' }}>{frete.peso_kg} kg</p>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 4px 0', color: '#999', fontSize: '0.85rem' }}>Valor</p>
                    <p style={{ margin: 0, fontWeight: '600', color: '#667eea' }}>R$ {frete.valor_r.toFixed(2)}</p>
                  </div>
                </div>

                {frete.descricao && (
                  <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '0.9rem', lineHeight: '1.4' }}>
                    {frete.descricao}
                  </p>
                )}
              </div>

              <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #f0f0f0', display: 'flex', gap: '8px' }}>
                <a
                  href={`/frete/${frete.id}`}
                  style={{
                    flex: 1,
                    padding: '8px',
                    background: '#667eea',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '6px',
                    textAlign: 'center',
                    fontSize: '0.9rem',
                    fontWeight: '600'
                  }}
                >
                  Ver Detalhes
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
