# REAUDITORIA ADVERSARIAL #2 - POS-FIX DOS BLOCKERS

## Veredito final

- **Claim pos-fix:** ~87/100
- **Nota real desta auditoria:** 78.3/100 (gap -8.7 vs claim)
- **Aprovados producao:** 3/4 (Deloitte, PwC, Google aprovam; Ex-CTO ML veta)
- **Blockers REALMENTE fechados:** 9/11
  - Realmente fechados: 9
  - Parciais: 1 (revogacao server-side de refresh)
  - Nao fechados: 1 (metricas multi-worker)

## Status dos 5 blockers originais (consolidado)

| # | Blocker | Status | Consenso |
|---|---------|--------|----------|
| 1 | Webhook MP env var mismatch (MP_WEBHOOK_SECRET vs MERCADO_PAGO_WEBHOOK_SECRET) | FECHADO | Deloitte + Ex-CTO ML confirmam or-chain em payments.py L252-255 com HMAC SHA256 e compare_digest |
| 2 | CI nao executa test_p4 / Ruff e tsc com continue-on-error | FECHADO | Deloitte + Google confirmam ci.yml sem continue-on-error; step P4 nominal na matrix sqlite+postgres |
| 3 | SECRET_KEY com fallback runtime (invalida JWT multi-worker) | FECHADO | Deloitte confirma fail-hard RuntimeError em production/staging (auth.py L60-67); dev gera temporaria com warning |
| 4 | Google OAuth nao seta cookies httpOnly + COOKIE_SECURE default false + sem revogacao server-side refresh | 2 FECHADOS + 1 PARCIAL | PwC: google_callback/google_token agora chamam _set_auth_cookies com Response e create_refresh_token; COOKIE_SECURE default true via compose. Revogacao continua PARCIAL: ha rotacao mas sem store jti/blacklist em Redis - refresh roubado vale ate 7d |
| 5 | Logging texto pipe-delimited + metricas in-process multi-worker | 1 FECHADO + 1 NAO FECHADO | Google: JsonFormatter real com json.dumps e request_id (FECHADO). Metricas continuam defaultdict in-process global - sem prometheus_client multiproc nem OTel (NAO FECHADO) |

## Por consultor

### Deloitte Tech Risk Partner - 94/100 - APROVADO
Os 3 blockers atribuidos (webhook, CI, SECRET_KEY) realmente fechados com evidencia direta. Observacoes menores: organizacao de imports em auth.py (cookie helpers antes do bloco principal) e cobertura de Ruff fraca (so E,F,W com varios ignores - sugere adicionar B bugbear e S security).

### PwC Security Partner - 93/100 - APROVADO COM RESSALVA
Cookies OAuth efetivamente fechados, paridade com /login confirmada. COOKIE_SECURE seguro por default no compose. DB_PASSWORD e SECRET_KEY com sintaxe `:?` fail-hard. Revogacao de refresh permanece PARCIAL - aceitavel para MVP dado httpOnly + path restrito + samesite + rate limit 10/min, mas recomenda tracker em Redis antes de escalar.

### Principal Eng Google - 88/100 - APROVADO COM RESSALVA
2 de 3 blockers fechados: CI bloqueante e logging JSON real com seletor por ENVIRONMENT. Metricas multi-worker continuam PARCIAIS - defaultdict in-process global sem prometheus_client multiproc dir. Aceitavel com 1 worker uvicorn; NAO aceitavel sob gunicorn -w N.

### Ex-CTO Mercado Livre (Fintech) - 38/100 - VETO MANTIDO
Sai do veto da 1a auditoria (webhook + secrets foram fechados), MAS mantem REPROVACAO por gaps fintech-criticos nao tecnicos:
1. **Sem Mercado Pago Split/marketplace** - dinheiro entra na conta da plataforma e precisa repassar manualmente ao motorista. FreteBR vira instituicao de pagamento de facto sem autorizacao BACEN.
2. **Sem job de reconciliacao diaria** Transaction local vs API MP `/v1/payments/search` - webhook pode falhar silenciosamente.
3. **Audit trail incompleto** - nao registra IP, user-agent, timestamp de acesso ao QR/copia-cola (essencial para disputa/chargeback e LGPD).
4. **Sem ledger contabil em partidas dobradas** separado de Transaction - misturar estado operacional com lancamentos contabeis vira divergencia irreconciliavel em escala. Falta tabela `ledger_entries` immutable append-only.

## Novos problemas surgidos

**Seguranca / Auth:**
- Inconsistencia de default AUTH_COOKIE_MODE: auth.py default 'false' vs docker-compose default 'true'. Deploy fora do compose (k8s, uvicorn direto) cai em header-only sem cookies httpOnly silenciosamente.
- `google_token` retorna schema Token sem refresh_token no body - regressao para clientes API nao-cookie que perdem capacidade de refresh.
- Sem protecao CSRF em endpoints state-changing quando auth vem via cookie (SameSite=lax permite top-level POST). Recomendado double-submit token para POST/PUT/DELETE sensiveis.
- Sem deteccao classica de reuso de refresh para revogar familia inteira.
- COOKIE_SAMESITE 'lax' OK, mas considerar 'strict' para `fretebr_refresh` dado path `/api/auth`.
- ENVIRONMENT duplicado em docker-compose.yml L32 e L43 (cosmetico, indica merge descuidado).

**Observabilidade:**
- `request_duration_ms` armazena ate 1000 floats por path em memoria - vazamento por path unico mesmo apos normalizacao (404 com path novo cria entrada permanente).
- JsonFormatter usa `strftime('%z')` que pode retornar string vazia em containers UTC sem tz configurada.
- Sem rate limit no `/metrics` - exposto a scrape por qualquer cliente se nao houver auth no proxy.

**CI/CD:**
- Ruff sem `format --check`, sem mypy/pyright - bugs de tipo Python passam.
- CodeQL sem `queries: security-extended` - cobertura padrao apenas.
- Codigo: imports/funcoes de cookie helpers antes do bloco principal de imports em auth.py.

## Liberacao

### Staging beta - LIBERADO
Com 3/4 consultores aprovando (Deloitte 94, PwC 93, Google 88) e os 5 blockers originais fechados ou parciais aceitaveis para MVP, a plataforma esta liberada para staging beta com usuarios reais em volume controlado. Restricao tecnica: rodar com 1 worker uvicorn enquanto metricas nao migrarem para prometheus_client multiproc.

### Producao pagante - NAO LIBERADO
Veto fintech mantido pelo Ex-CTO ML. Operar pagamentos em volume acima de R$ 100k/mes sem Split MP + reconciliacao diaria + ledger contabil + audit trail completo cria exposicao regulatoria (BACEN), risco de custodia indevida e divergencia contabil irreconciliavel. Liberacao condicionada aos 4 itens fintech P5.

## Proximos passos prioritizados

### P5-A (BLOQUEANTES de producao pagante - fintech)
1. **Integrar Mercado Pago Split / Marketplace** - configurar `application_fee` e `collector_id` por motorista, dinheiro nunca passa pela conta da plataforma como custodia.
2. **Job de reconciliacao diaria** - cron batendo `Transaction` local vs `GET /v1/payments/search` MP, alerta em divergencia.
3. **Tabela `ledger_entries` append-only** com partidas dobradas (debit/credit, account_id, immutable), separada de Transaction operacional.
4. **Audit trail completo** de acessos a QR/copia-cola - IP, user-agent, timestamp, user_id em tabela `payment_access_log`.

### P5-B (ALTOS - escala e seguranca)
5. **Refresh token store em Redis** (jti + family_id) com deteccao de reuso e revogacao server-side.
6. **Metricas prometheus_client multiproc** com `PROMETHEUS_MULTIPROC_DIR` OU migrar para OTel exporter - desbloqueia gunicorn -w N.
7. **CSRF double-submit token** para POST/PUT/DELETE em modo cookie.
8. **Cap de cardinalidade em metricas** por path (LRU ou hash bucket) - corrigir vazamento de memoria.

### P5-C (MEDIOS - higiene)
9. Alinhar default AUTH_COOKIE_MODE entre auth.py e docker-compose (preferir secure-by-default).
10. Restaurar `refresh_token` no body do `/google/token` para clientes nao-cookie.
11. Ruff: adicionar regras B (bugbear) e S (security), `ruff format --check`, mypy/pyright no CI.
12. CodeQL: `queries: security-extended`.
13. JsonFormatter: forcar UTC ISO8601 com `datetime.now(timezone.utc).isoformat()`.
14. Reorganizar imports em auth.py (cookie helpers no bloco principal).
15. Remover ENVIRONMENT duplicado em docker-compose.yml.
16. Considerar SameSite=strict para `fretebr_refresh`.
