# ✅ FreteBR Render Deployment - MANUAL (Último Passo!)

## 🚀 Status Atual
- ✅ Código FreteBR pronto em GitHub (Val7h/fretebr)
- ✅ Documentação completa
- ✅ Credenciais geradas
- ⏳ **FALTAM**: 3 recursos Render a criar manualmente

## 📋 Dados para Copiar e Colar

### Database PostgreSQL
```
Nome: fretebr-db
Database: fretebr
Usuário: fretebr_user
Região: Oregon (US West)
Versão: 18
```

### Backend Web Service
```
Nome: fretebr-backend
Repo GitHub: Val7h/fretebr
Branch: main

Build Command:
pip install -r backend/requirements.txt

Start Command:
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

Env Vars (adicione estas):
- DATABASE_URL = [COPIAR DA DATABASE DEPOIS]
- SECRET_KEY = vxK9pL2mQ4wR6tY8uI0oP3sD5fG7hJ9kL1mN3oP5q7r9s1t3u5v7w9x1y3z5a7b9
```

### Frontend Static Site
```
Nome: fretebr-frontend
Repo GitHub: Val7h/fretebr
Branch: main

Build Command:
cd frontend && npm install && npm run build

Publish Directory:
frontend/dist

Env Vars:
- VITE_API_URL = https://fretebr-backend.onrender.com/api
```

---

## 🎯 Passo a Passo MANUAL (10 minutos)

### PASSO 1: Criar Database (3 min)
1. Vá para https://dashboard.render.com
2. Clique **"+ New"** (roxo, canto superior direito)
3. Escolha **"PostgreSQL"**
4. **COPIE E COLE** exatamente:
   - Nome: `fretebr-db`
   - Database: `fretebr`
   - Usuário: `fretebr_user`
   - Deixe a senha como gerada (aleatória)
   - Região: `Oregon (US West)` (já está selecionada)
5. Clique **"Create Database"** (botão roxo)
6. ⏳ Aguarde 2-3 minutos enquanto cria
7. **IMPORTANTE**: Quando aparecer a tela com "Internal Database URL", **COPIE TODA A URL** (começa com `postgresql://...`)
8. Salve em local seguro ou deixe a aba aberta

### PASSO 2: Criar Backend (4 min)
1. De volta ao Dashboard (https://dashboard.render.com)
2. Clique **"+ New"** novamente
3. Escolha **"Web Service"**
4. Clique em **"GitHub"** e procure por `fretebr`
5. **COPIE E COLE** exatamente:
   - Name: `fretebr-backend`
   - Deixe "Environment" como `Python 3` (auto-detecta)
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Role para baixo até "Environment"
7. Clique **"Add Environment Variable"** e adicione:
   ```
   DATABASE_URL = [COLA AQUI A URL QUE COPIOU NO PASSO 1]
   ```
8. Clique **"Add"** novamente e adicione:
   ```
   SECRET_KEY = vxK9pL2mQ4wR6tY8uI0oP3sD5fG7hJ9kL1mN3oP5q7r9s1t3u5v7w9x1y3z5a7b9
   ```
9. Clique **"Create Web Service"**
10. ⏳ Aguarde build completar (2-3 min) - verá status "Building..."

### PASSO 3: Criar Frontend (3 min)
1. De volta ao Dashboard
2. Clique **"+ New"** novamente
3. Escolha **"Static Site"**
4. Conecte GitHub `fretebr` novamente
5. **COPIE E COLE** exatamente:
   - Name: `fretebr-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
6. Role para baixo até "Environment"
7. Clique **"Add Environment Variable"**:
   ```
   VITE_API_URL = https://fretebr-backend.onrender.com/api
   ```
8. Clique **"Create Static Site"**
9. ⏳ Aguarde build completar

---

## ⏳ Passo Final: Aguardar Tudo Ficar Verde

No Dashboard Render, você verá 3 serviços:
- `fretebr-db` → ✅ Deve ficar VERDE
- `fretebr-backend` → ✅ Deve ficar VERDE  
- `fretebr-frontend` → ✅ Deve ficar VERDE

Quando todos forem **VERDE com checkmark**, está pronto!

---

## 🧪 Testar Depois

Quando tudo estiver verde:

1. **Frontend:** https://fretebr-frontend.onrender.com
2. Clique **"Sign Up"**
3. Preencha:
   - Email: `teste@teste.com`
   - Senha: `123456`
   - Nome: `João`
   - Tipo: `Motorista`
4. Clique **"Cadastrar"**
5. Faça login com mesmo email/senha
6. Vê o **Dashboard** 🎉

---

## 📞 Se Ficar Preso

**Se um build falhar:** Clique no serviço e vá em "Logs" para ver o erro

**Se o Frontend não conectar:** Verifique se `VITE_API_URL` está correto (sem /api no final se o backend já tem)

**Timeout ao carregar:** Render pode levar até 5 min no primeiro build. Aguarde.

---

## ✅ Resultado Final

```
🌐 Frontend: https://fretebr-frontend.onrender.com
🔌 Backend:  https://fretebr-backend.onrender.com
💾 Database: PostgreSQL (automático)
🔒 SSL:      HTTPS (automático)
```

---

**FreteBR estará LIVE no mundo inteiro!** 🚀

Tempo total: ~10 minutos de manual + 15 minutos de builds automáticos = **25 minutos até estar ao vivo**
