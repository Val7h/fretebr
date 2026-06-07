import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { PostFretePage } from './pages/PostFretePage';
import { FindFretePage } from './pages/FindFretePage';
import { MyFretesPage } from './pages/MyFretesPage';
import { MyMatchesPage } from './pages/MyMatchesPage';
import { FreteDetailPage } from './pages/FreteDetailPage';
import { MatchDetailPage } from './pages/MatchDetailPage';
import { ChatPage } from './pages/ChatPage';
import { PaymentPage } from './pages/PaymentPage';
import { ReceiptPage } from './pages/ReceiptPage';
import { RatingPage } from './pages/RatingPage';

function HomePage() {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      color: 'white',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>🚚 FreteBR</h1>
      <p style={{ fontSize: '1.5rem', marginBottom: '40px', opacity: 0.9 }}>Dashboard</p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        maxWidth: '800px',
        width: '100%'
      }}>
        <button
          onClick={() => navigate('/procurar-fretes')}
          style={{
            padding: '20px',
            fontSize: '1.1rem',
            background: 'rgba(255,255,255,0.2)',
            border: '2px solid white',
            color: 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s',
            fontWeight: 'bold'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          🔍 Procurar Fretes
        </button>

        <button
          onClick={() => navigate('/postar-frete')}
          style={{
            padding: '20px',
            fontSize: '1.1rem',
            background: 'rgba(255,255,255,0.2)',
            border: '2px solid white',
            color: 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s',
            fontWeight: 'bold'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          📝 Postar Frete
        </button>

        <button
          onClick={() => navigate('/meus-fretes')}
          style={{
            padding: '20px',
            fontSize: '1.1rem',
            background: 'rgba(255,255,255,0.2)',
            border: '2px solid white',
            color: 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s',
            fontWeight: 'bold'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          📦 Meus Fretes
        </button>

        <button
          onClick={() => navigate('/meus-matches')}
          style={{
            padding: '20px',
            fontSize: '1.1rem',
            background: 'rgba(255,255,255,0.2)',
            border: '2px solid white',
            color: 'white',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s',
            fontWeight: 'bold'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.4)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          🤝 Meus Matches
        </button>
      </div>

      <p style={{ marginTop: '60px', opacity: 0.7, fontSize: '0.9rem' }}>
        ✅ Bem-vindo ao FreteBR - Marketplace de fretes inteligente
      </p>
    </div>
  );
}

function HeaderNav() {
  const location = useLocation();
  const navigate = useNavigate();

  if (location.pathname === '/') {
    return null;
  }

  return (
    <header style={{
      background: 'white',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      padding: '15px 30px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <h1 style={{ margin: 0, cursor: 'pointer', color: '#667eea' }} onClick={() => navigate('/')}>
        🚚 FreteBR
      </h1>
      <button
        onClick={() => navigate('/')}
        style={{
          padding: '10px 20px',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        ← Voltar
      </button>
    </header>
  );
}

function App() {
  return (
    <Router>
      <HeaderNav />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/postar-frete" element={<PostFretePage />} />
        <Route path="/procurar-fretes" element={<FindFretePage />} />
        <Route path="/meus-fretes" element={<MyFretesPage />} />
        <Route path="/meus-matches" element={<MyMatchesPage />} />
        <Route path="/frete/:id" element={<FreteDetailPage />} />
        <Route path="/match/:id" element={<MatchDetailPage />} />
        <Route path="/match/:id/chat" element={<ChatPage />} />
        <Route path="/match/:id/payment" element={<PaymentPage />} />
        <Route path="/match/:id/receipt" element={<ReceiptPage />} />
        <Route path="/match/:id/rating" element={<RatingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
