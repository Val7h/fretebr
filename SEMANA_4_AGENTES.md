# FreteBR - SEMANA 4 AGENTES
## PAYMENT INTEGRATION + HOSTINGER DEPLOYMENT + LAUNCH 🚀

**Data:** 27 de Junho a 01 de Julho, 2026  
**Goal:** Pix payment working + Deploy Hostinger + LIVE!  
**Owner:** Valth Menezes Guimarães  
**GitHub:** Val7h/fretebr  
**Status:** FINAL WEEK - GO LIVE

---

## 🎯 DELIVERABLES FINAIS (Sexta-feira 01/julho EOD)

- [ ] Backend: Mercado Pago Pix integration
- [ ] Backend: Payment endpoints (create, verify, webhook)
- [ ] Frontend: Payment page (checkout)
- [ ] Frontend: Receipt page
- [ ] Frontend: Rating/Review page
- [ ] Database: Transactions table
- [ ] Docker: Production-ready configuration
- [ ] Hostinger: Deploy complete (LIVE!)
- [ ] Monitoring: Logs + health checks running
- [ ] E2E: Full payment flow tested

**RESULTADO:** FreteBR LIVE em https://fretebr.com.br (ou seu domínio) 🎉

---

## 👥 3 AGENTES EM PARALELO

### **AGENTE 1: Backend Developer**

**Responsabilidade:** Pix Payment Integration

#### TAREFAS:

**Segunda (27/junho):**
- [ ] Create Mercado Pago account (if not done)
  - Go to mp.me
  - Create business account
  - Get API credentials: ACCESS_TOKEN, CLIENT_ID, CLIENT_SECRET
  - Switch from sandbox to production
- [ ] Create `backend/app/models/transaction.py`:
  - Transaction model with: id, match_id (FK), motorista_id, shipper_id, amount, status (pending/paid/failed), mp_id (mercado pago ID), created_at
- [ ] Create Alembic migration
- [ ] Update .env.example: MERCADO_PAGO_ACCESS_TOKEN
- [ ] PR #16: "Add Mercado Pago credentials + Transaction model"

**Terça (28/junho):**
- [ ] Create `backend/app/schemas/transaction.py`:
  - TransactionCreate, TransactionResponse
- [ ] Create `backend/app/crud/transaction.py`:
  - create_transaction(db, match_id, amount)
  - get_transaction(db, transaction_id)
  - update_transaction_status(db, transaction_id, status)
- [ ] Create `backend/app/services/payments.py`:
  - create_payment_pix(amount, match_id) → calls Mercado Pago API
  - verify_payment(mp_id) → checks if paid
  - handle_webhook(payload) → updates transaction status when user pays
  - get_qr_code(payment_id) → returns QR code for Pix
- [ ] PR #17: "Mercado Pago Pix service + CRUD"

**Quarta (29/junho):**
- [ ] Create `backend/app/api/payments.py` with endpoints:
  - POST /api/payments (create Pix payment)
    * Input: { match_id, amount }
    * Calls Mercado Pago API
    * Returns: { qr_code, payment_id, expiry }
  - GET /api/payments/{id} (get payment status)
  - POST /api/webhook/mercado-pago (webhook for payment confirmation)
    * Mercado Pago calls this when user pays
    * Updates transaction status to "paid"
  - GET /api/matches/{id}/receipt (get transaction receipt after paid)
- [ ] Include router in main.py
- [ ] PR #18: "Payment API endpoints"

**Quinta (30/junho):**
- [ ] Create tests: `backend/test_payments.py`:
  - test_create_payment() → creates transaction + gets QR code
  - test_verify_payment() → checks status
  - test_webhook_payment_confirmed() → updates status when MP sends webhook
  - test_payment_not_allowed_before_delivery() → only after "finalizado"
  - All tests passing
- [ ] Manual testing:
  - docker-compose up
  - Create full flow: motorista post → shipper accept → chat → delivery
  - When "finalizado": create payment
  - Test QR code generation
  - Simulate webhook (mark paid)
- [ ] PR #19: "Payment testing complete"

**Sexta (01/julho):**
- [ ] Final verification:
  - All payment endpoints working
  - Mercado Pago credentials from .env (not hardcoded)
  - Error handling: MP API failure shows error
  - Transactions stored in DB
  - Webhook working
  - Docker rebuild OK
- [ ] Create README section: "How to use Mercado Pago API"
- [ ] PR #20: "Payment integration complete - Production ready"

#### ACCEPTANCE CRITERIA:
```
✅ Mercado Pago account created
✅ API credentials from .env
✅ Transaction model + migrations
✅ POST /api/payments creates Pix payment
✅ GET /api/payments/{id} returns status
✅ QR code generation working
✅ Webhook endpoint accepts MP webhooks
✅ Status updates when payment confirmed
✅ All tests passing
✅ No hardcoded secrets
✅ Docker working
```

---

### **AGENTE 2: Frontend Developer**

**Responsabilidade:** Payment Pages + Final UI

#### TAREFAS:

**Segunda (27/junho):**
- [ ] Pull latest dev
- [ ] Update routes:
  - /match/{id}/payment → PaymentPage (protected)
  - /match/{id}/receipt → ReceiptPage (protected)
  - /match/{id}/rating → RatingPage (protected)
- [ ] Create `frontend/src/pages/PaymentPage.tsx`:
  - Show match details (origem, destino, valor)
  - Show QR code image (from backend)
  - Show payment expiry countdown
  - "Copy Pix Key" button
  - "Open WhatsApp to ask" button (optional)
  - Status: "Aguardando pagamento..." (polling every 2s)
  - On success: redirect to /match/{id}/receipt
  - On error/timeout: show error message
- [ ] PR #16: "Add Payment page with QR code"

**Terça (28/junho):**
- [ ] Create `frontend/src/pages/ReceiptPage.tsx`:
  - Show payment receipt:
    * Transaction ID
    * Amount paid
    * Date/time
    * Status: "Pago ✅"
    * Frete details
  - "Ir para Avaliação" button → /match/{id}/rating
  - "Voltar aos Matches" button
- [ ] Create `frontend/src/pages/RatingPage.tsx`:
  - Rate motorista (shipper rates) or shipper (motorista rates)
    * 5-star rating
    * Optional text feedback
  - Submit button
  - On success: show "Obrigado!" + redirect to /meus-matches
  - Rating appears on user profile
- [ ] Create `frontend/src/services/paymentApi.ts`:
  - createPayment(match_id, amount) → POST /api/payments
  - getPaymentStatus(payment_id) → GET /api/payments/{id}
  - getReceipt(match_id) → GET /api/matches/{id}/receipt
- [ ] PR #17: "Add Payment + Rating pages"

**Quarta (29/junho):**
- [ ] Update `frontend/src/pages/MatchDetailPage.tsx`:
  - Add "Fazer Pagamento" button (appears when match status = "finalizado")
  - Button only visible for shipper (who pays)
  - Click → /match/{id}/payment
- [ ] Update DashboardPage:
  - Add "Histórico de Pagamentos" link
  - Show recent transactions
- [ ] Create `frontend/src/components/PaymentStatus.tsx`:
  - Reusable component showing payment status
  - Polling for updates
- [ ] Test payment flow end-to-end:
  - Motorista post → shipper accept → chat → delivery marked
  - Shipper clicks "Fazer Pagamento"
  - Goes to PaymentPage → sees QR code
  - Simulate payment (mock API)
  - Redirects to ReceiptPage
  - Shows receipt
  - Go to RatingPage → rate
- [ ] PR #18: "Payment integration + Final UI"

**Quinta (30/junho):**
- [ ] Styling review (final):
  - QR code displays nicely
  - Payment status clear
  - Receipt formatted like real receipt
  - Responsive on mobile (critical for payments!)
- [ ] Test on mobile (375px) - payment UX must be perfect
- [ ] Error handling:
  - Network error during payment → show retry
  - Timeout → show error
  - Invalid QR code → show error
- [ ] Create help page: "Como pagar com Pix"
  - Screenshots of QR code
  - Copy-paste Pix key instructions
  - FAQ
- [ ] PR #19: "Final UI polish + Mobile optimization"

**Sexta (01/julho):**
- [ ] Final testing:
  - Full payment flow: order → QR → pay (mock) → receipt → rating
  - All pages mobile-responsive
  - All error states handled
  - Loading states showing
- [ ] Create demo mode (optional):
  - Allow testing without real payments
  - Mock QR code
  - Instant "payment" simulation
- [ ] Build verification
- [ ] PR #20: "Payment features complete - Production ready"

#### ACCEPTANCE CRITERIA:
```
✅ PaymentPage shows QR code + Pix key
✅ Countdown timer shows expiry
✅ Status polls for payment confirmation
✅ ReceiptPage shows transaction details
✅ RatingPage allows 5-star + feedback
✅ All pages responsive (mobile critical!)
✅ Error handling complete
✅ Loading states showing
✅ Full flow tested
✅ Demo mode working (optional)
```

---

### **AGENTE 3: DevOps / Deployment**

**Responsabilidade:** Hostinger Deployment + Go-Live

#### TAREFAS:

**Segunda (27/junho):**
- [ ] Prepare Hostinger:
  - SSH into Hostinger VPS
  - Clone repo: git clone https://github.com/Val7h/fretebr.git
  - Create .env with production values:
    - DATABASE_URL (PostgreSQL on Hostinger)
    - SECRET_KEY
    - MERCADO_PAGO_ACCESS_TOKEN
    - TWILIO_ACCOUNT_SID, AUTH_TOKEN, PHONE_NUMBER
  - docker-compose build
  - Create volumes for persistent data
- [ ] Setup SSL:
  - Let's Encrypt certificate (free)
  - Nginx reverse proxy
  - Port 443 (https)
- [ ] Create `HOSTINGER_DEPLOYMENT_FINAL.md`:
  - Step-by-step deployment
  - Domain setup
  - SSL setup
  - Database backups
- [ ] PR #16: "Hostinger deployment guide"

**Terça (28/junho):**
- [ ] Test deployment:
  - docker-compose up -d on Hostinger
  - Verify all 3 services healthy
  - Test endpoints: http://{ip}:8000/health
  - Test frontend: http://{ip}:3000
  - Test database: psql from host
- [ ] Setup monitoring:
  - Basic health check scripts
  - Logs accessible
  - Error notifications (optional: email on crash)
- [ ] Create `PRODUCTION_CHECKLIST.md`:
  - Pre-launch verification
  - All services healthy
  - Database backed up
  - SSL working
  - API responding
  - Payment system ready
- [ ] PR #17: "Monitoring + health checks setup"

**Quarta (29/junho):**
- [ ] Final pre-launch testing:
  - Full payment flow on production
  - WhatsApp notifications on production
  - Chat working
  - All pages loading fast (< 2s)
  - No errors in logs
  - Database transactions logged
- [ ] Load testing (if time):
  - Simulate 10 concurrent users
  - Check performance
  - Memory usage OK
  - Database OK under load
- [ ] Create incident response plan:
  - What to do if payment system down
  - What to do if WhatsApp down
  - Rollback procedure
  - Emergency contacts
- [ ] PR #18: "Pre-launch testing complete"

**Quinta (30/junho):**
- [ ] Soft launch (BETA):
  - Deploy to production
  - Internal testing only (you + team)
  - Monitor logs closely
  - Test all features
  - Fix any bugs immediately
- [ ] Create `LAUNCH_CHECKLIST.md`:
  - Final verification before public launch
  - All systems operational
  - Payments working
  - Notifications working
  - Chat working
  - Ratings working
  - Performance acceptable
  - Backups automated
- [ ] PR #19: "Soft launch complete - ready for public"

**Sexta (01/julho) - LAUNCH DAY:**
- [ ] 🚀 LAUNCH:
  - Deploy domain: fretebr.com.br (or IP if no domain)
  - Point DNS to Hostinger IP
  - Test on real domain
  - Monitor first hour closely
  - Be ready to rollback if needed
- [ ] Post-launch monitoring:
  - Watch logs for errors
  - Monitor performance
  - Verify payments processing
  - Verify notifications sending
  - Track any issues
- [ ] Create incident log
- [ ] Create post-launch report:
  - Launch time
  - Any issues encountered
  - How many users signed up
  - First payments processed
  - Next steps (scaling, features, etc)
- [ ] PR #20: "🚀 LAUNCH COMPLETE - FreteBR is LIVE!"

#### ACCEPTANCE CRITERIA:
```
✅ Hostinger deployment working
✅ Domain pointing to server
✅ SSL certificate installed (HTTPS)
✅ All services healthy on production
✅ Database backups automated
✅ Payment system verified
✅ WhatsApp notifications verified
✅ Logs accessible + monitored
✅ Performance acceptable (< 2s load)
✅ Incident response plan ready
✅ All PRs merged
✅ 🚀 LIVE and publicly accessible
```

---

## 📅 TIMELINE (Super Compressed - 5 DAYS)

| Dia | Backend | Frontend | DevOps |
|-----|---------|----------|--------|
| Seg (27) | MP account + Tx model | Payment page | Hostinger prep |
| Ter (28) | MP Pix service | Receipt page | Setup monitoring |
| Qua (29) | Payment endpoints | Rating page | Pre-launch test |
| Qui (30) | Payment tests | Final polish | Soft launch |
| Sex (01) | Final verification | Production ready | 🚀 LAUNCH! |

---

## 🎯 FINAL CHECKLIST (01/julho EOD)

- [ ] Backend: All payment endpoints working
- [ ] Frontend: Payment + Receipt + Rating pages complete
- [ ] DevOps: Hostinger deployment successful
- [ ] Payment: Mercado Pago Pix integration verified
- [ ] Security: All secrets in .env (no hardcoding)
- [ ] Testing: Full payment flow tested
- [ ] Monitoring: Logs + health checks active
- [ ] Domain: DNS pointing to Hostinger
- [ ] SSL: HTTPS working
- [ ] Launch: 🚀 FreteBR is LIVE!

---

## 🎊 AFTER LAUNCH

**Next Steps (não faz parte desta semana):**
1. Monitor logs for bugs
2. Add features based on user feedback
3. Scale infrastructure if needed
4. Marketing + user acquisition
5. Iterate on UX/UI

---

## 🚀 COMEÇAR AGORA

SEMANA 4 = FINAL WEEK = LAUNCH WEEK

Let's make FreteBR LIVE! 🎉🚀
