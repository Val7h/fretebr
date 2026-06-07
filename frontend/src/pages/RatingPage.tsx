import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface StarRatingProps {
  value: number;
  onChange: (value: number) => void;
}

const StarRating = ({ value, onChange }: StarRatingProps) => {
  const [hoverValue, setHoverValue] = useState(0);

  return (
    <div style={{ display: 'flex', gap: '8px', fontSize: '2.5rem' }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHoverValue(star)}
          onMouseLeave={() => setHoverValue(0)}
          style={{
            cursor: 'pointer',
            opacity: star <= (hoverValue || value) ? 1 : 0.3,
            transition: 'opacity 0.2s',
          }}
        >
          ⭐
        </span>
      ))}
    </div>
  );
};

export const RatingPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [stars, setStars] = useState(5);
  const [review, setReview] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState(false);
  const [userType, setUserType] = useState<'motorista' | 'shipper' | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!id || !userType) {
      setErro('Dados inválidos');
      return;
    }

    try {
      setIsLoading(true);
      setErro(null);

      const matchId = parseInt(id);

      if (userType === 'motorista') {
        // Motorista avaliando shipper
        await apiService.rateShipper(currentUser?.id || 0, stars, review.trim(), undefined, matchId);
      } else {
        // Shipper avaliando motorista
        await apiService.rateMotorista(currentUser?.id || 0, stars, review.trim(), undefined, matchId);
      }

      setSucesso(true);
      setTimeout(() => {
        navigate(-1);
      }, 2000);
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao enviar avaliação');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectType = (type: 'motorista' | 'shipper') => {
    setUserType(type);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif' }}>
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

      {!userType ? (
        <div
          style={{
            background: 'white',
            borderRadius: '12px',
            padding: '40px',
            boxShadow: '0 2px 16px rgba(0,0,0,0.08)',
            textAlign: 'center',
          }}
        >
          <h1 style={{ color: '#333', fontSize: '1.8rem', marginBottom: '30px' }}>
            ⭐ Avaliar Contato
          </h1>
          <p style={{ color: '#666', marginBottom: '30px', fontSize: '1rem' }}>
            Você faz parte de qual grupo?
          </p>

          <div style={{ display: 'grid', gap: '15px' }}>
            <button
              onClick={() => handleSelectType('motorista')}
              style={{
                padding: '20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '1rem',
                cursor: 'pointer',
                transition: 'all 0.3s',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              🚗 Sou Motorista
            </button>

            <button
              onClick={() => handleSelectType('shipper')}
              style={{
                padding: '20px',
                background: '#2e7d32',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '1rem',
                cursor: 'pointer',
                transition: 'all 0.3s',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(46, 125, 50, 0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              📦 Sou Shipper
            </button>
          </div>
        </div>
      ) : (
        <div
          style={{
            background: 'white',
            borderRadius: '12px',
            padding: '40px',
            boxShadow: '0 2px 16px rgba(0,0,0,0.08)',
          }}
        >
          <h1 style={{ marginTop: 0, color: '#333', fontSize: '1.8rem', marginBottom: '10px' }}>
            ⭐ Sua Avaliação
          </h1>
          <p style={{ color: '#666', marginBottom: '30px', fontSize: '0.95rem' }}>
            {userType === 'motorista'
              ? 'Qual sua experiência com o shipper?'
              : 'Qual sua experiência com o motorista?'}
          </p>

          {sucesso && (
            <div
              style={{
                background: '#e8f5e9',
                color: '#2e7d32',
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '20px',
                fontWeight: '600',
                textAlign: 'center',
              }}
            >
              ✅ Avaliação enviada com sucesso! Redirecionando...
            </div>
          )}

          {erro && (
            <div
              style={{
                background: '#fff0f0',
                color: '#cc0000',
                padding: '16px',
                borderRadius: '8px',
                marginBottom: '20px',
                fontWeight: '600',
              }}
            >
              {erro}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Seleção de Estrelas */}
            <div style={{ marginBottom: '30px', textAlign: 'center' }}>
              <p style={{ margin: '0 0 15px 0', color: '#999', fontSize: '0.9rem', textTransform: 'uppercase' }}>
                Escolha sua nota
              </p>
              <StarRating value={stars} onChange={setStars} />
              <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '1rem', fontWeight: '600' }}>
                {stars === 5 && '🌟 Excelente!'}
                {stars === 4 && '👍 Muito Bom!'}
                {stars === 3 && '😐 Bom'}
                {stars === 2 && '👎 Ruim'}
                {stars === 1 && '😞 Muito Ruim'}
              </p>
            </div>

            {/* Comentário */}
            <div style={{ marginBottom: '25px' }}>
              <label
                style={{
                  display: 'block',
                  fontWeight: '600',
                  marginBottom: '8px',
                  color: '#333',
                }}
              >
                Deixe um comentário (opcional)
              </label>
              <textarea
                value={review}
                onChange={(e) => setReview(e.target.value)}
                placeholder="Compartilhe sua experiência..."
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '0.95rem',
                  fontFamily: 'inherit',
                  minHeight: '120px',
                  resize: 'vertical',
                  boxSizing: 'border-box',
                }}
                maxLength={1000}
              />
              <p style={{ margin: '4px 0 0 0', color: '#999', fontSize: '0.8rem' }}>
                {review.length}/1000 caracteres
              </p>
            </div>

            {/* Botões */}
            <div
              style={{
                display: 'flex',
                gap: '10px',
              }}
            >
              <button
                type="button"
                onClick={() => {
                  setUserType(null);
                  setStars(5);
                  setReview('');
                  setErro(null);
                }}
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
                Voltar
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
                {isLoading ? 'Enviando...' : '✅ Enviar Avaliação'}
              </button>
            </div>
          </form>

          {/* Dicas */}
          <div style={{ marginTop: '30px', padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
            <p style={{ margin: '0 0 8px 0', fontWeight: '600', color: '#333', fontSize: '0.9rem' }}>
              💡 Dicas para uma boa avaliação:
            </p>
            <ul style={{ margin: '8px 0 0 20px', color: '#666', fontSize: '0.85rem' }}>
              <li>Seja honesto e justo</li>
              <li>Descreva sua experiência</li>
              <li>Mencione pontos positivos e negativos</li>
              <li>Ajude outros usuários a tomar decisões melhores</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
