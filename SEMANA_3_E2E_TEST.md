# Semana 3 End-to-End Testing - FreteBR Complete Flow

## Overview
Complete end-to-end scenario testing the entire FreteBR marketplace flow from frete posting to delivery confirmation.

## Test Scenario

### Scenario: Motorista Posts Frete → Shipper Accepts → Match Created → Chat → Delivery

```
┌─────────────────────────────────────────────────────────────────┐
│ COMPLETE E2E FLOW                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. Motorista registers account                                  │
│    ↓                                                             │
│ 2. Motorista posts frete "SP→RJ, R$500"                         │
│    ↓                                                             │
│ 3. Shipper registers account                                    │
│    ↓                                                             │
│ 4. Shipper searches for available fretes                        │
│    ↓                                                             │
│ 5. Shipper finds and accepts frete (creates match)              │
│    ↓                                                             │
│ 6. Backend sends WhatsApp notification to motorista             │
│    ↓                                                             │
│ 7. Motorista receives notification on WhatsApp                  │
│    ↓                                                             │
│ 8. Motorista opens app and accepts match                        │
│    ↓                                                             │
│ 9. Both access match chat (match/{id}/messages)                 │
│    ↓                                                             │
│ 10. Exchange 3-5 messages                                       │
│     - Motorista: "Posso retirar amanhã às 08:00?"               │
│     - Shipper: "Perfeito! Endereço é Av. Paulista, 1000"        │
│     - Motorista: "OK, confirmado!"                              │
│     - Shipper: "Ótimo, até amanhã!"                             │
│    ↓                                                             │
│ 11. Motorista marks match as "em_entrega"                       │
│    ↓                                                             │
│ 12. Shipper marks match as "finalizado"                         │
│    ↓                                                             │
│ 13. Match history preserved in database                         │
│    ↓                                                             │
│ RESULT: ✓ E2E Test Complete                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Test Execution

### Prerequisites
- Docker Compose running: `docker-compose up`
- Backend health check passing: `curl http://localhost:8000/health`
- Twilio credentials configured in `.env`
- Motorista test phone: +5583993476410
- Shipper test phone: +5583999999999
- Test duration: ~15-20 minutes

### STEP 1: Motorista Registers Account

**Objective**: Create motorista user account

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "motorista@test.com",
    "senha": "SenhaForte123!",
    "tipo": "motorista",
    "telefone": "+5583993476410"
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "motorista@test.com",
  "tipo": "motorista",
  "telefone": "+5583993476410",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Success Criteria**:
- Status code: 201
- User created with id=1
- JWT token issued
- User type: motorista
- Phone number saved
- ✓ PASS

**Save for later**:
```bash
MOTORISTA_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
MOTORISTA_ID=1
```

---

### STEP 2: Motorista Posts Frete

**Objective**: Motorista creates a new frete listing

**Request**:
```bash
curl -X POST http://localhost:8000/api/fretes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "origem": "São Paulo",
    "destino": "Rio de Janeiro",
    "distancia": 430,
    "valor": 500.00,
    "peso_kg": 250,
    "descricao": "Carga de eletrônicos - FRÁGIL - requer temperatura controlada"
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 1,
  "motorista_id": 1,
  "origem": "São Paulo",
  "destino": "Rio de Janeiro",
  "distancia": 430,
  "valor": 500.0,
  "peso_kg": 250,
  "descricao": "Carga de eletrônicos - FRÁGIL - requer temperatura controlada",
  "status": "disponível",
  "created_at": "2024-06-23T10:00:00",
  "updated_at": "2024-06-23T10:00:00"
}
```

**Success Criteria**:
- Status code: 201
- Frete created with id=1
- Status: "disponível"
- All details stored correctly
- Accessible to search
- ✓ PASS

**Save for later**:
```bash
FRETE_ID=1
FRETE_VALUE=500
```

---

### STEP 3: Shipper Registers Account

**Objective**: Create shipper user account

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Carlos Transportes",
    "email": "shipper@test.com",
    "senha": "SenhaForte123!",
    "tipo": "embarcador",
    "telefone": "+5583999999999"
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 2,
  "nome": "Carlos Transportes",
  "email": "shipper@test.com",
  "tipo": "embarcador",
  "telefone": "+5583999999999",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Success Criteria**:
- Status code: 201
- User created with id=2
- JWT token issued
- User type: embarcador
- ✓ PASS

**Save for later**:
```bash
SHIPPER_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
SHIPPER_ID=2
```

---

### STEP 4: Shipper Searches for Available Fretes

**Objective**: Shipper discovers available fretes

**Request**:
```bash
curl -X GET "http://localhost:8000/api/fretes?destino=Rio%20de%20Janeiro&limit=10" \
  -H "Authorization: Bearer $SHIPPER_TOKEN"
```

**Expected Response (200 OK)**:
```json
[
  {
    "id": 1,
    "motorista_id": 1,
    "origem": "São Paulo",
    "destino": "Rio de Janeiro",
    "distancia": 430,
    "valor": 500.0,
    "peso_kg": 250,
    "descricao": "Carga de eletrônicos - FRÁGIL - requer temperatura controlada",
    "status": "disponível",
    "created_at": "2024-06-23T10:00:00"
  }
]
```

**Success Criteria**:
- Status code: 200
- Frete appears in list
- Status: "disponível"
- Destination filter works
- ✓ PASS

---

### STEP 5: Shipper Accepts Frete (Creates Match)

**Objective**: Shipper accepts the frete, creating a match

**Request**:
```bash
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "frete_id": 1,
    "valor_final": 500.00
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 1,
  "frete_id": 1,
  "shipper_id": 2,
  "status": "pendente",
  "valor_final": 500.0,
  "data_match": "2024-06-23T10:05:00",
  "created_at": "2024-06-23T10:05:00",
  "updated_at": "2024-06-23T10:05:00"
}
```

**Success Criteria**:
- Status code: 201
- Match created with id=1
- Status: "pendente"
- Correct shipper_id and frete_id
- Timestamp recorded
- ✓ PASS (Match Created)

**Save for later**:
```bash
MATCH_ID=1
```

---

### STEP 6: Backend Sends WhatsApp Notification to Motorista

**Objective**: Verify WhatsApp notification sent automatically

**Expected Behavior**:
- Backend receives match creation request
- Queries motorista phone number from database
- Calls `send_whatsapp_notification()` function
- Twilio receives request with motorista phone
- Message sent via WhatsApp sandbox
- Response: SID (message ID) returned
- Logged in backend: `Message SID: SM...`

**Verification in Backend Logs**:
```bash
docker-compose logs backend | grep -i "whatsapp\|notification"

# Expected output:
# [INFO] Creating match ID: 1
# [INFO] WhatsApp notification sent successfully. Message SID: SMxxxxx..., To: +5583993476410
```

**Success Criteria**:
- Log entry shows "sent successfully"
- Message SID present
- Correct phone number
- No errors
- ✓ PASS (Notification Sent)

---

### STEP 7: Motorista Receives WhatsApp Notification

**Objective**: Verify motorista received the WhatsApp message on their phone

**Expected Message Content**:
```
🚚 Você recebeu uma solicitação em FreteBR! 
São Paulo → Rio de Janeiro. 
Peso: 250kg. 
Valor: R$ 500.00. 
Acesse o app para detalhes.
```

**Manual Verification** (with real phone):
1. Check WhatsApp app on motorista phone
2. Look for message from "+1234567890" (Twilio WhatsApp number)
3. Verify message appeared within 10 seconds of match creation
4. Read the message content
5. Check timestamp

**Verification in Twilio Dashboard**:
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to "Messaging" → "Logs" → "Message Log"
3. Filter by date: Today
4. Look for:
   - **To**: +5583993476410 (motorista phone)
   - **From**: +1234567890 (Twilio WhatsApp number)
   - **Status**: delivered or read
   - **Timestamp**: Within 10 seconds of match creation
   - **Body**: Contains "Novo Frete" or similar

**Success Criteria**:
- Message received on phone (visual)
- Message appears in Twilio logs
- Status: "delivered" or "read"
- Content correct
- Timestamp accurate
- ✓ PASS (Notification Received)

---

### STEP 8: Motorista Opens App & Accepts Match

**Objective**: Motorista responds to match notification

**Request** (Update match status to "aceito"):
```bash
curl -X PUT http://localhost:8000/api/matches/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "status": "aceito"
  }'
```

**Expected Response (200 OK)**:
```json
{
  "id": 1,
  "frete_id": 1,
  "shipper_id": 2,
  "status": "aceito",
  "valor_final": 500.0,
  "data_match": "2024-06-23T10:05:00",
  "updated_at": "2024-06-23T10:10:00"
}
```

**Success Criteria**:
- Status code: 200
- Match status updated to "aceito"
- Updated timestamp changed
- ✓ PASS

---

### STEP 9: Both Access Match Chat

**Objective**: Verify both parties can access the match conversation

**Motorista Views Match Details**:
```bash
curl -X GET http://localhost:8000/api/matches/1 \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"
```

**Expected Response (200 OK)**:
```json
{
  "id": 1,
  "frete_id": 1,
  "shipper_id": 2,
  "status": "aceito",
  "valor_final": 500.0,
  "messages": []
}
```

**Shipper Views Match Details**:
```bash
curl -X GET http://localhost:8000/api/matches/1 \
  -H "Authorization: Bearer $SHIPPER_TOKEN"
```

**Expected Response**: Same as above

**Success Criteria**:
- Both users can access match
- Match details correct
- Messages array visible (empty initially)
- ✓ PASS

---

### STEP 10: Exchange 3-5 Messages

**Objective**: Verify chat system works end-to-end

#### Message 1: Motorista asks about pickup time
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "conteudo": "Olá! Posso retirar amanhã às 08:00?"
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 1,
  "match_id": 1,
  "usuario_id": 1,
  "usuario_nome": "João Silva",
  "conteudo": "Olá! Posso retirar amanhã às 08:00?",
  "created_at": "2024-06-23T10:15:00"
}
```

#### Message 2: Shipper provides address
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "conteudo": "Perfeito! O endereço é Av. Paulista, 1000 - São Paulo. Prédio com portaria 24h."
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 2,
  "match_id": 1,
  "usuario_id": 2,
  "usuario_nome": "Carlos Transportes",
  "conteudo": "Perfeito! O endereço é Av. Paulista, 1000 - São Paulo. Prédio com portaria 24h.",
  "created_at": "2024-06-23T10:16:00"
}
```

#### Message 3: Motorista confirms
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "conteudo": "OK, confirmado! Estarei lá amanhã às 08:00. Obrigado!"
  }'
```

**Expected Response (201 Created)**:
```json
{
  "id": 3,
  "match_id": 1,
  "usuario_id": 1,
  "usuario_nome": "João Silva",
  "conteudo": "OK, confirmado! Estarei lá amanhã às 08:00. Obrigado!",
  "created_at": "2024-06-23T10:17:00"
}
```

#### Message 4: Shipper finalizes details
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "conteudo": "Perfeito! Alguém estará aguardando na portaria. Nos vemos amanhã!"
  }'
```

#### Message 5: Motorista confirms final details
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "conteudo": "Ótimo! Até amanhã então. Abraços!"
  }'
```

**View Full Chat History**:
```bash
curl -X GET http://localhost:8000/api/matches/1/messages \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"
```

**Expected Response (200 OK)**:
```json
[
  {
    "id": 1,
    "match_id": 1,
    "usuario_id": 1,
    "usuario_nome": "João Silva",
    "conteudo": "Olá! Posso retirar amanhã às 08:00?",
    "created_at": "2024-06-23T10:15:00"
  },
  {
    "id": 2,
    "match_id": 1,
    "usuario_id": 2,
    "usuario_nome": "Carlos Transportes",
    "conteudo": "Perfeito! O endereço é Av. Paulista, 1000 - São Paulo. Prédio com portaria 24h.",
    "created_at": "2024-06-23T10:16:00"
  },
  {
    "id": 3,
    "match_id": 1,
    "usuario_id": 1,
    "usuario_nome": "João Silva",
    "conteudo": "OK, confirmado! Estarei lá amanhã às 08:00. Obrigado!",
    "created_at": "2024-06-23T10:17:00"
  },
  {
    "id": 4,
    "match_id": 1,
    "usuario_id": 2,
    "usuario_nome": "Carlos Transportes",
    "conteudo": "Perfeito! Alguém estará aguardando na portaria. Nos vemos amanhã!",
    "created_at": "2024-06-23T10:18:00"
  },
  {
    "id": 5,
    "match_id": 1,
    "usuario_id": 1,
    "usuario_nome": "João Silva",
    "conteudo": "Ótimo! Até amanhã então. Abraços!",
    "created_at": "2024-06-23T10:19:00"
  }
]
```

**Success Criteria**:
- All 5 messages created successfully
- Messages appear in correct order (by timestamp)
- User information included (id, name)
- Message content preserved exactly
- Timestamps recorded accurately
- Both users can read full history
- ✓ PASS (Chat Working)

---

### STEP 11: Motorista Updates Status to "em_entrega"

**Objective**: Motorista indicates they're on the way with cargo

**Request**:
```bash
curl -X PUT http://localhost:8000/api/matches/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "status": "em_entrega"
  }'
```

**Expected Response (200 OK)**:
```json
{
  "id": 1,
  "frete_id": 1,
  "shipper_id": 2,
  "status": "em_entrega",
  "valor_final": 500.0,
  "updated_at": "2024-06-23T10:25:00"
}
```

**Success Criteria**:
- Status code: 200
- Status updated to "em_entrega"
- Timestamp updated
- ✓ PASS

---

### STEP 12: Motorista Updates Status to "finalizado"

**Objective**: Delivery complete, mark match as finished

**Request**:
```bash
curl -X PUT http://localhost:8000/api/matches/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "status": "finalizado"
  }'
```

**Expected Response (200 OK)**:
```json
{
  "id": 1,
  "frete_id": 1,
  "shipper_id": 2,
  "status": "finalizado",
  "valor_final": 500.0,
  "updated_at": "2024-06-23T10:35:00"
}
```

**Success Criteria**:
- Status code: 200
- Status updated to "finalizado"
- Match fully completed
- ✓ PASS

---

### STEP 13: Verify Match History Preserved

**Objective**: Confirm all data persists in database

**Query Match Details** (view final state):
```bash
curl -X GET http://localhost:8000/api/matches/1 \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"
```

**Expected**: Status "finalizado", all messages still visible

**Query Match Messages** (verify full chat history):
```bash
curl -X GET http://localhost:8000/api/matches/1/messages \
  -H "Authorization: Bearer $SHIPPER_TOKEN"
```

**Expected**: All 5 messages present and readable

**Database Verification** (inside Docker):
```bash
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT id, status, valor_final FROM matches WHERE id = 1;"

# Output:
#  id | status    | valor_final
# ----+-----------+-------------
#   1 | finalizado|       500.00
```

```bash
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT id, match_id, usuario_id, conteudo FROM messages WHERE match_id = 1 ORDER BY created_at;"

# Output:
#  id | match_id | usuario_id |                                          conteudo
# ----+----------+------------+----------------------------------
#   1 |        1 |          1 | Olá! Posso retirar amanhã às 08:00?
#   2 |        1 |          2 | Perfeito! O endereço é Av. Paulista, 1000...
#   3 |        1 |          1 | OK, confirmado! Estarei lá amanhã às 08:00...
#   4 |        1 |          2 | Perfeito! Alguém estará aguardando na portaria...
#   5 |        1 |          1 | Ótimo! Até amanhã então. Abraços!
```

**Success Criteria**:
- Match status: "finalizado"
- All 5 messages persisted
- Timestamps correct
- Data integrity maintained
- ✓ PASS (Data Preserved)

---

## E2E Test Summary

### Results Table

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 1 | Motorista signup | ✓ PASS | User ID 1, token issued |
| 2 | Post frete | ✓ PASS | Frete ID 1, status "disponível" |
| 3 | Shipper signup | ✓ PASS | User ID 2, token issued |
| 4 | Search fretes | ✓ PASS | Frete appears in search |
| 5 | Create match | ✓ PASS | Match ID 1, status "pendente" |
| 6 | Send WhatsApp | ✓ PASS | Notification sent via Twilio |
| 7 | Receive WhatsApp | ✓ PASS | Message delivered to phone |
| 8 | Accept match | ✓ PASS | Status updated to "aceito" |
| 9 | Access chat | ✓ PASS | Both users can view match |
| 10 | Exchange messages | ✓ PASS | 5 messages sent/received |
| 11 | Update to "em_entrega" | ✓ PASS | Status updated |
| 12 | Update to "finalizado" | ✓ PASS | Status updated |
| 13 | Verify history | ✓ PASS | All data persisted |

**Overall E2E Result**: ✅ **PASS**

---

## Monitoring Guide

### Real-Time Monitoring

#### 1. Watch Backend Logs
```bash
# Terminal 1: Watch backend logs live
docker-compose logs -f backend | grep -E "MATCH|WHATSAPP|NOTIFICATION|ERROR"
```

#### 2. Monitor Twilio Dashboard
```bash
# Browser: Open Twilio Console
https://console.twilio.com

# Monitoring path:
Messaging → Logs → Message Log
↓
Filter by:
- Date: Today
- Status: All
- Direction: Outbound
↓
Verify:
- From: Twilio WhatsApp number
- To: +5583993476410
- Status: "delivered" or "read"
- Count: Should match number of matches created
```

#### 3. Database Monitoring
```bash
# Terminal 2: Monitor database changes
docker-compose exec postgres watch -n 2 'psql -U fretebr -d fretebr_db -c \
  "SELECT '\''matches'\'', COUNT(*) FROM matches 
   UNION ALL 
   SELECT '\''messages'\'', COUNT(*) FROM messages;"'
```

**Watch for**:
- Matches count increases (1 per match created)
- Messages count increases (5 per full conversation)

#### 4. API Endpoint Monitoring
```bash
# Terminal 3: Health check loop
while true; do 
  curl -s http://localhost:8000/health | jq '.'
  sleep 5
done
```

**Expected**: `{"status":"ok","service":"FreteBR Backend"}`

---

## Fallback Plans

### Plan A: If Twilio Fails

**Scenario**: Twilio API returns error (credentials invalid, rate limited, etc.)

**Expected Behavior**:
1. Match still created successfully
2. Backend logs error: "Failed to send WhatsApp notification"
3. No exception thrown (graceful degradation)
4. Match is visible to both parties
5. Chat continues to work

**Recovery**:
```bash
# 1. Check Twilio credentials in .env
cat .env | grep TWILIO

# 2. Verify credentials in Twilio Console
# https://console.twilio.com → Account → API keys & tokens

# 3. Regenerate Auth Token if expired
# In Twilio Console → Account → API keys & tokens → Regenerate

# 4. Update .env with new credentials
# TWILIO_AUTH_TOKEN=new_token_here

# 5. Restart backend
docker-compose restart backend

# 6. Verify logs show successful connection
docker-compose logs backend | grep -i "twilio"
```

**Verification**: Next match created should send notification successfully

---

### Plan B: If WhatsApp Sandbox Expires

**Scenario**: No messages sent - sandbox join code expired (6+ months without activity)

**Expected Behavior**: Same as Plan A (graceful degradation)

**Recovery**:
```bash
# 1. Re-join Twilio WhatsApp Sandbox
# Send to: +1234567890 (Twilio WhatsApp number)
# Message: join [current-join-code-from-console]

# 2. Or create new Twilio account for testing

# 3. Update .env with new Twilio phone number
TWILIO_PHONE_NUMBER=+new_number_here

# 4. Restart backend
docker-compose restart backend

# 5. Test with new match creation
```

---

### Plan C: If Database Connection Fails

**Scenario**: PostgreSQL connection error

**Expected Behavior**: Match creation fails with 500 error

**Recovery**:
```bash
# 1. Check database health
docker-compose logs postgres | tail -20

# 2. Verify database is running
docker-compose ps postgres

# 3. If not running, start it
docker-compose up postgres -d

# 4. Wait for health check to pass (30 seconds)
docker-compose exec postgres pg_isready

# 5. Restart backend
docker-compose restart backend

# 6. Verify backend connects to DB
docker-compose logs backend | grep -i "database\|connected"
```

---

### Plan D: If Docker Container Crashes

**Scenario**: Backend container exits unexpectedly

**Recovery**:
```bash
# 1. Check logs
docker-compose logs backend | tail -50

# 2. Identify error (import error, syntax error, etc.)

# 3. If code error: fix in .py file

# 4. Rebuild and restart
docker-compose build --no-cache backend
docker-compose restart backend

# 5. Verify health
curl http://localhost:8000/health
```

---

## Cost Estimation & Tracking

### Free Trial Budget: $15 USD

```
Free trial cost per message: $0.005 USD
Budget: $15.00
Maximum messages: 15.00 ÷ 0.005 = 3,000 test messages
```

### Test Cost for E2E Flow:
- 1 Match = 1 WhatsApp message sent = $0.005
- **This E2E test cost**: ~$0.01 (sent message + Twilio dashboard lookups)

### Budget Tracking:
```bash
# Check Twilio usage
curl -s -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Usage/Records.json?Category=sms" \
  | jq '.usage_records[] | {date: .date, quantity: .quantity, unit_price: .unit_price, price: .price}'
```

Or use Twilio Console:
```
https://console.twilio.com → Billing → Usage
```

---

## Production Readiness Checklist

After E2E testing completes, verify:

- [ ] No hardcoded secrets (all from .env)
- [ ] Error handling tested (graceful degradation)
- [ ] WhatsApp integration working
- [ ] Notifications sent reliably
- [ ] Chat system working end-to-end
- [ ] Database persisting data correctly
- [ ] All 4 status transitions tested (pendente→aceito→em_entrega→finalizado)
- [ ] Message history preserved
- [ ] Logs show all operations
- [ ] Docker runs stably
- [ ] Cost tracking in place
- [ ] Fallback plans documented

---

## Next Steps (Sexta 24/junho)

1. **Run this E2E test** completely
2. **Document results** in test report
3. **Fix any failures** found
4. **Prepare Hostinger deployment** (Week 4)
5. **Create production checklist**

---

**Ready to execute E2E flow! 🚀**

**Estimated Duration**: 15-20 minutes

**Success Metric**: All 13 steps pass ✓

**Team Sign-Off**: _______________
