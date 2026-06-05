# FreteBR - Semana 3 Implementation Guide
## For Backend, Frontend, and DevOps Team Members

**Status:** SEGUNDA 20/junho Complete  
**Next Phase:** TERÇA 21/junho - Frontend Integration  
**Repository:** Val7h/fretebr (branch: dev)

---

## 🚀 QUICK START

### Prerequisites
- Docker + Docker Compose
- PostgreSQL 15
- Python 3.10+
- Node.js 18+ (frontend)

### Setup
```bash
# Clone and setup
git clone https://github.com/Val7h/fretebr.git
cd fretebr
git checkout dev

# Copy env file
cp .env.example .env

# Start services
docker-compose up --build

# Run migrations (inside container)
docker exec fretebr-backend python -m alembic upgrade head

# Run tests
docker exec fretebr-backend python -m pytest backend/test_matches.py -v
```

---

## 📋 BACKEND IMPLEMENTATION STATUS

### ✅ COMPLETED (SEGUNDA 20/junho)

#### Models
```python
# Match model - all fields implemented
class Match(Base):
    id: int
    frete_id: int (FK → fretes)
    shipper_id: int (FK → users)
    status: enum (pendente, aceito, em_entrega, finalizado, cancelado)
    valor_final: float
    data_match: datetime
    created_at: datetime
    updated_at: datetime
    
    relationships:
    - frete: Frete
    - shipper: User
    - messages: List[Message]

# Message model - chat functionality
class Message(Base):
    id: int
    match_id: int (FK → matches)
    sender_id: int (FK → users)
    conteudo: str (Text)
    created_at: datetime
    
    relationships:
    - match: Match
    - sender: User
```

#### API Endpoints (8 total)

```
POST /api/matches
  - Shipper accepts frete
  - Creates match + sends WhatsApp
  - Auth required (shipper only)
  - Returns: MatchResponse [201]

GET /api/matches
  - List user's matches
  - Motorista sees matches on their fretes
  - Shipper sees matches they accepted
  - Auth required
  - Returns: List[MatchResponse] [200]

GET /api/matches/{id}
  - Get match with full details + messages
  - User must be part of match
  - Auth required
  - Returns: MatchWithMessages [200]

PUT /api/matches/{id}/status
  - Update match status
  - Only motorista can update
  - Valid: pendente → aceito → em_entrega → finalizado
  - Auth required
  - Returns: MatchResponse [200]

GET /api/matches/{id}/messages
  - Get chat history
  - Ordered by created_at ASC
  - User must be part of match
  - Auth required
  - Returns: List[MessageResponse] [200]

POST /api/matches/{id}/messages
  - Send message in chat
  - User must be part of match
  - Auth required
  - Input: { conteudo }
  - Returns: MessageResponse [201]
```

#### WhatsApp Integration
```python
# Automatic notification when match created
send_whatsapp_notification(
    phone_number=motorista.telefone,  # "+55XXXXXXXXXXX"
    message="🚚 Você recebeu uma solicitação em FreteBR! {origem} → {destino}..."
)

# Uses Twilio SDK
# Credentials from .env:
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER

# Graceful error handling - doesn't crash if Twilio fails
```

#### CRUD Functions (11 total)

```python
# Match CRUD
create_match(db, shipper_id, frete_id, valor_final) → Match
get_match(db, match_id) → Match | None
list_matches(db, user_id, user_type) → List[Match]
update_match_status(db, match_id, new_status) → Match
cancel_match(db, match_id) → Match
delete_match(db, match_id) → bool

# Message CRUD
create_message(db, match_id, sender_id, conteudo) → Message
get_message(db, message_id) → Message | None
get_messages_by_match(db, match_id) → List[Message]
delete_message(db, message_id) → bool
```

#### Database Migrations
```sql
-- 002_create_matches_table.sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    frete_id INTEGER FK,
    shipper_id INTEGER FK,
    status VARCHAR,
    valor_final FLOAT,
    data_match TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX idx_matches_frete_id;
CREATE INDEX idx_matches_shipper_id;
CREATE INDEX idx_matches_status;

-- 003_create_messages_table.sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    match_id INTEGER FK,
    sender_id INTEGER FK,
    conteudo TEXT,
    created_at TIMESTAMP
);
CREATE INDEX idx_messages_match_id;
CREATE INDEX idx_messages_sender_id;
CREATE INDEX idx_messages_created_at;
```

---

## 🎨 FRONTEND TASKS (TERÇA 21/junho)

### To Do

#### Pages to Create
```tsx
// MyMatchesPage - show user's matches
pages/MyMatchesPage.tsx
  - Show all matches for current user
  - Display frete info + other user info
  - Status badges
  - Action buttons (chat, details, cancel)
  - Responsive grid layout

// MatchDetailPage - full match info
pages/MatchDetailPage.tsx
  - Match details (frete, users, status)
  - Timeline showing progression
  - Update status button (motorista only)
  - Chat button
  - Cancel button

// ChatPage - messaging interface
pages/ChatPage.tsx
  - Message list (scrollable, auto-scroll)
  - Message input + send button
  - Sender name + timestamp
  - Loading states
  - Error handling
```

#### Components
```tsx
// components/MatchTimeline.tsx
  - Visual progression: pendente → aceito → em_entrega → finalizado
  - Highlight current status
  - Tailwind styling

// components/ChatMessage.tsx
  - Single message view
  - Different style for own vs other's message
  - Timestamp, sender name
```

#### Services
```tsx
// services/matchesApi.ts
getMatches() → GET /api/matches
getMatchById(id) → GET /api/matches/{id}
acceptFrete(frete_id) → POST /api/matches
updateMatchStatus(id, status) → PUT /api/matches/{id}/status
getMessages(match_id) → GET /api/matches/{id}/messages
sendMessage(match_id, conteudo) → POST /api/matches/{id}/messages
```

#### Integration
```tsx
// Update FreteDetailPage
- Show "Quero Este Frete" button (shipper only)
- Only if status = disponível
- Call acceptFrete(frete_id)
- Redirect to /meus-matches

// Update HeaderNavigation
- Add "Meus Matches" link
- Show count of active matches

// Update DashboardPage
- Add Matches card/section
- Link to MyMatchesPage
```

---

## 🔧 DEVOPS TASKS (TERÇA 21/junho+)

### Twilio Setup
```bash
# 1. Create account at https://console.twilio.com
# 2. Get credentials:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# 3. Enable WhatsApp sandbox
# 4. Add test phone numbers
# 5. Update .env file

# 6. Test with docker-compose
docker-compose up
# Verify WhatsApp message received
```

### Environment Setup
```bash
# .env file should have:
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number
TWILIO_WHATSAPP_SANDBOX_ENABLED=true
NOTIFICATIONS_ENABLED=true
WHATSAPP_NOTIFICATIONS_ENABLED=true
```

### Docker Verification
```bash
# Build
docker-compose build --no-cache

# Run
docker-compose up

# Verify backend healthy
curl http://localhost:8000/health

# Check logs
docker-compose logs -f backend

# Run tests inside container
docker exec fretebr-backend python -m pytest backend/test_matches.py -v
```

---

## 🧪 TESTING GUIDE

### Run All Tests
```bash
docker exec fretebr-backend python -m pytest backend/test_matches.py -v
```

### Test Coverage
- 16+ test cases included
- Tests for happy path + error cases
- Mocks for Twilio (no real messages sent)
- SQLite in-memory database

### Manual Testing Flow

#### Step 1: Create Users
```bash
# Create motorista
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "motorista@test.com",
    "password": "password123",
    "tipo": "motorista",
    "nome": "João",
    "telefone": "+5511987654321"
  }'
# Copy access_token to MOTORISTA_TOKEN

# Create shipper
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "shipper@test.com",
    "password": "password123",
    "tipo": "shipper",
    "nome": "Maria",
    "telefone": "+5511912345678"
  }'
# Copy access_token to SHIPPER_TOKEN
```

#### Step 2: Create Frete
```bash
curl -X POST http://localhost:8000/api/fretes \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origem": "São Paulo",
    "destino": "Rio de Janeiro",
    "peso_kg": 100,
    "valor_r": 500,
    "descricao": "Teste"
  }'
# Copy frete_id
```

#### Step 3: Accept Frete
```bash
curl -X POST http://localhost:8000/api/matches \
  -H "Authorization: Bearer $SHIPPER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"frete_id": 1}'
# Should return 201 + match object
# WhatsApp notification sent to motorista
```

#### Step 4: Get Matches
```bash
# Motorista sees match
curl -X GET http://localhost:8000/api/matches \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"

# Shipper sees match
curl -X GET http://localhost:8000/api/matches \
  -H "Authorization: Bearer $SHIPPER_TOKEN"
```

#### Step 5: Send Messages
```bash
curl -X POST http://localhost:8000/api/matches/1/messages \
  -H "Authorization: Bearer $MOTORISTA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conteudo": "Oi, tudo bem?"}'
```

#### Step 6: Get Chat History
```bash
curl -X GET http://localhost:8000/api/matches/1/messages \
  -H "Authorization: Bearer $MOTORISTA_TOKEN"
```

---

## 📚 DOCUMENTATION LOCATIONS

| Document | Path | Purpose |
|----------|------|---------|
| Backend Summary | SEMANA_3_BACKEND_COMPLETE.md | Full overview |
| Daily Standup | STANDUP_SEGUNDA_20_06.md | Progress report |
| Week 3 Plan | SEMANA_3_AGENTES.md | All tasks for team |
| This Guide | SEMANA_3_IMPLEMENTATION_GUIDE.md | Developer guide |

---

## 🔐 SECURITY NOTES

### Authentication
- All endpoints require JWT token (except /api/auth/*)
- Token format: `Authorization: Bearer <token>`
- Token expires in 15 minutes (configurable)

### Authorization
- Shipper can only accept fretes (not motorista)
- Only motorista can update match status
- Users can only see their own matches/messages
- Cannot view/edit matches you're not part of

### Data Protection
- All passwords hashed with bcrypt
- Foreign keys with CASCADE delete (no orphaned records)
- SQL injection prevented via SQLAlchemy ORM
- No hardcoded secrets in code

---

## 📊 PERFORMANCE NOTES

### Database Indexes
- matches(frete_id) - for quick frete lookup
- matches(shipper_id) - for user's matches
- matches(status) - for status filtering
- messages(match_id) - for chat history
- messages(sender_id) - for user's messages
- messages(created_at) - for time ordering

### Query Optimization
- Joins on indexed columns
- Ordered queries for consistency
- Lazy loading of relationships (as needed)

---

## 🆘 TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'psycopg2'"
**Solution:** Inside docker container, dependencies are installed. Only happens in local dev.

### Issue: "TWILIO_ACCOUNT_SID not configured"
**Solution:** Check .env file has Twilio variables. Backend logs warning but continues.

### Issue: "Match not found" when getting match
**Solution:** Check user is motorista or shipper of the match (authorization).

### Issue: WhatsApp message not received
**Solution:** 
1. Verify TWILIO_PHONE_NUMBER is correct
2. Check motorista.telefone is in correct format (+55...)
3. Verify Twilio account has credits/trial active
4. Check Docker logs: `docker-compose logs backend | grep WhatsApp`

---

## 🚀 NEXT STEPS

### TERÇA 21/junho
- [ ] Frontend: MyMatches, MatchDetail, Chat pages
- [ ] Integration with Match APIs
- [ ] Styling + UX refinement

### QUARTA 22/junho
- [ ] Full API integration
- [ ] Message real-time updates (if needed)
- [ ] Error handling on frontend

### QUINTA 23/junho
- [ ] DevOps: Twilio final setup
- [ ] E2E testing with real flow
- [ ] Performance testing

### SEXTA 24/junho
- [ ] Final verification
- [ ] Production readiness checklist
- [ ] Deployment preparation

---

## 📞 SUPPORT

### Team Contacts
- Backend: Claude Haiku 4.5 (claude@anthropic.com)
- Frontend: [To be assigned]
- DevOps: [To be assigned]

### Resources
- Twilio Docs: https://www.twilio.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pydantic Docs: https://docs.pydantic.dev

---

## ✅ CHECKLIST FOR RELEASE

Before moving to SEXTA (Production Ready):

- [ ] All 16+ tests passing
- [ ] Backend APIs functional
- [ ] Frontend pages complete
- [ ] Chat messaging working
- [ ] WhatsApp notifications tested
- [ ] Docker build clean
- [ ] No console errors
- [ ] Authorization working
- [ ] Error handling complete
- [ ] Performance acceptable

---

## 📝 VERSION HISTORY

| Version | Date | Status | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-20 | BETA | Initial implementation (SEGUNDA complete) |
| 1.1 | 2026-06-21 | TBD | Frontend integration (TERÇA) |
| 1.2 | 2026-06-22 | TBD | Full API integration (QUARTA) |
| 1.3 | 2026-06-23 | TBD | DevOps + Testing (QUINTA) |
| 2.0 | 2026-06-24 | TBD | Production Ready (SEXTA) |

---

**Last Updated:** 2026-06-20 (SEGUNDA)  
**Next Update:** 2026-06-21 (TERÇA)

Good luck, team! 🚀
