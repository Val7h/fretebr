import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { PostFretePage } from './pages/PostFretePage';
import { FindFretePage } from './pages/FindFretePage';
import { MyFretesPage } from './pages/MyFretesPage';
import { MyProposalsPage } from './pages/MyProposalsPage';
import { MyMatchesPage } from './pages/MyMatchesPage';
import { FreteDetailPage } from './pages/FreteDetailPage';
import { MatchDetailPage } from './pages/MatchDetailPage';
import { ChatPage } from './pages/ChatPage';
import { PaymentPage } from './pages/PaymentPage';
import { ReceiptPage } from './pages/ReceiptPage';
import { RatingPage } from './pages/RatingPage';
import { TransactionHistoryPage } from './pages/TransactionHistoryPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { NotificationCenter } from './components/NotificationCenter';
import { useAuth } from './context/AuthContext';

function HomePage() {
  const navigate = useNavigate();
  const { currentUser, isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) return null;

  // ============= USUARIO LOGADO: dashboard simplificado =============
  if (isAuthenticated && currentUser) {
    const tipo = currentUser.tipo;
    const handleLogout = async () => {
      await logout();
      navigate('/login');
    };
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 'clamp(16px, 4vw, 32px)',
        color: 'white',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            flexWrap: 'wrap', gap: 12, marginBottom: 32,
          }}>
            <div>
              <h1 style={{ margin: 0, fontSize: 'clamp(1.4rem, 4vw, 2rem)' }}>
                🚚 FreteBR
              </h1>
              <p style={{ margin: '4px 0 0', opacity: 0.85, fontSize: '0.9rem' }}>
                Olá, {currentUser.nome.split(' ')[0]} ({tipo === 'motorista' ? 'Motorista' : 'Cliente'})
              </p>
            </div>
            <button
              onClick={handleLogout}
              style={{
                padding: '10px 18px',
                background: 'rgba(255,255,255,0.18)',
                border: '1px solid rgba(255,255,255,0.4)',
                color: 'white', borderRadius: 8, cursor: 'pointer',
                fontWeight: 600, fontSize: '0.9rem',
              }}
            >
              Sair
            </button>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 250px), 1fr))',
            gap: 16,
          }}>
            {tipo === 'motorista' && (
              <>
                <DashCard onClick={() => navigate('/procurar-fretes')}
                  icon="🔍" title="Procurar Fretes"
                  desc="Veja fretes disponíveis perto de você" />
                <DashCard onClick={() => navigate('/minhas-propostas')}
                  icon="📋" title="Minhas Propostas"
                  desc="Acompanhe propostas enviadas" />
                <DashCard onClick={() => navigate('/meus-matches')}
                  icon="🤝" title="Meus Fretes Aceitos"
                  desc="Fretes em andamento" />
                <DashCard onClick={() => navigate('/transacoes')}
                  icon="💰" title="Histórico"
                  desc="Pagamentos e ganhos" />
              </>
            )}
            {tipo === 'shipper' && (
              <>
                <DashCard onClick={() => navigate('/postar-frete')}
                  icon="📝" title="Postar Frete"
                  desc="Crie uma solicitação de transporte" />
                <DashCard onClick={() => navigate('/meus-fretes')}
                  icon="📦" title="Meus Fretes"
                  desc="Fretes que você postou" />
                <DashCard onClick={() => navigate('/meus-matches')}
                  icon="🤝" title="Em Andamento"
                  desc="Fretes com motorista aceito" />
                <DashCard onClick={() => navigate('/transacoes')}
                  icon="💰" title="Histórico"
                  desc="Pagamentos e recibos" />
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ============= LANDING (visitante nao logado) =============
  return (
    <div style={{ minHeight: '100vh', background: '#fff' }}>
      {/* Hero */}
      <section style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: 'clamp(40px, 8vw, 80px) clamp(20px, 5vw, 40px) clamp(60px, 10vw, 100px)',
        textAlign: 'center',
      }}>
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <div style={{ fontSize: 'clamp(2rem, 6vw, 3rem)', marginBottom: 8 }}>🚚</div>
          <h1 style={{
            fontSize: 'clamp(1.8rem, 6vw, 3rem)',
            margin: '0 0 16px', fontWeight: 800, letterSpacing: '-0.02em',
          }}>
            FreteBR
          </h1>
          <p style={{
            fontSize: 'clamp(1rem, 3vw, 1.3rem)',
            margin: '0 0 32px', opacity: 0.95, lineHeight: 1.5,
          }}>
            O jeito mais simples de <strong>contratar frete</strong> ou <strong>encontrar carga</strong> no Brasil.
          </p>

          <div style={{
            display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap',
            marginBottom: 24,
          }}>
            <button onClick={() => navigate('/login?mode=signup')} style={ctaPrimary}>
              Criar conta grátis
            </button>
            <button onClick={() => navigate('/login')} style={ctaSecondary}>
              Já tenho conta
            </button>
          </div>

          <p style={{ fontSize: 13, opacity: 0.8, margin: 0 }}>
            ✓ Sem cobranças no beta · ✓ Cadastro em 30 segundos
          </p>
        </div>
      </section>

      {/* Como funciona */}
      <section style={{
        padding: 'clamp(40px, 8vw, 80px) clamp(20px, 5vw, 40px)',
        maxWidth: 1100, margin: '0 auto',
      }}>
        <h2 style={{
          textAlign: 'center', fontSize: 'clamp(1.4rem, 4vw, 2rem)',
          margin: '0 0 8px', color: '#1a1a1a',
        }}>
          Como funciona
        </h2>
        <p style={{
          textAlign: 'center', color: '#666', fontSize: '1rem',
          margin: '0 0 40px',
        }}>
          Pra você que precisa enviar carga <strong>ou</strong> dirigir e ganhar com frete.
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 280px), 1fr))',
          gap: 24,
        }}>
          <FeatureCard
            icon="📦" badge="Para clientes"
            title="Poste seu frete em 1 minuto"
            steps={[
              'Escolha origem e destino',
              'Receba propostas de motoristas',
              'Aceite a melhor e pague via Pix',
            ]}
          />
          <FeatureCard
            icon="🚛" badge="Para motoristas"
            title="Ganhe dinheiro na estrada"
            steps={[
              'Veja fretes disponíveis na sua rota',
              'Faça sua proposta e converse no chat',
              'Receba o pagamento ao concluir',
            ]}
          />
        </div>
      </section>

      {/* Beneficios */}
      <section style={{
        background: '#f8f9fc',
        padding: 'clamp(40px, 8vw, 80px) clamp(20px, 5vw, 40px)',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <h2 style={{
            textAlign: 'center', fontSize: 'clamp(1.4rem, 4vw, 2rem)',
            margin: '0 0 40px', color: '#1a1a1a',
          }}>
            Por que usar FreteBR
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 200px), 1fr))',
            gap: 20,
          }}>
            <Benefit icon="🛡️" title="Pagamento seguro"
              desc="Pix com confirmação automática. Você só paga quando aceita a proposta." />
            <Benefit icon="💬" title="Chat integrado"
              desc="Combine detalhes direto com o motorista sem precisar trocar WhatsApp." />
            <Benefit icon="⭐" title="Avaliação dupla"
              desc="Cliente e motorista se avaliam — a comunidade fica confiável." />
            <Benefit icon="🇧🇷" title="100% brasileiro"
              desc="Feito por quem entende de frete no Brasil, com suporte em português." />
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section style={{
        textAlign: 'center',
        padding: 'clamp(40px, 8vw, 80px) clamp(20px, 5vw, 40px)',
      }}>
        <h2 style={{ fontSize: 'clamp(1.4rem, 4vw, 1.8rem)', margin: '0 0 12px', color: '#1a1a1a' }}>
          Pronto pra começar?
        </h2>
        <p style={{ color: '#666', margin: '0 0 24px' }}>
          Estamos em beta privado. Sem cobranças nessa fase.
        </p>
        <button onClick={() => navigate('/login?mode=signup')} style={{ ...ctaPrimary, background: '#667eea', color: 'white' }}>
          Criar conta grátis
        </button>
      </section>

      <footer style={{
        textAlign: 'center', padding: '20px',
        color: '#999', fontSize: 13, borderTop: '1px solid #eee',
      }}>
        © 2026 FreteBR · Marketplace de fretes em beta
      </footer>
    </div>
  );
}

// ===== Componentes de apoio da HomePage =====
function DashCard({ icon, title, desc, onClick }: {
  icon: string; title: string; desc: string; onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '20px', textAlign: 'left',
        background: 'rgba(255,255,255,0.15)',
        border: '1px solid rgba(255,255,255,0.3)',
        color: 'white', borderRadius: 12, cursor: 'pointer',
        transition: 'all 0.2s',
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.background = 'rgba(255,255,255,0.28)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'rgba(255,255,255,0.15)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div style={{ fontSize: '1.8rem', marginBottom: 8 }}>{icon}</div>
      <div style={{ fontWeight: 700, fontSize: '1.05rem', marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 13, opacity: 0.85 }}>{desc}</div>
    </button>
  );
}

function FeatureCard({ icon, badge, title, steps }: {
  icon: string; badge: string; title: string; steps: string[];
}) {
  return (
    <div style={{
      background: 'white', padding: 28, borderRadius: 16,
      boxShadow: '0 4px 24px rgba(102,126,234,0.08)',
      border: '1px solid #eef0f6',
    }}>
      <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>{icon}</div>
      <span style={{
        display: 'inline-block', padding: '4px 10px',
        background: '#eef0fe', color: '#667eea',
        borderRadius: 999, fontSize: 12, fontWeight: 600, marginBottom: 12,
      }}>{badge}</span>
      <h3 style={{ fontSize: '1.25rem', margin: '0 0 16px', color: '#1a1a1a' }}>{title}</h3>
      <ol style={{ paddingLeft: 0, margin: 0, listStyle: 'none' }}>
        {steps.map((s, i) => (
          <li key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: 12,
            color: '#333', fontSize: '0.95rem', padding: '6px 0',
          }}>
            <span style={{
              flexShrink: 0, width: 24, height: 24,
              background: '#667eea', color: 'white',
              borderRadius: '50%', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700,
            }}>{i + 1}</span>
            <span>{s}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function Benefit({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div style={{ textAlign: 'center', padding: 16 }}>
      <div style={{ fontSize: '2.2rem', marginBottom: 12 }}>{icon}</div>
      <div style={{ fontWeight: 700, color: '#1a1a1a', marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 14, color: '#666', lineHeight: 1.5 }}>{desc}</div>
    </div>
  );
}

const ctaPrimary: React.CSSProperties = {
  padding: '14px 28px', fontSize: '1rem', fontWeight: 700,
  background: 'white', color: '#667eea',
  border: 'none', borderRadius: 999, cursor: 'pointer',
  boxShadow: '0 8px 20px rgba(0,0,0,0.15)',
};

const ctaSecondary: React.CSSProperties = {
  padding: '14px 28px', fontSize: '1rem', fontWeight: 600,
  background: 'transparent', color: 'white',
  border: '2px solid rgba(255,255,255,0.6)', borderRadius: 999, cursor: 'pointer',
};

function HeaderNav() {
  const location = useLocation();
  const navigate = useNavigate();

  // Esconder na home, login, forgot e reset
  const hiddenOn = ['/', '/login', '/forgot-password', '/reset-password'];
  if (hiddenOn.includes(location.pathname)) return null;

  return (
    <header style={{
      background: 'white',
      boxShadow: '0 2px 10px rgba(0,0,0,0.06)',
      padding: 'clamp(10px, 2vw, 15px) clamp(16px, 4vw, 30px)',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <h1 style={{
        margin: 0, cursor: 'pointer', color: '#667eea',
        fontSize: 'clamp(1.1rem, 3vw, 1.4rem)', fontWeight: 700,
      }} onClick={() => navigate('/')}>
        🚚 FreteBR
      </h1>
      <button
        onClick={() => navigate('/')}
        style={{
          padding: 'clamp(8px, 1.5vw, 10px) clamp(14px, 2.5vw, 20px)',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer',
          fontWeight: 600,
          fontSize: '0.9rem',
        }}
      >
        🏠 Início
      </button>
    </header>
  );
}

function App() {
  return (
    <Router>
      <NotificationCenter />
      <HeaderNav />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/postar-frete" element={<ProtectedRoute><PostFretePage /></ProtectedRoute>} />
        <Route path="/procurar-fretes" element={<ProtectedRoute><FindFretePage /></ProtectedRoute>} />
        <Route path="/meus-fretes" element={<ProtectedRoute><MyFretesPage /></ProtectedRoute>} />
        <Route path="/minhas-propostas" element={<ProtectedRoute><MyProposalsPage /></ProtectedRoute>} />
        <Route path="/meus-matches" element={<ProtectedRoute><MyMatchesPage /></ProtectedRoute>} />
        <Route path="/frete/:id" element={<ProtectedRoute><FreteDetailPage /></ProtectedRoute>} />
        <Route path="/match/:id" element={<ProtectedRoute><MatchDetailPage /></ProtectedRoute>} />
        <Route path="/match/:id/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
        <Route path="/match/:id/payment" element={<ProtectedRoute><PaymentPage /></ProtectedRoute>} />
        <Route path="/match/:id/receipt" element={<ProtectedRoute><ReceiptPage /></ProtectedRoute>} />
        <Route path="/match/:id/rating" element={<ProtectedRoute><RatingPage /></ProtectedRoute>} />
        <Route path="/transacoes" element={<ProtectedRoute><TransactionHistoryPage /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;
