# 🎯 BRIEFING PARA ESPECIALISTAS - FRETEBR

**Data:** 2026-06-05  
**Objetivo:** Escalação Estratégica + Integração com Postos de Combustível  
**Timeline:** 6 meses para MVP comercial robusto  
**Investimento Estimado:** R$ 500K - 1M

---

## 📋 EXECUTIVE SUMMARY

**FreteBR** é um marketplace de fretes (ride-sharing para cargas) que está saindo do MVP e entrando em fase de growth hackers.

**Problema:** Crescimento orgânico é lento (50-100 motoristas/mês)

**Solução:** Integração estratégica com postos de combustível como canal de aquisição (CAC = R$ 20 vs R$ 500 de marketing digital)

**Objetivo:** 
- 100 postos onboarded em 6 meses
- 500 motoristas via postos/mês
- R$ 200M GMV/ano

**Especialistas Necessários:**
1. 🚚 **Especialista em Logística** - Otimizar rotas, compliance, operações
2. 🤝 **Especialista em Conexões Comerciais** - Onboarding de postos, parcerias

---

## 🎯 SITUAÇÃO ATUAL (MVP)

### Produto
```
✅ App motorista + shipper (React + FastAPI)
✅ Matching de fretes
✅ Sistema de pagamento básico
✅ Chat + rating ⭐ NEW
✅ Rastreamento real-time 🗺️ NEW
✅ Google OAuth login
✅ Programa de referência (motorista → motorista)
```

### Mercado
```
📊 DAU: 50 usuários
📦 Fretes/dia: 20
💰 GMV/mês: R$ 20K
🔄 Retenção 30d: 15%
```

### Foco Atual
- Melhorar confiança (rating, tracking, verificação)
- Aumentar engagement (notificações, gamification)
- Monetização de referrals

---

## 🚀 VISÃO ESTRATÉGICA (6 MESES)

### Fase 1: Logística & Compliance (Mês 1-2)

**Especialista Logística:**

1. **Análise de Rotas**
   - Implementar algoritmo de otimização de rotas
   - Calcular ETA com precisão
   - Sugerir rotas mais eficientes ao motorista

2. **Compliance & Segurança**
   - Documentação: CNH, CRLV, Foto, Comprovante de endereço
   - Verificação de background (bloqueios, multas)
   - Seguro de frete (parceria com seguradoras)
   - SLA: tempo máximo de entrega por região

3. **Operações**
   - Suporte 24/7 para motoristas
   - Processo de resolução de conflicts
   - Métricas de qualidade (on-time %, damage %)
   - KPIs de health check

**Entregáveis:**
- [ ] Algoritmo de otimização de rotas implementado
- [ ] Documentação de compliance 100% pronto
- [ ] SLAs definidos por região
- [ ] Sistema de verificação de motorista
- [ ] Dashboard operacional (admin)

---

### Fase 2: Go-To-Market com Postos (Mês 1-3)

**Especialista Conexões Comerciais:**

1. **Identificação de Postos**
   - Mapa de 500+ postos em SP (piloto)
   - Segmentação: grandes redes (Shell, Petrobrás) vs independentes
   - Modelo de negociação diferenciado por tier

2. **Abordagem & Negociação**
   - Pitch comercial: "Ganhe R$ 10/motorista + R$ 10/frete"
   - Demonstração de economia para postos
   - Contrato padrão com cláusulas
   - Timeline: "Motorista indicado → 6 meses de comissão"

3. **Onboarding**
   - Treinamento de frentista (30 min, virtual)
   - Código QR/NFC único por frentista
   - Dashboard de ganhos em tempo real
   - Suporte dedicado para postos

4. **Parcerias Estratégicas**
   - Desconto no combustível (via Mercado Pago, pré-pago, ou cashback)
   - Co-marketing (posts nas redes dos postos)
   - Revenue share: FreteBR subsidia 50% do primeiro mês

**Entregáveis:**
- [ ] Lista de 200+ postos com contatos
- [ ] Pitch deck + business case
- [ ] Contrato padrão + SLA
- [ ] Onboarding playbook
- [ ] 10 postos piloto com sucesso (Mês 3)

---

### Fase 3: Scaling & Operações (Mês 3-6)

**Ambos os Especialistas:**

1. **Escalação de Postos**
   - 100 postos ativos
   - 200+ frentistas
   - 4K motoristas indicados
   - R$ 200M GMV

2. **Otimização Operacional**
   - Reduzir CAC de R$ 20 para R$ 15 (maior volume)
   - Aumentar LTV de motorista (mais sticky)
   - Reduzir churn de frentista
   - Otimizar rotas em tempo real

3. **Expansão Geográfica**
   - SP → RJ, MG, BA, RS
   - Adaptar modelo por região

---

## 💰 BUSINESS CASE

### Cenário Base (1 Ano, SP)

```
Postos: 100
Frentistas: 200 (2 por posto)
Motoristas/mês: 20 × 200 frentistas = 4.000
Fretes/mês: 50 × 4.000 motoristas = 200.000
GMV/mês: 200.000 fretes × R$ 1.000 avg = R$ 200M

CUSTOS:
├─ Motorista signup: 4.000 × R$ 10 = R$ 40K
├─ Comissão fretes: 200.000 × R$ 10 = R$ 2M
├─ Desconto combustível: ~R$ 100K
├─ Suporte/ops: R$ 100K/mês = R$ 1.2M/ano
└─ Total: R$ 3.34M

RECEITA (10% takerate):
├─ 200.000 fretes × R$ 1.000 × 10% = R$ 20M
├─ Taxa marketplace: +2% = R$ 4M
└─ Total: R$ 24M

LUCRO: R$ 20.66M (após custos)
ROI: 6.2x em 1 ano
```

### CAC vs LTV

```
CAC (Cost Acquisition Cost):
├─ Via organismo: R$ 500
├─ Via postos: R$ 20
└─ Redução: 96%

LTV (Lifetime Value):
├─ Motorista ativo: ~R$ 10K/ano
├─ Retenção 12 meses: ~60% (com gamification)
└─ LTV total: R$ 6K

LTV/CAC:
├─ Organismo: 12x
└─ Postos: 300x
```

---

## 🎯 ESPECIALISTA 1: LOGÍSTICA

### Perfil Ideal
```
✅ 10+ anos experiência em logística/delivery
✅ Conhecimento de: rotas, SLAs, compliance, seguros
✅ Experiência com startups logistics (99App, iFood, Loggi)
✅ Network com seguradoras e órgãos reguladores
✅ Skills: operações, análise de dados, people management
```

### Responsabilidades

**Mês 1-2: Foundation**
- [ ] Desenhar arquitetura operacional
- [ ] Definir documentação requerida
- [ ] Criar SLAs por região
- [ ] Estabelecer parceria com seguradora
- [ ] Treinar time de suporte

**Mês 3-6: Scaling**
- [ ] Monitorar KPIs (on-time %, damage %, churn)
- [ ] Otimizar rotas (algoritmo)
- [ ] Expandir geográfica
- [ ] Resolver problemas operacionais
- [ ] Negociar com órgãos reguladores (ANTT, DETRAN)

### Deliverables
```
1. Documento de Compliance (50 pág)
2. SLA por região (rodoviário, urbano, long-haul)
3. Algoritmo de otimização de rotas
4. Dashboard operacional
5. Playbook de resolução de conflicts
6. Relatórios mensais de KPIs
```

### Métricas de Sucesso
```
✅ 99% on-time delivery
✅ <1% damage rate
✅ <10% churn motorista/mês
✅ ETA accuracy: ±10% 
✅ Zero compliance issues
```

---

## 🎯 ESPECIALISTA 2: CONEXÕES COMERCIAIS

### Perfil Ideal
```
✅ 10+ anos em B2B sales/partnerships
✅ Experiência com grandes redes (Shell, Petrobrás, Esso)
✅ Track record de 50+ contratos assinados
✅ Network em combustíveis, varejo, logística
✅ Skills: negociação, business development, closing
```

### Responsabilidades

**Mês 1: Research & Pitch**
- [ ] Mapear 500+ postos em SP
- [ ] Criar pitch deck + business case
- [ ] Definir contrato padrão
- [ ] Negociar com 5-10 postos grandes (Shell, Petrobrás, Esso)

**Mês 2-3: Pilots**
- [ ] Onboard 10 postos piloto
- [ ] Treinar frentistas
- [ ] Acompanhar metrics (motoristas indicados, ativação)
- [ ] Iterar modelo conforme feedback

**Mês 4-6: Scaling**
- [ ] Atingir 100 postos
- [ ] Estruturar tim sales (2-3 AEs)
- [ ] Automatizar onboarding
- [ ] Expandir para RJ, MG, BA, RS

### Deliverables
```
1. Mapa de postos + contatos (200+)
2. Pitch deck (15 slides) + business case
3. Contrato padrão + SLA
4. Onboarding playbook
5. Dashboard de métricas (real-time)
6. 10 postos onboarded com sucesso (Mês 3)
```

### Métricas de Sucesso
```
✅ 100 postos onboarded (Mês 6)
✅ 4.000 motoristas indicados/mês (Mês 6)
✅ Taxa de ativação: >80%
✅ Churn de posto: <5%/mês
✅ CAC: R$ 20
✅ Margem: >60%
```

---

## 📅 TIMELINE INTEGRADA

```
┌─────────────────────────────────────────────────────────────┐
│ MÊS 1: Foundation                                           │
├─────────────────────────────────────────────────────────────┤
│ Logística:                                                  │
│ ├─ Desenhar arquitetura operacional                        │
│ ├─ Definir documentação (CNH, CRLV, etc)                   │
│ └─ Criar SLAs por região                                   │
│                                                             │
│ Conexões Comerciais:                                        │
│ ├─ Mapear 500+ postos                                      │
│ ├─ Criar pitch deck                                        │
│ └─ Negociar com 5 postos grandes                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ MÊS 2: Pilots                                               │
├─────────────────────────────────────────────────────────────┤
│ Logística:                                                  │
│ ├─ Implementar verificação de motorista                    │
│ ├─ Setup seguro/compliance                                 │
│ └─ Criar dashboard operacional                             │
│                                                             │
│ Conexões Comerciais:                                        │
│ ├─ Onboard 5-10 postos piloto                              │
│ ├─ Treinar frentistas                                      │
│ └─ Acompanhar primeiros motoristas                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ MÊS 3: MVP Comercial                                        │
├─────────────────────────────────────────────────────────────┤
│ Logística:                                                  │
│ ├─ Monitorar operações (on-time, damage)                  │
│ ├─ Resolver problemas                                      │
│ └─ Otimizar rotas                                          │
│                                                             │
│ Conexões Comerciais:                                        │
│ ├─ 10 postos piloto com sucesso ✓                          │
│ ├─ Estruturar processo de sales                            │
│ └─ Iniciar roll-out de Mês 4                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ MÊS 4-6: Scaling                                            │
├─────────────────────────────────────────────────────────────┤
│ Logística:                                                  │
│ ├─ Escalar operações para 100 postos                       │
│ ├─ Expandir para novos estados                             │
│ └─ Otimizações contínuas                                   │
│                                                             │
│ Conexões Comerciais:                                        │
│ ├─ 100 postos onboarded                                    │
│ ├─ Expand para SP → RJ, MG, BA, RS                         │
│ └─ Build sales team                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 💼 ESTRUTURA DE TRABALHO

### Formato
```
✅ Consultoria: 3-6 meses (pode estender conforme necessidade)
✅ Modalidade: Full-time remoto/hybrid (SP)
✅ Remuneração: A negociar (equity + cash)
✅ Métricas: Bônus por atingir KPIs

Mínimo esperado:
├─ 40h/semana de work
├─ Reuniões 3x/semana com time
└─ Relatórios mensais de progresso
```

### Ferramentas
```
✅ Slack (comunicação)
✅ Google Drive (docs)
✅ Jira (tasks)
✅ FreteBR app + backend (product)
✅ Notion (planning)
```

---

## 🎯 SUCESSO = QUANDO?

### Logística ✅
```
[✅] Documentação 100% completa
[✅] SLA definidos e comunicados
[✅] Seguro ativo com cobertura
[✅] Dashboard operacional pronto
[✅] KPIs do mês 3 atingidos (99% on-time, <1% damage)
```

### Conexões Comerciais ✅
```
[✅] 10 postos piloto ativos (Mês 3)
[✅] 500+ motoristas indicados
[✅] Processo de sales estruturado
[✅] 100 postos onboarded (Mês 6)
[✅] 4K motoristas/mês ativados
```

---

## 📞 COMO COMEÇAR

**Próximas ações:**
1. [ ] Publicar oportunidade (LinkedIn, AngelList)
2. [ ] Entrevistar candidatos
3. [ ] Oferecer aos especialistas (Week 1 de Junho)
4. [ ] Onboarding (Week 2 de Junho)
5. [ ] Kick-off meeting (Week 3)

**Enviar para especialistas:**
- Este briefing
- Product deck (FreteBR)
- Acesso ao app + backend
- Contatos iniciais (10-15 postos)

---

## 🚀 IMPACTO ESPERADO

Ao fim dos 6 meses:

```
📊 Métrica                Antes      Depois      Crescimento
────────────────────────────────────────────────────────────
DAU                       50         500         +900%
Fretes/dia                20         200         +900%
GMV/mês                   R$ 20K     R$ 200M    +10.000x
Motoristas via postos     0          4.000      N/A
Postos ativos             0          100        N/A
CAC                       R$ 500     R$ 20      -96%
Retenção 30d              15%        50%        +230%
LTV/CAC                   12x        300x       +2.400%
```

---

**Especialistas: Prontos? Vamos ao FreteBR! 🚀**
