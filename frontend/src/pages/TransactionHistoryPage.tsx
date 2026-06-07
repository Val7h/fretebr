import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Transaction {
  id: number;
  match_id: number;
  motorista_id: number;
  motorista_nome: string;
  motorista_email: string;
  shipper_id: number;
  shipper_nome: string;
  shipper_email: string;
  amount: number;
  status: string;
  mp_payment_id: string | null;
  created_at: string;
  updated_at: string;
}

interface TransactionData {
  transacoes: Transaction[];
  total: number;
  total_amount: number;
}

interface Statistics {
  total_transacoes: number;
  total_pago: number;
  total_pendente: number;
  total_falhou: number;
  transacoes_por_status: {
    pago: number;
    pendente: number;
    falhou: number;
    cancelado: number;
    expirado: number;
  };
}

export const TransactionHistoryPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const [transacoes, setTransacoes] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  const ITEMS_PER_PAGE = 10;

  useEffect(() => {
    loadTransactions();
    loadStatistics();
  }, [filterStatus, page]);

  const loadTransactions = async () => {
    try {
      setIsLoading(true);
      setErro(null);
      const data: TransactionData = await apiService.getTransactions(
        ITEMS_PER_PAGE,
        page * ITEMS_PER_PAGE,
        filterStatus || undefined
      );
      setTransacoes(data.transacoes);
    } catch (err: any) {
      setErro(err?.response?.data?.detail || 'Erro ao carregar transações');
    } finally {
      setIsLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const data = await apiService.getTransactionStatistics();
      setStats(data);
    } catch (err: any) {
      console.error('Erro ao carregar estatísticas:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pago':
        return { bg: '#e8f5e9', color: '#2e7d32' };
      case 'pendente':
        return { bg: '#fff3e0', color: '#e65100' };
      case 'falhou':
        return { bg: '#ffebee', color: '#c62828' };
      case 'cancelado':
        return { bg: '#f5f5f5', color: '#666' };
      case 'expirado':
        return { bg: '#f5f5f5', color: '#666' };
      default:
        return { bg: '#f5f5f5', color: '#666' };
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pago':
        return '✅ Pago';
      case 'pendente':
        return '⏳ Pendente';
      case 'falhou':
        return '❌ Falhou';
      case 'cancelado':
        return '🚫 Cancelado';
      case 'expirado':
        return '⏰ Expirado';
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

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

      <h1 style={{ color: '#333', fontSize: '2rem', marginBottom: '30px' }}>
        💳 Histórico de Transações
      </h1>

      {/* Estatísticas */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Total de Transações</p>
            <p style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
              {stats.total_transacoes}
            </p>
          </div>

          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Total Pago</p>
            <p style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold', color: '#2e7d32' }}>
              R$ {stats.total_pago.toFixed(2)}
            </p>
          </div>

          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Pendente</p>
            <p style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold', color: '#e65100' }}>
              R$ {stats.total_pendente.toFixed(2)}
            </p>
          </div>

          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <p style={{ margin: '0 0 8px 0', color: '#999', fontSize: '0.85rem' }}>Falhou</p>
            <p style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold', color: '#c62828' }}>
              R$ {stats.total_falhou.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <button
          onClick={() => {
            setFilterStatus(null);
            setPage(0);
          }}
          style={{
            padding: '10px 16px',
            background: !filterStatus ? '#667eea' : '#f0f0f0',
            color: !filterStatus ? 'white' : '#333',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem',
          }}
        >
          Todos
        </button>
        {['pago', 'pendente', 'falhou'].map((status) => (
          <button
            key={status}
            onClick={() => {
              setFilterStatus(status);
              setPage(0);
            }}
            style={{
              padding: '10px 16px',
              background: filterStatus === status ? '#667eea' : '#f0f0f0',
              color: filterStatus === status ? 'white' : '#333',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.9rem',
            }}
          >
            {getStatusLabel(status)}
          </button>
        ))}
      </div>

      {/* Transações */}
      {isLoading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
          Carregando transações...
        </div>
      ) : erro ? (
        <div style={{ color: 'red', padding: '20px', background: '#fff0f0', borderRadius: '8px' }}>
          {erro}
        </div>
      ) : transacoes.length === 0 ? (
        <div style={{ padding: '60px 40px', textAlign: 'center', background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
          <p style={{ color: '#999', fontSize: '1.1rem' }}>Nenhuma transação encontrada</p>
        </div>
      ) : (
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.08)', overflow: 'hidden' }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f5f5f5', borderBottom: '1px solid #e0e0e0' }}>
                  <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', color: '#333' }}>ID</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Outro Usuário</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Valor</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Status</th>
                  <th style={{ padding: '16px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Data</th>
                  <th style={{ padding: '16px', textAlign: 'center', fontWeight: '600', color: '#333' }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {transacoes.map((t) => {
                  const isMotorista = currentUser?.tipo === 'motorista';
                  const outroPessoa = isMotorista ? t.shipper_nome : t.motorista_nome;
                  const statusColors = getStatusColor(t.status);

                  return (
                    <tr key={t.id} style={{ borderBottom: '1px solid #e0e0e0', background: '#fff' }}>
                      <td style={{ padding: '16px', color: '#667eea', fontWeight: '600' }}>#{t.id}</td>
                      <td style={{ padding: '16px', color: '#333' }}>
                        {outroPessoa}
                      </td>
                      <td style={{ padding: '16px', fontWeight: '600', color: '#333', fontSize: '1.1rem' }}>
                        R$ {t.amount.toFixed(2)}
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span
                          style={{
                            padding: '6px 12px',
                            background: statusColors.bg,
                            color: statusColors.color,
                            borderRadius: '12px',
                            fontSize: '0.85rem',
                            fontWeight: '600',
                          }}
                        >
                          {getStatusLabel(t.status)}
                        </span>
                      </td>
                      <td style={{ padding: '16px', color: '#666', fontSize: '0.9rem' }}>
                        {formatDate(t.created_at)}
                      </td>
                      <td style={{ padding: '16px', textAlign: 'center' }}>
                        <button
                          onClick={() => navigate(`/match/${t.match_id}`)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#667eea',
                            cursor: 'pointer',
                            fontWeight: '600',
                            textDecoration: 'none',
                            fontSize: '0.9rem',
                          }}
                        >
                          Ver
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Paginação */}
          <div style={{ padding: '16px', display: 'flex', justifyContent: 'center', gap: '8px', borderTop: '1px solid #e0e0e0' }}>
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              style={{
                padding: '8px 16px',
                background: page === 0 ? '#f0f0f0' : '#667eea',
                color: page === 0 ? '#999' : 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: page === 0 ? 'not-allowed' : 'pointer',
                fontWeight: '600',
              }}
            >
              ← Anterior
            </button>

            <span style={{ padding: '8px 16px', color: '#666', fontWeight: '600' }}>
              Página {page + 1}
            </span>

            <button
              onClick={() => setPage(page + 1)}
              disabled={transacoes.length < ITEMS_PER_PAGE}
              style={{
                padding: '8px 16px',
                background: transacoes.length < ITEMS_PER_PAGE ? '#f0f0f0' : '#667eea',
                color: transacoes.length < ITEMS_PER_PAGE ? '#999' : 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: transacoes.length < ITEMS_PER_PAGE ? 'not-allowed' : 'pointer',
                fontWeight: '600',
              }}
            >
              Próxima →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
