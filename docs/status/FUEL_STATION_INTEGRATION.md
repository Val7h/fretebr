# 🚀 Fuel Station Referral System - MVP

**Status:** ✅ Pronto para Integração  
**Modelo:** Growth Hacking via Postos de Combustível  
**ROI Esperado:** +60% motoristas via postos (3-6 meses)  

---

## 📊 O Modelo de Negócio

```
DONO DE POSTO / FRENTISTA
        │
        ├─→ Registra no sistema FreteBR
        ├─→ Recebe código único (ex: SHELL-SP-123-ABC)
        ├─→ Indica motoristas IRL (na bomba)
        │
        └─→ GANHOS:
            ├─ R$ 10 por motorista que se cadastra com seu código
            ├─ R$ 10 por frete que o motorista completa
            └─ Paga via Pix


MOTORISTA
        │
        ├─→ Vê código do frentista no posto
        ├─→ Se cadastra com código
        │
        └─→ BENEFÍCIOS:
            ├─ 3% desconto no combustível (válido 12 meses)
            ├─ Acesso normal à plataforma
            └─ Desconto aplicado automaticamente


FRETEBR (VOCÊ)
        │
        ├─→ Motoristas: Ganham novos usuários
        ├─→ Frentistas: Seu custo de aquisição
        │
        └─→ TRADE-OFF:
            ├─ Custo: R$ 10 por motorista + R$ 10 por frete
            ├─ Ganho: 1 motorista novo + ativação (completa fretes)
            └─ ROI: Positivo em ~3-5 fretes completados
```

---

## 🗄️ Tabelas Criadas

### `fuel_stations` (Postos de Combustível)
- Nome, CNPJ, endereço, cidade, estado
- Comissão percentual (configurável)
- Desconto para motorista (configurável)
- Status: pendente → ativo

### `fuel_station_attendants` (Frentistas)
- Nome, email, telefone
- Chave Pix para saques
- Vinculado a um posto

### `fuel_referral_codes` (Códigos Únicos)
- Formato: `SHELL-SP-123-ABC`
- Um código por frentista
- Status: ativo/inativo

### `fuel_station_referrals` (Indicações)
- Rastreia: frentista → motorista
- Status: pendente, ativo, pago
- Comissão: R$ 10 por indicação

### `fuel_discounts` (Descontos Motorista)
- 3% desconto no combustível
- Válido por 12 meses
- Vinculado ao código que originou

### `fuel_attendant_withdrawals` (Saques)
- Rastreia saques do frentista
- Status: pendente → processando → concluído
- Mínimo: R$ 10

---

## 🔌 Endpoints Criados

### **REGISTRAR NOVO POSTO**
```bash
POST /api/fuel-stations/register
{
  "nome": "Shell São Paulo",
  "cnpj": "00000000000191",
  "endereco": "Rua X, 123",
  "cidade": "São Paulo",
  "estado": "SP",
  "telefone": "(11) 9999-9999",
  "email": "gerente@shell.com.br",
  "dono_nome": "João Silva",
  "dono_email": "joao@shell.com.br"
}

Response:
{
  "id": "uuid",
  "nome": "Shell São Paulo",
  "status": "pendente",
  "desconto_motorista": 3.0,
  "comissao_percentual": 0.50
}
```

### **REGISTRAR FRENTISTA + GERAR CÓDIGO**
```bash
POST /api/fuel-stations/{station_id}/attendants
{
  "nome": "Maria das Bombas",
  "email": "maria@email.com",
  "telefone": "(11) 98888-8888",
  "pix_key": "maria@banco.com"
}

Response:
{
  "id": "uuid",
  "codigo": "SHELL-SP-456-XYZ",
  "descricao": "Código de Maria - Shell SP",
  "status": "ativo"
}
```

### **VALIDAR CÓDIGO (NO SIGNUP)**
```bash
GET /api/fuel-stations/codes/SHELL-SP-456-XYZ

Response:
{
  "codigo": "SHELL-SP-456-XYZ",
  "station_name": "Shell São Paulo",
  "desconto_percentual": 3.0,
  "comissao_frentista": 0.50
}
```

### **VER GANHOS DO FRENTISTA**
```bash
GET /api/fuel-stations/{station_id}/attendants/{attendant_id}/earnings

Response:
{
  "total_earned": 450.00,  // 45 fretes × R$ 10
  "referrals_completed": 45,
  "referrals_pending": 12,
  "referrals_total": 57,
  "recent_referrals": [...]
}
```

### **FRENTISTA SOLICITA SAQUE**
```bash
POST /api/fuel-stations/{station_id}/attendants/{attendant_id}/withdraw
{
  "amount": 450.00
}

Response:
{
  "id": "uuid",
  "amount": 450.00,
  "status": "pendente",
  "pix_key_used": "maria@banco.com"
}
```

---

## 🔗 Integração com Signup

**Arquivo:** `frontend/src/pages/SignupPage.tsx`

Modificar para aceitar `fuel_code` opcional:

```typescript
const [fuelCode, setFuelCode] = useState('');

const handleSignup = async () => {
  const data = {
    email,
    senha,
    nome_completo,
    tipo_usuario: 'motorista',
    fuel_referral_code: fuelCode,  // NOVO
  };
  
  const response = await apiService.signup(data);
  
  if (response && fuelCode) {
    // Motorista se cadastrou com código de posto
    // Desconto é criado automaticamente no backend
    console.log('Desconto de combustível ativado!');
  }
};
```

**Backend Signup Handler:**

```python
@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # ... validações existentes ...
    
    # Criar user
    user = User(...)
    db.add(user)
    db.flush()
    
    # NOVO: Se tem código de combustível, criar desconto
    if request.fuel_referral_code:
        code = db.query(FuelReferralCode).filter(
            FuelReferralCode.codigo == request.fuel_referral_code,
            FuelReferralCode.status == "ativo"
        ).first()
        
        if code:
            from app.routes.fuel_station import create_fuel_discount_for_motorista
            create_fuel_discount_for_motorista(user.id, code.id, db)
    
    db.commit()
    return UserResponse.from_orm(user)
```

---

## 🔗 Integração com Completion de Frete

**Arquivo:** `backend/app/api/matches.py`

Ao completar um frete:

```python
@router.put("/{match_id}/status")
def update_match_status(...):
    # ... lógica existente ...
    
    # Quando muda para "finalizado":
    if match_update.status == "finalizado":
        # Calcular comissão referral (já feito)
        frete_comissao = ...
        calculate_and_apply_referral_commission(...)
        
        # NOVO: Aplicar comissão do frentista
        from app.routes.fuel_station import apply_fuel_station_commission
        apply_fuel_station_commission(
            motorista_id=match.frete.motorista_id,
            valor_frete=match.frete.valor_frete,
            db=db
        )
    
    return updated_match
```

---

## 💰 Exemplos de ROI

### **Cenário: 1 Frentista Trabalhando 30 Dias**

```
Mês 1:
├─ Motoristas indicados: 15
├─ Comissão indicação: 15 × R$ 10 = R$ 150
├─ Fretes completados: 45 (3 por motorista)
├─ Comissão fretes: 45 × R$ 10 = R$ 450
└─ Total frentista: R$ 600

Mês 2-3:
├─ Ativação: 70% dos motoristas continuam usando
├─ Novos motoristas: +20
├─ Fretes completados: 100+
└─ Total acumulado: R$ 1.500+ por frentista

Seu custo:
├─ 15 motoristas × R$ 10 = R$ 150 (indicação)
├─ 45 fretes × R$ 10 = R$ 450 (comissão)
├─ Desconto combustível: ~R$ 45 (3% de ~R$ 1.500)
└─ Custo total: ~R$ 645

ROI:
├─ Motoristas novos: 15 ativos
├─ Fretes: 45 completados (~R$ 45.000 em GMV)
├─ Custo por motorista: R$ 43
└─ Break-even: ~3-4 fretes por motorista
```

---

## 🚀 Plano de Rollout

### **Fase 1: MVP (Primeira Semana)**
- [ ] Deploy backend (fuel_station routes)
- [ ] Integração com signup (fuel_code)
- [ ] Integração com match completion
- [ ] Dashboard simples de ganhos (frentista)

### **Fase 2: Onboarding (Semana 2)**
- [ ] Criar landing page para postos
- [ ] Email template de boas-vindas
- [ ] Dashboard para donocompletar
- [ ] Analytics: qual posto/frentista mais contribui

### **Fase 3: Scaling (Semana 3+)**
- [ ] Abordagem ativa de grandes redes de postos
- [ ] Negociação de descontos escalonados
- [ ] Pagamento automático via Mercado Pago
- [ ] App mobile com código QR para frentistas

---

## 📊 Previsões (1 Ano)

```
100 Postos × 2 Frentistas = 200 Frentistas
200 Frentistas × 20 motoristas/mês = 4.000 novos motoristas
4.000 motoristas × 50 fretes/ano = 200.000 fretes

Seu Custo:
├─ Indicações: 4.000 × R$ 10 = R$ 40.000
├─ Comissão fretes: 200.000 × R$ 10 = R$ 2.000.000
├─ Desconto combustível: ~R$ 100.000
└─ Total: ~R$ 2.140.000

Seu Ganho (10% takerate):
├─ 200.000 fretes × R$ 1.000 avg = R$ 200.000.000 GMV
├─ 10% takerate = R$ 20.000.000
└─ Lucro: R$ 20.000.000 - R$ 2.140.000 = R$ 17.860.000

CAC via Postos: R$ 535 (por motorista ativo)
LTV: ~R$ 10.000 (motorista completa 10 fretes/ano)
LTV/CAC: ~18.7x ✅ EXCELENTE
```

---

## ⚠️ Considerações

### **Regulatória**
- Verificar se precisa licença para operar programa de referência
- LGPD: motorista autoriza compartilhamento de dados com posto?

### **Técnica**
- Desconto combustível: como integrar com POS real?
  - Opção A: Combustível pré-pago (FreteBR compra, motorista usa)
  - Opção B: Parceria com rede de postos (Shell, Petrobrás)
  - Opção C: Cashback via Pix (desconto é crédito no app)

### **Operacional**
- Suporte para frentistas (não são tech-savvy)
- Pagamento confiável (Pix automático)
- Limite de saques (fraude?)

---

## 🎯 Success Metrics

Acompanhar em Dashboard:
- Motoristas cadastrados via posto
- Taxa de ativação (% que completa ≥1 frete)
- Fretes por motorista (via posto)
- Custo de aquisição médio
- Tempo para break-even
- Ganhos por frentista/posto

---

## 💡 Ideias Fase 2+

1. **Combustível como moeda**
   - Motorista ganha litros ao completar fretes
   - Usa litros em qualquer posto parceiro

2. **Programa de Loyalty**
   - Frentista ganha bonus se ativa 10+ motoristas
   - Motorista ganha bônus se completa 50 fretes

3. **Integração com Banco**
   - Frentista ganha "conta" FreteBR
   - Saldo visível em tempo real
   - Saque automático diário via Pix

4. **White Label**
   - Postos podem rebrandar programa
   - Boost de integração com seu serviço de delivery/logística

---

**Este MVP de Fuel Station é uma máquina de crescimento! 🚀**

Implementação estimada: **2-3 semanas**
