# Twilio WhatsApp Integration Setup - FreteBR

## Overview
This guide walks through setting up Twilio WhatsApp sandbox integration for FreteBR notifications.

## Prerequisites
- Email address (you can use any)
- Phone number (for WhatsApp sandbox testing)
- $15 USD free trial credits from Twilio

## Step 1: Create Twilio Account

1. Go to [https://www.twilio.com](https://www.twilio.com)
2. Click "Sign Up" in the top right corner
3. Enter your details:
   - Email: valthguime@gmail.com (or your email)
   - Password: Create a strong password
   - Full Name: Your Name
   - Account details:
     - Verify your phone number (required)
     - Create account name: "FreteBR"
4. Complete verification via SMS
5. Accept Terms & Conditions
6. You'll receive $15 USD in free trial credits

**Note:** Free trial has limitations - messages can only be sent to verified phone numbers. For production, you'll need to upgrade.

## Step 2: Get Twilio Credentials

After account creation:

### 2.1 Account SID & Auth Token
1. Go to [Twilio Console](https://console.twilio.com)
2. In the left sidebar, find "Account" → "API keys & tokens"
3. You'll see:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (copy this)
   - **Auth Token**: Hidden by default - click "eye" icon to reveal (copy this)

**⚠️ SECURITY**: Never share Auth Token! Keep it secret.

### 2.2 Get WhatsApp Sandbox Phone Number
1. In Twilio Console, go to "Messaging" → "Services" (or create new)
2. Select your service or create:
   - Service name: "FreteBR WhatsApp"
   - Select "Whatsapp" as channel
3. Go to "Messaging" → "Try it out" → "Send an SMS"
4. Enable WhatsApp
5. You'll see a Twilio WhatsApp sandbox number like: `+1234567890`
   - Copy this number

### 2.3 Verify Your Phone Number (WhatsApp Sandbox)
1. Go to "Messaging" → "WhatsApp" in Twilio Console
2. Find "Sandbox" section
3. Add your phone number to the verified list
4. Send WhatsApp message to Twilio's sandbox number with the join code (e.g., "join alpha-bravo")
5. You'll receive confirmation

**Example Sandbox Join Message:**
```
Send to: +1234567890 (Twilio's WhatsApp number)
Message: join alpha-bravo
```
(The exact code is shown in Twilio Console)

## Step 3: Configure Environment Variables

1. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

2. Add Twilio credentials to `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_SANDBOX_ENABLED=true
```

3. (Optional) For production WhatsApp, add:
```
TWILIO_WHATSAPP_PRODUCTION_NUMBER=+1234567890
```

## Step 4: Test Twilio Integration

### 4.1 Basic Python Test
```python
from twilio.rest import Client

account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"

client = Client(account_sid, auth_token)
message = client.messages.create(
    from_="whatsapp:+1234567890",  # Twilio WhatsApp number
    body="Test message from FreteBR!",
    to="whatsapp:+5583993476410"   # Your phone (with country code)
)
print(f"Message sent: {message.sid}")
```

### 4.2 Verify Phone Numbers
Before sending messages, verify both numbers:
- Twilio WhatsApp Sandbox phone (e.g., +1234567890)
- Your testing phone (e.g., +5583993476410)

## Step 5: Docker Setup

The Twilio SDK is installed automatically:

```bash
# Build Docker images
docker-compose build --no-cache

# Start services
docker-compose up

# Verify Twilio import
docker-compose exec backend python -c "from twilio.rest import Client; print('✓ Twilio import OK')"
```

## Step 6: Cost Estimation

- **Free Trial**: $15 USD (approximately 3,000 test messages)
- **Production Cost**: ~$0.005 - $0.01 per message (varies by country)
- **Recommended**: Start with free trial, upgrade account for production

## Step 7: Production Checklist

Before deploying to production:

- [ ] Upgrade Twilio account (remove free trial restrictions)
- [ ] Apply for WhatsApp Business Profile
- [ ] Verify business phone number in Twilio
- [ ] Set production WhatsApp number in `.env`
- [ ] Test end-to-end with real WhatsApp numbers
- [ ] Monitor Twilio usage/costs in dashboard
- [ ] Set up Twilio webhooks for delivery receipts (optional)
- [ ] Configure message retention policies

## Troubleshooting

### "Authentication failed"
- Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are correct
- Verify Auth Token has not expired
- In Twilio Console, regenerate Auth Token if needed

### "Invalid phone number"
- Ensure phone numbers include country code (e.g., +55 for Brazil)
- Format: `whatsapp:+5583993476410`
- Verify number is in WhatsApp Sandbox verified list

### "Sandbox access revoked"
- You have not sent a message in 6+ months
- Send a test message to re-activate: `join alpha-bravo`
- Check Twilio Console for current sandbox join code

### "Message not delivered"
- Check Twilio logs in Console: "Messaging" → "Logs"
- Ensure recipient phone is in sandbox verified list
- WhatsApp number format must be `whatsapp:+phonenumber`

## Resources

- [Twilio Console](https://console.twilio.com)
- [Twilio Python Docs](https://www.twilio.com/docs/sms/send-messages)
- [WhatsApp on Twilio](https://www.twilio.com/docs/whatsapp)
- [WhatsApp Sandbox Guide](https://www.twilio.com/docs/whatsapp/sandbox-mode)

## Next Steps

1. Verify integration with `backend/test_twilio.py`
2. Create notification system in `app/services/notifications.py`
3. Hook notifications to match creation in `app/api/fretes.py`
4. Test with Docker Compose
5. Deploy to Hostinger (Week 4)
