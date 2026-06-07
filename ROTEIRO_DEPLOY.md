# 🚀 ROTEIRO DE DEPLOY — STAGING BETA GRATUITO

**Objetivo:** colocar o FreteBR no ar pra usuários reais, **R$ 0/mês**, em ~30 minutos.

**Stack:**
- Backend → **Fly.io** (free tier: 3 VMs shared 256MB, ~700h/mês)
- Banco → **Fly Postgres** (free tier: 1 cluster 1GB)
- Frontend → **Vercel** (free tier: builds ilimitados)

---

## 🔑 ANTES DE COMEÇAR — guarde estes segredos

⚠️ **ESTES SÃO ÚNICOS PRO SEU DEPLOY — não compartilhe.**

```
SECRET_KEY=Vj1CxfU7vQ3aFIsDe4tt3iR2WkyZAYlg9FeWrNBDe1MgUVBmZMvpBYtkQqryPG_8hACZMtcOpbxudW6di71KBw

MERCADO_PAGO_WEBHOOK_SECRET=XS3LRJKrLZH8vyYsJFxGmDJ9-yagPqDRen5fkQ8kFIo
```

Salve em algum gerenciador de senha (Bitwarden, 1Password) ou num `.env.production.local` **fora do git**.

---

## 📋 PASSO 1 — Criar contas (5 min)

1. **Fly.io** → https://fly.io/app/sign-up (precisa cartão pra free tier, **não cobra** se ficar dentro do limite)
2. **Vercel** → https://vercel.com/signup (login com GitHub é mais simples)
3. **GitHub** → se ainda não tem repo, crie um privado e suba o código

---

## 🐳 PASSO 2 — Instalar Fly CLI (Windows)

No PowerShell:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
fly version
```

Login:
```powershell
fly auth login
```

---

## 🐘 PASSO 3 — Criar Postgres no Fly (2 min)

```powershell
cd C:\Users\Admin\FreteBR\backend
fly postgres create --name fretebr-db --region gru --vm-size shared-cpu-1x --volume-size 1
```

⚠️ **Anote a connection string que aparecer** — algo como:
```
postgres://fretebr:XXXXXX@fretebr-db.flycast:5432/fretebr?sslmode=disable
```

---

## 🚀 PASSO 4 — Deploy do Backend (5 min)

```powershell
cd C:\Users\Admin\FreteBR\backend
fly launch --no-deploy --copy-config --name fretebr-api --region gru
```

Setar segredos:
```powershell
fly secrets set `
  SECRET_KEY="Vj1CxfU7vQ3aFIsDe4tt3iR2WkyZAYlg9FeWrNBDe1MgUVBmZMvpBYtkQqryPG_8hACZMtcOpbxudW6di71KBw" `
  MERCADO_PAGO_WEBHOOK_SECRET="XS3LRJKrLZH8vyYsJFxGmDJ9-yagPqDRen5fkQ8kFIo" `
  DATABASE_URL="<<COLE A CONNECTION STRING DO POSTGRES AQUI>>"
```

Deploy:
```powershell
fly deploy
```

Verificar:
```powershell
fly status
curl https://fretebr-api.fly.dev/health
```

✅ Deve retornar `{"status":"ok","service":"FreteBR Backend"}`

---

## 🌐 PASSO 5 — Deploy do Frontend na Vercel (3 min)

### Opção A — pelo site (mais fácil)
1. Login em https://vercel.com
2. **Add New → Project**
3. Importa seu repo do GitHub
4. **Root Directory:** `frontend`
5. **Environment Variables:**
   - `VITE_API_URL` = `https://fretebr-api.fly.dev/api`
   - `VITE_AUTH_COOKIE_MODE` = `true`
6. Deploy!

### Opção B — pelo CLI
```powershell
cd C:\Users\Admin\FreteBR\frontend
npm install -g vercel
vercel login
vercel --prod
# Quando perguntar env vars, cole as duas acima
```

---

## 🌍 PASSO 6 — Configurar CORS no backend

A Vercel vai te dar uma URL tipo `fretebr-xxx.vercel.app`. Adicione ela no CORS:

Edite `backend/app/main.py`, encontra `allow_origins` e adiciona sua URL Vercel. Depois:

```powershell
cd C:\Users\Admin\FreteBR\backend
fly deploy
```

---

## ✅ PASSO 7 — Smoke test

Acesse a URL da Vercel. Faça:

1. Cadastra um shipper (use seu email real)
2. Posta um frete teste
3. Cadastra um motorista (outro email/aba anônima)
4. Faz proposta
5. Volta como shipper, aceita
6. Testa chat
7. Testa Pix (vai usar **modo MOCK** — botão "Simular pagamento" aparece)

---

## 📣 PASSO 8 — Convidar os 10 primeiros (o que importa!)

**Texto pronto pra WhatsApp** (copia, cola, edita):

> Oi! Tô lançando um marketplace de fretes (FreteBR) em beta privado.
> É grátis nessa fase — só preciso de feedback honesto.
> Topa testar 5 min? https://SUA-URL.vercel.app
>
> Se for motorista: cria conta como "motorista" e me diz se o fluxo de fazer proposta faz sentido.
>
> Se for shipper: cria como "shipper", posta um frete fictício e me conta se ficou claro.

**Onde postar:**
- 3 grupos de WhatsApp de caminhoneiros (procura nos grupos da sua cidade)
- 5 pessoas que você conhece que mexem com transporte
- LinkedIn (1 post curto descrevendo a dor)

**Meta da primeira semana:** 20 cadastros, 5 fretes postados, 3 propostas. Se atingir, está validado. Se não, ajusta o pitch antes de continuar.

---

## 📊 PASSO 9 — Monitorar

```powershell
# Logs do backend ao vivo
fly logs -a fretebr-api

# Métricas (Prometheus)
curl https://fretebr-api.fly.dev/metrics/summary

# Status
fly status -a fretebr-api
```

---

## 🛟 SE ALGO QUEBRAR

| Sintoma | O que fazer |
|---|---|
| `fly deploy` falha | `fly logs` pra ver o erro |
| Backend 500 no signup | Verificar se `DATABASE_URL` foi setada (passo 4) |
| Frontend não conecta | Verificar `VITE_API_URL` e CORS (passo 6) |
| Cookies não persistem | Conferir `VITE_AUTH_COOKIE_MODE=true` na Vercel + `force_https=true` no fly.toml |
| Pix retorna 503 | Estava esperando — modo MOCK ainda funciona (botão "Simular pagamento") |

---

## 💰 LIMITES DO FREE TIER

| Serviço | Free | Quando começa cobrar |
|---|---|---|
| Fly.io VMs | 3× shared-cpu-1x 256MB | A partir da 4ª ou se você ligar always-on |
| Fly Postgres | 1GB volume | Após 1GB usado |
| Vercel | 100GB bandwidth/mês | Improvável atingir em beta |

**Provavelmente vai ficar em R$ 0 enquanto tiver < 100 usuários ativos.**

---

## 📈 CRITÉRIO PRA TOMAR PRÓXIMA DECISÃO

Roda o beta por **2 semanas**. No fim, responda:

| Métrica | Mínimo | Boa | Excelente |
|---|---|---|---|
| Cadastros | 20 | 50 | 100+ |
| Fretes postados | 5 | 15 | 30+ |
| Propostas feitas | 3 | 10 | 25+ |
| Match aceito (engajamento) | 1 | 5 | 10+ |
| Mensagens trocadas | 5 | 20 | 50+ |

- **Atingiu "Mínimo":** segue pra Sprint P5-A (compliance pra cobrar)
- **Ficou abaixo:** entrevista 5 usuários que cadastraram mas não voltaram, ajusta o produto
- **Bombou:** acelera P5-A e busca um investidor anjo

---

## 🆘 SE FICAR EMPACADO

Me chama dizendo em que passo travou. Vou ajudar **só com a tela que precisa**:

- "Travou no passo 4" → te mando comandos específicos
- "Não recebi connection string" → fix imediato
- "CORS falhando" → patch exato

---

## 🎯 RESUMO EXECUTIVO

```
✅ Tudo configurado (fly.toml, vercel.json, Dockerfile, secrets gerados)
⏱  ~30 minutos pra estar no ar
💰 R$ 0/mês durante o beta
🎯 Meta: 20 cadastros em 2 semanas pra justificar Sprint P5-A
```

**Quando estiver no ar, me manda a URL pra eu rodar um smoke test E2E externo e te confirmar que tá tudo OK.** 🚀
