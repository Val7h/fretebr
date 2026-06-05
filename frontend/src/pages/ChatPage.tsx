import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesApi } from '../services/matchesApi';
import type { Match, Message } from '../services/matchesApi';
import { ChatMessage } from '../components/ChatMessage';
import { useAuth } from '../context/AuthContext';

export const ChatPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [match, setMatch] = useState<Match | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageText, setMessageText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (id) {
      fetchMatchAndMessages(id);
      // Set up polling to check for new messages every 3 seconds
      const pollInterval = setInterval(() => {
        fetchMessages(id);
      }, 3000);
      return () => clearInterval(pollInterval);
    }
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMatchAndMessages = async (matchId: string) => {
    setIsLoading(true);
    setError('');
    try {
      const matchData = await matchesApi.getMatchById(matchId);
      setMatch(matchData);
      await fetchMessages(matchId);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erro ao carregar chat';
      setError(errorMessage);
      console.error('Error fetching match and messages:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMessages = async (matchId: string) => {
    try {
      const data = await matchesApi.getMessages(matchId);
      setMessages(data);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText.trim() || !id) return;

    const text = messageText.trim();
    setMessageText('');
    setIsSending(true);

    try {
      await matchesApi.sendMessage(id, text);
      await fetchMessages(id);
      setIsSending(false);
      inputRef.current?.focus();
    } catch (err) {
      setError('Erro ao enviar mensagem');
      setMessageText(text); // Restore text if failed
      setIsSending(false);
      console.error('Error sending message:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  };

  const getOtherUserName = () => {
    if (currentUser?.tipo === 'motorista') {
      return match?.shipper?.nome || 'Shipper';
    } else {
      return match?.motorista?.nome || 'Motorista';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">FreteBR</h1>
            {match && (
              <p className="text-sm text-gray-600 mt-1">
                Chat com {getOtherUserName()} • {match.frete?.origem} →{' '}
                {match.frete?.destino}
              </p>
            )}
          </div>
          <button
            onClick={() => navigate(`/match/${id}`)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Ver Detalhes
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 mb-4">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-gray-600">Carregando chat...</div>
          </div>
        ) : (
          <>
            {/* Messages Container */}
            <div className="flex-1 bg-white rounded-lg shadow-md p-6 mb-4 overflow-y-auto">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-600">
                  <p>Nenhuma mensagem ainda. Comece a conversar!</p>
                </div>
              ) : (
                <>
                  {messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      message={message}
                      isOwn={message.sender_id === currentUser?.id}
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Message Input */}
            <form
              onSubmit={handleSendMessage}
              className="bg-white rounded-lg shadow-md p-4"
            >
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite sua mensagem..."
                  disabled={isSending || isLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:bg-gray-100 disabled:text-gray-600"
                />
                <button
                  type="submit"
                  disabled={isSending || !messageText.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-6 rounded-lg transition"
                >
                  {isSending ? 'Enviando...' : 'Enviar'}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {messageText.length} caracteres (Enter para enviar, Shift+Enter para quebra de linha)
              </p>
            </form>
          </>
        )}
      </main>
    </div>
  );
};
