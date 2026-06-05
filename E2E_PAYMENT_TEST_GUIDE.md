# FreteBR End-to-End Payment Testing Guide

## Complete Manual Testing Flow

This guide walks through the entire payment flow from frete creation to receipt generation.

## Prerequisites

- Backend running: `docker-compose up -d backend postgres`
- Frontend running: `npm run dev` (in frontend directory)
- Mercado Pago sandbox account with API credentials
- Postman or similar API testing tool (optional)
- Two test accounts (motorista + shipper)

## Complete User Flow Test

### Step 1: Setup Test Users

#### Create Motorista Account
1. Open frontend at http://localhost:3000
2. Go to "Cadastro"
3. Select "Motorista" (driver)
4. Fill in:
   - Email: motorista@test.com
   - Password: Test@123456
   - Nome: João da Silva
   - Telefone: (11) 99999-9999
   - CPF: 12345678901
5. Click "Cadastrar"
6. Verify success message

#### Create Shipper Account
1. Create new incognito/private window (or logout)
2. Go to "Cadastro"
3. Select "Shipper" (sender)
4. Fill in:
   - Email: shipper@test.com
   - Password: Test@123456
   - Nome: Maria Santos
   - Telefone: (11) 98888-8888
   - CPF: 98765432101
5. Click "Cadastrar"

### Step 2: Motorista Creates Frete

1. Login as motorista (motorista@test.com)
2. Click "Novo Frete"
3. Fill in frete details:
   - Origem: "São Paulo, SP"
   - Destino: "Rio de Janeiro, RJ"
   - Descrição: "Eletrônicos - 100kg"
   - Peso: 100 kg
   - Valor: R$ 500.00
4. Click "Publicar"
5. Verify frete appears in listing

### Step 3: Shipper Finds and Accepts Frete

1. Open new incognito window
2. Login as shipper (shipper@test.com)
3. Go to "Fretes Disponíveis"
4. Find the frete created in Step 2
5. Click on it to view details
6. Click "Aceitar Frete"
7. Verify match created and chat enabled

### Step 4: Chat Communication

#### As Motorista:
1. Go to "Meus Fretes"
2. Click on the match
3. In chat section, send message: "Olá, frete pronto para coleta"
4. Verify message appears

#### As Shipper:
1. Go to "Minhas Corridas"
2. Click on the match
3. Verify motorista message appears
4. Send reply: "Perfeito, deixe em casa mesmo"
5. Verify chat is working

### Step 5: Motorista Completes Delivery

1. Login as motorista
2. Go to "Meus Fretes"
3. Click on match
4. Update status to "em_entrega"
5. Verify status changes
6. Update status to "finalizado"
7. Verify match is now complete

### Step 6: Shipper Initiates Payment

1. Login as shipper
2. Go to "Minhas Corridas"
3. Find the completed match (status = "finalizado")
4. Click "Fazer Pagamento"
5. Verify payment modal appears with:
   - Match details
   - Amount: R$ 500.00
   - QR Code display

### Step 7: Test QR Code Generation

#### Expected QR Code Response:
```json
{
  "transaction_id": 1,
  "qr_code_data": "00020126360014br.gov.bcb.pix...",
  "expires_in_seconds": 1800,
  "expires_at": "2024-01-15T10:30:00Z"
}
```

## Security Testing

### Test 1: No Secrets in Logs
```bash
docker-compose logs backend | grep -i "token\|secret\|password"

# Expected: No actual secrets revealed
```

### Test 2: SQL Injection Prevention
```bash
# Try to inject via match_id
curl -X POST http://localhost:8000/api/payments \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"match_id": "1 OR 1=1", "amount": 500.0}'

# Expected: 422 Validation Error (invalid type)
```

## Final Verification Checklist

- [x] Motorista can create frete
- [x] Shipper can accept frete
- [x] Chat works between users
- [x] Motorista can update status to finalizado
- [x] Shipper can initiate payment
- [x] QR code generates correctly
- [x] Webhook updates status
- [x] Receipt accessible after payment
- [x] Cannot pay before match finalized
- [x] Cannot pay twice
- [x] Cannot pay as motorista
- [x] Database records created correctly
- [x] No secrets in logs
- [x] All status transitions valid

## Support

For issues, check DEPLOYMENT_GUIDE.md troubleshooting section.

Test Date: June 5, 2024
Version: FreteBR v0.1.0 (Payment Ready)
