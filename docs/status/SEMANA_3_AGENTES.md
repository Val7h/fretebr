# FreteBR - SEMANA 3 AGENTES
## Matches + WhatsApp Notifications + Chat

**Data:** 20 a 26 de Junho, 2026  
**Goal:** Shipper aceita frete, notificações via WhatsApp, chat básico  
**Owner:** Valth Menezes Guimarães  
**GitHub:** Val7h/fretebr

---

## 🎯 DELIVERABLES FINAIS (Sexta-feira 26/junho)

- [ ] Backend: Match model + CRUD endpoints
- [ ] Backend: WhatsApp notifications via Twilio
- [ ] Frontend: Match/Accept Frete page
- [ ] Frontend: Chat interface (basic)
- [ ] Database: `matches` table + schema
- [ ] Twilio: Setup + configured
- [ ] Docker: WhatsApp integration tested
- [ ] E2E: Shipper accepts frete → motorista receives notification

---

## 👥 3 AGENTES EM PARALELO

### **AGENTE 1: Backend Developer**

**Responsabilidade:** Match Model + API + Notifications

#### TAREFAS:

**Segunda (20/junho):**
- [ ] Pull latest `dev` branch
- [ ] Create `backend/app/models/match.py`:
  ```python
  class Match(Base):
    id: int (PK)
    frete_id: int (FK → fretes)
    shipper_id: int (FK → users)
    status: enum (pendente, aceito, em_entrega, finalizado, cancelado)
    valor_final: float
    data_match: datetime
    created_at: datetime
    updated_at: datetime
    frete: Frete (relationship)
    shipper: User (relationship)
    messages: List[Message] (relationship)
  ```
- [ ] Create `backend/app/models/message.py`:
  ```python
  class Message(Base):
    id: int (PK)
    match_id: int (FK → matches)
    sender_id: int (FK → users)
    conteudo: str
    created_at: datetime
    sender: User (relationship)
  ```
- [ ] Alembic migrations for both tables
- [ ] PR #11: "Add Match + Message models"

**Terça (21/junho):**
- [ ] Create schemas: `backend/app/schemas/match.py`
  - MatchBase, MatchCreate, MatchUpdate, MatchResponse
  - MatchWithMessages (include messages list)
- [ ] Create schemas: `backend/app/schemas/message.py`
  - MessageCreate, MessageResponse
- [ ] Create `backend/app/crud/match.py`:
  - create_match(db, shipper_id, frete_id)
  - get_match(db, match_id)
  - list_matches(db, user_id, user_type) - user's matches
  - update_match_status(db, match_id, new_status)
  - cancel_match(db, match_id)
- [ ] PR #12: "Add Match CRUD + schemas"

**Quarta (22/junho):**
- [ ] Create `backend/app/api/matches.py` with endpoints:
  - POST /api/matches (shipper accepts frete)
    * Input: { frete_id }
    * Creates match + sends notification
    * Returns: MatchResponse
  - GET /api/matches (my matches)
    * Motorista vê seus matches
    * Shipper vê seus matches
  - GET /api/matches/{id} (single match)
  - PUT /api/matches/{id}/status (update status)
    * Allowed transitions: pendente→aceito, aceito→em_entrega, em_entrega→finalizado
  - GET /api/matches/{id}/messages (get chat history)
- [ ] Include router in main.py
- [ ] PR #13: "Match API endpoints"

**Quinta (23/junho):**
- [ ] Create `backend/app/services/notifications.py`:
  - send_whatsapp_notification(phone, message)
  - Uses Twilio API
  - Environment vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
- [ ] Integrate notifications:
  - When shipper accepts frete (POST /matches) → send WhatsApp to motorista
  - Message: "Você recebeu uma solicitação em FreteBR! São Paulo → Rio de Janeiro. Valor: R$ 500. Clique para ver detalhes."
- [ ] Create `backend/app/api/messages.py`:
  - POST /api/matches/{id}/messages (send message in chat)
    * Input: { conteudo }
    * Creates message + stores in DB
    * Returns: MessageResponse
- [ ] PR #14: "WhatsApp notifications + Chat API"

**Sexta (24/junho):**
- [ ] Create tests: `backend/test_matches.py`:
  - test_shipper_accepts_frete() → creates match
  - test_list_motorista_matches() → returns motorista's matches
  - test_list_shipper_matches() → returns shipper's matches
  - test_update_match_status() → transitions status
  - test_send_message() → creates message in chat
  - test_unauthorized_accept() → motorista cannot accept own frete
  - All tests passing
- [ ] Manual testing:
  - docker-compose up
  - Create motorista + post frete
  - Create shipper + accept frete
  - Verify match created in database
  - Verify WhatsApp notification triggered (or mock in tests)
- [ ] PR #15: "Match testing complete"

#### ACCEPTANCE CRITERIA:
```
✅ Match model with all fields
✅ POST /api/matches creates match
✅ GET /api/matches returns user's matches only
✅ GET /api/matches/{id} returns single match
✅ PUT /api/matches/{id}/status updates status
✅ WhatsApp notification sent when match created
✅ Message CRUD working
✅ All tests passing (7+ tests)
✅ No hardcoded secrets (use env vars)
```

---

### **AGENTE 2: Frontend Developer**

**Responsabilidade:** Match Pages + Chat Interface

#### TAREFAS:

**Segunda (20/junho):**
- [ ] Pull latest `dev`
- [ ] Update routes in App.tsx:
  - /meus-matches → MyMatchesPage (protected, both roles)
  - /match/{id} → MatchDetailPage (protected)
  - /match/{id}/chat → ChatPage (protected)
- [ ] Create `frontend/src/pages/MyMatchesPage.tsx`:
  - Show user's matches (motorista or shipper)
  - For motorista: shows who accepted each of their fretes
  - For shipper: shows fretes they accepted
  - Status badges: pendente, aceito, em_entrega, finalizado
  - "Ir para chat" button → /match/{id}/chat
  - "Detalhes" button → /match/{id}
  - Responsive grid layout
- [ ] PR #11: "Add MyMatches page"

**Terça (21/junho):**
- [ ] Create `frontend/src/pages/MatchDetailPage.tsx`:
  - Show match details:
    * Frete info (origem, destino, peso, valor)
    * Motorista info (if shipper viewing)
    * Shipper info (if motorista viewing)
    * Status badge + timeline (pendente → aceito → em_entrega → finalizado)
    * "Ir para Chat" button
    * "Cancelar Match" button (if status = pendente)
    * "Marcar como Entregue" button (motorista, if status = em_entrega)
- [ ] Create `frontend/src/components/MatchTimeline.tsx`:
  - Visual timeline showing match progression
  - Tailwind styled
- [ ] PR #12: "Add MatchDetail page + Timeline"

**Quarta (22/junho):**
- [ ] Create `frontend/src/pages/ChatPage.tsx`:
  - Chat interface for motorista + shipper
  - Message list (scrollable)
  - Input field at bottom
  - Send button
  - Show sender name + timestamp for each message
  - Auto-scroll to latest message
  - Loading state while fetching messages
- [ ] Create `frontend/src/components/ChatMessage.tsx`:
  - Single message component
  - Styled differently for own vs other person's message
  - Timestamp
- [ ] Create `frontend/src/services/matchesApi.ts`:
  - getMatches() → GET /api/matches
  - getMatchById(id) → GET /api/matches/{id}
  - acceptFrete(frete_id) → POST /api/matches
  - updateMatchStatus(id, status) → PUT /api/matches/{id}/status
  - getMessages(match_id) → GET /api/matches/{id}/messages
  - sendMessage(match_id, message) → POST /api/matches/{id}/messages
- [ ] PR #13: "Chat page + API service"

**Quinta (23/junho):**
- [ ] Integrate "Quero Este Frete" button in FreteDetailPage:
  - Button only visible for shippers (check role)
  - Only visible if frete status = "disponível"
  - On click: call acceptFrete(frete_id)
  - On success: show toast "Frete aceito! Veja em Meus Matches"
  - Redirect to /meus-matches
- [ ] Update DashboardPage:
  - Add "Meus Matches" link for both roles
  - If motorista: show count of active matches
  - If shipper: show count of accepted fretes
- [ ] Update HeaderNavigation:
  - Add "Matches" link to main nav
- [ ] PR #14: "Integrate Match features into main flow"

**Sexta (24/junho):**
- [ ] Test full flow:
  - Motorista posts frete
  - Shipper finds frete
  - Shipper clicks "Quero"
  - Motorista sees new match
  - Both can access chat
  - Messages persist and display correctly
- [ ] Styling review:
  - Chat is clean, readable, responsive
  - Timestamps visible
  - User avatars/names visible
  - Consistent with design system
- [ ] Error handling:
  - Network errors show message
  - Unauthorized access redirects
  - Match not found → 404 page
- [ ] PR #15: "Full Match + Chat integration tested"

#### ACCEPTANCE CRITERIA:
```
✅ MyMatches page shows user's matches
✅ MatchDetail page shows full match info
✅ ChatPage functional (list + send messages)
✅ "Quero Este Frete" button visible + works
✅ Messages display in real-time
✅ Timestamps on messages
✅ Both motorista and shipper can chat
✅ Chat history persists
✅ Responsive design
✅ Error handling complete
```

---

### **AGENTE 3: DevOps / Twilio Integration**

**Responsabilidade:** WhatsApp Setup + Testing + Documentation

#### TAREFAS:

**Segunda (20/junho):**
- [ ] Research Twilio WhatsApp integration
- [ ] Create Twilio account (free trial)
- [ ] Get Twilio credentials:
  - TWILIO_ACCOUNT_SID
  - TWILIO_AUTH_TOKEN
  - TWILIO_PHONE_NUMBER (WhatsApp sandbox number)
- [ ] Document setup in `TWILIO_SETUP.md`:
  - How to create Twilio account
  - How to get credentials
  - How to activate WhatsApp sandbox
  - How to add test numbers
- [ ] Update `.env.example`:
  - Add TWILIO_ACCOUNT_SID
  - Add TWILIO_AUTH_TOKEN
  - Add TWILIO_PHONE_NUMBER
- [ ] PR #11: "Twilio setup documentation"

**Terça (21/junho):**
- [ ] Create Docker environment for Twilio:
  - Add twilio==9.2.1 to requirements.txt
  - Verify pip install works
- [ ] Create `backend/test_twilio.py`:
  - Test Twilio credentials are valid
  - Test sending sample WhatsApp message
  - Mock test (don't actually send, just verify API call)
- [ ] Update docker-compose.yml if needed
- [ ] PR #12: "Twilio dependencies + basic test"

**Quarta (22/junho):**
- [ ] Create `SEMANA_3_TESTING.md`:
  - How to test Match creation
  - How to test WhatsApp notification (with mock or real Twilio sandbox)
  - How to test chat
  - Expected outcomes
- [ ] Manual testing:
  - POST /api/matches with real Twilio account
  - Verify WhatsApp message received (if using real number)
  - Or verify message would be sent (with mock)
- [ ] Document any issues
- [ ] PR #13: "Match + WhatsApp testing guide"

**Quinta (23/junho):**
- [ ] Create `SEMANA_3_E2E_TEST.md`:
  - Full end-to-end flow:
    1. Login motorista → post frete
    2. Login shipper → find frete → click "Quero"
    3. Verify match created in DB
    4. Verify WhatsApp notif sent to motorista
    5. Both users access /match/{id}/chat
    6. Exchange messages
    7. Update match status
  - Step-by-step with expected results
- [ ] Create monitoring checklist:
  - How to monitor Twilio usage
  - How to check WhatsApp logs
  - Cost tracking
- [ ] PR #14: "E2E + monitoring documentation"

**Sexta (24/junho):**
- [ ] Final Docker testing:
  - docker-compose build --no-cache
  - docker-compose up
  - Verify all services healthy
  - Test Match creation (triggers WhatsApp notification)
- [ ] Verify Twilio integration:
  - Credentials loaded from .env
  - No hardcoded secrets
  - Error handling if Twilio fails (graceful fallback)
- [ ] Create final summary: `SEMANA_3_DEVOPS_COMPLETE.md`
- [ ] Create Hostinger deployment notes for Semana 4:
  - Twilio credentials in Hostinger .env
  - WhatsApp notifications will work in production
  - Cost implications
- [ ] PR #15: "Semana 3 complete + production ready"

#### ACCEPTANCE CRITERIA:
```
✅ Twilio account setup
✅ Credentials in .env (not hardcoded)
✅ WhatsApp integration working
✅ Notifications sent when match created
✅ Testing documentation complete
✅ E2E flow verified
✅ Error handling: Twilio failures don't crash app
✅ All 5 PRs merged
✅ No sensitive data in code
```

---

## 📅 DAILY STANDUP (9:00 AM Brasília)

**Format:**
```
Backend:
  Feito: [tarefa]
  Hoje: [tarefa]
  Blockers: [if any]

Frontend:
  Feito: [tarefa]
  Hoje: [tarefa]
  Blockers: [if any]

DevOps:
  Feito: [tarefa]
  Hoje: [tarefa]
  Blockers: [if any]
```

---

## 🔧 REQUIREMENTS FROM OWNER

- Seu número de telefone WhatsApp (para receber notificações de teste)
- Feedback no design do chat (gosta da interface?)
- Features adicionais?

---

## ⏱️ TIMELINE

- **Segunda (20/junho):** Models + Twilio setup
- **Terça (21/junho):** CRUD + Pages
- **Quarta (22/junho):** APIs + Chat
- **Quinta (23/junho):** Integration + Testing
- **Sexta (24/junho):** E2E + Production ready

---

## ✅ SEMANA 3 CHECKLIST (Sexta 26/junho EOD)

- [ ] Backend: Match + Message models
- [ ] Backend: Match CRUD APIs (6+ endpoints)
- [ ] Backend: WhatsApp notifications via Twilio
- [ ] Frontend: MyMatches page
- [ ] Frontend: MatchDetail page
- [ ] Frontend: Chat interface
- [ ] Frontend: "Quero Este Frete" integration
- [ ] DevOps: Twilio setup + testing
- [ ] E2E: Full match flow tested
- [ ] All PRs merged to `dev`
- [ ] Ready for Semana 4 (Payments + Deploy)

---

## 🚀 PRÓXIMA: SEMANA 4

**Semana 4 (27-01 Julho):**
- Payment integration (Pix)
- Final dashboard
- Deploy para Hostinger
- LAUNCH! 🎉

---

## 🎬 COMEÇAR AGORA

Semana 3 começa SEGUNDA 20/junho.
Vocês têm 1 semana para Matches + Chat + WhatsApp.
Let's GO! 🚀
