import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Loading com skeleton + spinner — vale a pena pra paginas com lista.
 */
export const Loading = ({ message = 'Carregando...' }: { message?: string }) => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexDirection: 'column', gap: 16, padding: 60,
    color: '#666',
  }}>
    <div style={{
      width: 40, height: 40,
      border: '3px solid #eee',
      borderTopColor: '#667eea',
      borderRadius: '50%',
      animation: 'fbr-spin 0.8s linear infinite',
    }} />
    <div style={{ fontSize: 14 }}>{message}</div>
    <style>{`@keyframes fbr-spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

/**
 * Empty state com ilustracao + CTA — converte 0 itens em "vamos comecar".
 */
export const EmptyState = ({
  icon = '📭',
  title,
  description,
  ctaLabel,
  ctaHref,
  onCta,
}: {
  icon?: string;
  title: string;
  description: string;
  ctaLabel?: string;
  ctaHref?: string;
  onCta?: () => void;
}) => {
  const navigate = useNavigate();
  const handleClick = () => {
    if (onCta) onCta();
    else if (ctaHref) navigate(ctaHref);
  };
  return (
    <div style={{
      textAlign: 'center', padding: 'clamp(40px, 8vw, 60px) 20px',
      background: 'white', borderRadius: 12,
      boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
    }}>
      <div style={{ fontSize: '4rem', marginBottom: 16, opacity: 0.85 }}>{icon}</div>
      <h3 style={{
        margin: '0 0 8px', color: '#1a1a1a',
        fontSize: 'clamp(1.1rem, 3vw, 1.4rem)',
      }}>
        {title}
      </h3>
      <p style={{
        color: '#666', margin: '0 auto 24px', maxWidth: 420,
        lineHeight: 1.5, fontSize: '0.95rem',
      }}>
        {description}
      </p>
      {ctaLabel && (
        <button onClick={handleClick} style={{
          padding: '12px 24px', background: '#667eea', color: 'white',
          border: 'none', borderRadius: 999, fontWeight: 600, cursor: 'pointer',
          fontSize: '0.95rem', boxShadow: '0 4px 12px rgba(102,126,234,0.3)',
        }}>
          {ctaLabel}
        </button>
      )}
    </div>
  );
};

/**
 * Erro padrao com botao de tentar novamente.
 */
export const ErrorState = ({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) => (
  <div style={{
    background: '#fff', border: '1px solid #fde4e4',
    borderRadius: 12, padding: 24, textAlign: 'center',
    boxShadow: '0 2px 8px rgba(198,40,40,0.06)',
  }}>
    <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>😕</div>
    <h3 style={{ margin: '0 0 8px', color: '#c62828' }}>Algo deu errado</h3>
    <p style={{ color: '#666', margin: '0 0 16px', fontSize: '0.95rem' }}>
      {message}
    </p>
    {onRetry && (
      <button onClick={onRetry} style={{
        padding: '10px 20px', background: '#c62828', color: 'white',
        border: 'none', borderRadius: 6, fontWeight: 600, cursor: 'pointer',
      }}>
        Tentar novamente
      </button>
    )}
  </div>
);

/**
 * Wrapper que centraliza titulo de pagina mobile-first.
 */
export const PageHeader = ({
  title, subtitle, action,
}: { title: string; subtitle?: string; action?: ReactNode }) => (
  <div style={{
    display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
    gap: 12, flexWrap: 'wrap', marginBottom: 24,
  }}>
    <div>
      <h1 style={{
        margin: 0, color: '#1a1a1a',
        fontSize: 'clamp(1.4rem, 4vw, 1.8rem)',
        fontWeight: 700,
      }}>
        {title}
      </h1>
      {subtitle && (
        <p style={{ margin: '4px 0 0', color: '#666', fontSize: '0.95rem' }}>
          {subtitle}
        </p>
      )}
    </div>
    {action}
  </div>
);

/**
 * Container padrao de pagina interna (mobile-first).
 */
export const PageContainer = ({ children }: { children: ReactNode }) => (
  <div style={{
    padding: 'clamp(16px, 4vw, 32px)',
    maxWidth: 1100, margin: '0 auto',
  }}>
    {children}
  </div>
);
