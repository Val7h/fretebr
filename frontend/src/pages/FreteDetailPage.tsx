import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ProposalModal } from '../components/ProposalModal';

interface Frete {
  id: number;
  origem: string;
  destino: string;
  peso_kg: number;
  valor_r: number;
  descricao: string;
  status: string;
  motorista_id: number;
  motorista: {
    id: number;
    nome: string;
    email: string;
  };
  created_at: string;
}

interface Proposta {
  id: number;
  motorista_id: number;
  motorista_nome: string;
  motorista_email: string;
  valor_proposta: number;
  status: string;
  mensagem: string;
  created_at: string;
}

export const FreteDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [frete, setFrete] = useState<Frete | null>(null);
  const [propostas, setPropostas] = useState<Proposta[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [aceitandoId, setAceitandoId] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setErro(null);

      if (!id) {
        setErro('Frete não encontrado');
        return;
      }

      const freteData = await apiService.getFrete(parseInt(id));
      setFrete(freteData);

      // Se for o shipper que postou, carregar propostas
      if (currentUser?.id === freteData.motorista_id) {
        try {
          const propData = await apiService.getFreteProposals(parseInt(id));
          setPropostas(propData);
        } catch (e) {
          // Sem propostas ainda
        }
      }
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao carregar frete');
    } finally {
      setIsLoading(false);
    }
  };

  const isShipper = currentUser?.tipo === 'shipper';
  const isOwner = currentUser?.id === frete?.motorista_id;
  const isMotorista = currentUser?.tipo === 'motorista';

  const handleAcceptProposal = async (proposalId: number) => {
    try {
      setAceitandoId(proposalId);
      await apiService.acceptProposal(proposalId);
      loadData();
    } catch (error: any) {
      alert(error?.response?.data?.detail || 'Erro ao aceitar proposta');
    } finally {
      setAceitandoId(null);
    }
  };

  const handleRejectProposal = async (proposalId: number) => {
    try {
      await apiService.rejectProposal(proposalId);
      loadData();
    } catch (error: any) {
      alert(error?.response?.data?.detail || 'Erro ao rejeitar proposta');
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Carregando detalhes...</p>
      </div>
    );
  }

  if (erro || !frete) {
    return (
      <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <div style={{ color: 'red', padding: '20px', background: '#fff0f0', borderRadius: '8px' }}>
          {erro || 'Frete não encontrado'}
        </div>
        <button
          onClick={() => navigate('/procurar-fretes')}
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
          Voltar
        </button>
      </div>
    );
  }

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
            📦 Detalhes do Frete
          </h1>
          <span
            style={{
              padding: '8px 16px',
              background: frete.status === 'disponível' ? '#e8f5e9' : '#fff3e0',
              color: frete.status === 'disponível' ? '#2e7d32' : '#e65100',
              borderRadius: '20px',
              fontWeight: '600',
            }}
          >
            {frete.status.charAt(0).toUpperCase() + frete.status.slice(1)}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginTop: '30px' }}>
          <div>
            <h3 style={{ margin: '0 0 15px 0', color: '#666', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Informações Principais
            </h3>
            <div style={{ display: 'grid', gap: '15px' }}>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Origem</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>📍 {frete.origem}</p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Destino</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>📍 {frete.destino}</p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Peso</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#333' }}>{frete.peso_kg} kg</p>
              </div>
              <div>
                <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.85rem' }}>Valor Base</p>
                <p style={{ margin: 0, fontWeight: '600', color: '#667eea', fontSize: '1.2rem' }}>
                  R$ {frete.valor_r.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 style={{ margin: '0 0 15px 0', color: '#666', fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Publicado por
            </h3>
            <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px' }}>
              <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Transportador</p>
              <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>
                {frete.motorista.nome}
              </p>
              <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                📧 {frete.motorista.email}
              </p>
            </div>

            {frete.descricao && (
              <div style={{ marginTop: '15px' }}>
                <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Descrição</p>
                <p style={{ margin: 0, color: '#666', fontSize: '0.95rem', lineHeight: '1.5' }}>
                  {frete.descricao}
                </p>
              </div>
            )}

            {isMotorista && !isOwner && frete.status === 'disponível' && (
              <button
                onClick={() => setShowProposalModal(true)}
                style={{
                  marginTop: '20px',
                  width: '100%',
                  padding: '12px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  fontSize: '1rem',
                }}
              >
                💼 Fazer Proposta
              </button>
            )}
          </div>
        </div>
      </div>

      {isOwner && (
        <div
          style={{
            background: 'white',
            borderRadius: '12px',
            padding: '30px',
            boxShadow: '0 2px 16px rgba(0,0,0,0.08)',
          }}
        >
          <h2 style={{ marginTop: 0, color: '#333', fontSize: '1.5rem', marginBottom: '20px' }}>
            💼 Propostas Recebidas ({propostas.length})
          </h2>

          {propostas.length === 0 ? (
            <p style={{ color: '#999', textAlign: 'center', padding: '30px 0' }}>
              Nenhuma proposta recebida ainda.
            </p>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {propostas.map((prop) => (
                <div
                  key={prop.id}
                  style={{
                    border: '1px solid #f0f0f0',
                    borderRadius: '8px',
                    padding: '15px',
                    background: prop.status === 'aceito' ? '#f0f8ff' : '#fff',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                    <div>
                      <p style={{ margin: '0 0 3px 0', fontWeight: '600', color: '#333' }}>
                        {prop.motorista_nome}
                      </p>
                      <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                        {prop.motorista_email}
                      </p>
                    </div>
                    <span
                      style={{
                        padding: '4px 12px',
                        background: prop.status === 'aceito' ? '#e8f5e9' : prop.status === 'rejeitado' ? '#ffebee' : '#fff3e0',
                        color: prop.status === 'aceito' ? '#2e7d32' : prop.status === 'rejeitado' ? '#c62828' : '#e65100',
                        borderRadius: '20px',
                        fontSize: '0.8rem',
                        fontWeight: '600',
                      }}
                    >
                      {prop.status === 'aceito' ? '✅ ACEITA' : prop.status === 'rejeitado' ? '❌ REJEITADA' : '⏳ PENDENTE'}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
                    <div>
                      <p style={{ margin: '0 0 2px 0', color: '#999', fontSize: '0.8rem' }}>Valor Proposto</p>
                      <p style={{ margin: 0, fontWeight: '600', color: '#667eea', fontSize: '1.1rem' }}>
                        R$ {prop.valor_proposta.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 2px 0', color: '#999', fontSize: '0.8rem' }}>Diferença</p>
                      <p style={{ margin: 0, fontWeight: '600', color: prop.valor_proposta < frete.valor_r ? '#2e7d32' : '#ff6b6b' }}>
                        {prop.valor_proposta < frete.valor_r ? '▼' : '▲'} R$ {Math.abs(prop.valor_proposta - frete.valor_r).toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {prop.mensagem && (
                    <div style={{ background: '#f9f9f9', padding: '10px', borderRadius: '6px', marginBottom: '10px' }}>
                      <p style={{ margin: '0 0 5px 0', color: '#999', fontSize: '0.8rem' }}>Mensagem</p>
                      <p style={{ margin: 0, color: '#666', fontSize: '0.9rem', fontStyle: 'italic' }}>
                        "{prop.mensagem}"
                      </p>
                    </div>
                  )}

                  {prop.status === 'pendente' && (
                    <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                      <button
                        onClick={() => handleAcceptProposal(prop.id)}
                        disabled={aceitandoId === prop.id}
                        style={{
                          flex: 1,
                          padding: '8px',
                          background: '#2e7d32',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          fontWeight: '600',
                          cursor: 'pointer',
                          fontSize: '0.9rem',
                          opacity: aceitandoId === prop.id ? 0.6 : 1,
                        }}
                      >
                        ✅ Aceitar
                      </button>
                      <button
                        onClick={() => handleRejectProposal(prop.id)}
                        style={{
                          flex: 1,
                          padding: '8px',
                          background: '#c62828',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          fontWeight: '600',
                          cursor: 'pointer',
                          fontSize: '0.9rem',
                        }}
                      >
                        ❌ Rejeitar
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <ProposalModal
        isOpen={showProposalModal}
        freteId={frete.id}
        freteOrigem={frete.origem}
        freteDestino={frete.destino}
        freteValor={frete.valor_r}
        onClose={() => setShowProposalModal(false)}
        onSuccess={loadData}
      />
    </div>
  );
};
