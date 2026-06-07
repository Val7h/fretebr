# 🚀 FreteBR Deploy RENDER - 30 MINUTOS

**Data:** 05 de Julho, 2026  
**Status:** PRONTO PARA DEPLOY  
**Tempo esperado:** 30 minutos  

---

## 📋 CREDENCIAIS GERADAS

Copie essas e guarde:

```
SECRET_KEY=vxK9pL2mQ4wR6tY8uI0oP3sD5fG7hJ9kL1mN3oP5q7r9s1t3u5v7w9x1y3z5a7b9

DATABASE_URL=(Render gera automaticamente - verá depois)

MERCADO_PAGO_ACCESS_TOKEN=(deixar em branco por agora)
TWILIO_ACCOUNT_SID=(deixar em branco por agora)
TWILIO_AUTH_TOKEN=(deixar em branco por agora)
TWILIO_PHONE_NUMBER=(deixar em branco por agora)
```

---

## 🎯 PASSO A PASSO (Clone e execute)

### **PASSO 1: Login Render (2 min)**

URL: https://render.com

1. Clique **"Sign Up"** (canto superior direito)
2. Escolha **"Continue with GitHub"**
3. Autorize com GitHub (Val7h)
4. Pronto! Você está no Render Dashboard

---

### **PASSO 2: Criar Database PostgreSQL (5 min)**

1. **Clique:** "New +" (botão roxo no topo)
2. **Escolha:** "PostgreSQL"
3. **Preencha:**
   - **Name:** `fretebr-db`
   - **Database:** `fretebr`
   - **User:** `fretebr_user`
   - **Password:** (Render gera aleatória - deixe como está)
   - **Region:** "São Paulo" (ou "Ohio" se quiser mais rápido)
4. **Clique:** "Create Database" (botão roxo)
5. ⏳ **AGUARDE 2-3 minutos** enquanto cria
6. Quando aparecer a tela com detalhes, **COPIA a `DATABASE_URL`** completa (começa com `postgresql://...`)
   - **Salva em algum lugar** - você vai usar no PASSO 3

✅ **Database criada!**

---

### **PASSO 3: Deploy Backend (7 min)**

1. **Clique:** "New +" (botão roxo)
2. **Escolha:** "Web Service"
3. **Conecte GitHub:**
   - Clique em "GitHub" 
   - Procure por `fretebr`
   - Selecione
4. **Configure:**
   - **Name:** `fretebr-backend`
   - **Environment:** Python 3.11 (auto-detecta)
   - **Build Command:** 
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command:**
     ```
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```
   - **Instance Type:** Free (ou Starter se pagar)
5. **Clique:** "Create Web Service" (roxo)
6. ⏳ **Enquanto builda** (2-3 min), **ADICIONE ENVIRONMENT VARIABLES:**
   - Procure por seção "Environment" na página
   - Clique em "Add Environment Variable"
   - Adicione CADA UMA:
     ```
     Key: DATABASE_URL
     Value: (cola aqui a URL que copiou no Passo 2)
     ```
     ```
     Key: SECRET_KEY
     Value: vxK9pL2mQ4wR6tY8uI0oP3sD5fG7hJ9kL1mN3oP5q7r9s1t3u5v7w9x1y3z5a7b9
     ```
   - Os outros 4 (MERCADO_PAGO, TWILIO) **deixe em branco por agora**
7. **Clique:** "Deploy" quando pronto
8. Quando ficar **verde** no Dashboard = sucesso ✅

✅ **Backend deployado!**

---

### **PASSO 4: Deploy Frontend (7 min)**

1. **Clique:** "New +" (roxo)
2. **Escolha:** "Static Site"
3. **Conecte GitHub:**
   - Procure `fretebr` novamente
   - Selecione
4. **Configure:**
   - **Name:** `fretebr-frontend`
   - **Build Command:**
     ```
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory:** `frontend/dist`
5. **Clique:** "Create Static Site"
6. ⏳ **Enquanto builda**, **ADICIONE ENVIRONMENT VARIABLE:**
   - Procure "Environment"
   - Clique "Add"
   ```
   Key: VITE_API_URL
   Value: https://fretebr-backend.onrender.com/api
   ```
7. **Clique:** "Deploy"
8. Quando ficar **verde** = sucesso ✅

✅ **Frontend deployado!**

---

## ⏳ AGUARDE FINAL (5 min)

Render vai:
- ✅ Build tudo
- ✅ Deploy databases
- ✅ Gerar URLs

Você verá no Dashboard quando tudo ficar **VERDE** (checkmarks verdes)

---

## ✅ RESULTADO FINAL

Quando tudo verde:

```
🌐 Frontend: https://fretebr-frontend.onrender.com
🔌 Backend:  https://fretebr-backend.onrender.com
💾 Database: PostgreSQL automático
🔒 SSL:      HTTPS automático ✅
```

---

## 🧪 TESTE AGORA (2 min)

1. **Vá para:** https://fretebr-frontend.onrender.com
2. **Clique:** "Sign up"
3. **Preencha:**
   - Email: `teste@teste.com`
   - Senha: `123456`
   - Nome: `João`
   - Tipo: "Motorista"
4. **Clique:** "Cadastrar"
5. **Faça login** com mesmo email/senha
6. Vê o **Dashboard** 🎉

---

## 🎊 PARABÉNS! 

**FreteBR está LIVE no mundo!** 🚀

---

## 📝 PRÓXIMAS ETAPAS (depois)

Quando quiser adicionar Mercado Pago + Twilio:

1. Crie contas em:
   - mercadopago.com (para Pix)
   - twilio.com (para WhatsApp)
2. Pega as credenciais
3. No Render Dashboard → Backend → Environment → Edita as 4 variáveis
4. Redeploy automático

Simples! 💪

---

## 🆘 SE FICAR PRESO

Se algo não carregar:
- **Render lento?** Aguarde mais (às vezes demora 5-10 min no primeiro build)
- **Build error?** Clique em "View Build Logs" para ver o erro
- **Frontend não conecta backend?** Verifique se `VITE_API_URL` está correto

---

**Você consegue fazer isso em 30 minutos!** 💪

Manda notícia quando Frontend ficar verde! 🟢
