import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Message {
  id: number;
  match_id: number;
  sender_id: number;
  conteudo: string;
  created_at: string;
  sender: {
    id: number;
    nome: string;
    email: string;
  };
}

interface ChatMessage {
  mensagens: Message[];
  total: number;
}

export const ChatPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [mensagens, setMensagens] = useState<Message[]>([]);
  const [novaMsg, setNovaMsg] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [lastLoadTime, setLastLoadTime] = useState(Date.now());

  // Scroll para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [mensagens]);

  // Carregar mensagens
  const loadMessages = async () => {
    try {
      if (!id) return;
      const data: ChatMessage = await apiService.getMatchMessages(parseInt(id));
      setMensagens(data.mensagens);
      setErro(null);
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao carregar mensagens');
    } finally {
      setIsLoading(false);
    }
  };

  // Carregar mensagens ao montar e fazer polling
  useEffect(() => {
    loadMessages();

    // Polling a cada 2 segundos
    const interval = setInterval(() => {
      loadMessages();
    }, 2000);

    return () => clearInterval(interval);
  }, [id]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!novaMsg.trim()) return;

    try {
      setEnviando(true);
      setErro(null);

      if (!id) return;

      await apiService.sendMessage(parseInt(id), novaMsg.trim());
      setNovaMsg('');
      setLastLoadTime(Date.now());

      // Recarregar mensagens imediatamente
      await loadMessages();
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao enviar mensagem');
    } finally {
      setEnviando(false);
    }
  };

  const handleDeleteMessage = async (messageId: number) => {
    if (!confirm('Tem certeza que deseja deletar esta mensagem?')) return;

    try {
      await apiService.deleteMessage(messageId);
      setMensagens(mensagens.filter(m => m.id !== messageId));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erro ao deletar mensagem');
    }
  };

  if (isLoading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Inter, system-ui, sans-serif' }}>
        <p>Carregando chat...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #f0f0f0' }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            marginBottom: '12px',
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
        <h1 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '1.8rem' }}>
          💬 Chat
        </h1>
        <p style={{ margin: '0', color: '#666', fontSize: '0.9rem' }}>
          Conversa com a outra parte sobre o frete
        </p>
      </div>

      {/* Mensagens */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 0',
          marginBottom: '20px',
          borderRadius: '8px',
          background: '#f9f9f9',
          paddingLeft: '20px',
          paddingRight: '20px',
        }}
      >
        {erro && (
          <div style={{ color: 'red', padding: '12px', background: '#fff0f0', borderRadius: '6px', marginBottom: '12px', fontSize: '0.9rem' }}>
            {erro}
          </div>
        )}

        {mensagens.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#999', padding: '40px 0' }}>
            <p>Nenhuma mensagem ainda. Comece a conversa!</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {mensagens.map((msg) => {
              const isOwn = msg.sender_id === currentUser?.id;
              const dataFormatada = new Date(msg.created_at).toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
              });

              return (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    justifyContent: isOwn ? 'flex-end' : 'flex-start',
                    marginBottom: '8px',
                  }}
                >
                  <div
                    style={{
                      maxWidth: '70%',
                      background: isOwn ? '#667eea' : 'white',
                      color: isOwn ? 'white' : '#333',
                      padding: '12px 16px',
                      borderRadius: '12px',
                      boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
                      position: 'relative',
                      wordWrap: 'break-word',
                    }}
                  >
                    {!isOwn && (
                      <p style={{ margin: '0 0 6px 0', fontSize: '0.75rem', opacity: 0.7, fontWeight: '600' }}>
                        {msg.sender.nome}
                      </p>
                    )}
                    <p style={{ margin: '0 0 4px 0', fontSize: '0.95rem', lineHeight: '1.4' }}>
                      {msg.conteudo}
                    </p>
                    <p style={{ margin: '0', fontSize: '0.75rem', opacity: 0.6 }}>
                      {dataFormatada}
                    </p>

                    {isOwn && (
                      <button
                        onClick={() => handleDeleteMessage(msg.id)}
                        style={{
                          position: 'absolute',
                          top: '-8px',
                          right: '-8px',
                          background: '#ff4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '50%',
                          width: '24px',
                          height: '24px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold',
                          padding: 0,
                        }}
                        title="Deletar mensagem"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSendMessage}
        style={{
          display: 'flex',
          gap: '10px',
          borderTop: '1px solid #f0f0f0',
          paddingTop: '20px',
        }}
      >
        <input
          type="text"
          value={novaMsg}
          onChange={(e) => setNovaMsg(e.target.value)}
          placeholder="Escreva sua mensagem..."
          maxLength={2000}
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '0.95rem',
            fontFamily: 'inherit',
            boxSizing: 'border-box',
          }}
          disabled={enviando}
        />
        <button
          type="submit"
          disabled={enviando || !novaMsg.trim()}
          style={{
            padding: '12px 24px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: enviando || !novaMsg.trim() ? 'not-allowed' : 'pointer',
            fontSize: '0.95rem',
            opacity: enviando || !novaMsg.trim() ? 0.6 : 1,
          }}
        >
          {enviando ? 'Enviando...' : '📤 Enviar'}
        </button>
      </form>

      <p style={{ margin: '12px 0 0 0', color: '#999', fontSize: '0.8rem', textAlign: 'center' }}>
        {novaMsg.length}/2000 caracteres
      </p>
    </div>
  );
};
