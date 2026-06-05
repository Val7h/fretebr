# Hostinger Deployment Guide - FreteBR Semana 4

## Overview
Comprehensive guide for deploying FreteBR to Hostinger with Twilio WhatsApp integration.

---

## Pre-Deployment Checklist

Before deploying to Hostinger, verify all Week 3 tests passed:

### Week 3 Completion
- [ ] TWILIO_SETUP.md reviewed
- [ ] backend/requirements.txt includes twilio==9.2.1
- [ ] backend/test_twilio.py passes all tests
- [ ] SEMANA_3_TESTING.md all 15 tests pass
- [ ] SEMANA_3_E2E_TEST.md complete flow succeeds
- [ ] SEMANA_3_MONITORING.md monitoring set up
- [ ] Docker Compose runs stably
- [ ] All 4 PRs merged to dev branch

### Twilio Account Status
- [ ] Twilio account created and activated
- [ ] Free trial has $5+ remaining (or upgrade to paid)
- [ ] WhatsApp sandbox fully configured
- [ ] Test phone numbers verified
- [ ] At least 1 successful WhatsApp message sent

### Code Quality
- [ ] No hardcoded secrets in code
- [ ] All credentials from environment variables
- [ ] Error handling tested and working
- [ ] Graceful degradation if Twilio fails
- [ ] Logs show all operations

---

## Hostinger Deployment Steps

### Step 1: Prepare Hostinger Account

**Prerequisites**:
- Hostinger account with hosting plan
- SSH access enabled
- Node.js 18+ support (check hosting plan)
- PostgreSQL database available

**Get Hostinger Details**:
1. Log in to [Hostinger Control Panel](https://hpanel.hostinger.com)
2. Navigate to "Advanced" → "SSH Access"
3. Note:
   - **SSH Host**: e.g., `abc123.hostinger.com`
   - **SSH Port**: Usually 22 or custom
   - **SSH Username**: Your hosting username
   - **SSH Password**: Set in control panel

4. Create PostgreSQL database:
   - Hosting → "Database Management"
   - Click "Create Database"
   - Database name: `fretebr_prod`
   - Username: `fretebr_user_prod`
   - Password: Generate strong password (min 12 chars)
   - Note DATABASE_URL: `postgresql://user:pass@host:5432/db`

---

### Step 2: Set Up Production Environment

#### 2.1 Connect via SSH

```bash
# On your local machine
ssh username@abc123.hostinger.com -p 22
# Enter password when prompted
```

#### 2.2 Clone Repository

```bash
# Navigate to web root
cd ~/public_html

# Clone FreteBR repo
git clone https://github.com/Val7h/fretebr.git
cd fretebr

# Switch to dev branch (has all Week 3 features)
git checkout dev

# Verify current commit
git log --oneline -1
```

#### 2.3 Create Production Environment File

```bash
# Create .env file
cat > .env << 'EOF'
# ========== DATABASE ==========
# Use Hostinger PostgreSQL credentials
DATABASE_URL=postgresql://fretebr_user_prod:your_password@db.hostinger.com:5432/fretebr_prod
POSTGRES_DB=fretebr_prod
POSTGRES_USER=fretebr_user_prod
POSTGRES_PASSWORD=your_strong_password

# ========== SECURITY ==========
# IMPORTANT: Generate a new secret key for production
SECRET_KEY=generate_with_python_secrets

# ========== JWT Configuration ==========
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ========== CORS ==========
# Replace with your production domain
ALLOWED_ORIGINS=https://fretebr.example.com,https://www.fretebr.example.com

# ========== APPLICATION ==========
ENVIRONMENT=production
DEBUG=false

# ========== VITE (Frontend) ==========
VITE_API_URL=https://api.fretebr.example.com

# ========== TWILIO WhatsApp Integration ==========
# Get these from Twilio Console (same as development)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_SANDBOX_ENABLED=true

# Optional: Use production WhatsApp (after account upgrade)
# TWILIO_WHATSAPP_PRODUCTION_NUMBER=+55...
# TWILIO_WHATSAPP_PRODUCTION_ENABLED=false

# ========== NOTIFICATIONS ==========
NOTIFICATIONS_ENABLED=true
WHATSAPP_NOTIFICATIONS_ENABLED=true
EOF
```

**Generate Secret Key**:
```bash
# On your local machine (Python 3)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Output: Copy this and paste into .env SECRET_KEY
```

#### 2.4 Update .env Values

```bash
# Edit with nano/vim
nano .env

# Update these fields:
# 1. DATABASE_URL: your Hostinger DB connection string
# 2. SECRET_KEY: generated token
# 3. ALLOWED_ORIGINS: your domain (https://fretebr.yoursite.com)
# 4. VITE_API_URL: your API domain
# 5. TWILIO_*: Keep from development (or use production values)

# Save: Ctrl+O, Enter, Ctrl+X
```

**Verify .env**:
```bash
# Check file was created
cat .env | head -20

# Verify no secrets are exposed
# (should show placeholder values or real values protected)
```

---

### Step 3: Install Backend Dependencies

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt --user

# Or if pip not available:
python -m pip install -r requirements.txt --user

# Verify Twilio installed
python -c "import twilio; print(f'Twilio {twilio.__version__} installed')"
# Expected: Twilio 9.2.1 installed
```

---

### Step 4: Initialize Database

```bash
# Navigate back to root
cd ..

# Create database tables using Alembic migrations
cd backend

# If using Alembic:
alembic upgrade head

# Or use SQLAlchemy create_all:
python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"

# Verify tables created
python -c "
from app.database import get_db
from sqlalchemy import inspect
db = next(get_db())
inspector = inspect(db.get_bind())
tables = inspector.get_table_names()
print(f'Created tables: {tables}')
"

# Expected output:
# Created tables: ['users', 'fretes', 'matches', 'messages']
```

---

### Step 5: Deploy Frontend

```bash
# Navigate to frontend
cd ../frontend

# Install Node dependencies
npm install

# Build for production
npm run build

# Verify build output
ls -la dist/

# Should contain:
# - index.html
# - assets/
# - favicon.svg
```

---

### Step 6: Set Up Web Server (Nginx / Apache)

#### Option A: Nginx (Recommended for Hostinger)

```bash
# Connect via SSH and edit nginx config
sudo nano /etc/nginx/sites-available/fretebr.conf

# Add configuration:
```

Create file `/etc/nginx/sites-available/fretebr.conf`:

```nginx
# Frontend (React)
server {
    listen 80;
    server_name fretebr.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name fretebr.example.com;

    # SSL certificates (use Let's Encrypt via Hostinger)
    ssl_certificate /etc/letsencrypt/live/fretebr.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fretebr.example.com/privkey.pem;

    # Root directory for frontend
    root /home/username/public_html/fretebr/frontend/dist;
    index index.html;

    # Serve static files
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Fallback to index.html for SPA routing
    location / {
        try_files $uri /index.html;
    }
}

# Backend (FastAPI)
server {
    listen 443 ssl;
    server_name api.fretebr.example.com;

    ssl_certificate /etc/letsencrypt/live/api.fretebr.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.fretebr.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fretebr.conf /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

#### Option B: Apache (if Hostinger uses Apache)

```apache
# In .htaccess at project root
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /

    # Redirect HTTP to HTTPS
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

    # Proxy API requests to backend
    RewriteRule ^api/(.*)$ http://localhost:8000/api/$1 [P,L]

    # Serve frontend files
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [L]
</IfModule>
```

---

### Step 7: Start Backend Service

#### Option A: Systemd Service (Recommended)

Create `/etc/systemd/system/fretebr-backend.service`:

```ini
[Unit]
Description=FreteBR Backend API
After=network.target

[Service]
Type=simple
User=fretebr
WorkingDirectory=/home/username/public_html/fretebr/backend
Environment="PATH=/home/username/.local/bin"
Environment="DATABASE_URL=postgresql://..."
Environment="SECRET_KEY=..."
Environment="TWILIO_ACCOUNT_SID=..."
Environment="TWILIO_AUTH_TOKEN=..."
Environment="TWILIO_PHONE_NUMBER=..."
ExecStart=/home/username/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fretebr-backend.service
sudo systemctl start fretebr-backend.service

# Check status
sudo systemctl status fretebr-backend.service

# View logs
sudo journalctl -u fretebr-backend.service -f
```

#### Option B: PM2 (Alternative)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: "fretebr-backend",
    script: "uvicorn",
    args: "app.main:app --host 0.0.0.0 --port 8000",
    cwd: "/home/username/public_html/fretebr/backend",
    env: {
      "DATABASE_URL": "postgresql://...",
      "SECRET_KEY": "...",
      "TWILIO_ACCOUNT_SID": "...",
      "TWILIO_AUTH_TOKEN": "...",
      "TWILIO_PHONE_NUMBER": "..."
    },
    instances: 1,
    exec_mode: "cluster",
    watch: false,
    max_memory_restart: "500M"
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js

# Ensure PM2 restarts on reboot
pm2 startup
pm2 save
```

---

### Step 8: Configure SSL Certificate

**Using Hostinger's Free SSL (Let's Encrypt)**:

1. Go to Hostinger Control Panel
2. Hosting → SSL Certificate
3. Click "Manage SSL"
4. Install Free Let's Encrypt SSL
5. Select domain: `fretebr.example.com`
6. Auto-renew: Enable

**Verification**:
```bash
# Test HTTPS
curl -k https://fretebr.example.com

# Should return HTML (frontend)

curl -k https://api.fretebr.example.com/health

# Should return: {"status":"ok","service":"FreteBR Backend"}
```

---

### Step 9: Configure Domain DNS

In your domain registrar (Namecheap, GoDaddy, etc.):

**Add DNS Records**:
```
Type: A
Name: @
Value: 123.45.67.89 (Hostinger IP)
TTL: 3600

Type: CNAME
Name: www
Value: @ (or fretebr.example.com)
TTL: 3600

Type: CNAME
Name: api
Value: @ (or fretebr.example.com)
TTL: 3600
```

**Wait for DNS propagation** (usually 5-30 minutes):
```bash
# Check DNS resolution
nslookup fretebr.example.com
nslookup api.fretebr.example.com

# Should resolve to Hostinger IP
```

---

### Step 10: Test Production Deployment

#### Test Backend Health
```bash
curl https://api.fretebr.example.com/health

# Expected: {"status":"ok","service":"FreteBR Backend"}
```

#### Test Frontend
```bash
# Open in browser: https://fretebr.example.com
# Should show FreteBR interface
```

#### Test API Endpoints
```bash
# Create user
curl -X POST https://api.fretebr.example.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Test User",
    "email": "test@example.com",
    "senha": "TestPass123!",
    "tipo": "motorista",
    "telefone": "+5583993476410"
  }'
```

#### Test WhatsApp Notifications
```bash
# Create a frete
# Accept with different user (creates match)
# Verify WhatsApp notification sent

# Check Twilio logs
# Should show message sent to +5583993476410
```

---

## Production Optimization

### Performance Tuning

#### 1. Database Optimization
```bash
# Create indexes for frequent queries
psql postgresql://user:pass@host:5432/db << 'EOF'
CREATE INDEX idx_fretes_motorista ON fretes(motorista_id);
CREATE INDEX idx_fretes_status ON fretes(status);
CREATE INDEX idx_matches_frete ON matches(frete_id);
CREATE INDEX idx_matches_shipper ON matches(shipper_id);
CREATE INDEX idx_messages_match ON messages(match_id);
CREATE INDEX idx_users_email ON users(email);
EOF
```

#### 2. Caching (Redis)
```python
# backend/app/cache.py
from redis import Redis

cache = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def cache_fretes():
    """Cache available fretes for 5 minutes"""
    cached = cache.get("available_fretes")
    if not cached:
        fretes = db.query(Frete).filter(Frete.status == "disponível").all()
        cache.set("available_fretes", json.dumps(fretes), ex=300)
    return cached
```

#### 3. API Response Compression
```python
# backend/app/main.py
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

#### 4. Frontend Asset Compression
- Built-in with `npm run build` (already gzipped)
- Configure nginx gzip: Already set in nginx config above

### Security Hardening

#### 1. Rate Limiting
```python
# backend/app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/fretes")
@limiter.limit("100/minute")
async def list_fretes(...):
    ...
```

#### 2. Request Validation
- All endpoints already use Pydantic schemas ✓
- Input validation in place ✓

#### 3. CORS Configuration
```python
# Already set in .env
ALLOWED_ORIGINS=https://fretebr.example.com,https://www.fretebr.example.com
```

#### 4. HTTPS Only
```python
# backend/app/main.py
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["fretebr.example.com", "api.fretebr.example.com"],
)
```

#### 5. Secure Headers
```python
# backend/app/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Monitoring in Production

### Set Up Uptime Monitoring

```bash
# Using Uptime Robot (free)
1. Go to https://uptimerobot.com
2. Create account
3. Add monitors:
   - http://fretebr.example.com
   - http://api.fretebr.example.com/health
4. Notification: Email on failure
5. Check interval: Every 5 minutes
```

### Log Aggregation

```bash
# Centralized logging with Papertrail
1. Sign up: https://papertrailapp.com
2. Get API token
3. Configure logrotate to forward logs:

cat > /etc/rsyslog.d/fretebr.conf << 'EOF'
:programname, isequal, "fretebr" @logsXXXXX.papertrailapp.com:XXXXX
EOF

sudo systemctl restart rsyslog
```

### Error Tracking

```bash
# Using Sentry (free tier)
1. Create account: https://sentry.io
2. Create project: Python
3. Get DSN
4. Add to backend:

# backend/app/main.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

---

## Database Backups

```bash
#!/bin/bash
# backup.sh - Run daily via cron

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="fretebr_backup_${DATE}.sql"

# Backup database
pg_dump postgresql://user:pass@host:5432/db > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Upload to cloud storage
aws s3 cp ${BACKUP_FILE}.gz s3://your-bucket/backups/

# Keep only last 30 days
find . -name "fretebr_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**Schedule daily backup**:
```bash
# Add to crontab
crontab -e

# Add line:
0 2 * * * /home/username/backup.sh >> /var/log/fretebr_backup.log 2>&1
```

---

## Upgrade Path

### When to Upgrade Twilio Account

**Free Trial Limit**: $15 USD
**Indicator to Upgrade**: When cost approaches $10 (80% used)

**Steps to Upgrade**:
1. Twilio Console → Billing → Account Settings
2. Click "Upgrade to Paid Account"
3. Enter payment method (credit/debit card)
4. Account immediately switches from free trial to paid
5. Billing starts: $0.005 per SMS/WhatsApp message

**After Upgrade**:
- [ ] Update TWILIO_WHATSAPP_PRODUCTION_ENABLED=true
- [ ] Switch to production WhatsApp number (if different)
- [ ] Remove sandbox restrictions
- [ ] Messages can be sent to any WhatsApp number (with valid credentials)

---

## Troubleshooting Production Issues

### Issue: Database Connection Timeout

```bash
# Check connection string
cat .env | grep DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# If fails: Check Hostinger firewall
# Contact Hostinger support to whitelist your IP
```

### Issue: WhatsApp Messages Not Sending

```bash
# Check backend logs
tail -f /var/log/fretebr-backend.log

# Verify Twilio credentials
grep TWILIO .env

# Test manually
curl -X POST https://api.fretebr.example.com/api/matches \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"frete_id": 1, "valor_final": 500}'

# Check Twilio logs
# https://console.twilio.com → Messaging → Logs
```

### Issue: Frontend Shows Blank Page

```bash
# Check browser console (F12)
# Look for CORS errors or 404s

# Verify frontend build
ls -la frontend/dist/index.html

# Check nginx logs
tail -f /var/log/nginx/error.log

# Verify API proxy works
curl https://api.fretebr.example.com/health
```

### Issue: High Memory Usage

```bash
# Check backend process
ps aux | grep uvicorn

# Limit memory
# Edit /etc/systemd/system/fretebr-backend.service
# Add: MemoryLimit=500M

# Or use PM2 memory limit
pm2 set fretebr-backend max_memory_restart 500M
```

---

## Success Checklist

After deployment, verify:

- [ ] Frontend loads at https://fretebr.example.com
- [ ] API responds at https://api.fretebr.example.com/health
- [ ] SSL certificate valid (no warnings)
- [ ] Database connected and tables created
- [ ] User signup works
- [ ] Frete creation works
- [ ] Match creation works
- [ ] WhatsApp notification sends
- [ ] Chat messages work
- [ ] All status transitions work
- [ ] Monitoring in place
- [ ] Backups configured
- [ ] Error tracking set up

**Deployment Status**: ✅ **COMPLETE**

---

## Next Steps (Week 4+)

1. **Monitor production** for 1 week
2. **Gather user feedback** from beta testers
3. **Optimize based on metrics**
4. **Marketing & user acquisition**
5. **Scale infrastructure** as needed

---

**FreteBR is live! 🚀**

**Production URL**: https://fretebr.example.com  
**API URL**: https://api.fretebr.example.com  
**Deployment Date**: [Date]  
**Deployer**: [Name]  
**Status**: ✅ Live in Production
