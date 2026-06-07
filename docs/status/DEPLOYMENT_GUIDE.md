# FreteBR Production Deployment Guide

## Overview

FreteBR is a FastAPI + React/Next.js marketplace for freight transportation with integrated payment processing via Mercado Pago Pix.

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 13+
- Mercado Pago Business Account
- Node.js 18+
- Python 3.9+

## Environment Setup

### 1. Create `.env` file from `.env.example`

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

#### Database Configuration
```env
POSTGRES_DB=fretebr
POSTGRES_USER=fretebr_user
POSTGRES_PASSWORD=your_secure_password_here_min_12_chars
DATABASE_URL=postgresql://fretebr_user:your_password@db:5432/fretebr
```

Generate a secure password:
```bash
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

#### Security Settings
```env
SECRET_KEY=your_secret_key_min_32_chars
# Generate with:
python -c "import secrets; print(secrets.token_urlsafe(32))"

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Mercado Pago Configuration

1. **Create Mercado Pago Account**
   - Go to https://www.mercadopago.com.br
   - Create a business account
   - Access the Developer Dashboard: https://www.mercadopago.com.br/developers/panel

2. **Get API Credentials**
   - Navigate to "Credenciais" (Credentials)
   - Copy your `ACCESS_TOKEN`
   - Note your `CLIENT_ID` and `CLIENT_SECRET`

3. **Add to `.env`**
   ```env
   MERCADO_PAGO_ACCESS_TOKEN=your_access_token_here
   MERCADO_PAGO_WEBHOOK_SECRET=your_webhook_secret_here
   MERCADO_PAGO_ENVIRONMENT=production  # or sandbox for testing
   ```

4. **Setup Webhook** (After deployment)
   - Go to Mercado Pago Dashboard → Webhooks
   - Add webhook URL: `https://yourdomain.com/api/webhook/mercado-pago`
   - Select events: `payment.created`, `payment.updated`
   - Copy the webhook secret and add to `.env`

#### Twilio Configuration (Optional)
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_SANDBOX_ENABLED=true
```

#### CORS Settings
```env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

#### Application Settings
```env
ENVIRONMENT=production
DEBUG=false
VITE_API_URL=https://api.yourdomain.com
```

## Database Setup

### Using Docker Compose (Recommended)

```bash
# Start database
docker-compose up -d db

# Wait for database to be ready
sleep 10

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Manual PostgreSQL Setup

```bash
# Create database
createdb -U postgres fretebr

# Connect and create user
psql -U postgres -d fretebr

# In psql:
CREATE USER fretebr_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fretebr TO fretebr_user;
```

## Building and Running

### Option 1: Docker Compose (Production)

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm run start
```

## Payment Flow

### Complete Payment Process

1. **Motorista Posts Frete**
   - Creates freight listing with details and price

2. **Shipper Accepts**
   - Shipper finds frete and clicks "Accept"
   - Match created, chat enabled

3. **Chat Communication**
   - Both parties negotiate details via chat

4. **Delivery Completed**
   - Motorista updates status to "em_entrega"
   - After delivery, updates to "finalizado"

5. **Payment (Pix)**
   - Shipper initiates payment
   - Receives QR code for Pix payment
   - Scans with any bank app
   - Payment confirmed automatically
   - Motorista receives notification

6. **Receipt**
   - After payment, receipt is available
   - Shows transaction details

### API Endpoints

#### Payment Management

```bash
# Create payment request
POST /api/payments
{
  "match_id": 1,
  "amount": 500.0
}
Response:
{
  "transaction_id": 1,
  "qr_code_data": "00020126...",
  "expires_in_seconds": 1800,
  "expires_at": "2024-01-15T10:30:00Z"
}

# Get payment status
GET /api/payments/{transaction_id}
Response:
{
  "transaction_id": 1,
  "status": "pendente|pago|falhou|cancelado|expirado",
  "amount": 500.0,
  "expires_at": "2024-01-15T10:30:00Z"
}

# Get receipt (after payment)
GET /api/payments/{match_id}/receipt
Response:
{
  "transaction_id": 1,
  "match_id": 1,
  "amount": 500.0,
  "status": "pago",
  "payment_date": "2024-01-15T10:25:00Z"
}

# List user transactions
GET /api/payments/1/list?status=pago&limit=50
Response: [
  { "transaction_id": 1, "status": "pago", ... },
  ...
]

# Webhook (Mercado Pago calls this)
POST /api/webhook/mercado-pago
# Automatically updates transaction status
```

## Security Best Practices

### Environment Variables
- Never commit `.env` to git
- Use different credentials for staging/production
- Rotate API keys regularly

### Database
- Use strong passwords
- Enable SSL connections in production
- Regular backups
- Limit database access to backend only

### API
- Enable CORS only for your domain(s)
- Use HTTPS in production
- Rate limiting (recommended)
- Input validation (implemented)

### Payments
- Never log full payment details
- Use webhook signatures (configured)
- Monitor payment status changes
- Implement fraud detection (optional)

## Monitoring

### View Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Manual
tail -f /var/log/fretebr/backend.log
```

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "service": "FreteBR Backend"}
```

### Database Backups

```bash
# Backup
pg_dump -U fretebr_user -h localhost fretebr > backup.sql

# Restore
psql -U fretebr_user -h localhost fretebr < backup.sql
```

## Troubleshooting

### Payment Issues

**"Payment service unavailable"**
- Check MERCADO_PAGO_ACCESS_TOKEN in .env
- Verify Mercado Pago API status
- Check network connectivity
- Review API logs: `docker-compose logs backend | grep "Payment"`

**"Transaction not found"**
- Ensure match_id is correct
- Verify match status is "finalizado"
- Check database has transaction records

**Webhook not received**
- Verify webhook URL in Mercado Pago dashboard
- Check firewall/NAT settings
- Verify webhook secret is correct
- Check logs for webhook errors

### Database Issues

**Connection refused**
```bash
# Check database is running
docker-compose logs db

# Restart database
docker-compose restart db

# Verify connection
psql -U fretebr_user -h localhost -d fretebr -c "SELECT 1"
```

**Migration failures**
```bash
# Check migration status
alembic current

# View all migrations
alembic history

# Rollback last migration
alembic downgrade -1
```

### API Issues

**502 Bad Gateway**
- Check backend logs
- Verify backend is running
- Check port conflicts

**CORS errors**
- Verify frontend URL in ALLOWED_ORIGINS
- Check browser console for error details

## Performance Optimization

### Database
- Indexes created for: match_id, motorista_id, shipper_id, status, created_at
- Connection pooling configured
- Query optimization in progress

### Backend
- Caching implemented for frequently accessed data (future)
- Async operations where possible
- Rate limiting (recommended implementation)

### Frontend
- Code splitting configured
- Image optimization
- Bundle size monitoring

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs, check payment reconciliation
- **Weekly**: Backup database, verify webhook delivery
- **Monthly**: Update dependencies, security patches
- **Quarterly**: Performance review, scaling assessment

### Dependency Updates

```bash
# Check for updates
pip list --outdated
npm outdated

# Update
pip install --upgrade package-name
npm update

# Test before deploying to production
```

## Support

- Documentation: See README.md
- Issues: GitHub Issues
- Email: support@fretebr.com.br

## Version History

- **v0.1.0** (2024-01-15): Initial release with Mercado Pago Pix integration
  - User authentication (motorista/shipper)
  - Freight marketplace
  - Match acceptance and chat
  - Mercado Pago Pix payments
  - Real-time notifications (Twilio WhatsApp)
