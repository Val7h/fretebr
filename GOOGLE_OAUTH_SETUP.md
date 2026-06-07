# 🔐 Google OAuth 2.0 Setup - FreteBR

**Status:** ✅ Backend Implementado  
**Versão:** 1.0  
**Data:** 2026-06-05

---

## 📋 Pré-requisitos

- [ ] Google Cloud Project criado
- [ ] Google OAuth 2.0 credentials configuradas
- [ ] Client ID do Google
- [ ] Client Secret do Google
- [ ] Redirect URI configurada

---

## 🚀 PASSO 1: Criar Google Cloud Project

### 1.1 Acessar Google Cloud Console
1. Ir para https://console.cloud.google.com/
2. Criar novo projeto: `FreteBR` (ou seu nome)
3. Aguardar criação (leva ~30 segundos)

### 1.2 Habilitar Google+ API
1. Pesquisar "Google+ API"
2. Clicar em "Enable"
3. Aguardar ativação

---

## 🔑 PASSO 2: Criar OAuth 2.0 Credentials

### 2.1 Criar Consent Screen
1. Ir para: **APIs & Services > OAuth consent screen**
2. Escolher **External** (User Type)
3. Preencher formulário:
   - **App name**: FreteBR
   - **User support email**: seu-email@example.com
   - **Developer contact**: seu-email@example.com
4. Clicar **Save and Continue**
5. Em Scopes: adicionar
   - `openid`
   - `email`
   - `profile`
6. Clicar **Save and Continue**
7. Clicar **Save and Continue** (Test Users)
8. Clicar **Back to Dashboard**

### 2.2 Criar OAuth 2.0 Client ID
1. Ir para: **APIs & Services > Credentials**
2. Clicar **+ Create Credentials > OAuth client ID**
3. Selecionar: **Web application**
4. Preencher:
   - **Name**: FreteBR Web
   - **Authorized JavaScript origins**: (adicionar URIs)
     - `http://localhost:3000`
     - `http://localhost:8000`
     - `https://seudominio.com` (produção)
   - **Authorized redirect URIs**: (adicionar URIs)
     - `http://localhost:8000/api/auth/google/callback`
     - `http://localhost:3000/login/callback`
     - `https://seudominio.com/api/auth/google/callback` (produção)
5. Clicar **Create**

### 2.3 Copiar Credentials
Na tela de confirmação, copiar:
- **Client ID**: `ABC123.apps.googleusercontent.com`
- **Client Secret**: `DEF456GHI789`

⚠️ **IMPORTANTE:** Client Secret deve ser mantido secreto!

---

## 🔧 PASSO 3: Configurar Backend FreteBR

### 3.1 Instalar dependências
```bash
cd C:/Users/Admin/FreteBR/backend
pip install -r requirements.txt
```

Verifica se contém:
```
google-auth-oauthlib==1.2.0
google-auth==2.27.0
```

### 3.2 Adicionar variáveis ao `.env`
```bash
# Arquivo: backend/.env (ou seu arquivo de config)

# Google OAuth
GOOGLE_CLIENT_ID=ABC123.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=DEF456GHI789
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Outros (já existentes)
SECRET_KEY=seu-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3.3 Executar Migration SQL
```bash
# Conectar no PostgreSQL
psql -U seu_user -d fretebr

# Executar migration
\i migrations/add_google_oauth.sql

# Verificar
\d users
```

Você deve ver:
```
 google_id | character varying | not null unique
 foto      | character varying |
```

### 3.4 Reiniciar Backend
```bash
cd C:/Users/Admin/FreteBR/backend
uvicorn app.main:app --reload
```

Verificar logs:
```
✅ Application startup complete
```

---

## 🌐 PASSO 4: Testar Endpoints

### 4.1 Obter Google Login URL
```bash
curl -X GET http://localhost:8000/api/auth/google/login-url
```

Response:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "client_id": "ABC123.apps.googleusercontent.com"
}
```

### 4.2 Fazer Login (Fluxo Manual)
1. Copiar `auth_url` da resposta acima
2. Abrir no navegador
3. Autorizar
4. Será redirecionado: `http://localhost:8000/api/auth/google/callback?code=...`

### 4.3 Trocar Code por Token (Automático no Backend)
Backend processa automaticamente. Se sucesso, recebe:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 123
}
```

### 4.4 Usar Token
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response:
```json
{
  "id": 123,
  "email": "usuario@gmail.com",
  "nome": "João Silva",
  "foto": "https://lh3.googleusercontent.com/...",
  "google_id": "118765123456789",
  "tipo": "motorista",
  "telefone": null,
  "cpf": null,
  "created_at": "2026-06-05T12:34:56",
  "updated_at": "2026-06-05T12:34:56"
}
```

---

## 💻 PASSO 5: Integrar Frontend

### 5.1 Instalar Google Login Library
```bash
cd C:/Users/Admin/FreteBR/frontend
npm install @react-oauth/google
```

### 5.2 Envolver App em GoogleOAuthProvider
```typescript
// frontend/src/App.tsx

import { GoogleOAuthProvider } from '@react-oauth/google';

function App() {
  return (
    <GoogleOAuthProvider clientId="ABC123.apps.googleusercontent.com">
      {/* seu aplicativo */}
    </GoogleOAuthProvider>
  );
}
```

### 5.3 Criar Componente Login Google
```typescript
// frontend/src/components/GoogleLoginButton.tsx

import { useGoogleLogin } from '@react-oauth/google';

export function GoogleLoginButton() {
  const login = useGoogleLogin({
    onSuccess: async (codeResponse) => {
      try {
        // Enviar code para backend
        const response = await fetch('http://localhost:8000/api/auth/google/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: codeResponse.code,
            fuel_referral_code: localStorage.getItem('fuelCode') // opcional
          })
        });

        const data = await response.json();

        if (response.ok) {
          // Salvar token
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user_id', data.user_id);

          // Redirecionar
          window.location.href = '/dashboard';
        } else {
          console.error('Erro:', data.detail);
        }
      } catch (error) {
        console.error('Erro ao fazer login:', error);
      }
    },
    flow: 'auth-code',
  });

  return (
    <button onClick={() => login()} style={{ padding: '10px 20px' }}>
      🔐 Login com Google
    </button>
  );
}
```

### 5.4 Adicionar ao Login Page
```typescript
// frontend/src/pages/LoginPage.tsx

import { GoogleLoginButton } from '../components/GoogleLoginButton';

export function LoginPage() {
  return (
    <div>
      <h1>Login FreteBR</h1>

      {/* Email/Senha */}
      <form>
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Senha" />
        <button type="submit">Login</button>
      </form>

      <hr />
      <p>Ou faça login com:</p>

      {/* Google */}
      <GoogleLoginButton />
    </div>
  );
}
```

---

## 🔄 FLUXO COMPLETO

```
┌─────────────────────────────────────────────────────────┐
│                    GOOGLE OAUTH FLOW                    │
└─────────────────────────────────────────────────────────┘

1️⃣ USUÁRIO CLICA "Login com Google"
   └─ Frontend chama: useGoogleLogin()

2️⃣ GOOGLE ABRE TELA DE AUTORIZAÇÃO
   └─ Usuário autoriza FreteBR

3️⃣ GOOGLE REDIRECIONA COM CÓDIGO
   └─ Frontend recebe: authorization code
   └─ Envia para backend: POST /api/auth/google/token

4️⃣ BACKEND PROCESSA
   └─ Troca código por access_token (Google)
   └─ Obtém dados do usuário
   └─ Cria/atualiza usuário no banco
   └─ Gera JWT token FreteBR

5️⃣ BACKEND RETORNA TOKEN
   └─ Frontend recebe JWT
   └─ Salva em localStorage
   └─ Faz requisições com Authorization header

6️⃣ USUÁRIO LOGADO
   └─ Pode usar plataforma normalmente
```

---

## 📊 ENDPOINTS GOOGLE

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/auth/google/login-url` | GET | Obter URL de login do Google |
| `/api/auth/google/callback` | GET | Callback do Google (redirect) |
| `/api/auth/google/token` | POST | Trocar code por token (alternativa) |

---

## 🔐 Segurança

### ✅ O que é feito automaticamente:
- ✅ Validação de Client Secret
- ✅ Validação de authorization code
- ✅ Validação de Redirect URI
- ✅ JWT token com expiration
- ✅ User info salvo no banco (email, nome, google_id)
- ✅ Password é opcional (Google users não têm senha)

### ⚠️ Recomendações:
- 🔒 Manter `GOOGLE_CLIENT_SECRET` em `.env` (nunca em código)
- 🔒 Usar HTTPS em produção (obrigatório pelo Google)
- 🔒 Validar token JWT antes de cada requisição
- 🔒 Implementar rate limiting no endpoint `/api/auth/google/token`
- 🔒 Logar todas as tentativas de login

### 🚫 O que o Google valida:
- ✅ Client ID correto
- ✅ Client Secret correto
- ✅ Authorization code válido (expiração: 10 minutos)
- ✅ Redirect URI está na whitelist
- ✅ Scopes solicitados (openid, email, profile)

---

## 🐛 Troubleshooting

### Erro: "Google OAuth não está configurado"
```
❌ GOOGLE_CLIENT_ID ou GOOGLE_CLIENT_SECRET não estão definidos no .env
✅ Solução: Verificar arquivo .env e adicionar valores
```

### Erro: "Falha ao autenticar com Google"
```
❌ Authorization code inválido ou expirou
✅ Solução: Tentar login novamente (código expira em 10 min)
```

### Erro: "Email already registered"
```
❌ Usuário tentando se registrar com email que já existe
✅ Solução: Automaticamente vincula Google ID ao usuário existente
```

### Erro: "Redirect URI mismatch"
```
❌ Redirect URI no Google não corresponde ao do backend
✅ Solução: 
   1. Ir para Google Cloud Console
   2. Ir para Credentials
   3. Editar OAuth 2.0 Client ID
   4. Verificar "Authorized redirect URIs"
   5. Adicionar: http://localhost:8000/api/auth/google/callback
```

---

## 📱 Frontend Integration (Resume)

```typescript
// 1. Envolver app
<GoogleOAuthProvider clientId="...">
  <App />
</GoogleOAuthProvider>

// 2. Botão de login
<button onClick={() => login()}>
  Login com Google
</button>

// 3. Handler no callback
onSuccess: async (codeResponse) => {
  const res = await fetch('/api/auth/google/token', {
    method: 'POST',
    body: JSON.stringify({ code: codeResponse.code })
  });
  const token = await res.json();
  localStorage.setItem('token', token.access_token);
}

// 4. Usar token
fetch('/api/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

## ✨ Com Fuel Code (Bonus)

Se o usuário tem um código do posto:

```typescript
// Frontend: Salvar código antes de fazer login
localStorage.setItem('fuelCode', 'SHELL-SP-123-ABC');

// Backend: Automaticamente cria desconto
onSuccess: async (codeResponse) => {
  const res = await fetch('/api/auth/google/token', {
    method: 'POST',
    body: JSON.stringify({
      code: codeResponse.code,
      fuel_referral_code: localStorage.getItem('fuelCode')
    })
  });
  // ✅ Motorista já tem 3% desconto + frentista ganha R$ 10
}
```

---

## 🎯 Próximos Passos

1. [ ] Criar Google Cloud Project
2. [ ] Gerar Client ID + Secret
3. [ ] Configurar .env no backend
4. [ ] Executar migration SQL
5. [ ] Testar endpoint `/api/auth/google/login-url`
6. [ ] Integrar frontend com @react-oauth/google
7. [ ] Testar fluxo completo de login
8. [ ] Configurar HTTPS em produção
9. [ ] Deploy no Render/Vercel

---

**Sistema de Google OAuth ✅ Pronto para Integração! 🚀**
