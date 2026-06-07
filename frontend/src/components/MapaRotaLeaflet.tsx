import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useEffect } from 'react';
import 'leaflet/dist/leaflet.css';

// Corrigir ícones padrão do Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Ícones customizados
const iconOrigem = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const iconDestino = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface MapaRotaLeafletProps {
  origem: string;
  destino: string;
  coordOrigem?: { lat: number; lng: number };
  coordDestino?: { lat: number; lng: number };
  distancia?: number;
  tempo?: string;
  compact?: boolean;
}

// Componente para ajustar o zoom/bounds do mapa
const MapaBounds = ({ coordOrigem, coordDestino }: any) => {
  const map = useMap();

  useEffect(() => {
    if (coordOrigem && coordDestino) {
      const bounds = L.latLngBounds([
        [coordOrigem.lat, coordOrigem.lng],
        [coordDestino.lat, coordDestino.lng]
      ]);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coordOrigem, coordDestino, map]);

  return null;
};

export const MapaRotaLeaflet = ({
  origem,
  destino,
  coordOrigem,
  coordDestino,
  distancia,
  tempo,
  compact = false
}: MapaRotaLeafletProps) => {
  if (!coordOrigem || !coordDestino) {
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

  const altura = compact ? 200 : 350;
  const largura = '100%';

  return (
    <div style={{
      background: 'white',
      padding: compact ? '0' : '20px',
      borderRadius: '10px',
      border: '1px solid #eee',
      overflow: 'hidden'
    }}>
      {!compact && (
        <h4 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '1rem', fontWeight: '600' }}>
          📍 Rota de Entrega
        </h4>
      )}

      <MapContainer
        center={L.latLng(coordOrigem.lat, coordOrigem.lng)}
        zoom={6}
        style={{
          width: largura,
          height: `${altura}px`,
          borderRadius: compact ? '10px' : '8px',
          border: '1px solid #ddd'
        }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Marker de Origem */}
        <Marker position={L.latLng(coordOrigem.lat, coordOrigem.lng)} icon={iconOrigem}>
          <Popup>
            <div style={{ fontSize: '0.9rem', fontWeight: '600' }}>
              🟢 Origem<br />
              {origem}
            </div>
          </Popup>
        </Marker>

        {/* Marker de Destino */}
        <Marker position={L.latLng(coordDestino.lat, coordDestino.lng)} icon={iconDestino}>
          <Popup>
            <div style={{ fontSize: '0.9rem', fontWeight: '600' }}>
              🔴 Destino<br />
              {destino}
            </div>
          </Popup>
        </Marker>

        {/* Linha de Rota */}
        <Polyline
          positions={[
            L.latLng(coordOrigem.lat, coordOrigem.lng),
            L.latLng(coordDestino.lat, coordDestino.lng)
          ]}
          pathOptions={{ color: '#667eea', weight: 3, opacity: 0.8, dashArray: '5, 5' }}
        />

        {/* Ajustar bounds */}
        <MapaBounds coordOrigem={coordOrigem} coordDestino={coordDestino} />
      </MapContainer>

      {/* Informações de Rota */}
      {distancia && !compact && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          marginTop: '15px'
        }}>
          <div style={{
            background: '#f9f9f9',
            padding: '12px',
            borderRadius: '6px',
            border: '1px solid #eee',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>
              DISTÂNCIA
            </p>
            <p style={{ margin: '5px 0 0 0', color: '#667eea', fontSize: '1.2rem', fontWeight: '700' }}>
              {distancia.toLocaleString('pt-BR')} km
            </p>
          </div>

          {tempo && (
            <div style={{
              background: '#f9f9f9',
              padding: '12px',
              borderRadius: '6px',
              border: '1px solid #eee',
              textAlign: 'center'
            }}>
              <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>
                TEMPO EST.
              </p>
              <p style={{ margin: '5px 0 0 0', color: '#764ba2', fontSize: '1.2rem', fontWeight: '700' }}>
                ⏱️ {tempo}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
