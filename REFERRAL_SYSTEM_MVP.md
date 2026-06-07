# 🎁 FreteBR Referral System - MVP

**Status:** ✅ Pronto para Integração  
**Data:** 5 de Junho, 2026  
**Tempo de Implementação:** 3-4 dias  

---

## 📋 Resumo Executivo

Sistema de indicação de motoristas que permite:
- Motorista A rejeita um frete e indica Motorista B
- Se Motorista B aceita, Motorista A ganha 20% da comissão FreteBR
- Crescimento orgânico via word-of-mouth
- Dashboard simples para acompanhar ganhos

---

## 🏗️ Arquitetura Técnica

### **Modelos de Dados**

```python
# Tabela: referrals
┌─────────────────────────────────────┐
│ id (UUID)                           │
│ referrer_motorista_id (FK→users)    │ ← Quem indicou
│ referred_motorista_id (FK→users)    │ ← Quem foi indicado
│ frete_id (FK→fretes)                │ ← Qual frete
│ comissao_valor (DECIMAL)            │ ← Valor ganho
│ status (VARCHAR)                    │ ← pending|completed|rejected|expired
│ created_at / completed_at           │
└─────────────────────────────────────┘

# Tabela: referral_withdrawals
┌─────────────────────────────────────┐
│ id (UUID)                           │
│ motorista_id (FK→users)             │
│ amount (DECIMAL)                    │
│ status (VARCHAR)                    │ ← pending|completed|failed
│ transaction_id (UUID)               │
│ created_at / completed_at           │
└─────────────────────────────────────┘

# Alteração em matches
├─ referrer_motorista_id (FK→users, nullable)
```

---

## 🔌 API Endpoints

### **POST /api/referrals/indicate**
Indicar um motorista para um frete

```bash
POST /api/referrals/indicate
Content-Type: application/json
Authorization: Bearer {token}

{
  "referred_motorista_id": "uuid-motorista-b",
  "frete_id": "uuid-frete"
}

Response 201:
{
  "id": "uuid-referral",
  "referrer_motorista_id": "uuid-a",
  "referred_motorista_id": "uuid-b",
  "frete_id": "uuid-frete",
  "comissao_valor": 0.00,
  "status": "pending",
  "created_at": "2026-06-05T10:00:00",
  "completed_at": null
}
```

### **GET /api/referrals/earnings**
Ver ganhos totais de referências

```bash
GET /api/referrals/earnings
Authorization: Bearer {token}

Response 200:
{
  "total_earned": 245.50,
  "referrals_completed": 5,
  "referrals_pending": 3,
  "referrals_rejected": 1,
  "recent_referrals": [
    {
      "id": "uuid",
      "referred_motorista_name": "João Silva",
      "status": "completed",
      "comissao_valor": 50.00,
      "created_at": "2026-06-01",
      "completed_at": "2026-06-02"
    },
    ...
  ]
}
```

### **GET /api/referrals/history?skip=0&limit=20&status_filter=completed**
Histórico completo de indicações

```bash
GET /api/referrals/history
Authorization: Bearer {token}

Response 200:
[
  {
    "id": "uuid",
    "referred_motorista_name": "Maria Santos",
    "frete_id": "uuid-frete",
    "status": "completed",
    "comissao_valor": 50.00,
    "created_at": "2026-06-01",
    "completed_at": "2026-06-02"
  },
  ...
]
```

### **POST /api/referrals/withdraw**
Solicitar saque de ganhos

```bash
POST /api/referrals/withdraw
Content-Type: application/json
Authorization: Bearer {token}

{
  "amount": 150.00
}

Response 201:
{
  "id": "uuid-withdrawal",
  "motorista_id": "uuid",
  "amount": 150.00,
  "status": "pending",
  "created_at": "2026-06-05T11:00:00",
  "completed_at": null
}
```

---

## 💰 Lógica de Comissão

**Quando um frete é completado:**

```python
# Se existe referral para este frete:
if referral exists and motorista_indicado aceitou:
    
    # Calcular comissão
    frete_comissao = 100.00  # 10% do valor do frete (exemplo)
    referrer_ganha = frete_comissao * 0.20  # 20%
    
    # Aplicar limites
    referrer_ganha = max(referrer_ganha, 5.00)    # Mínimo R$ 5
    referrer_ganha = min(referrer_ganha, 100.00)  # Máximo R$ 100
    
    # Atualizar status
    referral.status = "completed"
    referral.comissao_valor = referrer_ganha
    referral.completed_at = now()
```

---

## 🎨 Frontend Components

### **1. ReferralModal (Modal de Indicação)**

**Localização:** `frontend/src/components/ReferralModal.tsx`

**Uso:**
```tsx
<ReferralModal 
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  freightId={selectedFreight.id}
  onSuccess={() => refreshFreights()}
/>
```

**Trigger:** Quando motorista clica "Não posso pegar" em um frete
- Abre modal
- Busca motorista por nome/telefone
- Confirma indicação
- Mostra mensagem de sucesso

### **2. ReferralDashboard (Dashboard de Ganhos)**

**Localização:** `frontend/src/pages/ReferralDashboard.tsx`

**Rota:** `/dashboard/referrals`

**Funcionalidades:**
- Total ganho em indicações
- Contadores: Concluídas / Pendentes / Rejeitadas
- Histórico de indicações
- Botão de saque
- Info box "Como Funciona?"

---

## 🔄 Fluxo Completo (User Story)

```
1. MOTORISTA A REJEITA FRETE
   └─ Modal de Indicação aparece
   
2. MOTORISTA A BUSCA E SELECIONA MOTORISTA B
   └─ Sistema valida que B existe e está ativo
   └─ Cria Referral(status=pending)
   
3. MOTORISTA A VÊ CONFIRMAÇÃO
   └─ "✅ Indicado! Você ganhará comissão se ele aceitar"
   
4. MOTORISTA B RECEBE NOTIFICAÇÃO
   └─ WhatsApp: "João te indicou para frete de R$ 500"
   
5. MOTORISTA B ACEITA FRETE
   └─ Match criada com referrer_id = A
   └─ Referral muda para: pending_completion
   
6. MOTORISTA B COMPLETA FRETE
   └─ Sistema calcula: frete_comissao × 0.20 = ganho_de_A
   └─ Aplicar limites (min R$ 5, máx R$ 100)
   └─ Referral.status = "completed"
   
7. MOTORISTA A VÊ GANHO
   └─ Dashboard mostra R$ 50 ganhos
   └─ Pode sacar quando tiver ≥ R$ 10
   
8. MOTORISTA A SOLICITA SAQUE
   └─ Sistema cria ReferralWithdrawal(status=pending)
   └─ TODO: Integrar com Mercado Pago para transferência
```

---

## 📊 Arquivo de Migrações

**Localização:** `backend/migrations/add_referral_system.sql`

**Executar:**
```bash
cd backend
alembic upgrade head
# ou
psql -U user -d fretebr < migrations/add_referral_system.sql
```

---

## 🧪 Testes

**Localização:** `backend/tests/test_referral.py`

**Cobertura:**
- ✅ Indicação bem-sucedida
- ✅ Falha auto-indicação
- ✅ Ganhos vazios (novo motorista)
- ✅ Cálculo de comissão
- ✅ Limites de comissão (min/max)
- ✅ Fluxo de status
- ✅ Múltiplas referências

**Executar:**
```bash
pytest tests/test_referral.py -v
```

---

## 🚀 Integração com Código Existente

### **1. Modificar `CompletarFreteendpoint` em `matches`**

Quando um match muda para status `concluido`:

```python
from app.routes.referral import calculate_and_apply_referral_commission

# Ao completar match:
@router.put("/matches/{match_id}/complete")
async def complete_match(match_id: UUID, db: Session = Depends(get_db)):
    # ... lógica existente ...
    
    # NOVO: Calcular comissão de referência
    frete_comissao = calculate_frete_commission(match.frete)
    calculate_and_apply_referral_commission(
        match.id, 
        frete_comissao, 
        db
    )
    
    return match
```

### **2. Adicionar Link no Dashboard**

Em `frontend/src/pages/Dashboard.tsx`:

```tsx
<Link to="/dashboard/referrals">
  💰 Meus Ganhos com Indicações
</Link>
```

### **3. Adicionar Modal ao Rejeitar Frete**

Em `frontend/src/pages/FindFrete.tsx`:

```tsx
const [showReferralModal, setShowReferralModal] = useState(false);

const handleReject = (freight: Frete) => {
  setSelectedFreight(freight);
  setShowReferralModal(true);  // NOVO
};

<ReferralModal
  isOpen={showReferralModal}
  onClose={() => setShowReferralModal(false)}
  freightId={selectedFreight?.id}
  onSuccess={() => {
    setShowReferralModal(false);
    // Recarregar fretes
  }}
/>
```

---

## 📈 Métricas para Monitorar

Após deploy, acompanhe:

1. **Taxa de Indicações**
   - Quantas indicações por dia
   - Qual % converte em aceitos

2. **Ganhos Médios**
   - Ganho médio por motorista
   - Ganho total da plataforma em comissões

3. **Saque Requests**
   - Quantos motoristas estão sacando
   - Quanto está sendo sacado por mês

4. **Rejeição vs Indicação**
   - % de rejeições que viram indicações
   - Impacto na taxa de conclusão de fretes

---

## 🔐 Segurança & Validações

✅ **Implementado:**
- Validar que referrer != referred (CheckConstraint)
- Validar motorista B existe e está ativo
- Validar frete existe
- Validar saldo antes de saque
- Limites min/max de comissão

⚠️ **TODO (Fase 2):**
- Rate limiting em indicações (1 por minuto)
- Detecção de fraude (múltiplas indicações do mesmo motorista)
- Auditoria de saques

---

## 💡 Próximos Passos (Fase 2)

1. **Código de Referência Único**
   - Cada motorista tem código tipo "JOAO2024"
   - Compartilhar no WhatsApp
   - Bônus ao usar código

2. **Tiers de Comissão**
   - Bronze: 20% (0-10 indicações)
   - Prata: 25% (10-50 indicações)
   - Ouro: 30% (50+ indicações)

3. **Desafios Mensais**
   - "Indique 5 motoristas este mês, ganhe bônus R$ 50"
   - Ranking mensal

4. **Integração Completa**
   - Saque automático via Mercado Pago
   - Notificação quando ganho é creditado
   - Histórico de saques

---

## 📞 Troubleshooting

**Problema:** Indicação não funciona
- Verif icação: Motorista B está ativo?
- Verificação: Frete ainda está disponível?
- Logs: Ver erro na resposta da API

**Problema:** Ganhos não aparecem
- Verificação: Frete foi completado?
- Verificação: Match tem referrer_id?
- Logs: Ver função `calculate_and_apply_referral_commission`

---

## 📚 Arquivos Criados

```
backend/
├─ migrations/add_referral_system.sql
├─ app/models/referral.py
├─ app/schemas/referral.py
├─ app/routes/referral.py
└─ tests/test_referral.py

frontend/
├─ src/components/ReferralModal.tsx
└─ src/pages/ReferralDashboard.tsx
```

---

**MVP Referral System está pronto para integração! 🚀**

Tempo estimado de integração com código existente: **2-3 dias**
