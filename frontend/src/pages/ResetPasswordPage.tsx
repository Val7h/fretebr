import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { apiService } from '../services/api';

export const ResetPasswordPage = () => {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') || '';

  const [senha, setSenha] = useState('');
  const [senha2, setSenha2] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState(false);

  useEffect(() => {
    if (!token) setErro('Token de reset ausente na URL.');
  }, [token]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro(null);
    if (senha.length < 8 || !/[A-Za-z]/.test(senha) || !/\d/.test(senha)) {
      setErro('Senha precisa ter ao menos 8 caracteres, 1 letra e 1 numero.');
      return;
    }
    if (senha !== senha2) {
      setErro('As senhas nao conferem.');
      return;
    }
    try {
      setLoading(true);
      await (apiService as any).post('/auth/reset-password', {
        token,
        new_password: senha,
      });
      setSucesso(true);
      setTimeout(() => navigate('/login'), 2500);
    } catch (e: any) {
      setErro(e?.response?.data?.detail || 'Erro ao redefinir senha.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea, #764ba2)', fontFamily: 'Inter, sans-serif',
    }}>
      <div style={{
        background: 'white', borderRadius: 12, padding: 32, width: 360,
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
      }}>
        <h1 style={{ marginTop: 0, color: '#333' }}>🔑 Redefinir senha</h1>

        {sucesso ? (
          <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: 16, borderRadius: 8 }}>
            ✅ Senha redefinida! Redirecionando para login...
          </div>
        ) : (
          <form onSubmit={submit}>
            {erro && (
              <div style={{
                background: '#fff0f0', color: '#c62828', padding: 12, borderRadius: 6,
                marginBottom: 16, fontSize: 14,
              }}>
                {erro}
              </div>
            )}

            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6, color: '#333' }}>
              Nova senha
            </label>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              placeholder="Min 8 chars, 1 letra e 1 numero"
              style={inputStyle}
              required
            />

            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6, marginTop: 16, color: '#333' }}>
              Confirme a senha
            </label>
            <input
              type="password"
              value={senha2}
              onChange={(e) => setSenha2(e.target.value)}
              placeholder="Repita a senha"
              style={inputStyle}
              required
            />

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: 20, width: '100%', padding: 12,
                background: '#667eea', color: 'white', border: 'none',
                borderRadius: 6, fontWeight: 600, cursor: 'pointer',
                opacity: loading ? 0.6 : 1,
              }}
            >
              {loading ? 'Salvando...' : 'Redefinir senha'}
            </button>

            <button
              type="button"
              onClick={() => navigate('/login')}
              style={{
                marginTop: 10, width: '100%', padding: 10,
                background: 'transparent', color: '#667eea',
                border: 'none', cursor: 'pointer', fontSize: 13,
              }}
            >
              Voltar ao login
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 6,
  fontSize: 14, boxSizing: 'border-box',
};
