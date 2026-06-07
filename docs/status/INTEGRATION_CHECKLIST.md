# ⚡ Integração Rápida - Referral System

**Tempo estimado:** 2-3 horas  
**Dificuldade:** Média  

---

## 📋 Step-by-Step

### **PASSO 1: Database (10 min)**

```bash
# 1. Copiar SQL para seu cliente PostgreSQL (DBeaver / pgAdmin)
cat backend/migrations/add_referral_system.sql

# 2. Executar no seu database FreteBR
# (Copiar conteúdo e colar no SQL Editor)

# 3. Validar tabelas criadas
SELECT * FROM referrals;
SELECT * FROM referral_withdrawals;
```

✅ **Checklist:**
- [ ] Tabela `referrals` criada
- [ ] Tabela `referral_withdrawals` criada
- [ ] Coluna `referrer_motorista_id` adicionada em `matches`
- [ ] Índices criados

---

### **PASSO 2: Backend - Models (5 min)**

```bash
# 1. Copiar arquivo
cp backend/app/models/referral.py ./seu-projeto/app/models/

# 2. Adicionar em app/models/__init__.py
# Adicionar estas linhas:
from .referral import Referral, ReferralWithdrawal
```

**Arquivo:** `app/models/referral.py`

✅ **Checklist:**
- [ ] Arquivo copiado
- [ ] Importado em `__init__.py`
- [ ] Sem erros de import

---

### **PASSO 3: Backend - Schemas (5 min)**

```bash
# 1. Copiar arquivo
cp backend/app/schemas/referral.py ./seu-projeto/app/schemas/

# 2. Adicionar em app/schemas/__init__.py se usar
# (Opcional, mas recomendado)
```

**Arquivo:** `app/schemas/referral.py`

✅ **Checklist:**
- [ ] Arquivo copiado
- [ ] Sem erros de import

---

### **PASSO 4: Backend - Routes (15 min)**

```bash
# 1. Copiar arquivo
cp backend/app/routes/referral.py ./seu-projeto/app/routes/

# 2. Editar app/main.py
```

**Em `app/main.py`, adicione:**

```python
# No topo (imports):
from app.routes.referral import router as referral_router

# Após a linha de imports de modelos:
from app.models import User, Frete, Match, Message, Transaction, Referral, ReferralWithdrawal

# Na seção de include_router (após os routers existentes):
app.include_router(referral_router)
```

✅ **Checklist:**
- [ ] Router importado
- [ ] Modelos importados em main.py
- [ ] Router incluído
- [ ] Sem erros ao iniciar API (`uvicorn app.main:app --reload`)

---

### **PASSO 5: Backend - Integração com Matches (15 min)**

**Arquivo:** `app/routes/matches.py` ou onde completa frete

Encontre a função que marca match como concluído. Deve ser algo como:

```python
@router.put("/matches/{match_id}/complete")
async def complete_match(match_id: UUID, db: Session = Depends(get_db)):
    # ... código existente ...
    
    match.status = "concluido"
    db.commit()
    
    # ADICIONE ISTO AQUI ⬇️
```

**Adicione:**

```python
# No topo do arquivo:
from app.routes.referral import calculate_and_apply_referral_commission

# No final da função (após commit):
# Calcular comissão de referência (se existir)
if match.frete:
    # Calcular comissão do frete (seu % da plataforma)
    frete_comissao = Decimal(str(match.frete.valor_frete)) * Decimal("0.10")  # 10%
    calculate_and_apply_referral_commission(match.id, frete_comissao, db)
```

**Versão Completa:**
```python
@router.put("/matches/{match_id}/complete")
async def complete_match(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # ... validações existentes ...
    
    match.status = "concluido"
    match.completed_at = datetime.utcnow()
    db.commit()
    
    # ⭐ NOVO: Calcular comissão de referência
    if match.frete:
        frete_comissao = Decimal(str(match.frete.valor_frete)) * Decimal("0.10")
        calculate_and_apply_referral_commission(match.id, frete_comissao, db)
    
    return MatchResponse.from_orm(match)
```

✅ **Checklist:**
- [ ] Função encontrada
- [ ] Import adicionado
- [ ] Código inserido antes/depois correto
- [ ] Sem erros ao reiniciar API

---

### **PASSO 6: Frontend - Componentes (10 min)**

```bash
# 1. Copiar Modal
cp frontend/src/components/ReferralModal.tsx ./seu-projeto/src/components/

# 2. Copiar Dashboard
cp frontend/src/pages/ReferralDashboard.tsx ./seu-projeto/src/pages/
```

✅ **Checklist:**
- [ ] Ambos arquivos copiados
- [ ] Sem erros de import em seu projeto

---

### **PASSO 7: Frontend - Routing (5 min)**

**Arquivo:** `frontend/src/App.tsx` ou arquivo de rotas

Adicione a rota:

```tsx
import ReferralDashboard from './pages/ReferralDashboard';

// Em suas routes:
<Route path="/dashboard/referrals" element={<ReferralDashboard />} />
```

✅ **Checklist:**
- [ ] Rota adicionada
- [ ] Acesso via `/dashboard/referrals` funciona

---

### **PASSO 8: Frontend - Modal no Rejeitar Frete (10 min)**

**Arquivo:** Página onde motorista rejeita frete (provavelmente `FindFrete.tsx` ou similar)

Adicione na função de rejeição:

```tsx
import { ReferralModal } from '../components/ReferralModal';

// No estado do componente:
const [showReferralModal, setShowReferralModal] = useState(false);
const [selectedFreightId, setSelectedFreightId] = useState<string | null>(null);

// Na função que rejeita:
const handleRejectFreight = (freight: Frete) => {
  setSelectedFreightId(freight.id);
  setShowReferralModal(true);  // ⭐ NOVO
};

// Render (após seu botão de rejeição):
<ReferralModal
  isOpen={showReferralModal}
  onClose={() => setShowReferralModal(false)}
  freightId={selectedFreightId || ''}
  onSuccess={() => {
    setShowReferralModal(false);
    // Recarregar fretes se necessário
    fetchFreights();
  }}
/>
```

✅ **Checklist:**
- [ ] Modal renderiza ao rejeitar
- [ ] Busca de motorista funciona
- [ ] Indicação salva com sucesso

---

### **PASSO 9: Frontend - Link no Dashboard (5 min)**

**Arquivo:** Dashboard principal (página inicial após login)

Adicione um card/link:

```tsx
<Link to="/dashboard/referrals" className="card-link">
  <div className="card">
    <h3>💰 Meus Ganhos</h3>
    <p>Indique motoristas e ganhe comissão</p>
  </div>
</Link>
```

✅ **Checklist:**
- [ ] Link visível no dashboard
- [ ] Clicável e funciona

---

### **PASSO 10: Testes (20 min)**

```bash
# 1. Copiar testes
cp backend/tests/test_referral.py ./seu-projeto/tests/

# 2. Rodar testes
cd backend
pytest tests/test_referral.py -v

# 3. Validar todos passam
```

✅ **Checklist:**
- [ ] Todos 8+ testes passam
- [ ] Sem erros ou warnings

---

## 🧪 Teste Manual Completo

**Cenário: Motorista A indica Motorista B e ganha comissão**

### **1. Criar 2 motoristas no seu database**

```sql
INSERT INTO users (id, email, tipo_usuario, nome_completo) 
VALUES 
  ('motor-a', 'a@test.com', 'motorista', 'João'),
  ('motor-b', 'b@test.com', 'motorista', 'Maria');
```

### **2. Criar 1 frete**

```sql
INSERT INTO fretes (id, shipper_id, valor_frete, status) 
VALUES ('frete-1', 'shipper-id', 1000, 'disponivel');
```

### **3. Testar API - Indicação**

```bash
curl -X POST http://localhost:8000/api/referrals/indicate \
  -H "Authorization: Bearer {token_joao}" \
  -H "Content-Type: application/json" \
  -d '{
    "referred_motorista_id": "motor-b",
    "frete_id": "frete-1"
  }'

# Esperado: Status 201, referral criado
```

### **4. Testar API - Ver Ganhos**

```bash
curl http://localhost:8000/api/referrals/earnings \
  -H "Authorization: Bearer {token_joao}"

# Esperado: total_earned: 0, referrals_pending: 1
```

### **5. Simular Aceitação + Conclusão**

```sql
-- Motorista B aceita
INSERT INTO matches (id, frete_id, motorista_id, status) 
VALUES ('match-1', 'frete-1', 'motor-b', 'concluido');

-- Completar match (via API ou manual)
UPDATE matches SET status = 'concluido' WHERE id = 'match-1';
```

### **6. Verificar Comissão Aplicada**

```bash
# Ver ganhos novamente
curl http://localhost:8000/api/referrals/earnings \
  -H "Authorization: Bearer {token_joao}"

# Esperado: total_earned: 20.00, referrals_completed: 1
```

### **7. Testar Saque**

```bash
curl -X POST http://localhost:8000/api/referrals/withdraw \
  -H "Authorization: Bearer {token_joao}" \
  -H "Content-Type: application/json" \
  -d '{"amount": 20.00}'

# Esperado: Status 201, withdrawal criado
```

---

## ✅ Validation Checklist

```
[ ] Database
  [ ] Tabelas criadas
  [ ] Índices criados
  [ ] Dados de teste inseridos

[ ] Backend
  [ ] Models importados
  [ ] Router registrado
  [ ] Integration com matches working
  [ ] API endpoints respondendo

[ ] Frontend
  [ ] Componentes renderizando
  [ ] Modal abrindo ao rejeitar
  [ ] Dashboard carregando dados
  [ ] Rota acessível

[ ] Testes
  [ ] Testes unitários passando
  [ ] Teste manual completo OK
  [ ] Fluxo A→B funcionando

[ ] Deploy
  [ ] Sem erros ao iniciar
  [ ] Logs limpos
  [ ] Pronto para produção
```

---

## 🚨 Troubleshooting Rápido

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: No module named 'app.models.referral'` | Verificar se arquivo está na pasta correta |
| `Error executing query: duplicate key value violates unique constraint` | Migration já foi executada (ignorar) |
| `TypeError: calculate_and_apply_referral_commission() missing argument` | Verificar imports e chamada em matches.py |
| Modal não abre ao rejeitar | Verificar se ReferralModal está importado e `setShowReferralModal(true)` é chamado |
| `/api/referrals/earnings` retorna 403 | Verificar se motorista está autenticado com token válido |
| Dashboard referral em branco | Verificar console do navegador para erros de API |

---

## 📞 Próximos Passos

Após integração:
1. Testar com usuários em staging
2. Monitorar métricas (indicações/semana, taxa de conversão)
3. Ajustar % de comissão se necessário
4. Deploy em produção
5. Comunicar nova feature para motoristas

---

**Integração concluída! 🎉**

Tempo total estimado: **2-3 horas**
