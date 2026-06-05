import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { DashboardPage } from './pages/DashboardPage';
import { PostFretePage } from './pages/PostFretePage';
import { FindFretePage } from './pages/FindFretePage';
import { MyFretesPage } from './pages/MyFretesPage';
import { FreteDetailPage } from './pages/FreteDetailPage';
import { MyMatchesPage } from './pages/MyMatchesPage';
import { MatchDetailPage } from './pages/MatchDetailPage';
import { ChatPage } from './pages/ChatPage';
import { PaymentPage } from './pages/PaymentPage';
import { ReceiptPage } from './pages/ReceiptPage';
import { RatingPage } from './pages/RatingPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/postar-frete"
            element={
              <ProtectedRoute>
                <PostFretePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/procurar-fretes"
            element={
              <ProtectedRoute>
                <FindFretePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/meus-fretes"
            element={
              <ProtectedRoute>
                <MyFretesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/frete/:id"
            element={
              <ProtectedRoute>
                <FreteDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/meus-matches"
            element={
              <ProtectedRoute>
                <MyMatchesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match/:id"
            element={
              <ProtectedRoute>
                <MatchDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match/:id/chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match/:id/payment"
            element={
              <ProtectedRoute>
                <PaymentPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match/:id/receipt"
            element={
              <ProtectedRoute>
                <ReceiptPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/match/:id/rating"
            element={
              <ProtectedRoute>
                <RatingPage />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
