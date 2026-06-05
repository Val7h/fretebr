import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import { useAuth } from '../context/AuthContext';
import type { Match } from '../services/matchesApi';

export const RatingPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [match, setMatch] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [rating, setRating] = useState(5);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    if (id) {
      fetchMatch(id);
    }
  }, [id]);

  const fetchMatch = async (matchId: string) => {
    setIsLoading(true);
    setError('');
    try {
      const data = await matchesApi.getMatchById(matchId);
      setMatch(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar match';
      setError(errorMessage);
      console.error('Error fetching match:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitRating = async () => {
    if (!match || !id) return;

    if (feedback.length > 500) {
      setError('Feedback não pode exceder 500 caracteres');
      return;
    }

    setIsSubmitting(true);
    setError('');
    try {
      // Mock API call - in production, call: await ratingsApi.submitRating(id, rating, feedback);
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API call

      setSuccess(true);
      setTimeout(() => {
        navigate('/meus-matches');
      }, 2000);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao enviar avaliação';
      setError(errorMessage);
      console.error('Error submitting rating:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRatingLabel = (value: number) => {
    const labels = ['Péssimo', 'Ruim', 'Neutro', 'Bom', 'Excelente'];
    return labels[value - 1] || '';
  };

  const isMotoristaUser = currentUser?.tipo === 'motorista';
  const ratingTarget = isMotoristaUser ? match?.shipper : match?.motorista;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados da avaliação...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
          <button
            onClick={() => navigate('/meus-matches')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Voltar
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-6">
            {error}
          </div>
        )}

        {!match || !ratingTarget ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Avaliação não disponível</h2>
            <button
              onClick={() => navigate('/meus-matches')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
            >
              Voltar aos Matches
            </button>
          </div>
        ) : success ? (
          /* Success State */
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4 animate-bounce">✅</div>
            <h2 className="text-3xl font-bold text-green-600 mb-4">Obrigado pela Avaliação!</h2>
            <p className="text-gray-600 mb-6">Sua avaliação foi registrada com sucesso.</p>
            <p className="text-sm text-gray-500">Redirecionando para seus matches...</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h1 className="text-3xl font-bold text-gray-900">Avalie a Entrega</h1>
            </div>

            {/* User Info Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {isMotoristaUser ? 'Avaliando Shipper' : 'Avaliando Motorista'}
              </h2>
              <div className="flex items-center gap-4 bg-gray-50 p-4 rounded-lg">
                <div className="w-12 h-12 bg-blue-200 rounded-full flex items-center justify-center">
                  <span className="text-xl">👤</span>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{ratingTarget.nome}</p>
                  <p className="text-sm text-gray-600">{ratingTarget.email}</p>
                </div>
              </div>
            </div>

            {/* Frete Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Resumo do Frete</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Rota</p>
                  <p className="font-semibold text-gray-900">
                    {match.frete?.origem} → {match.frete?.destino}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Valor</p>
                  <p className="font-semibold text-green-600">R$ {match.frete?.valor_r.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Peso</p>
                  <p className="font-semibold text-gray-900">{match.frete?.peso_kg} kg</p>
                </div>
                <div>
                  <p className="text-gray-600">Status</p>
                  <p className="font-semibold text-green-600">Entregue ✅</p>
                </div>
              </div>
            </div>

            {/* Rating Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Sua Avaliação</h2>

              {/* Stars */}
              <div className="mb-8">
                <p className="text-sm text-gray-600 mb-4">Como foi sua experiência?</p>
                <div className="flex justify-center gap-4 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      className={`text-5xl transition-transform ${
                        star <= rating ? 'scale-125 text-yellow-400' : 'text-gray-300 hover:text-yellow-200'
                      }`}
                    >
                      ⭐
                    </button>
                  ))}
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-500 mb-1">{rating}/5</p>
                  <p className="text-lg text-gray-600">{getRatingLabel(rating)}</p>
                </div>
              </div>

              {/* Feedback Textarea */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback (opcional)
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Diga-nos mais sobre sua experiência..."
                  maxLength={500}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                />
                <div className="text-right text-xs text-gray-500 mt-2">
                  {feedback.length}/500 caracteres
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmitRating}
              disabled={isSubmitting}
              className={`w-full py-3 px-4 rounded-lg font-medium text-white transition ${
                isSubmitting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isSubmitting ? 'Enviando Avaliação...' : 'Enviar Avaliação'}
            </button>

            {/* Cancel Button */}
            <button
              onClick={() => navigate('/meus-matches')}
              disabled={isSubmitting}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-3 px-4 rounded-lg transition"
            >
              Voltar sem Avaliar
            </button>
          </div>
        )}
      </main>
    </div>
  );
};
