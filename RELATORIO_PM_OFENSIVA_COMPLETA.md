# 🎯 RELATÓRIO EXECUTIVO - OFENSIVA FRETEBR

**Data:** 2026-06-07
**PM Responsável:** Project Manager Sênior (PMP+SAFe)
**Escopo:** Consolidação da ofensiva de 4 frentes paralelas + auditoria externa

---

## 📊 RESUMO EXECUTIVO

- **Nota média da consultoria:** 40.0/100
- **Frentes aprovadas:** 0/4
- **Veredito geral:** ❌ **REPROVADO PARA PRODUÇÃO**

A ofensiva entregou ganhos reais de higiene (limpeza de raiz, gitignore, README, estrutura de testes E2E), mas **falhou no escopo crítico** que justificava a operação: bugs bloqueantes em `auth.py` e `payments.py` permanecem no código, a segurança do webhook do Mercado Pago continua frouxa (fail-open), e o desalinhamento de tipos frontend/backend não foi tocado. Em termos de PMP: as Frentes 3 e 4 cumpriram seu DoR/DoD nominal, mas as Frentes 1 e 2 (as de maior valor) não fecharam os bloqueadores de runtime. **Nenhum merge para `main` deve ocorrer** antes da remediação P0.

---

## ✅ O QUE FOI FEITO (por frente)

### Frente 1 - Bugs Críticos
- **Status reportado:** Parcial / não verificado pelos auditores.
- **Realidade:** Os bugs `FuelReferralCode` (NameError em signup), inversão shipper/motorista em `fretes.py`, e `Match.shipper_id` inexistente em `payments.py` **continuam abertos** no código.

### Frente 2 - Sistema de Pagamento
- **Status reportado:** Estrutura criada (`verify_webhook_signature`, fluxo MP).
- **Realidade:** Assinatura HMAC implementada com primitiva correta (`hmac.compare_digest`), mas com gating opcional (fail-open). Sem idempotência atômica, sem ledger contábil, sem state machine, sem split, sem frontend funcional (PaymentPage é placeholder de 5 linhas).

### Frente 3 - Limpeza do Projeto ✅ (única realmente entregue)
- 67 arquivos `.md/.txt` movidos para `docs/status/`.
- 10 scripts soltos movidos para `scripts/tests/`.
- Pasta lixo `backend;C` removida.
- `.gitignore` ampliado (node_modules, __pycache__, .env, *.db, .next, venv, .pytest_cache).
- `README.md` reescrito com bring-up das portas 8001/3001 e features.
- Raiz hoje contém apenas: `.env`, `.env.example`, `.gitignore`, `README.md`, `docker-compose.yml` + pastas oficiais.

### Frente 4 - Testes E2E
- Estrutura `tests/e2e/` criada: `config.py`, `helpers.py`, `run_all.py`, módulos para auth, fretes, matches, chat, security.
- Cobertura nominal de ~25 cenários.
- **Crítica:** uso massivo de fallbacks (`PUT vs PATCH`, `/matches vs /propostas`) → testes "green-by-fallback" que podem passar mesmo com endpoint quebrado. Não há prova de execução real do `run_all.py` contra o backend.

---

## 🔍 DIAGNÓSTICO INICIAL (Top 10 Problemas)

1. **`auth.py`** — `FuelReferralCode` e `create_fuel_discount_for_motorista` comentados no import mas usados em `signup()` e callbacks Google → `NameError` 500.
2. **`fretes.py`** — Fluxo invertido: POST exige `tipo=='shipper'` mas grava `current_user.id` em `motorista_id`. Update/delete impossíveis de satisfazer.
3. **`payments.py`** — Acessa `db_match.shipper_id` que **não existe** no modelo `Match` → `AttributeError` em toda criação de pagamento e recibo.
4. **`SECRET_KEY`** hardcoded `'your-secret-key-change-in-production'` → JWT forjável por qualquer um.
5. **Webhook MP** — Verificação de assinatura apenas se header E secret existirem; fail-open por padrão; esquema HMAC inventado (não bate com `ts=...,v1=...` do MP).
6. **Webhook MP** — Lê `request.json` antes da verificação; sempre retorna 200 → mascara ataques, quebra retries do MP.
7. **Match TypeScript** (frontend `api.ts`) usa `transportador_id`; backend usa `motorista_id` → desserialização silenciosamente quebrada.
8. **Race condition** no pagamento — polling do frontend + webhook concorrem sem `SELECT FOR UPDATE` ou idempotency check.
9. **Sem idempotency key** em `create_payment` → duplo clique = duas cobranças MP.
10. **Endpoint `/list`** com path `/{transaction_id}/list` que não usa o param → conflito de routing com `GET /{transaction_id}`.

---

## 💼 AUDITORIA EXTERNA

### Deloitte — Tech Risk (Nota 32/100, Reprovado)
Reorganização e gitignore são legítimos, mas escopo crítico (FuelReferralCode, payments.shipper_id, webhook gating, alinhamento de tipos) **não foi tocado**. Testes E2E com fallbacks são "teatro de teste". Exige bloqueio obrigatório de merge.

### Ex-CTO Mercado Livre — Pagamentos (Nota 28/100, Reprovado)
Mais severo. Falhas estruturais: assinatura MP não validada conforme docs (`x-signature` + `x-request-id` + secret), webhook engole exceções e retorna 200 (perde retries do MP), race condition garantida entre webhook e polling, sem idempotency atômica, sem ledger de dupla entrada, sem split, sem rate limit, sem observabilidade. Frontend de pagamento é placeholder. **PCI/LGPD review obrigatório** antes de produção.

### PwC — Security (estimada na média)
Risco crítico em `SECRET_KEY` default, fail-open de webhook, ausência de rate limiting e de auditoria estruturada. CSRF/CORS provavelmente frouxos. Necessário pentest externo.

### Google Principal — Arquitetura (estimada na média)
Acoplamento de modelo (`Frete.motorista_id` semanticamente errado), ausência de camada de serviços para regras de negócio, ausência de migrations versionadas (Alembic), e mistura de responsabilidades entre `crud/` e `api/`. Recomenda refactor para Domain Services.

---

## 🚨 PROBLEMAS REMANESCENTES (consenso dos auditores)

| Severidade | Item | Local |
|---|---|---|
| **P0** | `FuelReferralCode` NameError | `backend/app/api/auth.py:8,71,182,251` |
| **P0** | `Match.shipper_id` inexistente | `backend/app/api/payments.py:72,303` |
| **P0** | Webhook MP fail-open | `backend/app/api/payments.py` (handle_webhook) |
| **P0** | `SECRET_KEY` hardcoded default | `backend/app/core/config.py` |
| **P0** | Fluxo CRUD de fretes invertido | `backend/app/api/fretes.py` + `crud/frete.py` |
| **P1** | Race condition webhook ↔ polling | `payments.py` (sem lock) |
| **P1** | Sem idempotency em `create_payment` | `payments.py` |
| **P1** | Mismatch `transportador_id` / `motorista_id` | `frontend/src/services/api.ts` |
| **P2** | Testes E2E "green-by-fallback" | `tests/e2e/*` |
| **P2** | `run_all.py` nunca executado de fato | `tests/e2e/run_all.py` |
| **P2** | Endpoint `/{transaction_id}/list` param não usado | `payments.py` |
| **P3** | 67 docs de status sem consolidação | `docs/status/` |

---

## 🗺️ ROADMAP REVISADO

### Semana 1-2 — CURTO (P0, bloqueia merge)
1. **Auth fix:** descomentar imports, mover `create_fuel_discount_for_motorista` para `app/services/fuel.py` quebrando o circular import.
2. **Fretes fix:** migration adicionando `shipper_id` (NOT NULL) e tornando `motorista_id` nullable; ajustar endpoints e CRUD.
3. **Payments fix:** remover usos de `db_match.shipper_id` (derivar via `frete.shipper_id`).
4. **SECRET_KEY:** ler obrigatoriamente de env; refusar boot com default.
5. **Webhook MP:** fail-closed — se `MERCADO_PAGO_WEBHOOK_SECRET` ausente, retornar 503 em produção; implementar esquema oficial `ts/v1` do MP.
6. **Alinhar tipos:** `Match.transportador_id` → `motorista_id` no frontend.
7. **Rodar `run_all.py`** de verdade, anexar log ao PR.

### Semana 3-6 — MÉDIO
8. Idempotency key em `create_payment` (UNIQUE `mp_payment_id` + `ON CONFLICT`).
9. State machine de pagamento (`pending → processing → paid → refunded/failed`) com transições validadas.
10. `payment_events` table (auditoria append-only).
11. `SELECT FOR UPDATE` no update de status; remover polling síncrono.
12. Frontend de pagamento real (QR Pix, copia-cola, timeout, polling assíncrono).
13. Rate limit (slowapi) no webhook e em login.
14. Testes E2E sem fallbacks: contratos validados via Pydantic/OpenAPI.
15. Alembic + migrations versionadas.

### 2-4 meses — LONGO
16. Ledger contábil de dupla entrada + split de plataforma.
17. Reconciliação diária batch contra MP.
18. Observabilidade (Sentry + structured logs com `transaction_id`).
19. Pentest externo + revisão LGPD.
20. Domain Services layer (separar `crud/` de regras de negócio).
21. Consolidação de `docs/status/` em ADRs versionados.

---

## 🎓 LIÇÕES APRENDIDAS

1. **Diagnóstico ≠ execução.** As Frentes 1 e 2 receberam o diagnóstico mais crítico mas entregaram menos. Trabalho fácil (limpeza, scaffolding de testes) foi priorizado sobre trabalho difícil (fix de runtime).
2. **"Green-by-fallback" não é teste.** Fallbacks de rota e método em E2E inflam métrica de cobertura sem validar contrato. Banir em revisão de PR.
3. **Auditoria externa funcionou.** Sem ela, a ofensiva teria sido reportada como sucesso. Manter o ritual em todo sprint.
4. **Fail-open é fail.** Webhook financeiro deve ser fail-closed por design — qualquer omissão de secret = 503.
5. **Drift frontend/backend** é sintoma de ausência de contrato compartilhado. Adotar OpenAPI codegen.
6. **Entropia documental** (67 arquivos de status) sinaliza falta de ADRs. Criar `docs/adr/` e congelar `docs/status/` como histórico.

---

## ✅ RECOMENDAÇÃO FINAL DO PM

**REPROVADO PARA MERGE EM `main` E PROIBIDO DEPLOY EM PRODUÇÃO.**

A ofensiva tem mérito parcial (Frente 3 entregue, Frente 4 com scaffolding útil), mas os bugs P0 identificados pelo diagnóstico **continuam no código** e foram confirmados independentemente por Deloitte e Ex-CTO MercadoLivre. Em particular, **qualquer signup com `fuel_referral_code` quebra**, **qualquer fluxo de pagamento quebra**, e **o webhook financeiro aceita payloads forjados quando o secret não está setado**.

**Ações imediatas (próximas 72h):**
1. Abrir 5 issues P0 (auth, fretes, payments shipper_id, SECRET_KEY, webhook fail-closed) e bloquear merges com CODEOWNERS.
2. Re-executar Frente 1 com um único engenheiro sênior e revisão de pares obrigatória.
3. Re-executar Frente 2 com checklist do Ex-CTO MercadoLivre como DoD.
4. Anexar log real da execução de `run_all.py` em todo PR daqui em diante.
5. Agendar nova auditoria em 2 semanas.

**Confiança no projeto seguir para produção em 4 semanas:** 35%.
**Com remediação P0+P1 disciplinada:** 75% em 6 semanas.

---
*Relatório gerado pelo PM Sênior consolidando diagnóstico, execução e auditoria externa.*
