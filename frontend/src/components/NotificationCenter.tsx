import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface Notification {
  id: number;
  tipo: string;
  titulo: string;
  conteudo: string;
  is_read: boolean;
  match_id: number | null;
  frete_id: number | null;
  user_from_id: number | null;
  created_at: string;
  read_at: string | null;
}

interface NotificationData {
  notificacoes: Notification[];
  total: number;
  nao_lidas: number;
}

export const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notificacoes, setNotificacoes] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Carregar notificações ao abrir
  const loadNotifications = async () => {
    try {
      setIsLoading(true);
      const data: NotificationData = await apiService.getNotifications(20, 0, false);
      setNotificacoes(data.notificacoes);
      setUnreadCount(data.nao_lidas);
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Poll de notificações a cada 10 segundos
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await apiService.getUnreadCount();
        setUnreadCount(data.unread_count);
      } catch (error) {
        console.error('Erro ao verificar notificações:', error);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // Carregar quando abrir
  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen]);

  const handleMarkAsRead = async (notifId: number) => {
    try {
      await apiService.markAsRead(notifId);
      setNotificacoes(notificacoes.map(n =>
        n.id === notifId ? { ...n, is_read: true } : n
      ));
      setUnreadCount(Math.max(0, unreadCount - 1));
    } catch (error) {
      console.error('Erro ao marcar como lido:', error);
    }
  };

  const handleDelete = async (notifId: number) => {
    try {
      await apiService.deleteNotification(notifId);
      const notif = notificacoes.find(n => n.id === notifId);
      setNotificacoes(notificacoes.filter(n => n.id !== notifId));
      if (notif && !notif.is_read) {
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
    } catch (error) {
      console.error('Erro ao deletar notificação:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await apiService.markAllAsRead();
      setNotificacoes(notificacoes.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Erro ao marcar todas como lidas:', error);
    }
  };

  const getNotificationIcon = (tipo: string) => {
    switch (tipo) {
      case 'proposta':
        return '💼';
      case 'aceito':
        return '✅';
      case 'rejeitado':
        return '❌';
      case 'mensagem':
        return '💬';
      case 'avaliacao':
        return '⭐';
      default:
        return 'ℹ️';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Agora';
    if (minutes < 60) return `${minutes}m atrás`;
    if (hours < 24) return `${hours}h atrás`;
    if (days < 7) return `${days}d atrás`;

    return date.toLocaleDateString('pt-BR');
  };

  return (
    <div style={{ position: 'relative' }}>
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '50%',
          width: '50px',
          height: '50px',
          fontSize: '1.5rem',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 12px rgba(102, 126, 234, 0.4)',
          zIndex: 1000,
        }}
        title="Notificações"
      >
        🔔
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-5px',
              right: '-5px',
              background: '#ff4444',
              color: 'white',
              borderRadius: '50%',
              width: '24px',
              height: '24px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.8rem',
              fontWeight: 'bold',
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: '80px',
            right: '20px',
            background: 'white',
            borderRadius: '12px',
            width: '380px',
            maxHeight: '600px',
            boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
            zIndex: 1001,
            display: 'flex',
            flexDirection: 'column',
            fontFamily: 'Inter, system-ui, sans-serif',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '16px',
              borderBottom: '1px solid #f0f0f0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h3 style={{ margin: 0, color: '#333', fontSize: '1rem', fontWeight: '600' }}>
              Notificações
            </h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#667eea',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: '600',
                  padding: 0,
                }}
              >
                Marcar todas como lidas
              </button>
            )}
          </div>

          {/* Content */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              minHeight: '200px',
            }}
          >
            {isLoading ? (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: '#999' }}>
                Carregando...
              </div>
            ) : notificacoes.length === 0 ? (
              <div style={{ padding: '40px 20px', textAlign: 'center', color: '#999' }}>
                Nenhuma notificação
              </div>
            ) : (
              <div>
                {notificacoes.map((notif) => (
                  <div
                    key={notif.id}
                    style={{
                      padding: '12px 16px',
                      borderBottom: '1px solid #f0f0f0',
                      background: notif.is_read ? '#fff' : '#f9f9f9',
                      cursor: 'pointer',
                      transition: 'background 0.2s',
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = notif.is_read ? '#f5f5f5' : '#f0f0f0';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = notif.is_read ? '#fff' : '#f9f9f9';
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1, paddingRight: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{ fontSize: '1.2rem' }}>
                            {getNotificationIcon(notif.tipo)}
                          </span>
                          <h4
                            style={{
                              margin: 0,
                              color: '#333',
                              fontSize: '0.9rem',
                              fontWeight: notif.is_read ? '500' : '600',
                            }}
                          >
                            {notif.titulo}
                          </h4>
                        </div>
                        <p
                          style={{
                            margin: '4px 0 0 0',
                            color: '#666',
                            fontSize: '0.85rem',
                            lineHeight: '1.4',
                          }}
                        >
                          {notif.conteudo}
                        </p>
                        <p
                          style={{
                            margin: '6px 0 0 0',
                            color: '#999',
                            fontSize: '0.75rem',
                          }}
                        >
                          {formatTime(notif.created_at)}
                        </p>
                      </div>

                      {/* Actions */}
                      <div style={{ display: 'flex', gap: '4px' }}>
                        {!notif.is_read && (
                          <button
                            onClick={() => handleMarkAsRead(notif.id)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: '#667eea',
                              cursor: 'pointer',
                              fontSize: '0.8rem',
                              padding: '4px 8px',
                            }}
                            title="Marcar como lido"
                          >
                            ✓
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(notif.id)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#999',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            padding: '0 4px',
                          }}
                          title="Deletar"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Close Button */}
          <div
            style={{
              padding: '12px 16px',
              borderTop: '1px solid #f0f0f0',
              textAlign: 'center',
            }}
          >
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: '#f0f0f0',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                color: '#333',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.9rem',
              }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {/* Overlay */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1000,
          }}
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};
