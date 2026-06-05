# FreteBR Week 4 - E2E Payment Flow Testing Guide

## Overview
Complete end-to-end testing guide for the payment flow: Order → Payment → Receipt → Rating

---

## Test Scenario 1: Complete Payment Flow

### Step 1: Setup Two User Accounts
```
User 1 (Motorista):
- Email: motorista@test.com
- Password: test123456
- Role: Motorista

User 2 (Shipper):
- Email: shipper@test.com
- Password: test123456
- Role: Shipper
```

### Step 2: Motorista Posts a Frete
1. Login as Motorista
2. Navigate to `/postar-frete`
3. Fill in form:
   - Origin: "São Paulo, SP"
   - Destination: "Rio de Janeiro, RJ"
   - Weight: "500" kg
   - Value: "R$ 1500.00"
   - Description: "Carregamento teste"
4. Click "Postar Frete"
5. Verify frete appears on dashboard

### Step 3: Shipper Finds and Accepts Frete
1. Login as Shipper
2. Navigate to `/procurar-fretes`
3. Find the frete posted by Motorista
4. Click on frete
5. Review details
6. Click "Aceitar Frete" (if available) or similar action
7. Should create a Match

### Step 4: Both Users Chat and Agree on Details
1. Both users navigate to `/meus-matches`
2. Click on the match
3. Both click "Ir para Chat"
4. Exchange messages (simulate agreement on delivery details)
5. Go back to match details

### Step 5: Motorista Marks Delivery as Complete
1. Still logged in as Motorista
2. On MatchDetailPage
3. Check status is "aceito"
4. Click "Marcar como Em Entrega"
5. Status should change to "em_entrega"
6. Click "Marcar como Entregue"
7. Status should change to "finalizado"

### Step 6: Shipper Initiates Payment
1. Switch to Shipper account
2. Navigate to `/meus-matches`
3. Click on the match
4. Should now see **"💳 Fazer Pagamento"** button (prominent green button)
5. Click button
6. Should navigate to `/match/{id}/payment`

### Step 7: PaymentPage Verification
Verify the following on PaymentPage:

✅ **Header**
- "Confirmar Pagamento" title visible
- Back button to match details

✅ **Frete Details Section**
- Origin: "São Paulo, SP"
- Destination: "Rio de Janeiro, RJ"
- Weight: "500 kg"
- Value: "R$ 1,500.00"

✅ **QR Code Section**
- QR code image displays (placeholder is fine)
- Text "Escaneie este código QR..."
- Visible on mobile (minimum 48x48px, target 200x200px+)

✅ **Pix Key Section**
- Pix key displays in copyable input field
- "Copiar" button is visible and clickable
- Button text changes to "✓ Copiado" after clicking
- Button turns green when copied

✅ **Status Section**
- Shows countdown timer (starts at 5:00)
- Timer counts down every second
- Status text: "Aguardando pagamento..."
- Pulse animation on status indicator
- Text: "Verificando status automaticamente a cada 2 segundos"

✅ **Mobile Responsiveness (Test on 375px width)**
- No horizontal scrolling
- QR code fits on screen
- Buttons large enough to tap (minimum 44px height)
- Text readable (minimum 16px on input)
- Spacing consistent
- No layout shifts

### Step 8: Test Pix Key Copy Functionality
1. Click "Copiar" button
2. Verify button text changes to "✓ Copiado"
3. Verify button background changes to green
4. Open another tab and try to paste (verify it's in clipboard)
5. Wait 2 seconds
6. Button should return to original state

### Step 9: Simulate Payment Success (Mock)
For testing purposes, you can:
- Modify PaymentPage to have a "Simular Pagamento Sucesso" button (dev mode)
- OR wait for random success (currently 5% chance every 2 seconds)
- OR manually update payment status in database

Expected behavior after success:
- Page shows "✅ Pagamento Confirmado!"
- Redirect to `/match/{id}/receipt` after ~1.5 seconds

---

## Test Scenario 2: ReceiptPage Verification

### Step 1: Navigate to Receipt (After Payment Success)
- Should automatically redirect after payment confirmation
- OR navigate directly to `/match/{id}/receipt`

### Step 2: Verify Receipt Content

✅ **Success Header**
- Large green checkmark: "✅"
- Title: "Pagamento Confirmado"
- Subtitle: "Seu pagamento foi recebido com sucesso"
- Green border around header

✅ **Receipt Details (Invoice Style)**
- Professional receipt design
- FreteBR header with "Recibo de Pagamento"

✅ **Transaction Details Section**
- Transaction ID: (match ID)
- Valor Pago: "R$ 1,500.00" (in green, larger font)
- Método de Pagamento: "Pix"
- Data e Hora: (current date/time in PT-BR format)

✅ **Frete Details**
- Origem: "São Paulo, SP"
- Destino: "Rio de Janeiro, RJ"
- Peso: "500 kg"
- Status: "Entregue ✅"

✅ **Participants Section**
- REMETENTE box showing Shipper info (blue background)
  - Name
  - Email
- TRANSPORTISTA box showing Motorista info (green background)
  - Name
  - Email

✅ **Action Buttons**
- "Ir para Avaliação ⭐" (blue button)
- "Baixar Recibo 📄" (gray button - for PDF export)
- "Voltar aos Matches" (gray button)

✅ **Mobile Responsiveness**
- Layout stacks properly on mobile
- Text doesn't overflow
- Receipt looks "printable"
- No horizontal scrolling
- Professional appearance maintained

### Step 3: Download Receipt Test
1. Click "Baixar Recibo 📄"
2. File should download as `recibo-{match_id}.html`
3. Open downloaded file in browser
4. Verify all details are there
5. Try to print (Ctrl+P) and verify layout

---

## Test Scenario 3: RatingPage Verification

### Step 1: Navigate to Rating Page
1. Click "Ir para Avaliação ⭐" button on ReceiptPage
2. Should navigate to `/match/{id}/rating`

### Step 2: Verify Page Content

✅ **Header Section**
- "Avalie a Entrega" title visible

✅ **User Info Card**
- Shows target user (e.g., "Avaliando Shipper")
- Displays user avatar (👤 emoji)
- Shows user name
- Shows user email

✅ **Frete Summary**
- Route: "São Paulo, SP → Rio de Janeiro, RJ"
- Value: "R$ 1,500.00"
- Weight: "500 kg"
- Status: "Entregue ✅"

✅ **Rating Section**
- Question: "Como foi sua experiência?"
- 5 large stars (⭐)
- Stars are clickable
- Selected stars are yellow and scaled up
- Unselected stars are gray
- Below stars:
  - Current rating display: "5/5"
  - Rating label: "Excelente" (or appropriate label)

**Rating Labels:**
- ⭐ = "Péssimo" (1 star)
- ⭐⭐ = "Ruim" (2 stars)
- ⭐⭐⭐ = "Neutro" (3 stars)
- ⭐⭐⭐⭐ = "Bom" (4 stars)
- ⭐⭐⭐⭐⭐ = "Excelente" (5 stars)

✅ **Feedback Textarea**
- Label: "Feedback (opcional)"
- Placeholder: "Diga-nos mais sobre sua experiência..."
- Max 500 characters
- Character counter at bottom: "0/500 caracteres"
- Grows to 4 rows

### Step 3: Test Star Rating Interaction
1. Click each star from 1-5
2. Verify:
   - Stars light up correctly
   - Label updates
   - Rating number updates
   - Selected stars are scaled up (125%)

### Step 4: Test Feedback Input
1. Click on textarea
2. Type some feedback: "Ótima entrega! Recomendo."
3. Verify character count updates: "28/500 caracteres"
4. Try typing more (simulate 500+ chars)
5. Verify input stops at 500 chars

### Step 5: Submit Rating
1. Ensure rating is selected (e.g., 5 stars)
2. Optionally add feedback
3. Click "Enviar Avaliação" button
4. Button should show "Enviando Avaliação..." (loading state)
5. After ~1s, should show success page:
   - "✅ Obrigado pela Avaliação!"
   - Message: "Sua avaliação foi registrada com sucesso."
   - "Redirecionando para seus matches..."
6. After 2 seconds, redirect to `/meus-matches`

✅ **Mobile Responsiveness**
- Stars are large and touchable (minimum 48x48px total area)
- Textarea is usable on mobile
- Buttons have good touch targets (44px+ height)
- Text readable on small screens
- No horizontal scrolling

---

## Test Scenario 4: Navigation Flow

### Verify Back Navigation
1. On PaymentPage: Click back button → should go to `/match/{id}`
2. On ReceiptPage: Click "Voltar aos Matches" → should go to `/meus-matches`
3. On RatingPage: Click "Voltar sem Avaliar" → should go to `/meus-matches`

### Verify Forward Navigation
1. On MatchDetailPage: Click "Fazer Pagamento" → goes to `/match/{id}/payment`
2. On PaymentPage: Auto-redirect on payment success → goes to `/match/{id}/receipt`
3. On ReceiptPage: Click "Ir para Avaliação" → goes to `/match/{id}/rating`
4. On RatingPage: Auto-redirect on success → goes to `/meus-matches`

---

## Test Scenario 5: Error Handling

### Test Payment Timeout
1. On PaymentPage, wait for countdown to reach 0
2. Page should show "❌ Pagamento Expirou"
3. Message: "O código QR expirou. Crie um novo pagamento para continuar."
4. Click "Criar Novo Pagamento"
5. Should fetch new payment and reset timer

### Test Network Error (Simulated)
1. Open DevTools (F12)
2. Go to Network tab
3. Throttle connection to "Offline"
4. On PaymentPage, try to fetch payment status
5. Should gracefully handle error (possibly show retry message)
6. Restore connection

### Test Invalid Rating
- Try submitting rating with feedback > 500 chars
- Should prevent submission with error message

---

## Mobile Testing Checklist (CRITICAL)

Test on actual mobile device or use DevTools (F12 → Device Toolbar)

Width: 375px (iPhone SE)

### PaymentPage
- [ ] QR code visible and square
- [ ] Pix key input readable
- [ ] Buttons at least 44px tall
- [ ] No horizontal scrolling
- [ ] Timer readable
- [ ] Copy button works on mobile

### ReceiptPage
- [ ] All text readable (no overflow)
- [ ] Receipt looks "printable"
- [ ] Participant boxes stack vertically
- [ ] Buttons properly spaced
- [ ] No horizontal scrolling

### RatingPage
- [ ] Stars large enough to tap
- [ ] Textarea usable on mobile
- [ ] Character counter visible
- [ ] Buttons have good spacing
- [ ] No horizontal scrolling

---

## Performance Testing

### PageLoad Performance
- [ ] PaymentPage loads in < 2s (with QR code)
- [ ] ReceiptPage loads in < 2s
- [ ] RatingPage loads in < 2s

### Polling Performance (PaymentPage)
- [ ] Status polling doesn't cause lag
- [ ] Timer updates smoothly
- [ ] No memory leaks on long polling

### Browser Compatibility
- [ ] Chrome latest
- [ ] Firefox latest
- [ ] Safari latest
- [ ] Mobile Safari

---

## Acceptance Criteria Checklist

- [ ] PaymentPage shows QR code + Pix key
- [ ] Countdown timer shows expiry
- [ ] Status auto-polls every 2 seconds
- [ ] ReceiptPage shows transaction details
- [ ] RatingPage allows 5-star + feedback
- [ ] Full flow tested: order → payment → receipt → rating
- [ ] Mobile responsive (375px+)
- [ ] Error handling complete (network, timeout, invalid)
- [ ] Loading states showing
- [ ] Success messages clear
- [ ] No console errors
- [ ] All routes protected (ProtectedRoute)

---

## Demo Mode (Optional but Nice)

For demos, add a "Simular Pagamento" button that:
1. Simulates instant payment confirmation
2. Shows "✅ Pagamento Confirmado!" immediately
3. Automatically redirects to receipt

This helps with live demos without actual payment processing.

---

## Troubleshooting

### Issue: PaymentPage not showing
- Check route is registered in App.tsx
- Verify match exists and status is correct
- Check browser console for errors

### Issue: QR code not displaying
- Verify QR code URL is valid
- Check image format (PNG, JPG)
- Try clearing browser cache

### Issue: Timer not counting down
- Check if JavaScript is enabled
- Verify useEffect dependencies
- Check browser console for errors

### Issue: Mobile layout broken
- Use DevTools Device Toolbar to test
- Check responsive classes (sm:, md:, lg:)
- Verify Tailwind CSS is loaded

---

## Notes for Next Steps (SEXTA - 01/julho)

1. Connect to real backend payment API
2. Implement actual Pix QR code generation
3. Add real payment status polling
4. Integrate with payment service (e.g., Stripe, Gerencianet)
5. Add payment history to dashboard
6. Implement rating statistics

---

**Last Updated:** June 30, 2026
**Test Date:** _____________
**Tester:** _____________
**Status:** ✅ PASSED / ❌ FAILED
