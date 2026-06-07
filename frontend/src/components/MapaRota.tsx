import { useMemo } from 'react';
import { COORDENADAS_CIDADES } from '../data/freteData';

interface MapaRotaProps {
  origem: string;
  destino: string;
  distancia?: number;
  tempo?: string;
  compact?: boolean;
}

export const MapaRota = ({ origem, destino, distancia, tempo, compact = false }: MapaRotaProps) => {
  const { pontoOrigem, pontoDestino, linhaPath } = useMemo(() => {
    const coord1 = COORDENADAS_CIDADES[origem];
    const coord2 = COORDENADAS_CIDADES[destino];

    if (!coord1 || !coord2) {
      return { pontoOrigem: null, pontoDestino: null, linhaPath: '' };
    }

    // Mapa simplificado do Brasil: lat [-33.8 a 5.3], lng [-73.9 a -34.8]
    // Normalizar para SVG (0-400 x 0-300)
    const normalizarX = (lng: number) => ((lng + 73.9) / (73.9 - 34.8)) * 400;
    const normalizarY = (lat: number) => ((5.3 - lat) / (5.3 + 33.8)) * 300;

    const x1 = normalizarX(coord1.lng);
    const y1 = normalizarY(coord1.lat);
    const x2 = normalizarX(coord2.lng);
    const y2 = normalizarY(coord2.lat);

    // Caminho com curva bezier para ficar mais bonito
    const controlX = (x1 + x2) / 2;
    const controlY = (y1 + y2) / 2 - 50; // Controle para curva
    const path = `M ${x1} ${y1} Q ${controlX} ${controlY} ${x2} ${y2}`;

    return {
      pontoOrigem: { x: x1, y: y1, nome: origem.split(', ')[0] },
      pontoDestino: { x: x2, y: y2, nome: destino.split(', ')[0] },
      linhaPath: path
    };
  }, [origem, destino]);

  if (!pontoOrigem || !pontoDestino) {
    return (
      <div style={{
        background: '#f0f0f0',
        padding: '20px',
        borderRadius: '8px',
        textAlign: 'center',
        color: '#999'
      }}>
        <p>Selecione origem e destino para ver o mapa</p>
      </div>
    );
  }

  const altura = compact ? 200 : 300;
  const largura = compact ? 300 : 400;

  return (
    <div style={{
      background: '#f9f9f9',
      padding: compact ? '15px' : '20px',
      borderRadius: '10px',
      border: '1px solid #eee'
    }}>
      {!compact && (
        <>
          <h4 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '1rem', fontWeight: '600' }}>
            📍 Rota de Entrega
          </h4>
        </>
      )}

      <svg
        width={largura}
        height={altura}
        viewBox={`0 0 ${largura} ${altura}`}
        style={{
          border: '1px solid #ddd',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #e8f4f8 0%, #f0f9ff 100%)',
          display: 'block',
          margin: compact ? '0 auto' : '0 auto 15px'
        }}
      >
        {/* Linha de rota com gradiente */}
        <defs>
          <linearGradient id="gradienteRota" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#667eea', stopOpacity: 0.8 }} />
            <stop offset="100%" style={{ stopColor: '#764ba2', stopOpacity: 0.8 }} />
          </linearGradient>

          <filter id="shadow">
            <feDropShadow dx="2" dy="2" stdDeviation="3" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Mapa simplificado - contorno do Brasil */}
        <g opacity="0.15" strokeWidth="1">
          {/* Simplificação: desenhar alguns estados principais */}
          <circle cx="90" cy="100" r="15" fill="none" stroke="#999" />
          <circle cx="120" cy="110" r="12" fill="none" stroke="#999" />
          <circle cx="150" cy="90" r="18" fill="none" stroke="#999" />
          <circle cx="200" cy="130" r="20" fill="none" stroke="#999" />
          <circle cx="180" cy="80" r="25" fill="none" stroke="#999" />
        </g>

        {/* Linha de rota */}
        <path
          d={linhaPath}
          stroke="url(#gradienteRota)"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
          filter="url(#shadow)"
        />

        {/* Ponto de Origem */}
        <g>
          <circle
            cx={pontoOrigem.x}
            cy={pontoOrigem.y}
            r="8"
            fill="#2ecc71"
            stroke="white"
            strokeWidth="3"
            filter="url(#shadow)"
          />
          <circle
            cx={pontoOrigem.x}
            cy={pontoOrigem.y}
            r="14"
            fill="none"
            stroke="#2ecc71"
            strokeWidth="2"
            opacity="0.3"
          />
          {!compact && (
            <text
              x={pontoOrigem.x}
              y={pontoOrigem.y - 20}
              textAnchor="middle"
              style={{
                fontSize: '12px',
                fontWeight: '600',
                fill: '#333',
                pointerEvents: 'none'
              }}
            >
              {pontoOrigem.nome}
            </text>
          )}
        </g>

        {/* Ponto de Destino */}
        <g>
          <circle
            cx={pontoDestino.x}
            cy={pontoDestino.y}
            r="8"
            fill="#e74c3c"
            stroke="white"
            strokeWidth="3"
            filter="url(#shadow)"
          />
          <circle
            cx={pontoDestino.x}
            cy={pontoDestino.y}
            r="14"
            fill="none"
            stroke="#e74c3c"
            strokeWidth="2"
            opacity="0.3"
          />
          {!compact && (
            <text
              x={pontoDestino.x}
              y={pontoDestino.y + 25}
              textAnchor="middle"
              style={{
                fontSize: '12px',
                fontWeight: '600',
                fill: '#333',
                pointerEvents: 'none'
              }}
            >
              {pontoDestino.nome}
            </text>
          )}
        </g>
      </svg>

      {/* Informações de Rota */}
      {distancia && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          marginTop: compact ? '0' : '15px',
          fontSize: compact ? '0.85rem' : '0.95rem'
        }}>
          <div style={{
            background: 'white',
            padding: compact ? '8px' : '12px',
            borderRadius: '6px',
            border: '1px solid #eee',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0, color: '#999', fontSize: compact ? '0.75rem' : '0.85rem', fontWeight: '600' }}>
              DISTÂNCIA
            </p>
            <p style={{ margin: '5px 0 0 0', color: '#667eea', fontSize: compact ? '1rem' : '1.2rem', fontWeight: '700' }}>
              {distancia.toLocaleString('pt-BR')} km
            </p>
          </div>

          {tempo && (
            <div style={{
              background: 'white',
              padding: compact ? '8px' : '12px',
              borderRadius: '6px',
              border: '1px solid #eee',
              textAlign: 'center'
            }}>
              <p style={{ margin: 0, color: '#999', fontSize: compact ? '0.75rem' : '0.85rem', fontWeight: '600' }}>
                TEMPO EST.
              </p>
              <p style={{ margin: '5px 0 0 0', color: '#764ba2', fontSize: compact ? '1rem' : '1.2rem', fontWeight: '700' }}>
                ⏱️ {tempo}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
