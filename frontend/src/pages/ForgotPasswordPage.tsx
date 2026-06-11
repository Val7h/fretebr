import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);
  const [debugLink, setDebugLink] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro(null);
    try {
      setLoading(true);
      const resp: any = await (apiService as any).post('/auth/forgot-password', { email });
      setEnviado(true);
      // Em staging sem SMTP, backend retorna debug_reset_link para testes
      if (resp?.data?.debug_reset_link) setDebugLink(resp.data.debug_reset_link);
    } catch (e: any) {
      setErro(e?.response?.data?.detail || 'Erro ao processar pedido.');
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
        <h1 style={{ marginTop: 0, color: '#333' }}>🔑 Esqueci minha senha</h1>

        {enviado ? (
          <div>
            <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: 16, borderRadius: 8, marginBottom: 16 }}>
              ✅ Se o email existir, enviaremos instruções para redefinir sua senha.
            </div>
            {debugLink && (
              <div style={{ background: '#fff3e0', color: '#e65100', padding: 12, borderRadius: 6, fontSize: 12, marginBottom: 16, wordBreak: 'break-all' }}>
                <strong>[STAGING]</strong> SMTP não configurado. Link de reset:
                <br /><a href={debugLink} style={{ color: '#e65100' }}>{debugLink}</a>
              </div>
            )}
            <button
              onClick={() => navigate('/login')}
              style={{
                width: '100%', padding: 12, background: '#667eea', color: 'white',
                border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer',
              }}
            >
              Voltar ao login
            </button>
          </div>
        ) : (
          <form onSubmit={submit}>
            <p style={{ color: '#666', fontSize: 14, marginTop: 0 }}>
              Digite seu email cadastrado. Enviaremos um link para você criar uma nova senha.
            </p>

            {erro && (
              <div style={{ background: '#fff0f0', color: '#c62828', padding: 12, borderRadius: 6, marginBottom: 16, fontSize: 14 }}>
                {erro}
              </div>
            )}

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              style={{
                width: '100%', padding: 10, border: '1px solid #ddd', borderRadius: 6,
                fontSize: 14, boxSizing: 'border-box',
              }}
              required
            />

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: 16, width: '100%', padding: 12,
                background: '#667eea', color: 'white', border: 'none',
                borderRadius: 6, fontWeight: 600, cursor: 'pointer',
                opacity: loading ? 0.6 : 1,
              }}
            >
              {loading ? 'Enviando...' : 'Enviar link de reset'}
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
