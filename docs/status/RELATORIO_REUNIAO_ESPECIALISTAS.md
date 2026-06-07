# Relatório de Reunião de Especialistas — FreteBR

**Data:** 07/06/2026
**Conduzido por:** Gerente Geral
**Escopo:** Auditoria técnica completa do marketplace FreteBR (FastAPI + React/Vite)

---

## Contexto Auditado

- Backend: `C:\Users\Admin\FreteBR\backend\app` (FastAPI + SQLAlchemy + SQLite)
- Frontend: `C:\Users\Admin\FreteBR\frontend\src` (React + TypeScript + Vite)
- Módulos: auth, fretes, matches, messages, notifications, transactions, payments (Mercado Pago Pix), referral, fuel_station, rating, tracking, agents

---

## 1. ARQUITETO DE SOFTWARE

### Bom
- Separacao clara em `api/`, `models/`, `schemas/`, `crud/`, `services/`.
- Routers registrados de forma modular em `main.py`.
- Frontend organizado em `pages/`, `components/`, `services/`.

### Problemas
- **Duplicacao de organizacao**: existe `app/api/` (auth, fretes, matches, payments) e `app/routes/` (referral, fuel_station, rating, tracking, agents). Sem padrao unico.
- **Servicos API duplicados no frontend**: `api.ts`, `fretesApi.ts`, `matchesApi.ts`, `paymentApi.ts` — sem ownership claro de quem chama o que.
- **76 arquivos .md/.txt na raiz** (SEMANA_1..4, RELATORIO_*, STANDUP_*, varios INTEGRATION_COMPLETE). Documentacao caotica, dificulta onboarding.
- **Import circular conhecido e comentado** em `auth.py` (`# TODO: Fix circular import` para `create_fuel_discount_for_motorista`) — codigo usa `FuelReferralCode` mesmo com import comentado: vai estourar `NameError` em runtime se `fuel_referral_code` for enviado.
- `docker-compose.yml` na raiz mas nao revisado nesta auditoria; existe pasta suspeita `backend;C` (lixo no filesystem).
- `ReferralDashboard.tsx.bak` versionado.

### Melhorias
- Consolidar tudo em `app/api/` ou `app/routes/` (escolher um padrao).
- Arquivar docs antigas em `docs/historico/`.
- Habilitar Alembic — `Base.metadata.create_all` em `main.py` nao escala para producao.

---

## 2. ESPECIALISTA EM SEGURANCA

### Bom
- JWT com expiracao configuravel.
- Bearer token via `HTTPBearer`.
- Hash de senha existente (`verify_password`/`hash_password`).
- Webhook Mercado Pago aceita `X-Signature`.

### Problemas CRITICOS
- **SECRET_KEY default hardcoded**: `os.getenv("SECRET_KEY", "your-secret-key-change-in-production")` (auth.py:20). Se `.env` falhar em producao, JWTs sao forjaveis trivialmente.
- **NameError exploitavel**: no fluxo `/signup`, se `user.fuel_referral_code` for enviado, o codigo referencia `FuelReferralCode` que **nao esta importado** (linha comentada). Crash 500 garantido — DoS facil.
- **Webhook Mercado Pago nao valida assinatura**: `handle_webhook(payload, signature)` recebe `X-Signature` mas a verificacao real depende do servico; nao ha rejeicao explicita de payload nao assinado. Risco de marcar transacoes como pagas sem pagamento.
- **Webhook sempre retorna 200** mesmo em erro (`payments.py:269`) — bom para MP, mas mascara falhas reais. Sem log estruturado / alertas.
- **CORS** com `allow_methods=["*"]` e `allow_headers=["*"]` para multiplas portas locais. Producao precisa whitelist explicita.
- **Token sem refresh token** — expiracao de 30min forca re-login frequente OU forca aumentar TTL (pior).
- **Sem rate limiting** em `/login`, `/signup`, `/google/callback` — brute force livre.
- **Validacao fraca**: `telefone or "11999999999"` em `payments.py:116` envia telefone falso ao Mercado Pago se shipper nao tiver telefone.
- **Sem validacao de CPF** no model `User`.

### Melhorias
- Falhar startup se `SECRET_KEY` nao estiver setado.
- Implementar slowapi/limiter.
- Refresh token + revogacao.
- Assinatura HMAC obrigatoria no webhook.

---

## 3. ESPECIALISTA EM UX/UI

### Bom
- Telas cobrindo fluxo completo: Login, FindFrete, PostFrete, MyFretes, MyProposals, Chat, Rating, Payment, Receipt.
- Componentes dedicados: `ProposalModal`, `NotificationCenter`, `PaymentStatus`, `MapaRotaLeaflet`.

### Problemas
- **Confusao semantica grave** (ver Produto/Backend): "PostFrete" + "MyFretes" + "FindFrete" + "MyProposals" + "MyMatches" — o usuario shipper e o motorista provavelmente nao entendem qual tela e deles. Nao ha documentacao de fluxo.
- Sem skeleton/loading states padronizados (nao identificados nesta amostra).
- Sem feedback de erro estruturado — `localStorage.getItem('jwt_token')` direto, sem tratamento de 401 global no interceptor.
- Sem responsividade documentada — `App.css` raiz sugere CSS adhoc.

### Melhorias
- Onboarding com tour guiado.
- Interceptor de resposta 401 -> logout automatico.
- Padronizar design system (Tailwind ou MUI).

---

## 4. ESPECIALISTA EM BACKEND

### Bom
- Uso correto de `Depends`, `HTTPException`, status codes.
- Paginacao com `skip/limit` em fretes.
- Transactions encapsuladas em `crud/`.
- Idempotencia parcial em `create_payment` (verifica transacao existente, marca expirada).

### Problemas CRITICOS
- **MODELO DE DOMINIO INVERTIDO**: `Frete.motorista_id` (frete.py:18) — o frete pertence ao motorista. Mas `POST /api/fretes` exige `tipo == "shipper"` (fretes.py:30). Resultado: shipper cria frete, mas o frete e gravado com `motorista_id = current_user.id` (do shipper!). **Isso quebra todo o dominio** — um shipper aparece como motorista do proprio frete. Causa bugs em cascata em matches, payments, ratings.
- **GET /meus-fretes** so permite motorista, mas frete e criado por shipper — shipper nunca consegue ver os proprios fretes via esta rota.
- **PUT/DELETE /fretes/{id}** so permitido a motoristas — shippers que criaram nao podem editar/excluir.
- **Match.create** usa Query params (`valor_proposta`, `mensagem` como Query) em vez de body JSON — anti-pattern REST.
- `list_user_transactions` em `payments.py:337` esta na rota `/{transaction_id}/list` — path mal desenhado (transaction_id nao e usado).
- N+1 queries provaveis em `get_payment_status` (acessa `frete.motorista` etc sem `joinedload`).
- `create_all` no startup em vez de migracoes.

### Melhorias
- Refatorar `Frete` para `shipper_id` (poster) + `motorista_id` opcional (aceito).
- Body JSON em POST `/matches`.
- Alembic + indices em queries de listagem.

---

## 5. ESPECIALISTA EM FRONTEND

### Bom
- TypeScript com interfaces tipadas (`Frete`, `Match`, `Payment`, `User`).
- Axios interceptor para JWT.
- `ProtectedRoute` existente.

### Problemas
- **Tipos desalinhados com backend**: `Match.transportador_id` no frontend (api.ts:49) vs `motorista_id` no backend. **Quebra silenciosamente** consumo da API.
- **URL hardcoded**: `http://localhost:8001/api` em `api.ts:4` — sem `.env`/`import.meta.env.VITE_API_URL`.
- **Sem interceptor de resposta** para 401/403/network errors.
- **localStorage para JWT** — vulneravel a XSS. Considerar httpOnly cookie.
- 4 services API diferentes (`api.ts`, `fretesApi.ts`, `matchesApi.ts`, `paymentApi.ts`) sem padronizacao.
- `Frete.valor_r` (sem `$`) — nome de campo confuso.
- Arquivo `.bak` versionado.

### Melhorias
- Unificar em React Query/TanStack Query.
- Variaveis de ambiente Vite.
- Tipos gerados do OpenAPI (openapi-typescript).

---

## 6. ESPECIALISTA EM PRODUTO

### Bom
- Cobertura ampla: posting, matching, chat, rating, tracking, pagamento Pix, referral, integracao posto de gasolina (diferencial brasileiro).
- Google OAuth ja integrado.
- Notificacoes implementadas.

### Problemas
- **Falta clareza de papel**: nao existe um "Shipper" coerente nos modelos (relationships User nao tem `fretes_posted` para shipper).
- **Pagamento incompleto**: split de valores (taxa de plataforma) nao identificado. Marketplace sem revenue model.
- **Sem KYC** para motoristas (CNH, CRLV, ANTT). Risco regulatorio brasileiro.
- **Sem seguro de carga** nem integracao com seguradora.
- **Sem disputas**: e se a carga sumir? Nao ha fluxo.
- **Excesso de features paralelas** (fuel_station, referral, agents) sem o core estavel.
- LGPD nao endercada (sem politica, sem consentimento explicito).

### Melhorias
- Congelar features novas e estabilizar core (post -> match -> aceite -> pagamento -> entrega -> rating).
- Definir comissao da plataforma.
- Roadmap KYC + LGPD antes de producao.

---

## CONSENSO DA EQUIPE

O sistema tem **escopo ambicioso e cobertura impressionante**, mas sofre de **inconsistencia fundamental no modelo de dominio** (Frete.motorista_id usado por shipper), **debito de seguranca producao-bloqueante** (SECRET_KEY default, NameError em runtime, webhook sem assinatura validada), e **divida documental severa** (76 arquivos .md soltos). Funciona em demo, mas nao esta pronto para producao.

---

## TOP 5 PROBLEMAS CRITICOS

1. **Modelo Frete invertido**: `motorista_id` recebe `current_user.id` do shipper em `POST /api/fretes`. Quebra dominio inteiro. Bug arquitetural.
2. **NameError em /signup e /google/callback**: `FuelReferralCode` referenciado sem import — 500 garantido se `fuel_referral_code` enviado.
3. **SECRET_KEY com default inseguro**: `"your-secret-key-change-in-production"` permite forja de JWT se env faltar.
4. **Tipo Match desalinhado**: frontend usa `transportador_id`, backend retorna `motorista_id`. Bug silencioso.
5. **Webhook Mercado Pago sem rejeicao de payload nao assinado** + sempre retorna 200: risco de marcar pagamentos falsos como confirmados.

---

## ROADMAP

### Curto Prazo (1-2 semanas) — Estabilizacao
- [ ] Corrigir modelo `Frete`: adicionar `shipper_id`, manter `motorista_id` nullable para aceite. Migracao de dados.
- [ ] Corrigir import de `FuelReferralCode` em `auth.py` (resolver circular).
- [ ] Forcar `SECRET_KEY` obrigatorio no startup.
- [ ] Alinhar tipos frontend/backend (`transportador_id` -> `motorista_id`).
- [ ] Validar assinatura HMAC do webhook Mercado Pago.
- [ ] Limpar arquivos .md/.txt da raiz para `docs/historico/`.
- [ ] Remover `backend;C/`, `.bak`, lixo.

### Medio Prazo (3-6 semanas) — Producao-Ready
- [ ] Alembic (migracoes versionadas).
- [ ] Rate limiting (slowapi).
- [ ] Refresh token + interceptor 401 no frontend.
- [ ] Variaveis de ambiente Vite (`VITE_API_URL`).
- [ ] Unificar services frontend (React Query).
- [ ] Testes E2E core (post -> match -> pay -> rating).
- [ ] Logs estruturados (structlog) + Sentry.
- [ ] CI/CD com testes obrigatorios.

### Longo Prazo (2-4 meses) — Mercado
- [ ] KYC motorista (CNH/CRLV/ANTT via integracao Serpro).
- [ ] Split de pagamento (comissao plataforma).
- [ ] Fluxo de disputa/seguro.
- [ ] LGPD: politica de privacidade, consentimento, direito ao esquecimento.
- [ ] Mobile (React Native ou PWA com push).
- [ ] Migrar SQLite -> PostgreSQL.
- [ ] Observabilidade (Grafana, Prometheus).

---

## MATURIDADE DO SISTEMA

**Nota: 42/100**

| Dimensao | Nota |
|---|---|
| Arquitetura | 55 |
| Seguranca | 25 |
| UX/UI | 50 |
| Backend | 40 |
| Frontend | 55 |
| Produto/Mercado | 35 |

**Justificativa:** Cobertura funcional de MVP avancado (mereceria 65+), mas penalizado pelo bug arquitetural do modelo Frete, falhas de seguranca producao-bloqueantes e divida documental.

---

## PROXIMOS PASSOS RECOMENDADOS

1. **PARAR features novas** (referral, fuel station, agents).
2. Esta semana: corrigir os 5 problemas criticos acima.
3. Semana seguinte: Alembic + testes E2E do core.
4. Antes de qualquer producao: auditoria de seguranca externa + LGPD.
5. So entao retomar diferenciais (fuel station, referrals).

— Gerente Geral
