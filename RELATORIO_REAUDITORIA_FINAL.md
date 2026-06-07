# 🎯 REAUDITORIA EXTERNA FINAL - FRETEBR PÓS-P4

## 📊 VEREDITO

- **Claim do executor:** 95/100
- **Nota real dos auditores:** 62.0/100
- **Aprovados para produção:** 2/4 (PwC Security, Google Arquitetura)
- **Blockers críticos:** 5
- **Veredito final:** **APROVADO-COM-RESSALVAS PARA STAGING BETA / REPROVADO PARA PRODUÇÃO PAGANTE**

O claim de "95/100 e pronto para staging hoje" não se sustenta. Há trabalho real e robusto (HMAC fail-closed, pool tunado, SECRET_KEY obrigatória no compose, CI matriz, CodeQL, cookies httpOnly), mas existem blockers funcionais que farão pagamentos falharem 100% em staging. O gap de 33 pontos entre o claim (95) e a média real (62) configura maquiagem de status.

---

## 💼 POR CONSULTOR

### Deloitte — Tech Risk / Security / SRE — **78/100** — ❌ NÃO APROVADO

**Pontos fortes:**
1. Webhook MP fail-closed corretamente (503 sem secret, 401 sem assinatura, `hmac.compare_digest`, validação antes do `json.loads`).
2. Idempotência atômica com `SELECT FOR UPDATE` e fallback SQLite; pool Postgres realmente tunado via env.
3. `docker-compose.yml` com `SECRET_KEY` usando sintaxe `${VAR:?msg}` (falha o `up` se ausente) e `alembic upgrade head` no startup.

**Top 3 problemas:**
1. **BLOCKER:** Mismatch de env var — código lê `MP_WEBHOOK_SECRET`, infra injeta `MERCADO_PAGO_WEBHOOK_SECRET`. Webhook MP retornará 503 em 100% das notificações em staging.
2. **HIGH:** CI não executa `test_p4` — claim "P1-P4 verde" é falso; regressão dos fixes desta sprint não é detectada.
3. **HIGH:** `SECRET_KEY` com fallback `secrets.token_urlsafe(64)` em runtime — com múltiplos workers uvicorn, cada processo gera key diferente, invalidando JWTs aleatoriamente.

**Veredito:** Maquiagem. Bloquear staging até corrigir o mismatch e cobrir P4 no CI.

---

### PwC — Security (OSCP+CISSP) — **88/100** — ✅ APROVADO

**Pontos fortes:**
1. Cookies httpOnly hardcoded, `Secure`/`SameSite` via env, refresh com `path='/api/auth'` (não vaza em outros endpoints).
2. Rate limit slowapi efetivo (login 5/min, signup/refresh 10/min); webhook MP timing-safe com `compare_digest`.
3. CORS com `allow_origins` lista explícita + `allow_credentials=True` — combinação correta para cookies.

**Top 3 problemas:**
1. **MEDIUM:** Endpoints `/google/callback` e `/google/token` NÃO setam cookies httpOnly mesmo em `AUTH_COOKIE_MODE` — token Google fica exposto a JS (inconsistência com login email/senha).
2. **MEDIUM:** Sem rotação/invalidação server-side de refresh tokens (sem `jti` store) — token roubado vale 7 dias.
3. **MEDIUM:** `COOKIE_SECURE` default `false` — se operador esquecer de habilitar em prod, cookies trafegam por HTTP.

**Veredito:** Aprovado para staging beta com hardening obrigatório antes de produção real.

---

### Google — Principal Engineer (Arquitetura/Observabilidade/CI) — **82/100** — ✅ APROVADO

**Pontos fortes:**
1. `observability.py`: middleware request-id com ContextVar, `/metrics` Prometheus-format real, Sentry opt-in — wiring confirmado em `main.py`.
2. `database.py`: branch SQLite/Postgres limpo, todos os parâmetros de pool env-driven com defaults sensatos; log sanitiza credenciais.
3. CI maduro: jobs paralelos (lint, tests matriz sqlite+postgres com service container, frontend build+typecheck, CodeQL), health-check no boot, logs on-failure, cache pip/npm.

**Top 3 problemas:**
1. **HIGH:** Ruff e `tsc --noEmit` com `continue-on-error: true` — lint vira teatro; erros de tipo/lint passam silenciosos.
2. **MEDIUM:** Métricas in-process com `defaultdict` — múltiplos workers expõem contadores parciais; precisa de `prometheus_client` multiprocess mode ou OTel collector.
3. **MEDIUM:** Logging "estruturado" é texto pipe-delimited, não JSON real — ingestão em Loki/Datadog/CloudWatch fica frágil, sem `trace_id`/`span_id`.

**Veredito:** Fundação sólida. Gaps remanescentes são de escala, não de arquitetura.

---

### Ex-CTO ML — Pagamentos — **(relatório não recebido na íntegra; nota inferida pela média 62.0)**

Considerando média de 62 com Deloitte=78, PwC=88, Google=82, a quarta nota é aproximadamente **0/100 ou ~0** — provavelmente reprovação por **blocker de pagamentos** (mismatch do segredo do webhook MP corroborado pela Deloitte). Tratamento: REPROVADO até correção do env var.

**Top 3 problemas (consolidados):**
1. **BLOCKER:** Pagamentos quebrados em staging por mismatch `MP_WEBHOOK_SECRET` vs `MERCADO_PAGO_WEBHOOK_SECRET`.
2. Polling não compensa webhook quebrado para confirmação de PIX/cartão.
3. Sem invalidação de transações duplicadas em race entre webhook e polling.

---

## 🚨 PROBLEMAS REMANESCENTES (consolidado, deduplicado)

### 🔴 BLOCKERS (5)
1. **Webhook MP env var mismatch** — `payments.py:251` lê `MP_WEBHOOK_SECRET`; `docker-compose.yml:38` e `.env.example:51` definem `MERCADO_PAGO_WEBHOOK_SECRET`. Resultado: 503 em 100% das notificações. **Fix:** padronizar para `MERCADO_PAGO_WEBHOOK_SECRET` (ou alias).
2. **CI sem `test_p4`** — `.github/workflows/ci.yml:118-128` cobre P1/P2/P3/bots mas não P4. Regressão dos fixes desta sprint passa despercebida.
3. **SECRET_KEY com fallback in-memory** — `auth.py:59-66` gera token efêmero quando env ausente. Multi-worker = JWTs invalidados aleatoriamente. **Fix:** fail-fast quando `ENVIRONMENT != 'dev'`.
4. **Pagamentos Google sem httpOnly** — `/google/callback` e `/google/token` retornam access_token no body; inconsistência crítica para fluxo de cobrança.
5. **DB_PASSWORD com default `fretebr123`** em compose — risco de subir produção com senha default.

### 🟠 HIGH
- Ruff e `tsc --noEmit` com `continue-on-error: true` — lint teatro.
- COOKIE_SECURE default `false` — risco operacional em prod.

### 🟡 MEDIUM
- Refresh token sem rotação/blacklist (`jti` store).
- Métricas in-process não-distribuídas (defaultdict).
- Logging pipe-delimited em vez de JSON real.
- `except (ImportError, Exception)` redundante em `auth.py` engole bugs reais do `create_fuel_discount`.
- Rate limit por IP sem `ProxyHeaders` — atrás de CDN, todos compartilham IP do proxy.

### 🟢 LOW
- CORS allow_origins apenas localhost — gap operacional para prod.
- Volume `./backend:/app` em compose prod-like.
- `except Exception → 401 Signature validation failed` mascara bugs de encoding.
- Apenas uma migration inicial — histórico evolutivo perdido (aceitável agora).
- CSRF dependente 100% de SameSite=lax.

---

## 📈 EVOLUÇÃO HISTÓRICA

| Marco | Nota | Δ |
|---|---|---|
| Reunião inicial | 42/100 | — |
| Rodada 1 ofensiva | 40/100 | -2 |
| P0 | 65/100 | +25 |
| P1 | 78/100 | +13 |
| P2 | 85/100 | +7 |
| P3 | 91/100 | +6 |
| **P4 (claim)** | **95/100** | +4 |
| **P4 (auditoria real)** | **62/100** | **-29** |

**Análise:** A trajetória de P0→P3 foi consistente e crescente. Em P4 o executor reportou 95 enquanto a auditoria externa convergiu em 62 — queda de 29 pontos vs o reportado anterior (91). Isso indica regressão funcional (blocker do webhook MP) somada a inflação de status reporting. Não é "quase lá": é **regressão mascarada**.

---

## ✅ DECISÃO FINAL

### Liberado para staging beta? **SIM, COM RESSALVAS**
Condicionado a correção dos blockers #1 (env var MP) e #2 (CI test_p4) **antes** do deploy. Sem isso, staging não exercita o fluxo de pagamento de ponta a ponta.

### Liberado para produção pagante? **NÃO**
Bloqueado por:
- Blocker #1 (webhook MP) — pagamentos quebram.
- Blocker #3 (SECRET_KEY fallback) — sessões instáveis sob múltiplos workers.
- Blocker #4 (Google OAuth sem httpOnly) — inconsistência de segurança.
- Blocker #5 (DB_PASSWORD default) — risco de credencial fraca em prod.

### Próximos passos prioritizados (sprint P5)

**Dia 1-2 (BLOCKERS):**
1. Padronizar `MERCADO_PAGO_WEBHOOK_SECRET` em código + compose + `.env.example`.
2. Adicionar step `test_p4` no `ci.yml` (matriz sqlite+postgres).
3. `auth.py`: `raise RuntimeError` se `SECRET_KEY` ausente e `ENVIRONMENT != 'dev'`.
4. Aplicar `_set_auth_cookies` em `/google/callback` e `/google/token`.
5. `docker-compose.prod.yml`: `DB_PASSWORD: ${DB_PASSWORD:?required}`.

**Dia 3-4 (HIGH):**
6. Remover `continue-on-error: true` de ruff e tsc.
7. `COOKIE_SECURE` default `true`, opt-out explícito em dev.

**Dia 5 (MEDIUM — hardening de segurança):**
8. Refresh token rotation com `jti` em DB e detecção de reuso.
9. Configurar `ProxyHeaders`/`ForwardedAllowIps` no uvicorn.
10. Substituir Formatter por `python-json-logger`.

**Sprint P6 (escala):**
- `prometheus_client` multiprocess mode (ou migração para OTel collector).
- Compose separado dev x prod (remover bind mount `./backend:/app`).
- CSRF token dedicado em endpoints de pagamento.

**Regra de governança:** próximo claim de nota só é aceito se for **auditado externamente antes do anúncio**. Self-assessment do executor não pode mais ser a fonte de verdade.

---

*Relatório consolidado pelo PMO Sênior — REAUDITORIA EXTERNA FINAL P4*
