import { useState } from 'react';
import { apiService } from '../services/api';

interface ProposalModalProps {
  isOpen: boolean;
  freteId: number;
  freteOrigem: string;
  freteDestino: string;
  freteValor: number;
  onClose: () => void;
  onSuccess: () => void;
}

export const ProposalModal = ({
  isOpen,
  freteId,
  freteOrigem,
  freteDestino,
  freteValor,
  onClose,
  onSuccess,
}: ProposalModalProps) => {
  const [valorProposta, setValorProposta] = useState(freteValor.toString());
  const [mensagem, setMensagem] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro(null);

    const valor = parseFloat(valorProposta);
    if (isNaN(valor) || valor <= 0) {
      setErro('Valor deve ser maior que 0');
      return;
    }

    try {
      setIsLoading(true);
      await apiService.createProposal(freteId, valor, mensagem);
      onSuccess();
      onClose();
    } catch (error: any) {
      setErro(error?.response?.data?.detail || 'Erro ao fazer proposta');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '12px',
          padding: '40px',
          maxWidth: '500px',
          width: '90%',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          fontFamily: 'Inter, system-ui, sans-serif',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginTop: 0, color: '#333', fontSize: '1.5rem' }}>
          📦 Fazer Proposta
        </h2>

        <div
          style={{
            background: '#f5f5f5',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
          }}
        >
          <p style={{ margin: '0 0 8px 0', color: '#666', fontSize: '0.9rem' }}>
            <strong>Rota:</strong> {freteOrigem} → {freteDestino}
          </p>
          <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>
            <strong>Valor base:</strong> R$ {freteValor.toFixed(2)}
          </p>
        </div>

        {erro && (
          <div
            style={{
              background: '#fff0f0',
              color: '#cc0000',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '20px',
              fontSize: '0.9rem',
              border: '1px solid #ffcccc',
            }}
          >
            {erro}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
              }}
            >
              Seu Valor da Proposta (R$) *
            </label>
            <input
              type="number"
              value={valorProposta}
              onChange={(e) => setValorProposta(e.target.value)}
              step="0.01"
              min="0"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '1rem',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
              }}
              required
            />
          </div>

          <div style={{ marginBottom: '25px' }}>
            <label
              style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
              }}
            >
              Mensagem para o Shipper (opcional)
            </label>
            <textarea
              value={mensagem}
              onChange={(e) => setMensagem(e.target.value)}
              placeholder="Ex: Entrega em 2 dias, veículo refrigerado..."
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '1rem',
                boxSizing: 'border-box',
                fontFamily: 'inherit',
                minHeight: '80px',
                resize: 'vertical',
              }}
              maxLength={500}
            />
            <p style={{ margin: '4px 0 0 0', color: '#999', fontSize: '0.8rem' }}>
              {mensagem.length}/500 caracteres
            </p>
          </div>

          <div
            style={{
              display: 'flex',
              gap: '10px',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                background: 'white',
                color: '#333',
                fontWeight: '600',
                cursor: 'pointer',
                fontSize: '1rem',
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                borderRadius: '6px',
                background: '#667eea',
                color: 'white',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
                opacity: isLoading ? 0.6 : 1,
              }}
            >
              {isLoading ? 'Enviando...' : 'Enviar Proposta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
