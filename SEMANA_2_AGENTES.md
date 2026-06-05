# FreteBR - SEMANA 2 AGENTES
## Features Core: Motoristas + Shippers + Fretes

**Data:** 13 a 19 de Junho, 2026  
**Goal:** Motoristas conseguem postar fretes, Shippers conseguem achar fretes  
**Owner:** Valth Menezes Guimarães  
**GitHub:** Val7h/fretebr

---

## 🎯 DELIVERABLES FINAIS (Sexta-feira 19/junho)

- [ ] Backend: API endpoints para fretes (POST, GET, LIST)
- [ ] Frontend: Página "Postar Frete" (motoristas)
- [ ] Frontend: Página "Encontrar Fretes" (shippers)
- [ ] Frontend: Dashboard atualizado com links para features
- [ ] Database: tabela `fretes` com migrations
- [ ] Docker: tudo funcionando localmente
- [ ] E2E: motorista posta frete, shipper vê na lista

---

## 👥 3 AGENTES EM PARALELO

### **AGENTE 1: Backend Developer**

**Responsabilidade:** API Fretes + Database

#### TAREFAS:

**Segunda (13/junho):**
- [ ] Pull latest `dev` branch
- [ ] Create `backend/app/models/frete.py`:
  ```python
  class Frete(Base):
    id: int (PK)
    motorista_id: int (FK → users)
    origem: str
    destino: str
    peso_kg: float
    valor_r$: float
    status: enum (disponível, aceito, entregue, cancelado)
    descricao: str
    created_at: datetime
    updated_at: datetime
    motorista: User (relationship)
  ```
- [ ] Create Alembic migration: `create_fretes_table`
- [ ] Run migration (local)
- [ ] PR #6: "Frete model + migration"

**Terça (14/junho):**
- [ ] Create `backend/app/schemas/frete.py`:
  - FreteBase, FreteCreate, FreteUpdate, FreteResponse
  - Include motorista_id + motorista name
- [ ] Create `backend/app/crud/frete.py`:
  - create_frete(db, motorista_id, frete_schema)
  - get_frete(db, frete_id)
  - list_fretes(db, skip, limit, status=None)
  - update_frete(db, frete_id, frete_update)
  - delete_frete(db, frete_id)
- [ ] PR #7: "Frete CRUD operations"

**Quarta (15/junho):**
- [ ] Create `backend/app/api/fretes.py` with endpoints:
  - POST /api/fretes (motorista posts frete) - requires auth
  - GET /api/fretes (list all available)
  - GET /api/fretes/{id} (get single)
  - GET /api/meus-fretes (my fretes - motorista only)
  - PUT /api/fretes/{id} (update - motorista only)
  - DELETE /api/fretes/{id} (cancel - motorista only)
- [ ] Add permission checks (only motorista can post/update own)
- [ ] PR #8: "Frete endpoints"

**Quinta (16/junho):**
- [ ] Update `backend/app/main.py` to include fretes router
- [ ] Update test file: `backend/test_fretes.py`:
  - Test create frete
  - Test list fretes
  - Test get single frete
  - Test update own frete
  - Test delete own frete
  - Test permission (shipper can't post)
- [ ] PR #9: "Frete tests"

**Sexta (17/junho):**
- [ ] Verify all endpoints working:
  - POST /api/fretes → creates frete
  - GET /api/fretes → returns list
  - GET /api/meus-fretes → returns motorista's fretes only
- [ ] Test with Frontend
- [ ] Docker: rebuild + test
- [ ] PR #10: "Frete API complete + tested"

#### ACCEPTANCE CRITERIA:
```
✅ Frete model created with all fields
✅ POST /api/fretes → creates frete (motorista only)
✅ GET /api/fretes → lists all available fretes
✅ GET /api/fretes/{id} → returns single frete
✅ GET /api/meus-fretes → returns motorista's fretes only
✅ PUT /api/fretes/{id} → updates frete (motorista only)
✅ DELETE /api/fretes/{id} → deletes frete (motorista only)
✅ Shipper cannot POST fretes (403 error)
✅ All tests passing
✅ Docker working
```

---

### **AGENTE 2: Frontend Developer**

**Responsabilidade:** UI Pages (PostFrete + FindFrete)

#### TAREFAS:

**Segunda (13/junho):**
- [ ] Pull latest `dev`
- [ ] Create `frontend/src/pages/PostFretePage.tsx`:
  - Form with fields: origem, destino, peso_kg, valor_r$, descricao
  - Dropdown for common cidades (SP, RJ, MG, PE, etc)
  - Submit button calls `api.createFrete()`
  - On success: redirects to `/meus-fretes` with success message
  - On error: shows error message
  - Only visible for motoristas (check user type)
- [ ] Create form component: `frontend/src/components/FreteForm.tsx`
- [ ] PR #6: "PostFrete page + form"

**Terça (14/junho):**
- [ ] Create `frontend/src/pages/FindFretePage.tsx`:
  - List of all available fretes
  - Each frete shows: origem, destino, peso, valor, motorista name
  - Search/filter by destination city
  - Sort by valor or distance
  - Click frete card → go to detail page
- [ ] Create `frontend/src/components/FreteCard.tsx`:
  - Card component showing frete info
  - Motorista name + rating (placeholder)
  - "Ver detalhes" button
- [ ] PR #7: "FindFrete page + FreteCard"

**Quarta (15/junho):**
- [ ] Create `frontend/src/pages/FreteDetailPage.tsx`:
  - Show full frete details
  - "Quero este frete" button (for shippers)
  - Motorista info + contact (placeholder)
  - Map (placeholder - can add Google Maps later)
- [ ] Create `frontend/src/services/fretesApi.ts`:
  - getFretes() - GET /api/fretes
  - getFreteById(id) - GET /api/fretes/{id}
  - getMyFretes() - GET /api/meus-fretes
  - createFrete(data) - POST /api/fretes
  - updateFrete(id, data) - PUT /api/fretes/{id}
  - deleteFrete(id) - DELETE /api/fretes/{id}
- [ ] PR #8: "Frete detail page + API service"

**Quinta (16/junho):**
- [ ] Create `frontend/src/pages/MyFretesPage.tsx`:
  - Show motorista's posted fretes
  - Status badge (disponível, aceito, entregue)
  - Edit button (if disponível)
  - Delete button
  - Add new frete button → links to /postar-frete
- [ ] Update `frontend/src/pages/DashboardPage.tsx`:
  - Add navigation cards:
    - "Postar Frete" (motorista only) → /postar-frete
    - "Procurar Fretes" (shipper only) → /procurar-fretes
    - "Meus Fretes" (motorista only) → /meus-fretes
  - Show different dashboard for motorista vs shipper
- [ ] PR #9: "My fretes page + dashboard nav"

**Sexta (17/junho):**
- [ ] Test all pages:
  - Login as motorista → see "Postar Frete" link
  - Click → goes to form
  - Fill form → submit
  - Check if frete appears in /meus-fretes
  - Login as shipper → see "Procurar Fretes"
  - Check if posted frete appears in list
- [ ] Styling: ensure pages match design system (Tailwind)
- [ ] Responsive: test on mobile
- [ ] PR #10: "Frete features complete + tested"

#### ACCEPTANCE CRITERIA:
```
✅ PostFrete page: motorista can post frete
✅ FindFrete page: shows list of available fretes
✅ FreteDetail page: shows single frete details
✅ MyFretes page: shows motorista's posted fretes
✅ Dashboard updated: shows role-specific nav
✅ Motorista only sees "Postar Frete"
✅ Shipper only sees "Procurar Fretes"
✅ All forms working + validated
✅ Error handling + success messages
✅ Responsive design (mobile ok)
✅ Tailwind styling consistent
```

---

### **AGENTE 3: DevOps / Integration**

**Responsabilidade:** Docker + Testing + Hostinger Prep

#### TAREFAS:

**Segunda (13/junho):**
- [ ] Pull latest `dev`
- [ ] Update docker-compose.yml if needed
- [ ] Rebuild backend + frontend images
- [ ] Test locally: docker-compose up
- [ ] Verify all containers start
- [ ] Check logs for errors
- [ ] PR #6: "Docker rebuild + verify"

**Terça (14/junho):**
- [ ] Create `SEMANA_2_TESTING.md`:
  - Manual testing checklist
  - API endpoints to test
  - Frontend flows to test
  - Expected results
- [ ] Test backend Frete endpoints:
  - POST /api/fretes (create)
  - GET /api/fretes (list)
  - GET /api/meus-fretes
  - GET /api/fretes/{id}
- [ ] Document any issues
- [ ] PR #7: "Testing documentation"

**Quarta (15/junho):**
- [ ] Create E2E test script: `SEMANA_2_E2E_TEST.md`
  - Full user journey: motorista creates frete → shipper finds it
  - Step by step instructions
  - Expected outcomes
- [ ] Test full flow locally
- [ ] Document results
- [ ] PR #8: "E2E testing guide"

**Quinta (16/junho):**
- [ ] Create `HOSTINGER_PREP.md`:
  - Instructions for deploying to Hostinger (for Semana 4)
  - Environment variables needed for prod
  - Database setup for prod
  - SSL setup notes
  - Monitoring setup
- [ ] Create deployment checklist
- [ ] PR #9: "Hostinger preparation guide"

**Sexta (17/junho):**
- [ ] Final Docker testing
- [ ] Verify everything works:
  - Backend APIs responding
  - Frontend loading
  - Database connected
  - Auth working
  - Frete features working
- [ ] Create final summary: `SEMANA_2_SUMMARY.md`
- [ ] PR #10: "Semana 2 complete + ready for Semana 3"

#### ACCEPTANCE CRITERIA:
```
✅ docker-compose.yml updated
✅ All containers running
✅ Backend Frete endpoints working
✅ Frontend Frete pages loading
✅ E2E flow tested manually
✅ Testing documentation complete
✅ Hostinger preparation guide ready
✅ All 5 PRs merged
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

- Pode testar Semana 1 localmente antes? (recomendado)
- Feedback no código? (issues no GitHub)
- Features adicionais desejadas?

---

## 📞 BLOCKER ESCALATION

Se agentes ficarem presos:
- Backend issue: DevOps ajuda com Docker
- Frontend issue: Backend clarifica API
- DevOps issue: Backend/Frontend clara o que é esperado

---

## ✅ SEMANA 2 CHECKLIST (Sexta 19/junho EOD)

- [ ] Backend: API Fretes completo (CRUD)
- [ ] Frontend: PostFrete page
- [ ] Frontend: FindFrete page
- [ ] Frontend: Dashboard updated
- [ ] DevOps: Docker testing done
- [ ] Testing: E2E flow verified
- [ ] Hostinger: Prep guide ready
- [ ] All PRs merged to `dev`
- [ ] Ready for Semana 3 (Matches + Notifications)

---

## 🎬 COMEÇAR AGORA

Semana 2 começa SEGUNDA 13/junho.
Vocês têm 1 semana para features CORE.
Let's GO! 🚀
