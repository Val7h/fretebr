import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { SignupPayload } from '../services/api';

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login, signup, isLoading } = useAuth();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nome, setNome] = useState('');
  const [tipo, setTipo] = useState<'motorista' | 'shipper'>('motorista');
  const [erro, setErro] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro(null);

    if (!email || !password) {
      setErro('Email e senha são obrigatórios');
      return;
    }

    try {
      await login(email, password);
      navigate('/');
    } catch (error: any) {
      setErro(error?.response?.data?.detail || 'Erro ao fazer login');
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro(null);

    if (!email || !password || !nome) {
      setErro('Todos os campos são obrigatórios');
      return;
    }

    try {
      const payload: SignupPayload = {
        email,
        password,
        nome,
        tipo,
      };
      await signup(payload);
      navigate('/');
    } catch (error: any) {
      setErro(error?.response?.data?.detail || 'Erro ao se cadastrar');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Inter, system-ui, sans-serif',
        padding: '20px',
      }}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          width: '100%',
          maxWidth: '400px',
          padding: '40px',
        }}
      >
        <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '30px', fontSize: '1.8rem' }}>
          🚚 FreteBR
        </h1>

        {/* Modo de autenticação */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
          <button
            onClick={() => {
              setMode('login');
              setErro(null);
            }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '6px',
              background: mode === 'login' ? '#667eea' : '#f0f0f0',
              color: mode === 'login' ? 'white' : '#333',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s',
            }}
          >
            Login
          </button>
          <button
            onClick={() => {
              setMode('signup');
              setErro(null);
            }}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '6px',
              background: mode === 'signup' ? '#667eea' : '#f0f0f0',
              color: mode === 'signup' ? 'white' : '#333',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s',
            }}
          >
            Cadastro
          </button>
        </div>

        {/* Erro */}
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

        {/* Login Form */}
        {mode === 'login' && (
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontWeight: '600',
                fontSize: '1rem',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1,
                transition: 'all 0.3s',
              }}
              onMouseOver={(e) => {
                if (!isLoading) e.currentTarget.style.background = '#5568d3';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = '#667eea';
              }}
            >
              {isLoading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
        )}

        {/* Signup Form */}
        {mode === 'signup' && (
          <form onSubmit={handleSignup}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Nome Completo
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Seu Nome"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Tipo de Usuário
              </label>
              <select
                value={tipo}
                onChange={(e) => setTipo(e.target.value as 'motorista' | 'shipper')}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                  cursor: 'pointer',
                }}
              >
                <option value="motorista">🚗 Motorista</option>
                <option value="shipper">📦 Shipper (Embarcador)</option>
              </select>
            </div>

            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#333' }}>
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  boxSizing: 'border-box',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontWeight: '600',
                fontSize: '1rem',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.6 : 1,
                transition: 'all 0.3s',
              }}
              onMouseOver={(e) => {
                if (!isLoading) e.currentTarget.style.background = '#5568d3';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = '#667eea';
              }}
            >
              {isLoading ? 'Cadastrando...' : 'Cadastrar'}
            </button>
          </form>
        )}

        <p style={{ textAlign: 'center', color: '#999', marginTop: '20px', fontSize: '0.9rem' }}>
          {mode === 'login' ? 'Não tem conta? Clique em Cadastro' : 'Já tem conta? Clique em Login'}
        </p>
      </div>
    </div>
  );
};
