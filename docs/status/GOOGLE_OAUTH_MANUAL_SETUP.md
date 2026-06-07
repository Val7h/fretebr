# 🔐 Google OAuth - Setup Manual (Passo-a-Passo Visual)

**Status:** Projeto FreteBR criado ✅  
**Próximo:** Habilitar APIs + Criar OAuth Credentials  
**Tempo:** ~10 minutos

---

## 📋 INFORMAÇÕES DO PROJETO

```
Project Name: FreteBR
Project ID: fretebr-498600
Project Number: 335984369739
```

---

## 🚀 PASSO 1: Abrir Google Cloud Console

1. **Abrir em nova aba:**
   ```
   https://console.cloud.google.com/?project=fretebr-498600
   ```

2. **Verificar se está no projeto FreteBR** (canto superior esquerdo deve mostrar "FreteBR")

---

## 🔌 PASSO 2: Habilitar APIs

### 2.1 Ir para APIs & Services
```
Left sidebar > APIs & Services > Enabled APIs and Services
```

Ou acesso direto:
```
https://console.cloud.google.com/apis/dashboard?project=fretebr-498600
```

### 2.2 Habilitar Google Sign-In API
```
Click "Enable APIs and Services" (botão azul no topo)
├─ Search: "Google Sign-In"
├─ Click resultado: "Google+ API"
└─ Click "ENABLE"
```

### 2.3 Habilitar Google Identity Services
```
Repetir para "Google Identity Services"
├─ Search: "Google Identity"
├─ Click: "Google Identity Services API"
└─ Click "ENABLE"
```

✅ Ambas as APIs devem estar "Enabled" (verde).

---

## 🔑 PASSO 3: Criar OAuth Consent Screen

### 3.1 Ir para Consent Screen
```
Left sidebar > APIs & Services > OAuth consent screen

Ou direto:
https://console.cloud.google.com/apis/consent?project=fretebr-498600
```

### 3.2 Preencher Consent Screen (External)
```
User Type: 🔘 External (não mude)
└─ Click "CREATE"

Formulário:
├─ App name: FreteBR
├─ User support email: seu-email@gmail.com
├─ Developer contact: seu-email@gmail.com
└─ Click "SAVE AND CONTINUE"

Scopes:
├─ Click "Add or remove scopes"
├─ Search e marque:
│  ✅ openid
│  ✅ email
│  ✅ profile
│  ✅ ../auth/userinfo.email
│  ✅ ../auth/userinfo.profile
└─ Click "UPDATE" e depois "SAVE AND CONTINUE"

Test Users (pode pular):
└─ Click "SAVE AND CONTINUE"

Summary:
└─ Click "BACK TO DASHBOARD"
```

---

## 🔐 PASSO 4: Criar OAuth 2.0 Credentials

### 4.1 Ir para Credentials
```
Left sidebar > APIs & Services > Credentials

Ou direto:
https://console.cloud.google.com/apis/credentials?project=fretebr-498600
```

### 4.2 Criar OAuth 2.0 Client ID
```
Click "CREATE CREDENTIALS" > "OAuth client ID"

Application Type: 🔘 Web application
└─ Click

Formulário:
├─ Name: FreteBR Web

├─ Authorized JavaScript origins:
│  (Adicionar cada uma, uma por uma)
│  ✅ http://localhost:3000
│  ✅ http://localhost:8000
│  ✅ http://127.0.0.1:3000
│  ✅ http://127.0.0.1:8000

├─ Authorized redirect URIs:
│  (Adicionar cada uma, uma por uma)
│  ✅ http://localhost:8000/api/auth/google/callback
│  ✅ http://127.0.0.1:8000/api/auth/google/callback
│  ✅ http://localhost:3000/login/callback
│  ✅ http://127.0.0.1:3000/login/callback

└─ Click "CREATE"
```

### 4.3 Copiar Credentials
```
Tela de sucesso vai mostrar:

📋 CLIENT ID:
   COPIAR: xxxxxxxx.apps.googleusercontent.com

📋 CLIENT SECRET:
   COPIAR: xxxxxxxxxxxxxxxx

(Guardar em lugar seguro!)
```

---

## 💾 PASSO 5: Configurar .env Backend

### 5.1 Abrir arquivo .env
```
Arquivo: C:\Users\Admin\FreteBR\backend\.env
```

### 5.2 Adicionar valores
```bash
# Google OAuth
GOOGLE_CLIENT_ID=cole-aqui-o-client-id
GOOGLE_CLIENT_SECRET=cole-aqui-o-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

**Exemplo:**
```bash
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefg1234567890
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### 5.3 Salvar arquivo

---

## 🗄️ PASSO 6: Executar Migration SQL

### 6.1 Conectar no PostgreSQL
```bash
psql -U seu_usuario -d fretebr
```

Ou via pgAdmin (GUI)

### 6.2 Executar migration
```sql
-- Cole o conteúdo de:
-- C:\Users\Admin\FreteBR\backend\migrations\add_google_oauth.sql

-- Resumido:
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN foto VARCHAR(500);
CREATE INDEX idx_users_google_id ON users(google_id);
ALTER TABLE users ADD CONSTRAINT check_auth_method 
  CHECK (password_hash IS NOT NULL OR google_id IS NOT NULL);
```

### 6.3 Verificar
```sql
\d users
-- Deve mostrar colunas: google_id e foto
```

---

## 🚀 PASSO 7: Testar Backend

### 7.1 Instalar dependências
```bash
cd C:\Users\Admin\FreteBR\backend
pip install -r requirements.txt
```

### 7.2 Iniciar servidor
```bash
uvicorn app.main:app --reload
```

Deve aparecer:
```
✅ Uvicorn running on http://127.0.0.1:8000
```

### 7.3 Testar endpoint
```bash
curl http://localhost:8000/api/auth/google/login-url
```

Response esperada:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "client_id": "123456789.apps.googleusercontent.com"
}
```

✅ Se retornar JSON com `auth_url` → Google OAuth está funcionando!

---

## ✅ CHECKLIST FINAL

- [ ] Projeto FreteBR criado
- [ ] Google+ API habilitada
- [ ] Google Identity Services habilitada
- [ ] OAuth Consent Screen criado
- [ ] OAuth 2.0 Credentials criados
- [ ] Client ID copiado
- [ ] Client Secret copiado
- [ ] .env atualizado
- [ ] Migration SQL executada
- [ ] Backend iniciado
- [ ] Endpoint `/api/auth/google/login-url` testado

---

## 🆘 Problemas Comuns

### Erro: "Google OAuth não está configurado"
```
✅ Solução: Verificar se GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET 
           estão corretos no .env
```

### Erro: "Redirect URI mismatch"
```
✅ Solução: Verificar se a Redirect URI no Google Cloud Console 
           é exatamente igual ao GOOGLE_REDIRECT_URI no .env
```

### Erro: "JavaScript error in Google Cloud Console"
```
✅ Solução: Desabilitar extensões do navegador temporariamente
           Ou usar navegador privado
```

---

## 📱 Próximo: Frontend Integration

Depois que backend estiver funcionando:

1. Instalar @react-oauth/google
2. Adicionar GoogleOAuthProvider no App.tsx
3. Criar componente GoogleLoginButton
4. Testar fluxo completo

---

**Tempo estimado:** 10-15 minutos  
**Dificuldade:** ⭐ Fácil (apenas clicar e copiar)

Qualquer dúvida, é só avisar! 🚀
