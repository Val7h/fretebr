# Semana 3 Testing Checklist - FreteBR WhatsApp Integration

## Overview
This document outlines comprehensive testing for the WhatsApp notification system integrated with the FreteBR match creation flow.

## Testing Environment Setup

### Prerequisites
1. Twilio account with free trial ($15 USD)
2. WhatsApp sandbox configured
3. Test phone numbers registered:
   - Owner/Tester phone: Your phone number
   - Motorista test phone: WhatsApp-enabled number
4. Docker & Docker Compose installed
5. Backend running with Twilio credentials configured

### Start Testing Environment
```bash
cd /c/Users/Admin/fretebr

# Build images with no cache
docker-compose build --no-cache

# Start all services
docker-compose up

# In another terminal, verify backend health
curl http://localhost:8000/health

# Should output: {"status":"ok","service":"FreteBR Backend"}
```

## Test Matrix

### Test 1: Twilio Integration Verification
**Endpoint**: Internal health check  
**Goal**: Verify Twilio SDK is properly loaded

```bash
# Inside Docker container
docker-compose exec backend python -c "from twilio.rest import Client; print('✓ Twilio import OK')"

# Expected output: ✓ Twilio import OK
```

**Success Criteria**:
- No import errors
- Twilio SDK version 9.2.1 loaded
- No missing dependencies

---

### Test 2: POST /api/fretes → Create Frete (Motorista)
**Endpoint**: `POST /api/fretes`  
**Description**: Motorista posts a new frete  
**Expected Behavior**: Frete created successfully (no notification yet - owner is motorista)

#### Using curl:

```bash
# 1. Sign up as motorista
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva (Motorista)",
    "email": "motorista@test.com",
    "senha": "senha123",
    "tipo": "motorista",
    "telefone": "+5583993476410"
  }'

# Response (save the access_token):
# {
#   "id": 1,
#   "nome": "João Silva (Motorista)",
#   "email": "motorista@test.com",
#   "tipo": "motorista",
#   "access_token": "eyJ0eXAi..."
# }

MOTORISTA_TOKEN="eyJ0eXAi..."

# 2. Create a frete
curl -X POST http://localhost:8000/api/fretes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "origem": "São Paulo",
    "destino": "Rio de Janeiro",
    "distancia": 430,
    "valor": 500.00,
    "descricao": "Carga de eletrônicos - frágil"
  }'

# Response:
# {
#   "id": 1,
#   "motorista_id": 1,
#   "origem": "São Paulo",
#   "destino": "Rio de Janeiro",
#   "status": "disponível",
#   "valor": 500.0,
#   "created_at": "2024-06-22T10:00:00"
# }
```

**Success Criteria**:
- Frete created with status "disponível"
- ID generated correctly
- No errors or exceptions
- ✓ PASS

---

### Test 3: Sign Up as Shipper
**Endpoint**: `POST /api/auth/signup`  
**Description**: Create shipper user account  
**Expected Behavior**: Shipper account created with JWT token

```bash
# Sign up as shipper
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Carlos Shipping",
    "email": "shipper@test.com",
    "senha": "senha123",
    "tipo": "embarcador",
    "telefone": "+5583999999999"
  }'

# Response (save the access_token):
# {
#   "id": 2,
#   "nome": "Carlos Shipping",
#   "email": "shipper@test.com",
#   "tipo": "embarcador",
#   "access_token": "eyJ0eXAi..."
# }

SHIPPER_TOKEN="eyJ0eXAi..."
```

**Success Criteria**:
- User account created
- JWT token issued
- Correct user type (embarcador)
- ✓ PASS

---

### Test 4: GET /api/fretes → List Available Fretes
**Endpoint**: `GET /api/fretes`  
**Description**: Shipper searches for available fretes  
**Expected Behavior**: Returns list of available fretes

```bash
curl -X GET "http://localhost:8000/api/fretes?destino=Rio%20de%20Janeiro&limit=10" \
  -H "Authorization: Bearer $SHIPPER_TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "origem": "São Paulo",
#     "destino": "Rio de Janeiro",
#     "status": "disponível",
#     "valor": 500.0,
#     "motorista_id": 1
#   }
# ]
```

**Success Criteria**:
- Frete appears in list
- Status is "disponível"
- Motorista information present
- ✓ PASS

---

### Test 5: POST /api/matches → Create Match & Send WhatsApp
**Endpoint**: `POST /api/matches`  
**Description**: Shipper accepts frete, creating a match  
**Expected Behavior**: Match created + WhatsApp notification sent to motorista

```bash
# Create a match (shipper accepts frete)
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{
    "frete_id": 1,
    "valor_final": 500.00
  }'

# Response:
# {
#   "id": 1,
#   "frete_id": 1,
#   "shipper_id": 2,
#   "status": "pendente",
#   "valor_final": 500.0,
#   "data_match": "2024-06-22T10:05:00"
# }
```

**Expected WhatsApp Message** (sent to motorista):
```
🎉 Novo Frete Aceito!
Carlos Shipping quer fazer seu frete: SP → RJ (R$ 500,00)
ID do Match: 1
Status: Pendente
👉 Clique para aceitar: https://fretebr.app/match/1
```

**Success Criteria**:
- Match created with status "pendente"
- Match ID generated
- **WhatsApp notification sent to +5583993476410**
- Message contains frete details
- Message contains match link
- Motorista receives notification on WhatsApp
- ✓ PASS (if WhatsApp message received)

---

### Test 6: Verify WhatsApp Message in Twilio Dashboard
**Location**: [Twilio Console](https://console.twilio.com)  
**Path**: Messaging → Logs → Message Log

**Check**:
1. Open Twilio Console
2. Go to "Messaging" → "Logs" → "Message Log"
3. Look for recent messages
4. Verify:
   - From: Twilio WhatsApp number (+1234567890)
   - To: Motorista phone (+5583993476410)
   - Status: delivered / read
   - Body: Contains frete/match details
   - Timestamp: Recent (within last 5 minutes)

**Success Criteria**:
- Message appears in logs
- Status shows "delivered" (or "read" if already read)
- Content correct
- No errors
- ✓ PASS

---

### Test 7: POST /api/matches/{id}/messages → Send Chat Message
**Endpoint**: `POST /api/matches/{id}/messages`  
**Description**: Motorista and Shipper exchange messages in match  
**Expected Behavior**: Message saved + visible to both parties

```bash
# Motorista sends a message
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -d '{
    "conteudo": "Olá! Posso retirar amanhã às 08:00?"
  }'

# Response:
# {
#   "id": 1,
#   "match_id": 1,
#   "usuario_id": 1,
#   "conteudo": "Olá! Posso retirar amanhã às 08:00?",
#   "created_at": "2024-06-22T10:10:00"
# }
```

**Success Criteria**:
- Message created with correct content
- Associated with correct match
- Timestamp accurate
- ✓ PASS

---

### Test 8: GET /api/matches/{id}/messages → Get Chat History
**Endpoint**: `GET /api/matches/{id}/messages`  
**Description**: Retrieve full chat history for a match  
**Expected Behavior**: Returns ordered list of messages

```bash
curl -X GET http://localhost:8000/api/matches/1/messages \
  -H "Authorization: Bearer $SHIPPER_TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "match_id": 1,
#     "usuario_id": 1,
#     "usuario_nome": "João Silva",
#     "conteudo": "Olá! Posso retirar amanhã às 08:00?",
#     "created_at": "2024-06-22T10:10:00"
#   }
# ]
```

**Success Criteria**:
- Messages returned in order
- User information included
- Correct match_id
- All message content preserved
- ✓ PASS

---

### Test 9: GET /api/matches → List User's Matches
**Endpoint**: `GET /api/matches`  
**Description**: User views their active matches  
**Expected Behavior**: Returns list of matches for authenticated user

```bash
# As motorista
curl -X GET http://localhost:8000/api/matches \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "frete_id": 1,
#     "status": "pendente",
#     "valor_final": 500.0,
#     "shipper_name": "Carlos Shipping"
#   }
# ]
```

**Success Criteria**:
- Only user's matches returned
- Status visible
- Counterparty information included
- ✓ PASS

---

## Manual WhatsApp Testing (with Real Phone)

### Option A: Using Twilio Sandbox (Recommended for MVP)

#### Step 1: Add Your Phone to Sandbox
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to "Messaging" → "Try it out" → "Send an SMS"
3. Find WhatsApp Sandbox section
4. Send WhatsApp to Twilio's sandbox number with join code:
   ```
   Send to: +1234567890 (your Twilio WhatsApp number)
   Message: join alpha-bravo
   ```
5. Wait for confirmation from Twilio
6. You're now in the sandbox!

#### Step 2: Test Notification Flow
1. Update `.env` with test phone:
   ```
   MOTORISTA_TEST_PHONE=+5583993476410
   SHIPPER_TEST_PHONE=+5583999999999
   ```

2. Create test scenario:
   ```bash
   # 1. Create motorista account
   # 2. Post frete
   # 3. Create shipper account
   # 4. Create match (triggers notification)
   # 5. **CHECK YOUR WHATSAPP PHONE** for message
   ```

3. Expected message:
   ```
   🎉 Novo Frete Aceito!
   [Shipper Name] quer fazer seu frete: [Route] (R$ [Value])
   👉 Clique para aceitar: https://fretebr.app/match/[ID]
   ```

#### Step 3: Test Delivery Status
1. Open WhatsApp on your phone
2. Look for message from "+1234567890"
3. Verify:
   - Message received ✓
   - Message readable ✓
   - Timestamp correct ✓
4. Go back to Twilio Console → "Message Log"
5. Verify status shows "delivered" or "read"

### Option B: Production WhatsApp (After Account Upgrade)

**Requirements**:
- Upgrade from free trial to paid account
- Apply for WhatsApp Business Profile
- Verify business phone number
- Get dedicated WhatsApp number
- Update `.env` with production number

**Testing**:
- Same flow as Sandbox
- No join codes needed
- Messages to any WhatsApp number
- Metrics visible in Twilio dashboard

---

## Backend Error Handling Testing

### Test 10: Invalid Twilio Credentials
**Scenario**: TWILIO_AUTH_TOKEN is wrong or expired

```bash
# Update .env with invalid token
TWILIO_AUTH_TOKEN=invalid_token_12345

# Restart backend
docker-compose restart backend

# Try to create match
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{"frete_id": 1, "valor_final": 500.0}'

# Expected: Match should still be created
# Backend logs should show: "Twilio notification failed - credentials invalid"
# No crash, graceful degradation
```

**Success Criteria**:
- Match created despite Twilio error
- No 500 error response
- Error logged properly
- Backend continues operating
- ✓ PASS (graceful failure)

---

### Test 11: Missing Notification Environment Variables
**Scenario**: TWILIO_PHONE_NUMBER not set

```bash
# Update .env
TWILIO_PHONE_NUMBER=

# Restart backend
docker-compose restart backend

# Try to create match
curl -X POST http://localhost:8000/api/matches \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -d '{"frete_id": 1, "valor_final": 500.0}'

# Expected: Match created, notification skipped
# Backend logs should show: "Twilio phone number not configured"
```

**Success Criteria**:
- Match created
- No error response
- Error logged
- Graceful skip of notification
- ✓ PASS

---

### Test 12: Network/Rate Limit Error
**Scenario**: Twilio API temporarily unavailable (simulated)

```bash
# This is tested via unit tests with mocks
# See: backend/test_twilio.py → TestTwilioErrorHandling

# Run pytest
pytest backend/test_twilio.py::TestTwilioErrorHandling -v
```

**Expected Output**:
```
test_authentication_error PASSED
test_invalid_phone_number PASSED
test_rate_limit_error PASSED
```

**Success Criteria**:
- All error cases handled
- Proper exceptions raised
- Logging captures errors
- ✓ PASS

---

## Docker Verification

### Test 13: Docker Build
```bash
docker-compose build --no-cache

# Expected: All services build successfully
# Output: Successfully built fretebr_backend
#         Successfully built fretebr_frontend
#         Successfully built fretebr_postgres
```

**Success Criteria**:
- No build errors
- All layers cached/built
- Python dependencies installed
- Twilio SDK included in backend image
- ✓ PASS

---

### Test 14: Docker Services Health
```bash
docker-compose up

# Wait 10 seconds for startup

# Check health
docker-compose ps

# Expected:
# CONTAINER                STATUS
# fretebr_postgres      Up (healthy)
# fretebr_backend       Up (healthy)
# fretebr_frontend      Up
```

**Success Criteria**:
- All containers running
- PostgreSQL healthy
- Backend health check passing
- Frontend running
- ✓ PASS

---

### Test 15: Docker Backend Logs
```bash
docker-compose logs backend | tail -20

# Expected: No errors or exceptions
# Should see:
# - "Application startup complete"
# - "Uvicorn running on 0.0.0.0:8000"
# - "Connected to PostgreSQL"
# - "(Optional) Twilio SDK loaded"
```

**Success Criteria**:
- Clean startup logs
- No warning/error messages
- API endpoints listening
- Database connected
- ✓ PASS

---

## Testing Checklist

Use this checklist to track progress:

```markdown
## Week 3 Testing Checklist

### Unit Tests
- [ ] Test 1: Twilio SDK imports correctly
- [ ] Test 2: POST /api/fretes creates frete
- [ ] Test 3: POST /api/auth/signup creates shipper
- [ ] Test 4: GET /api/fretes lists available

### Integration Tests
- [ ] Test 5: POST /api/matches creates match + sends WhatsApp
- [ ] Test 6: Verify WhatsApp message in Twilio logs
- [ ] Test 7: POST /api/matches/{id}/messages creates message
- [ ] Test 8: GET /api/matches/{id}/messages returns history
- [ ] Test 9: GET /api/matches lists user matches

### Error Handling
- [ ] Test 10: Invalid Twilio credentials handled gracefully
- [ ] Test 11: Missing env vars handled gracefully
- [ ] Test 12: Network errors handled in pytest

### Docker
- [ ] Test 13: Docker Compose builds successfully
- [ ] Test 14: All services start and are healthy
- [ ] Test 15: Backend logs show clean startup

### Manual WhatsApp Testing
- [ ] Phone added to Twilio sandbox
- [ ] WhatsApp notification received on real phone
- [ ] Message content correct
- [ ] Delivery status shows in Twilio logs

### Documentation
- [ ] TWILIO_SETUP.md complete
- [ ] SEMANA_3_TESTING.md complete
- [ ] All tests pass locally
- [ ] Docker runs successfully
```

---

## Metrics & Monitoring

### Twilio Dashboard Metrics
After testing, check [Twilio Console](https://console.twilio.com):

1. **Messaging** → "Overview"
   - Messages Sent: Should show test messages
   - Messages Received: Should show join codes
   - Message Status Breakdown: delivered, read, failed

2. **Usage** → "Messages"
   - Total usage: Should be low (test messages only)
   - Cost estimate: ~$0.005 × number of messages

3. **Logs** → "Message Log"
   - Filter by date: Today
   - Verify all notifications appear
   - Check delivery status

### Backend Logs
```bash
docker-compose logs backend | grep -i "notification\|twilio\|match"

# Should see entries like:
# [INFO] Creating match ID: 1
# [INFO] Sending WhatsApp notification to +5583993476410
# [INFO] Twilio response: SID=SMxxx...
```

### Cost Tracking
- Free trial: $15 USD
- Each notification: ~$0.005
- 1000 notifications = $5
- Budget is more than sufficient for MVP testing

---

## Next Steps

1. **Review this checklist** with the team
2. **Execute all tests** in order
3. **Document results** in test report
4. **Fix any failures** before Quinta (23/junho)
5. **Prepare Hostinger deployment** (Semana 4)

---

## Support / Troubleshooting

### Can't send WhatsApp message?
- Check phone is in sandbox joined list
- Verify phone format: `whatsapp:+55[number]`
- Check Twilio logs for error codes
- Ensure credentials in .env are correct

### Backend not starting?
- Check logs: `docker-compose logs backend`
- Verify database is healthy: `docker-compose logs postgres`
- Ensure .env has all required variables
- Try rebuild: `docker-compose build --no-cache`

### Twilio account locked?
- Check Twilio Console for notifications
- Verify account credit (free trial $15)
- Contact Twilio support if needed

---

**Ready to test! 🚀**
