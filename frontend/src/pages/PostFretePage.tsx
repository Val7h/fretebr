import { useState, useMemo } from 'react';
import {
  ESTADOS_BRASIL,
  CIDADES_POR_ESTADO,
  CALCULAR_DISTANCIA,
  CALCULAR_PRECO_FRETE,
  ESTIMAR_TEMPO,
} from '../data/freteData';
import { MapaRota } from '../components/MapaRota';

interface FormData {
  estado_origem: string;
  cidade_origem: string;
  estado_destino: string;
  cidade_destino: string;
  peso_kg: string;
  descricao: string;
  urgencia: 'normal' | 'alta' | 'muito alta';
  data_entrega: string;
  telefone: string;
  email: string;
}

interface ModalState {
  aberto: boolean;
  titulo: string;
  mensagem: string;
  tipo: 'sucesso' | 'erro';
}

export const PostFretePage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    estado_origem: '',
    cidade_origem: '',
    estado_destino: '',
    cidade_destino: '',
    peso_kg: '',
    descricao: '',
    urgencia: 'normal',
    data_entrega: '',
    telefone: '',
    email: ''
  });

  const [erros, setErros] = useState<Record<string, string>>({});
  const [modal, setModal] = useState<ModalState>({
    aberto: false,
    titulo: '',
    mensagem: '',
    tipo: 'sucesso'
  });

  // Cálculos automáticos
  const precoCalculado = useMemo(() => {
    if (!formData.estado_origem || !formData.cidade_origem || !formData.estado_destino || !formData.cidade_destino || !formData.peso_kg) {
      return null;
    }

    const origem = `${formData.cidade_origem}, ${formData.estado_origem}`;
    const destino = `${formData.cidade_destino}, ${formData.estado_destino}`;
    const distancia = CALCULAR_DISTANCIA(origem, destino);
    const preco = CALCULAR_PRECO_FRETE(distancia, parseInt(formData.peso_kg) || 0);
    const tempo = ESTIMAR_TEMPO(distancia);

    return { distancia, preco, tempo };
  }, [formData.estado_origem, formData.cidade_origem, formData.estado_destino, formData.cidade_destino, formData.peso_kg]);

  const cidadesOrigem = formData.estado_origem ? CIDADES_POR_ESTADO[formData.estado_origem as keyof typeof CIDADES_POR_ESTADO] || [] : [];
  const cidadesDestino = formData.estado_destino ? CIDADES_POR_ESTADO[formData.estado_destino as keyof typeof CIDADES_POR_ESTADO] || [] : [];

  const validarStep = (stepNum: number): boolean => {
    const novosErros: Record<string, string> = {};

    if (stepNum === 1) {
      if (!formData.estado_origem) novosErros.estado_origem = 'Estado de origem é obrigatório';
      if (!formData.cidade_origem) novosErros.cidade_origem = 'Cidade de origem é obrigatória';
      if (!formData.estado_destino) novosErros.estado_destino = 'Estado de destino é obrigatório';
      if (!formData.cidade_destino) novosErros.cidade_destino = 'Cidade de destino é obrigatória';
      if (!formData.peso_kg) novosErros.peso_kg = 'Peso é obrigatório';
      const peso = parseInt(formData.peso_kg);
      if (peso < 100) novosErros.peso_kg = 'Peso mínimo é 100 kg';
      if (peso > 30000) novosErros.peso_kg = 'Peso máximo é 30.000 kg';
    }

    if (stepNum === 2) {
      if (!formData.descricao.trim()) novosErros.descricao = 'Descrição é obrigatória';
      if (!formData.data_entrega) novosErros.data_entrega = 'Data de entrega é obrigatória';
    }

    if (stepNum === 3) {
      if (!formData.telefone.trim()) novosErros.telefone = 'Telefone é obrigatório';
      if (!formData.email.trim()) novosErros.email = 'Email é obrigatório';
      if (formData.email && !formData.email.includes('@')) novosErros.email = 'Email inválido';
    }

    setErros(novosErros);
    return Object.keys(novosErros).length === 0;
  };

  const handleProxima = () => {
    if (validarStep(step)) {
      setStep(step + 1);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validarStep(step)) {
      setModal({
        aberto: true,
        titulo: '✅ Frete Postado com Sucesso!',
        mensagem: `Seu frete foi publicado e está visível para transportadores. Você receberá notificações de interesse.`,
        tipo: 'sucesso'
      });

      // Resetar form após 3 segundos
      setTimeout(() => {
        setModal({ aberto: false, titulo: '', mensagem: '', tipo: 'sucesso' });
        setStep(1);
        setFormData({
          estado_origem: '',
          cidade_origem: '',
          estado_destino: '',
          cidade_destino: '',
          peso_kg: '',
          descricao: '',
          urgencia: 'normal',
          data_entrega: '',
          telefone: '',
          email: ''
        });
      }, 3000);
    }
  };

  return (
    <div style={{ background: '#f5f5f5', minHeight: '100vh', padding: '20px', fontFamily: 'Inter, system-ui, sans-serif' }}>
      <div style={{ maxWidth: '750px', margin: '0 auto' }}>
        <h1 style={{ color: '#333', textAlign: 'center', marginBottom: '10px', fontSize: '2rem', fontWeight: '600' }}>📝 Postar Novo Frete</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px', fontSize: '0.95rem' }}>Publique seu frete e receba propostas de transportadores</p>

        {/* Progress Bar */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '40px',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          {[1, 2, 3].map((s, idx) => (
            <div key={s} style={{ display: 'flex', alignItems: 'center' }}>
              <div
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: s <= step ? '#667eea' : '#e0e0e0',
                  color: s <= step ? 'white' : '#999',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.1rem',
                  cursor: s < step ? 'pointer' : 'default',
                  transition: 'all 0.3s',
                  boxShadow: s <= step ? '0 4px 12px rgba(102, 126, 234, 0.3)' : 'none'
                }}
                onClick={() => s < step && setStep(s)}
                onMouseOver={(e) => {
                  if (s < step) {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                {s}
              </div>
              {idx < 2 && (
                <div style={{
                  width: '40px',
                  height: '2px',
                  background: s < step ? '#667eea' : '#e0e0e0',
                  margin: '0 8px'
                }}></div>
              )}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          {/* Step 1: Rota e Carga */}
          {step === 1 && (
            <div style={{
              background: 'white',
              padding: '35px',
              borderRadius: '12px',
              boxShadow: '0 2px 16px rgba(0,0,0,0.08)'
            }}>
              <h2 style={{ marginTop: 0, marginBottom: '25px', color: '#333', fontSize: '1.3rem', fontWeight: '600' }}>📍 Rota e Carga</h2>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Estado de Origem *</label>
                  <select
                    value={formData.estado_origem}
                    onChange={(e) => setFormData({ ...formData, estado_origem: e.target.value, cidade_origem: '' })}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.estado_origem ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem',
                      fontFamily: 'inherit'
                    }}
                  >
                    <option value="">Selecionar...</option>
                    {ESTADOS_BRASIL.map(estado => (
                      <option key={estado.sigla} value={estado.sigla}>{estado.nome} ({estado.sigla})</option>
                    ))}
                  </select>
                  {erros.estado_origem && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.estado_origem}</p>}
                </div>

                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Cidade de Origem *</label>
                  <select
                    value={formData.cidade_origem}
                    onChange={(e) => setFormData({ ...formData, cidade_origem: e.target.value })}
                    disabled={!formData.estado_origem}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.cidade_origem ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem',
                      fontFamily: 'inherit',
                      opacity: !formData.estado_origem ? 0.5 : 1,
                      cursor: !formData.estado_origem ? 'not-allowed' : 'pointer'
                    }}
                  >
                    <option value="">Selecionar...</option>
                    {cidadesOrigem.map(cidade => (
                      <option key={cidade} value={cidade}>{cidade}</option>
                    ))}
                  </select>
                  {erros.cidade_origem && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.cidade_origem}</p>}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '25px' }}>
                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Estado de Destino *</label>
                  <select
                    value={formData.estado_destino}
                    onChange={(e) => setFormData({ ...formData, estado_destino: e.target.value, cidade_destino: '' })}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.estado_destino ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem',
                      fontFamily: 'inherit'
                    }}
                  >
                    <option value="">Selecionar...</option>
                    {ESTADOS_BRASIL.map(estado => (
                      <option key={estado.sigla} value={estado.sigla}>{estado.nome} ({estado.sigla})</option>
                    ))}
                  </select>
                  {erros.estado_destino && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.estado_destino}</p>}
                </div>

                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Cidade de Destino *</label>
                  <select
                    value={formData.cidade_destino}
                    onChange={(e) => setFormData({ ...formData, cidade_destino: e.target.value })}
                    disabled={!formData.estado_destino}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.cidade_destino ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem',
                      fontFamily: 'inherit',
                      opacity: !formData.estado_destino ? 0.5 : 1,
                      cursor: !formData.estado_destino ? 'not-allowed' : 'pointer'
                    }}
                  >
                    <option value="">Selecionar...</option>
                    {cidadesDestino.map(cidade => (
                      <option key={cidade} value={cidade}>{cidade}</option>
                    ))}
                  </select>
                  {erros.cidade_destino && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.cidade_destino}</p>}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '25px' }}>
                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Peso (kg) * <span style={{ fontSize: '0.85rem', color: '#999' }}>100 - 30.000</span></label>
                  <input
                    type="number"
                    placeholder="500"
                    min="100"
                    max="30000"
                    value={formData.peso_kg}
                    onChange={(e) => setFormData({ ...formData, peso_kg: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.peso_kg ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem'
                    }}
                  />
                  {erros.peso_kg && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.peso_kg}</p>}
                </div>

                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Urgência</label>
                  <select
                    value={formData.urgencia}
                    onChange={(e) => setFormData({ ...formData, urgencia: e.target.value as 'normal' | 'alta' | 'muito alta' })}
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
                    <option value="normal">🟢 Normal</option>
                    <option value="alta">🟠 Alta</option>
                    <option value="muito alta">🔴 Muito Alta</option>
                  </select>
                </div>
              </div>

              {/* Resumo de Preço */}
              {precoCalculado && (
                <>
                  <div style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #556cd6 100%)',
                    padding: '20px',
                    borderRadius: '10px',
                    color: 'white',
                    marginBottom: '25px'
                  }}>
                    <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.9, marginBottom: '8px' }}>Estimativa de Frete</p>
                    <h3 style={{ margin: 0, fontSize: '1.8rem', fontWeight: '700' }}>R$ {precoCalculado.preco.toLocaleString('pt-BR')}</h3>
                    <p style={{ margin: '10px 0 0 0', fontSize: '0.85rem', opacity: 0.8 }}>
                      📍 {precoCalculado.distancia.toLocaleString('pt-BR')} km · ⏱️ {precoCalculado.tempo}
                    </p>
                  </div>

                  {/* Mapa da Rota */}
                  <MapaRota
                    origem={`${formData.cidade_origem}, ${formData.estado_origem}`}
                    destino={`${formData.cidade_destino}, ${formData.estado_destino}`}
                    distancia={precoCalculado.distancia}
                    tempo={precoCalculado.tempo}
                  />
                </>
              )}
            </div>
          )}

          {/* Step 2: Detalhes */}
          {step === 2 && (
            <div style={{
              background: 'white',
              padding: '35px',
              borderRadius: '12px',
              boxShadow: '0 2px 16px rgba(0,0,0,0.08)'
            }}>
              <h2 style={{ marginTop: 0, marginBottom: '25px', color: '#333', fontSize: '1.3rem', fontWeight: '600' }}>📋 Detalhes da Carga</h2>

              <div style={{ marginBottom: '25px' }}>
                <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Descrição *</label>
                <textarea
                  placeholder="Descreva o conteúdo, tipo de embalagem, instruções especiais, cuidados de manuseio, etc..."
                  value={formData.descricao}
                  onChange={(e) => setFormData({ ...formData, descricao: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: erros.descricao ? '2px solid #ff4444' : '1px solid #ddd',
                    borderRadius: '6px',
                    boxSizing: 'border-box',
                    fontSize: '1rem',
                    minHeight: '120px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
                {erros.descricao && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.descricao}</p>}
              </div>

              <div>
                <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Data de Entrega *</label>
                <input
                  type="date"
                  value={formData.data_entrega}
                  onChange={(e) => setFormData({ ...formData, data_entrega: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: erros.data_entrega ? '2px solid #ff4444' : '1px solid #ddd',
                    borderRadius: '6px',
                    boxSizing: 'border-box',
                    fontSize: '1rem'
                  }}
                />
                {erros.data_entrega && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.data_entrega}</p>}
              </div>
            </div>
          )}

          {/* Step 3: Contato */}
          {step === 3 && (
            <div style={{
              background: 'white',
              padding: '35px',
              borderRadius: '12px',
              boxShadow: '0 2px 16px rgba(0,0,0,0.08)'
            }}>
              <h2 style={{ marginTop: 0, marginBottom: '25px', color: '#333', fontSize: '1.3rem', fontWeight: '600' }}>📱 Informações de Contato</h2>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Telefone *</label>
                  <input
                    type="tel"
                    placeholder="(11) 99999-9999"
                    value={formData.telefone}
                    onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.telefone ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem'
                    }}
                  />
                  {erros.telefone && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.telefone}</p>}
                </div>

                <div>
                  <label style={{ fontWeight: '600', display: 'block', marginBottom: '8px', color: '#333', fontSize: '0.95rem' }}>Email *</label>
                  <input
                    type="email"
                    placeholder="seu@email.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: erros.email ? '2px solid #ff4444' : '1px solid #ddd',
                      borderRadius: '6px',
                      boxSizing: 'border-box',
                      fontSize: '1rem'
                    }}
                  />
                  {erros.email && <p style={{ color: '#ff4444', fontSize: '0.85rem', margin: '5px 0 0 0' }}>{erros.email}</p>}
                </div>
              </div>

              {/* Resumo Final */}
              <div style={{
                background: '#f9f9f9',
                border: '1px solid #eee',
                padding: '20px',
                borderRadius: '10px',
                marginBottom: '30px'
              }}>
                <h4 style={{ marginTop: 0, marginBottom: '15px', color: '#333', fontSize: '1.1rem', fontWeight: '600' }}>📦 Resumo do Frete</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', fontSize: '0.95rem' }}>
                  <div>
                    <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>ROTA</p>
                    <p style={{ margin: '8px 0 0 0', color: '#333', fontWeight: '600' }}>📍 {formData.cidade_origem}, {formData.estado_origem} → {formData.cidade_destino}, {formData.estado_destino}</p>
                  </div>
                  <div>
                    <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>CARGA</p>
                    <p style={{ margin: '8px 0 0 0', color: '#333', fontWeight: '600' }}>📦 {formData.peso_kg} kg</p>
                  </div>
                  <div>
                    <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>ENTREGA</p>
                    <p style={{ margin: '8px 0 0 0', color: '#333', fontWeight: '600' }}>📅 {formData.data_entrega}</p>
                  </div>
                  <div>
                    <p style={{ margin: 0, color: '#999', fontSize: '0.85rem', fontWeight: '600' }}>URGÊNCIA</p>
                    <p style={{ margin: '8px 0 0 0', color: '#333', fontWeight: '600' }}>
                      {formData.urgencia === 'normal' ? '🟢 Normal' : formData.urgencia === 'alta' ? '🟠 Alta' : '🔴 Muito Alta'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Botões */}
          <div style={{
            display: 'flex',
            gap: '15px',
            marginTop: '30px',
            justifyContent: 'space-between'
          }}>
            <button
              type="button"
              onClick={() => setStep(step - 1)}
              disabled={step === 1}
              style={{
                padding: '13px 32px',
                background: step === 1 ? '#e0e0e0' : '#f0f0f0',
                color: '#333',
                border: '1px solid #ddd',
                borderRadius: '6px',
                cursor: step === 1 ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '0.95rem',
                opacity: step === 1 ? 0.5 : 1,
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                if (step !== 1) {
                  e.currentTarget.style.background = '#e8e8e8';
                }
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = step === 1 ? '#e0e0e0' : '#f0f0f0';
              }}
            >
              ← Anterior
            </button>

            {step < 3 ? (
              <button
                type="button"
                onClick={handleProxima}
                style={{
                  padding: '13px 32px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  transition: 'all 0.2s',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#556cd6';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = '#667eea';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                Próxima →
              </button>
            ) : (
              <button
                type="submit"
                style={{
                  padding: '13px 32px',
                  background: '#2ecc71',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  transition: 'all 0.2s',
                  boxShadow: '0 4px 12px rgba(46, 204, 113, 0.3)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#27ae60';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = '#2ecc71';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                ✓ Publicar Frete
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Modal de Sucesso */}
      {modal.aberto && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '16px',
            textAlign: 'center',
            maxWidth: '450px',
            width: '90%',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.2)',
            border: '2px solid #2ecc71'
          }}>
            <div style={{ fontSize: '3.5rem', marginBottom: '20px', animation: 'bounce 0.6s' }}>
              ✅
            </div>
            <h2 style={{ margin: '0 0 15px 0', color: '#2ecc71', fontSize: '1.8rem', fontWeight: '700' }}>
              {modal.titulo}
            </h2>
            <p style={{ margin: '0 0 25px 0', color: '#666', fontSize: '1rem', lineHeight: '1.5' }}>
              {modal.mensagem}
            </p>
            <p style={{ margin: 0, color: '#999', fontSize: '0.9rem' }}>
              Redirecionando em instantes...
            </p>
          </div>
          <style>{`
            @keyframes bounce {
              0%, 100% { transform: scale(1); }
              50% { transform: scale(1.1); }
            }
          `}</style>
        </div>
      )}
    </div>
  );
};
