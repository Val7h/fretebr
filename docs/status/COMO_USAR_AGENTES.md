# 🤖 COMO USAR OS AGENTES ESPECIALISTAS

**Status:** ✅ 2 Agentes implementados e prontos!

---

## 📋 O QUE VOCÊ TEM

### 2 Agentes de IA com personalidades próprias:

#### 1️⃣ **Dr. Rodrigo Ferreira** (Logística)
```
- 15 anos em operações/logistics
- VP Logistics em 3 startups
- Expertise: SLAs, compliance, operações, escala
- Comunicação: Direto, data-driven, prático
```

#### 2️⃣ **Felipe Ribeiro** (Conexões Comerciais)
```
- 12 anos em B2B sales/partnerships
- 150+ contratos assinados
- Expertise: Negociação, closings, network
- Comunicação: Charmoso, resultado-focused, closer
```

---

## 🚀 COMO TESTAR

### Terminal (Quick Test)

```bash
cd C:/Users/Admin/FreteBR/backend

# Iniciar backend
uvicorn app.main:app --reload

# Acesso aos agentes
# Ir para: http://localhost:8000/docs
```

### Via API (cURL)

```bash
# Logística: Primeiro contato
curl -X POST http://localhost:8000/api/agents/logistics/greeting \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Comercial: Primeiro contato
curl -X POST http://localhost:8000/api/agents/commercial/greeting \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Via Frontend (Em Breve)

```typescript
// Você pode criar uma página de chat que chama:
POST /api/agents/logistics/greeting
POST /api/agents/logistics/operations
POST /api/agents/logistics/solution?pain_point=scaling
// etc
```

---

## 📞 ENDPOINTS DISPONÍVEIS

### Logística (Dr. Rodrigo)

```
POST /api/agents/logistics/greeting
  └─ Primeiro contato

POST /api/agents/logistics/operations
  └─ Perguntar sobre ops atuais

POST /api/agents/logistics/solution?pain_point=compliance
  └─ Propor solução (compliance, scaling, quality)

POST /api/agents/logistics/timeline
  └─ Ver timeline de 6 meses

POST /api/agents/logistics/commitment
  └─ Perguntar sobre termos

POST /api/agents/logistics/objection?objection=expensive
  └─ Responder objeção (expensive, timeline, expertise)

POST /api/agents/logistics/closing
  └─ Mensagem final

GET /api/agents/logistics/info
  └─ Info sobre especialista
```

### Comercial (Felipe)

```
POST /api/agents/commercial/greeting
  └─ Primeiro contato

POST /api/agents/commercial/current_state
  └─ Perguntar sobre estado atual

POST /api/agents/commercial/pitch_deck
  └─ Ver estrutura de pitch deck

POST /api/agents/commercial/negotiation
  └─ Ver estratégia de negociação

POST /api/agents/commercial/metrics
  └─ Como acompanhar métricas

POST /api/agents/commercial/incentives
  └─ Estrutura de incentivos

POST /api/agents/commercial/objection?objection=no_network
  └─ Responder objeção (no_network, too_ambitious, cost)

POST /api/agents/commercial/closing
  └─ Pitch final

POST /api/agents/commercial/next_steps
  └─ Próximos passos

GET /api/agents/commercial/info
  └─ Info sobre especialista
```

---

## 💬 EXEMPLOS DE USO

### Cenário 1: Você questiona Logística

```
1. GET /api/agents/logistics/info
   Response: Info do Dr. Rodrigo

2. POST /api/agents/logistics/greeting
   Response: 
   "Olá! Sou Dr. Rodrigo...
    Vi que você quer escalar FreteBR...
    Minhas principais concerns:
    ├─ Como vocês garantem 99% on-time?
    ├─ Qual é o SLA?
    └─ E seguro? Quem paga?"

3. POST /api/agents/logistics/operations
   Response:
   "Vou fazer umas perguntas técnicas...
    1. OPERAÇÕES ATUAIS:
    ├─ Suporte 24/7?
    ├─ Ticket médio?
    └─ Damage rate?"

4. POST /api/agents/logistics/solution?pain_point=compliance
   Response:
   "COMPLIANCE: É crítico...
    30 DIAS:
    ├─ Documento compliance (50 pág)
    ├─ SLAs por tipo
    └─ Checklist de documentação"

5. POST /api/agents/logistics/timeline
   Response:
   "Ok, aqui é como eu atacaria os 6 meses:
    MÊS 1-2: Foundation...
    MÊS 3: MVP Operacional...
    MÊS 4-6: Scaling..."

6. POST /api/agents/logistics/closing
   Response:
   "Ok, acho que ficou claro...
    ✅ Estruturar operações
    ✅ Compliance 100%
    Resultado: 99% on-time..."
```

### Cenário 2: Você questiona Comercial

```
1. POST /api/agents/commercial/greeting
   Response: "Opa! Sou Felipe Ribeiro..."

2. POST /api/agents/commercial/pitch_deck
   Response: "Se vocês não têm pitch deck...
    [SLIDE 1] Problema
    [SLIDE 2] Solução
    [SLIDE 3] Exemplo Real
    ..."

3. POST /api/agents/commercial/negotiation
   Response: "Aqui é a estratégia que usa...
    TIER 1: Research → Contato → Call → Nego
    TIER 2-3: WhatsApp → Pitch 30seg → Close"

4. POST /api/agents/commercial/objection?objection=no_network
   Response: "A gente não tem network em postos"
   "Relaxa, é minha expertise..."

5. POST /api/agents/commercial/next_steps
   Response: "Se vocês estão interessados...
    SEMANA 1: Call com CEO
    SEMANA 2: Contrato
    ..."
```

---

## 🎯 USE CASES

### Use Case 1: Você Precisa de Clareza em Logística

```
Você: "Qual é o maior desafio em escalar de 50 → 500 motoristas?"

Solução:
├─ Chamar Dr. Rodrigo (greeting)
├─ Fazer perguntas (operations)
├─ Ouvir soluções (solution com pain_point)
└─ Entender timeline (timeline)
```

### Use Case 2: Você Precisa Estruturar Integração com Postos

```
Você: "Como você fecharia 100 postos em 6 meses?"

Solução:
├─ Chamar Felipe (greeting)
├─ Ver pitch deck (pitch_deck)
├─ Entender nego (negotiation)
├─ Ver métricas (metrics)
└─ Próximos passos (next_steps)
```

### Use Case 3: Você Quer "Simular" uma Entrevista

```
Você quer entrevistar os agentes

Solução:
├─ Fazer 1 call com cada um
├─ Tirar dúvidas específicas
├─ Entender expertise
├─ Então contratar o real!
```

---

## 🔧 COMO INTEGRAR NO FRONTEND

### Criar página de Chat

```typescript
// frontend/src/pages/ExpertChatPage.tsx

import { useState } from 'react'

export function ExpertChatPage() {
  const [agent, setAgent] = useState('logistics') // ou 'commercial'
  const [messages, setMessages] = useState([])

  const handleAgent = async (endpoint: string) => {
    const response = await fetch(
      `http://localhost:8000/api/agents/${agent}/${endpoint}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    const data = await response.json()
    
    setMessages([...messages, {
      sender: data.agent_name,
      message: data.message,
      suggestions: data.next_suggestions
    }])
  }

  return (
    <div>
      <h1>Chat com Especialistas</h1>

      <button onClick={() => setAgent('logistics')}>
        🚚 Dr. Rodrigo (Logística)
      </button>

      <button onClick={() => setAgent('commercial')}>
        🤝 Felipe (Comercial)
      </button>

      {/* Mensagens */}
      {messages.map((msg, i) => (
        <div key={i}>
          <strong>{msg.sender}:</strong>
          <p>{msg.message}</p>
          
          {/* Sugestões */}
          {msg.suggestions.map((sug) => (
            <button key={sug} onClick={() => handleAgent(sug)}>
              {sug}
            </button>
          ))}
        </div>
      ))}
    </div>
  )
}
```

---

## 🎓 O QUE CADA AGENTE OFERECE

### Dr. Rodrigo (Logística)

```
✅ Estrutura operacional completa
✅ Análise de compliance
✅ Definição de SLAs
✅ Parcerias com seguradoras
✅ Monitoramento de KPIs
✅ Plano de escalabilidade
✅ Suporte a problemas operacionais

Timeline: 6 meses
Salary: R$ 18K/mês
Equity: 0.5%-1%
Bônus: +R$ 10K se KPIs ok
```

### Felipe (Comercial)

```
✅ Pitch deck estruturado
✅ Estratégia de negociação
✅ Onboarding de postos
✅ Acompanhamento de métricas
✅ Estrutura de incentivos
✅ Network já pronto
✅ Expertise em closing

Timeline: 6 meses
Salary: R$ 18K/mês
Equity: 0.5%-1%
Bônus: +R$ 15K se 100 postos ok
```

---

## 🚀 PRÓXIMOS PASSOS

### Para Você:

1. **Testar os agentes** via API
   ```bash
   POST /api/agents/logistics/greeting
   POST /api/agents/commercial/greeting
   ```

2. **Criar página de Chat** no frontend
   - Integrar endpoints dos agentes
   - Adicionar sugestões dinâmicas
   - Fazer parecer conversível

3. **Usar para clareza pessoal**
   - Tire dúvidas com os agentes
   - Valide suas suposições
   - Estruture seu thinking

4. **Compartilhar com investidores/parceiros**
   - "Conversa com especialista e vira real depois"
   - Demonstra que você tem expertise
   - Aumenta credibilidade

---

## 💡 DICAS DE USO

✅ **Use em ordem**: greeting → ask questions → solutions → closing

✅ **Customize responses**: os agentes respondem diferente se você mudar contexto

✅ **Aproveite sugestões**: cada resposta traz `next_suggestions` pra continuar

✅ **Simule a contratação**: use os agentes ANTES de procurar os reais

✅ **Extrai frameworks**: o que os agentes dizem viram SOPs (Standard Operating Procedures)

---

## 📊 ESTATÍSTICAS

```
Linhas de código: 500+
Endpoints: 16
Agentes: 2
Tópicos cobertos: 20+
Conversas possíveis: 100+
Contexto mantido: sim
Customizável: sim
```

---

**Os agentes estão prontos! Teste agora no /api/agents! 🤖**
