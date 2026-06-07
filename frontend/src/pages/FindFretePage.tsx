import { useState, useMemo, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Frete } from '../services/api';
import {
  ESTADOS_BRASIL,
  CIDADES_POR_ESTADO,
  CALCULAR_DISTANCIA,
  CALCULAR_PRECO_FRETE,
  ESTIMAR_TEMPO,
  COORDENADAS_CIDADES,
} from '../data/freteData';
import { MapaRotaLeaflet } from '../components/MapaRotaLeaflet';

export const FindFretePage = () => {
  const [filtros, setFiltros] = useState({
    estado_origem: '',
    cidade_origem: '',
    estado_destino: '',
    cidade_destino: '',
    peso_min: 0,
    peso_max: 30000,
    urgencia: 'todas'
  });

  const [fretesApi, setFretesApi] = useState<Frete[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Carregar fretes da API
  useEffect(() => {
    loadFretes();
  }, []);

  const loadFretes = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.getAvailableFretes();
      setFretesApi(data);
    } catch (err: any) {
      setError('Erro ao carregar fretes');
      setFretesApi([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fretes com cálculo automático de distância e preço
  const fretes = useMemo(() => {
    return fretesApi.map(frete => {
      const distancia = CALCULAR_DISTANCIA(frete.origem, frete.destino);
      const preco = CALCULAR_PRECO_FRETE(distancia, frete.peso_kg);
      const tempo = ESTIMAR_TEMPO(distancia);

      return {
        ...frete,
        distancia,
        tempo_estimado: tempo
      };
    });
  }, [fretesApi]);

  // Filtrar fretes
  const fretesFiltr = useMemo(() => {
    return fretes.filter(f => {
      // Filtrar por origem
      if (filtros.estado_origem) {
        if (!f.origem.endsWith(filtros.estado_origem)) return false;
      }
      if (filtros.cidade_origem && !f.origem.startsWith(filtros.cidade_origem)) return false;

      // Filtrar por destino
      if (filtros.estado_destino) {
        if (!f.destino.endsWith(filtros.estado_destino)) return false;
      }
      if (filtros.cidade_destino && !f.destino.startsWith(filtros.cidade_destino)) return false;

      // Filtrar por peso
      if (f.peso_kg < filtros.peso_min || f.peso_kg > filtros.peso_max) return false;

      // Filtrar por urgência
      if (filtros.urgencia !== 'todas' && f.urgencia !== filtros.urgencia) return false;

      return true;
    });
  }, [fretes, filtros]);

  const cidadesOrigem = filtros.estado_origem ? CIDADES_POR_ESTADO[filtros.estado_origem as keyof typeof CIDADES_POR_ESTADO] || [] : [];
  const cidadesDestino = filtros.estado_destino ? CIDADES_POR_ESTADO[filtros.estado_destino as keyof typeof CIDADES_POR_ESTADO] || [] : [];

  return (
    <div style={{ background: '#f5f5f5', minHeight: '100vh', padding: '20px', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ color: '#333', marginBottom: '30px', fontSize: '2rem', fontWeight: '600' }}>🔍 Procurar Fretes Disponíveis</h1>

        {/* Filtros */}
        <div style={{
          background: 'white',
          padding: '25px',
          borderRadius: '10px',
          marginBottom: '30px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#333', fontSize: '1.2rem', fontWeight: '600' }}>Filtros de Busca</h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px'
          }}>
            {/* Origem */}
            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Estado de Origem</label>
              <select
                value={filtros.estado_origem}
                onChange={(e) => setFiltros({ ...filtros, estado_origem: e.target.value, cidade_origem: '' })}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  boxSizing: 'border-box',
                  fontSize: '1rem',
                  fontFamily: 'inherit'
                }}
              >
                <option value="">Selecionar estado...</option>
                {ESTADOS_BRASIL.map(estado => (
                  <option key={estado.sigla} value={estado.sigla}>{estado.nome} ({estado.sigla})</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Cidade de Origem</label>
              <select
                value={filtros.cidade_origem}
                onChange={(e) => setFiltros({ ...filtros, cidade_origem: e.target.value })}
                disabled={!filtros.estado_origem}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  boxSizing: 'border-box',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  opacity: !filtros.estado_origem ? 0.5 : 1,
                  cursor: !filtros.estado_origem ? 'not-allowed' : 'pointer'
                }}
              >
                <option value="">Selecionar cidade...</option>
                {cidadesOrigem.map(cidade => (
                  <option key={cidade} value={cidade}>{cidade}</option>
                ))}
              </select>
            </div>

            {/* Destino */}
            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Estado de Destino</label>
              <select
                value={filtros.estado_destino}
                onChange={(e) => setFiltros({ ...filtros, estado_destino: e.target.value, cidade_destino: '' })}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  boxSizing: 'border-box',
                  fontSize: '1rem',
                  fontFamily: 'inherit'
                }}
              >
                <option value="">Selecionar estado...</option>
                {ESTADOS_BRASIL.map(estado => (
                  <option key={estado.sigla} value={estado.sigla}>{estado.nome} ({estado.sigla})</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Cidade de Destino</label>
              <select
                value={filtros.cidade_destino}
                onChange={(e) => setFiltros({ ...filtros, cidade_destino: e.target.value })}
                disabled={!filtros.estado_destino}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  boxSizing: 'border-box',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  opacity: !filtros.estado_destino ? 0.5 : 1,
                  cursor: !filtros.estado_destino ? 'not-allowed' : 'pointer'
                }}
              >
                <option value="">Selecionar cidade...</option>
                {cidadesDestino.map(cidade => (
                  <option key={cidade} value={cidade}>{cidade}</option>
                ))}
              </select>
            </div>

            {/* Urgência */}
            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Urgência</label>
              <select
                value={filtros.urgencia}
                onChange={(e) => setFiltros({ ...filtros, urgencia: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  boxSizing: 'border-box',
                  fontSize: '1rem',
                  fontFamily: 'inherit'
                }}
              >
                <option value="todas">🟦 Todas</option>
                <option value="normal">🟢 Normal</option>
                <option value="alta">🟠 Alta</option>
                <option value="muito alta">🔴 Muito Alta</option>
              </select>
            </div>

            {/* Peso */}
            <div>
              <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>
                Peso: {filtros.peso_min.toLocaleString('pt-BR')} - {filtros.peso_max.toLocaleString('pt-BR')} kg
              </label>
              <input
                type="range"
                min="0"
                max="30000"
                step="500"
                value={filtros.peso_max}
                onChange={(e) => setFiltros({ ...filtros, peso_max: parseInt(e.target.value) })}
                style={{ width: '100%', cursor: 'pointer' }}
              />
            </div>
          </div>
        </div>

        {/* Lista de Fretes */}
        <div>
          {isLoading ? (
            <div style={{
              background: 'white',
              padding: '40px',
              borderRadius: '10px',
              textAlign: 'center',
              boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
            }}>
              <p style={{ color: '#666', fontSize: '1.1rem' }}>Carregando fretes...</p>
            </div>
          ) : error ? (
            <div style={{
              background: 'white',
              padding: '40px',
              borderRadius: '10px',
              textAlign: 'center',
              boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
              borderLeft: '4px solid #ff4444'
            }}>
              <p style={{ color: '#ff4444', fontSize: '1.1rem' }}>{error}</p>
              <button
                onClick={loadFretes}
                style={{
                  marginTop: '20px',
                  padding: '10px 20px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Tentar Novamente
              </button>
            </div>
          ) : (
            <>
              <h3 style={{ color: '#333', marginBottom: '20px', fontSize: '1.2rem', fontWeight: '600' }}>
                📦 {fretesFiltr.length} frete{fretesFiltr.length !== 1 ? 's' : ''} disponível{fretesFiltr.length !== 1 ? 's' : ''}
              </h3>

              {fretesFiltr.length === 0 ? (
                <div style={{
                  background: 'white',
                  padding: '40px',
                  borderRadius: '10px',
                  textAlign: 'center',
                  boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
                }}>
                  <p style={{ color: '#999', fontSize: '1.1rem' }}>Nenhum frete encontrado com estes filtros 😔</p>
                </div>
              ) : (
            <div style={{ display: 'grid', gap: '20px' }}>
              {fretesFiltr.map(frete => (
                <div
                  key={frete.id}
                  style={{
                    background: 'white',
                    padding: '25px',
                    borderRadius: '10px',
                    boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    border: frete.urgencia === 'muito alta' ? '2px solid #ff4444' : frete.urgencia === 'alta' ? '2px solid #ff8800' : '1px solid #eee',
                    borderLeft: '4px solid ' + (frete.urgencia === 'muito alta' ? '#ff4444' : frete.urgencia === 'alta' ? '#ff8800' : '#667eea')
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(102, 126, 234, 0.15)';
                    e.currentTarget.style.transform = 'translateY(-4px)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.08)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '25px', alignItems: 'start' }}>
                  {/* Lado Esquerdo: Detalhes */}
                  <div>
                    {/* Rota */}
                    <div style={{ marginBottom: '20px' }}>
                      <div style={{ marginBottom: '15px' }}>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>De</p>
                        <h3 style={{ margin: '8px 0 0 0', color: '#333', fontSize: '1.2rem', fontWeight: '600' }}>📍 {frete.origem}</h3>
                      </div>
                      <div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Para</p>
                        <h3 style={{ margin: '8px 0 0 0', color: '#333', fontSize: '1.2rem', fontWeight: '600' }}>📍 {frete.destino}</h3>
                      </div>
                    </div>

                    {/* Grid de Detalhes */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
                      {/* Carga */}
                      <div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', fontWeight: '600' }}>Carga</p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '1.1rem', fontWeight: '600', color: '#333' }}>📦 {frete.peso_kg.toLocaleString('pt-BR')} kg</p>
                      </div>

                      {/* Distância */}
                      <div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', fontWeight: '600' }}>Distância</p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '1.1rem', fontWeight: '700', color: '#667eea' }}>{frete.distancia.toLocaleString('pt-BR')} km</p>
                      </div>

                      {/* Tempo */}
                      <div>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', fontWeight: '600' }}>Tempo Est.</p>
                        <p style={{ margin: '5px 0 0 0', fontSize: '1rem', fontWeight: '600', color: '#333' }}>⏱️ {frete.tempo_estimado}</p>
                      </div>
                    </div>

                    {/* Descrição */}
                    <div style={{ marginTop: '15px' }}>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: '#999', fontWeight: '600', marginBottom: '5px' }}>Descrição</p>
                      <p style={{ margin: 0, fontSize: '0.95rem', color: '#666' }}>{frete.descricao}</p>
                    </div>
                  </div>

                  {/* Lado Direito: Mapa Compacto + Valor */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <MapaRotaLeaflet
                      origem={frete.origem}
                      destino={frete.destino}
                      coordOrigem={COORDENADAS_CIDADES[frete.origem]}
                      coordDestino={COORDENADAS_CIDADES[frete.destino]}
                      distancia={frete.distancia}
                      compact={true}
                    />

                    {/* Valor e Ações */}
                    <div style={{
                      background: 'white',
                      padding: '15px',
                      borderRadius: '8px',
                      border: '1px solid #eee',
                      textAlign: 'center'
                    }}>
                      <p style={{ margin: 0, fontSize: '0.75rem', color: '#999', fontWeight: '600', marginBottom: '8px' }}>VALOR DA CARGA</p>
                      <h2 style={{ margin: '0 0 12px 0', color: '#667eea', fontSize: '1.7rem', fontWeight: '700' }}>
                        R$ {frete.valor_r.toLocaleString('pt-BR')}
                      </h2>
                      <button style={{
                        padding: '10px 16px',
                        background: '#667eea',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        fontSize: '0.85rem',
                        transition: 'all 0.2s',
                        width: '100%',
                        marginBottom: '8px'
                      }}
                      onMouseOver={(e) => { e.currentTarget.style.background = '#556cd6'; e.currentTarget.style.transform = 'scale(1.02)'; }}
                      onMouseOut={(e) => { e.currentTarget.style.background = '#667eea'; e.currentTarget.style.transform = 'scale(1)'; }}
                      >
                        ✓ Aceitar
                      </button>
                      <p style={{
                        margin: 0,
                        fontSize: '0.75rem',
                        color: frete.urgencia === 'muito alta' ? '#ff4444' : frete.urgencia === 'alta' ? '#ff8800' : '#2ecc71',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        {frete.urgencia === 'muito alta' ? '🔴 URGENTE' : frete.urgencia === 'alta' ? '🟠 ALTA' : '🟢 NORMAL'}
                      </p>
                    </div>
                  </div>
                </div>
                </div>
              ))}
            </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
