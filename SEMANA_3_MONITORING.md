# Semana 3 Monitoring & Cost Management Guide - FreteBR

## Overview
Comprehensive guide for monitoring FreteBR WhatsApp notifications, tracking costs, and managing production readiness.

---

## Twilio Dashboard Monitoring

### Access Twilio Console
```
URL: https://console.twilio.com
Email: (your Twilio account email)
Password: (your Twilio password)
```

### Primary Monitoring Locations

#### 1. Message Logs (Most Important)
**Path**: Messaging → Logs → Message Log

**What to Monitor**:
- All WhatsApp messages sent
- Delivery status (queued, sent, delivered, read, failed)
- Error details if messages fail
- Timestamp and recipient information

**How to Check**:
1. Open [Twilio Console](https://console.twilio.com)
2. Click "Messaging" in left sidebar
3. Click "Logs" → "Message Log"
4. View all messages from last 30 days
5. Click any message to see details

**Key Columns**:
| Column | Purpose | Good Value | Bad Value |
|--------|---------|-----------|-----------|
| To | Recipient phone | +5583993476410 | Invalid/missing |
| From | Sender (Twilio) | +1234567890 | Wrong number |
| Status | Delivery status | delivered, read | failed, undelivered |
| Body | Message content | "Novo Frete..." | Empty/truncated |
| Age | When sent | Minutes ago | Hours ago (delayed) |

**Filter Tips**:
- Filter by date: "Last 24 hours" (for recent tests)
- Filter by status: "All" (see failures)
- Search by phone: "+5583993476410" (single user)
- Search by keyword: "Frete" (find specific messages)

---

#### 2. Usage & Billing
**Path**: Billing → Usage

**What to Track**:
- Monthly message count
- Cost per message
- Total cost to date
- Remaining free trial budget

**How to Check**:
1. Open [Twilio Console](https://console.twilio.com)
2. Click "Billing" in left sidebar
3. Click "Usage" → "Breakdown by service"
4. View Messages usage

**Cost Calculation**:
```
Messages Sent: 10
Cost per message: $0.005 USD
Total cost: 10 × $0.005 = $0.05 USD
Remaining budget: $15.00 - $0.05 = $14.95 USD
```

---

#### 3. Account Overview
**Path**: Account → General Settings

**What to Verify**:
- Account status: "Active" (not suspended)
- Free trial status: Time remaining
- Account Type: "Free Trial" (until upgrade)
- Phone numbers verified

**Important**: If account shows "Suspended", billing is locked. Contact Twilio support.

---

## Backend Monitoring

### View Real-Time Logs

```bash
# Terminal: Watch backend logs live
docker-compose logs -f backend

# Or filter for specific keywords
docker-compose logs -f backend | grep -E "Match|WhatsApp|Notification|ERROR"
```

### What to Look For in Logs

#### Successful Notification
```
[INFO] Creating match ID: 1
[INFO] WhatsApp notification sent successfully. Message SID: SMxxxxx..., To: +5583993476410
[INFO] Match created and notification queued
```

#### Failed Notification (Expected Failure - Graceful)
```
[INFO] Creating match ID: 1
[WARNING] Twilio credentials not configured. Skipping notification.
[INFO] Match created (notification skipped)
```

#### Error (Unexpected - Needs Investigation)
```
[ERROR] Failed to send WhatsApp notification: Authentication failed
[ERROR] Twilio phone number not configured
[ERROR] Invalid phone number format
```

### Log Levels

- `[DEBUG]` - Detailed information (rarely needed)
- `[INFO]` - Normal operation
- `[WARNING]` - Something unexpected (non-critical)
- `[ERROR]` - Something failed (critical)
- `[CRITICAL]` - System down

**Response**: If you see ERROR or CRITICAL, restart backend:
```bash
docker-compose restart backend
```

---

## Database Monitoring

### Check Database Health

```bash
# Is database running?
docker-compose ps postgres

# Expected output:
# CONTAINER      STATUS
# fretebr_postgres    Up (healthy)
```

### Monitor Tables

#### Matches Created
```bash
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT COUNT(*) as total_matches, 
          status, 
          COUNT(*) as count 
   FROM matches 
   GROUP BY status 
   ORDER BY count DESC;"

# Example output:
#  total_matches | status    | count
# ---------------+-----------+-------
#        5       | finalizado|   3
#        5       | aceito    |   1
#        5       | pendente  |   1
```

#### Messages Sent
```bash
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT COUNT(*) as total_messages FROM messages;"

# Example output:
#  total_messages
# ----------------
#        25
```

#### Users Created
```bash
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT COUNT(*) as total_users, 
          tipo, 
          COUNT(*) as count 
   FROM users 
   GROUP BY tipo;"

# Example output:
#  total_users | tipo      | count
# ------+-------+-------
#   3   | motorista |   2
#   3   | embarcador|   1
```

### Verify Data Integrity

```bash
# Check orphaned matches (shouldn't exist)
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT m.id FROM matches m 
   LEFT JOIN fretes f ON m.frete_id = f.id 
   WHERE f.id IS NULL;"

# Expected: No results (zero rows returned)
```

---

## Cost Tracking

### Weekly Cost Report

**Day 1 (Monday)**:
- Messages sent: 5 (setup testing)
- Cost: 5 × $0.005 = $0.025 USD
- Budget remaining: $15.00 - $0.025 = $14.975 USD

**Day 2 (Tuesday)**:
- Messages sent: 10 (dependency testing)
- Cost: 10 × $0.005 = $0.05 USD
- Cumulative: $0.075 USD
- Budget remaining: $14.925 USD

**Day 3 (Wednesday)**:
- Messages sent: 15 (testing guide)
- Cost: 15 × $0.005 = $0.075 USD
- Cumulative: $0.15 USD
- Budget remaining: $14.85 USD

**Day 4 (Thursday)**:
- Messages sent: 20 (E2E testing)
- Cost: 20 × $0.005 = $0.10 USD
- Cumulative: $0.25 USD
- Budget remaining: $14.75 USD

**Day 5 (Friday)**:
- Messages sent: 10 (final verification)
- Cost: 10 × $0.005 = $0.05 USD
- Cumulative: $0.30 USD
- **Budget remaining: $14.70 USD**

### Monthly Projection

```
Week 1 (Dev): $0.30
Week 2 (Dev): $0.50 (more testing)
Week 3 (Dev): $0.75 (feature completion)
Week 4 (Prod): $5.00 (100 live users × 50 msg/user/month = 5000 msg)

Monthly cost estimate: ~$7 USD (well under budget)
Annual cost estimate: ~$85 USD
```

### Budget Alert

- **Free trial**: $15.00 USD
- **Alert at**: $12.00 (80% used)
- **Critical at**: $14.50 (97% used)
- **Action**: Upgrade account before hitting $15

---

## Health Checks

### Quick Health Check (Automated)

```bash
# Run every 5 minutes
watch -n 300 'curl -s http://localhost:8000/health | jq ".status"'

# Expected: "ok"
# If error: docker-compose logs backend | tail -20
```

### Full System Health Check (Manual)

```bash
#!/bin/bash
# save as: health_check.sh
# run with: bash health_check.sh

echo "=== FreteBR System Health Check ==="
echo ""

# 1. Docker status
echo "1. Docker Status:"
docker-compose ps
echo ""

# 2. Backend health
echo "2. Backend Health:"
curl -s http://localhost:8000/health | jq "."
echo ""

# 3. Database connection
echo "3. Database Connection:"
docker-compose exec postgres pg_isready -U fretebr
echo ""

# 4. Twilio credentials
echo "4. Twilio Configuration:"
docker-compose exec backend python -c "import os; print('Account SID:', 'SET' if os.getenv('TWILIO_ACCOUNT_SID') else 'MISSING')"
echo ""

# 5. Recent errors
echo "5. Recent Errors (last 10):"
docker-compose logs backend | grep "ERROR" | tail -10
echo ""

# 6. Message count
echo "6. Message Count (last hour):"
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT COUNT(*) FROM messages WHERE created_at > NOW() - INTERVAL '1 hour';"
echo ""

echo "=== Health Check Complete ==="
```

### When to Alert

| Issue | Severity | Action |
|-------|----------|--------|
| Backend down | CRITICAL | Restart: `docker-compose restart backend` |
| Database down | CRITICAL | Restart: `docker-compose up postgres -d` |
| Twilio auth failure | HIGH | Check credentials, regenerate token |
| High error rate (>10% failures) | HIGH | Check logs, investigate root cause |
| Free trial budget 80% used | MEDIUM | Plan account upgrade |
| Messages delayed >5min | MEDIUM | Check Twilio status page |
| Database errors | MEDIUM | Check logs, backup data |

---

## Alerting Strategy

### Email Alerts (for Production)

When upgrading to production, set up email alerts:

**Twilio Alerts**:
1. Go to [Twilio Console](https://console.twilio.com)
2. Account → Security → Email preferences
3. Enable: "Billing alerts"
4. Set: "Alert when balance drops below $5"

**Docker Alerts** (via external monitoring):
- Uptime Robot (free tier): Monitor `http://backend:8000/health`
- Sentry (free tier): Capture backend errors
- CloudWatch (AWS): Log and monitor metrics

### Example Alert Rules

**Rule 1**: If messages_failed > 5 in 1 hour
```
Severity: High
Action: Email admin, check Twilio dashboard
Recovery: Verify phone numbers, regenerate credentials
```

**Rule 2**: If backend response_time > 2 seconds
```
Severity: Medium
Action: Log and investigate
Recovery: Check database queries, optimize slow endpoints
```

**Rule 3**: If free trial budget < $2 remaining
```
Severity: Low
Action: Email reminder to upgrade
Recovery: Upgrade to paid account
```

---

## Performance Metrics

### Key Metrics to Track

#### Message Delivery Time
```bash
# Measure time from request to Twilio response
# Expected: < 1 second
# Goal: < 500ms

# Log entry example:
# [INFO] Message sent in 0.342 seconds (SID: SMxxxxx)
```

#### Match Creation Latency
```bash
# Measure time from POST /matches to WhatsApp queued
# Expected: < 2 seconds
# Goal: < 1 second

# Benchmark: docker-compose exec backend python -c "
from timeit import timeit
import requests
print(f'Match creation time: {timeit(...)} seconds')
"
```

#### Database Query Performance
```bash
# Check slow queries
docker-compose exec postgres psql -U fretebr -d fretebr_db -c \
  "SELECT query, calls, mean_time FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;"
```

#### Error Rate
```bash
# Calculate error percentage
ERROR_COUNT=$(docker-compose logs backend | grep "ERROR" | wc -l)
TOTAL_REQUESTS=$(docker-compose logs backend | grep "POST /api/matches" | wc -l)
ERROR_RATE=$((ERROR_COUNT * 100 / TOTAL_REQUESTS))
echo "Error rate: ${ERROR_RATE}%"

# Target: < 1% errors
```

### SLA (Service Level Agreement)

For MVP (Week 3-4):
- **Availability**: 95% (production)
- **Message Delivery**: 99% (should reach phones)
- **Latency**: < 2 seconds (match to notification)
- **Data Persistence**: 100% (no data loss)

---

## Production Monitoring Setup

Before deploying to Hostinger (Week 4), set up:

### 1. Log Aggregation
```bash
# Docker logs to file
docker-compose logs backend > logs/backend.log &
docker-compose logs postgres > logs/postgres.log &

# Or use centralized logging:
# - Papertrail (free tier)
# - Loggly (free tier)
# - ELK Stack (self-hosted)
```

### 2. Uptime Monitoring
```bash
# Check every 5 minutes
curl -f http://localhost:8000/health || send_alert

# Or use Uptime Robot:
# - Add monitoring URL: http://backend:8000/health
# - Check interval: Every 5 minutes
# - Notification: Email on failure
```

### 3. Database Backups
```bash
# Backup database daily
docker-compose exec postgres pg_dump -U fretebr fretebr_db > backup_$(date +%Y%m%d).sql

# Test restore:
psql -U fretebr -d fretebr_db < backup_20240623.sql
```

### 4. Cost Monitoring
```bash
# Check Twilio billing daily
curl -s -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Balance" \
  | jq ".balance"

# Alert if balance drops below $2
```

---

## Troubleshooting Guide

### Issue: WhatsApp Messages Not Being Sent

**Symptoms**:
- Match created but no WhatsApp notification
- Backend logs don't show Twilio call

**Check**:
1. Twilio credentials configured?
   ```bash
   docker-compose exec backend python -c "import os; print(os.getenv('TWILIO_ACCOUNT_SID'))"
   # Should print: ACxxxxx...
   ```

2. Phone numbers valid?
   ```bash
   # Check backend logs
   docker-compose logs backend | grep -i "invalid\|phone"
   ```

3. Sandbox joined?
   - Go to Twilio Console → Messaging → WhatsApp
   - Check: Your phone in sandbox joined list
   - If not: Send "join [code]" to Twilio number

**Fix**:
```bash
# Verify credentials
cat .env | grep TWILIO

# If missing, add and restart
docker-compose restart backend

# Test manually:
curl -X POST http://localhost:8000/api/matches \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"frete_id": 1, "valor_final": 500}'

# Check logs
docker-compose logs backend | grep -i "whatsapp"
```

---

### Issue: Database Connection Errors

**Symptoms**:
- 500 errors when creating matches
- Backend logs: "Connection refused"

**Check**:
```bash
docker-compose ps postgres

# Should show: Up (healthy)
# If down: docker-compose up postgres -d
```

**Fix**:
```bash
# Restart database
docker-compose restart postgres

# Wait for health check
sleep 10

# Restart backend
docker-compose restart backend

# Verify connection
docker-compose logs backend | grep -i "database\|connected"
```

---

### Issue: Twilio Authentication Failed

**Symptoms**:
- Backend logs: "Authentication failed"
- Twilio console shows no messages

**Check**:
1. Is token valid?
   ```bash
   cat .env | grep TWILIO_AUTH_TOKEN
   # Should be long string (not "invalid_token")
   ```

2. Has token expired?
   - Twilio tokens don't expire, but account can be suspended
   - Check Twilio Console → Account → General Settings
   - Status should be: "Active"

**Fix**:
```bash
# Regenerate Auth Token:
# 1. Twilio Console → Account → API keys & tokens
# 2. Click icon to generate new token
# 3. Copy new token

# Update .env
TWILIO_AUTH_TOKEN=new_token_here

# Restart backend
docker-compose restart backend

# Test
curl -X POST http://localhost:8000/api/matches ...
```

---

### Issue: High Cost / Over Budget

**Symptoms**:
- Twilio usage shows > $10 spent
- Free trial ending soon

**Check**:
```bash
# View all messages sent
curl -s -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
  | jq '.messages | length'

# Calculate cost
echo "Cost = count × 0.005"
```

**Actions**:
1. Identify high-volume sources
   ```bash
   docker-compose logs backend | grep "notification sent" | wc -l
   ```

2. Disable notifications if needed
   ```bash
   # Update .env
   WHATSAPP_NOTIFICATIONS_ENABLED=false
   
   # Restart
   docker-compose restart backend
   ```

3. Upgrade account (required for production anyway)
   - Twilio Console → Billing → Upgrade Account
   - Enter payment method
   - Account switches to paid

---

## Maintenance Schedule

### Daily (Automated)
- [ ] Health check API endpoint
- [ ] Monitor error logs
- [ ] Verify database connectivity

### Weekly (Manual)
- [ ] Review Twilio message logs
- [ ] Check cost tracking
- [ ] Review slow queries
- [ ] Test message delivery

### Monthly (Periodic)
- [ ] Backup database
- [ ] Review and optimize logs
- [ ] Upgrade Twilio account (if still on free trial)
- [ ] Performance analysis

### Before Production
- [ ] Upgrade Twilio account to paid
- [ ] Set up monitoring/alerting
- [ ] Configure backups
- [ ] Document runbooks
- [ ] Train team on monitoring

---

## Support & Resources

### Twilio Support
- **Console**: https://console.twilio.com
- **Docs**: https://www.twilio.com/docs/
- **Status Page**: https://status.twilio.com
- **Support**: Twilio Console → Support → Create Ticket

### Common Issues
- [WhatsApp Sandbox Guide](https://www.twilio.com/docs/whatsapp/sandbox-mode)
- [Message Delivery Issues](https://www.twilio.com/docs/sms/troubleshooting-sms)
- [Authentication Errors](https://www.twilio.com/docs/api/errors)

### FreteBR Documentation
- TWILIO_SETUP.md - Setup guide
- SEMANA_3_TESTING.md - Testing procedures
- SEMANA_3_E2E_TEST.md - End-to-end flow

---

**Monitoring setup complete! 🚀**

Next: Deploy to Hostinger (Week 4)
