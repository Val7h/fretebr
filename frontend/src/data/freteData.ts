// Estados brasileiros com suas principais cidades
export const ESTADOS_BRASIL = [
  { sigla: 'SP', nome: 'São Paulo' },
  { sigla: 'RJ', nome: 'Rio de Janeiro' },
  { sigla: 'MG', nome: 'Minas Gerais' },
  { sigla: 'BA', nome: 'Bahia' },
  { sigla: 'SC', nome: 'Santa Catarina' },
  { sigla: 'RS', nome: 'Rio Grande do Sul' },
  { sigla: 'PR', nome: 'Paraná' },
  { sigla: 'PE', nome: 'Pernambuco' },
  { sigla: 'CE', nome: 'Ceará' },
  { sigla: 'PA', nome: 'Pará' },
  { sigla: 'GO', nome: 'Goiás' },
  { sigla: 'DF', nome: 'Distrito Federal' },
];

// Cidades principais por estado
export const CIDADES_POR_ESTADO: Record<string, string[]> = {
  SP: ['São Paulo', 'Campinas', 'Santos', 'Sorocaba', 'Ribeirão Preto', 'Piracicaba'],
  RJ: ['Rio de Janeiro', 'Niterói', 'Duque de Caxias', 'Nova Iguaçu', 'São Gonçalo'],
  MG: ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Divinópolis'],
  BA: ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari', 'Ilhéus'],
  SC: ['Florianópolis', 'Joinville', 'Blumenau', 'Santa Catarina', 'Criciúma'],
  RS: ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Santa Maria', 'Novo Hamburgo'],
  PR: ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel'],
  PE: ['Recife', 'Jaboatão', 'Olinda', 'Caruaru', 'Petrolina'],
  CE: ['Fortaleza', 'Caucaia', 'Juazeiro', 'Maracanaú', 'Sobral'],
  PA: ['Belém', 'Ananindeua', 'Santarém', 'Marabá', 'Altamira'],
  GO: ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde', 'Inhumas'],
  DF: ['Brasília'],
};

// Coordenadas das cidades para calcular distância
export const COORDENADAS_CIDADES: Record<string, { lat: number; lng: number }> = {
  'São Paulo, SP': { lat: -23.5505, lng: -46.6333 },
  'Rio de Janeiro, RJ': { lat: -22.9068, lng: -43.1729 },
  'Belo Horizonte, MG': { lat: -19.9167, lng: -43.9345 },
  'Salvador, BA': { lat: -12.9714, lng: -38.5014 },
  'Brasília, DF': { lat: -15.7942, lng: -47.8822 },
  'Fortaleza, CE': { lat: -3.7319, lng: -38.5267 },
  'Recife, PE': { lat: -8.0476, lng: -34.877 },
  'Manaus, AM': { lat: -3.1190, lng: -60.0217 },
  'Curitiba, PR': { lat: -25.4284, lng: -49.2733 },
  'Porto Alegre, RS': { lat: -30.0277, lng: -51.2005 },
  'Belém, PA': { lat: -1.4558, lng: -48.4969 },
  'Goiânia, GO': { lat: -15.7975, lng: -48.8841 },
  'Campinas, SP': { lat: -22.9056, lng: -47.0581 },
  'Niterói, RJ': { lat: -22.8833, lng: -43.1 },
  'Uberlândia, MG': { lat: -18.9186, lng: -48.2772 },
  'Feira de Santana, BA': { lat: -12.2667, lng: -39.2667 },
  'Florianópolis, SC': { lat: -27.5969, lng: -48.5495 },
};

// Tabela de preço de frete baseado em distância e peso
// Preço = (distância/1000) * (peso/100) * fator
export const CALCULAR_PRECO_FRETE = (distancia: number, peso: number): number => {
  // Fator base: aumenta com urgência
  // Para 500kg em 430km = aproximadamente R$2.500
  const fatorBase = 11.6; // R$/km/tonelada

  const preco = (distancia / 1000) * (peso / 100) * fatorBase;

  // Preço mínimo de R$800
  return Math.max(preco, 800);
};

// Calcular distância entre duas cidades (Haversine formula)
export const CALCULAR_DISTANCIA = (
  origem: string,
  destino: string
): number => {
  const coord1 = COORDENADAS_CIDADES[origem];
  const coord2 = COORDENADAS_CIDADES[destino];

  if (!coord1 || !coord2) {
    return 0;
  }

  const R = 6371; // Raio da Terra em km
  const dLat = ((coord2.lat - coord1.lat) * Math.PI) / 180;
  const dLng = ((coord2.lng - coord1.lng) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((coord1.lat * Math.PI) / 180) *
      Math.cos((coord2.lat * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distancia = R * c;

  // Adicionar 15% por estradas não-lineares
  return Math.round(distancia * 1.15);
};

// Estimar tempo de viagem (média 80 km/h)
export const ESTIMAR_TEMPO = (distancia: number): string => {
  const horas = Math.round(distancia / 80);
  const dias = Math.ceil(horas / 24);

  if (horas < 24) {
    return `${horas}h ${Math.round((horas % 1) * 60)}m`;
  }
  return `${dias}d`;
};

// Fretes de exemplo para busca
export const FRETES_EXEMPLO = [
  {
    id: '1',
    origem: 'São Paulo, SP',
    destino: 'Rio de Janeiro, RJ',
    peso_kg: 500,
    distancia: 430,
    urgencia: 'alta' as const,
    descricao: 'Eletrônicos frágeis - vidro temperado. Cuidado!',
  },
  {
    id: '2',
    origem: 'Belo Horizonte, MG',
    destino: 'São Paulo, SP',
    peso_kg: 1200,
    distancia: 580,
    urgencia: 'normal' as const,
    descricao: 'Carga geral - paletes de alimentos industrializados',
  },
  {
    id: '3',
    origem: 'Brasília, DF',
    destino: 'Salvador, BA',
    peso_kg: 2500,
    distancia: 1850,
    urgencia: 'muito alta' as const,
    descricao: 'Alimentos perecíveis - refrigerado. Tempo crítico!',
  },
  {
    id: '4',
    origem: 'Curitiba, PR',
    destino: 'São Paulo, SP',
    peso_kg: 8000,
    distancia: 410,
    urgencia: 'normal' as const,
    descricao: 'Cimento e materiais de construção',
  },
  {
    id: '5',
    origem: 'Porto Alegre, RS',
    destino: 'São Paulo, SP',
    peso_kg: 15000,
    distancia: 1100,
    urgencia: 'normal' as const,
    descricao: 'Máquinas agrícolas - equipamentos industriais',
  },
];
