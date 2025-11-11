# Quick Start Guide

Get Athlethia up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- Telegram Bot Token (optional, for Telegram integration)
- WhatsApp Business API credentials (optional, for WhatsApp integration)

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
WHATSAPP_API_KEY=your_whatsapp_api_key_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
DATABASE_URL=sqlite:///./athlethia.db
EOF

# 3. Initialize database
python -m app.db.init_db

# 4. Run the application
python run.py
```

## Get Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token and add it to `.env`

## Test the API

Once running, visit:

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Test Link Scanning

```bash
curl -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Use Telegram Bot

1. Find your bot on Telegram (search for the username you created)
2. Send `/start` to begin
3. Send any message with a link
4. Bot will automatically scan and respond

## Next Steps

- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [README.md](README.md) for full documentation
- See [GRANT_PROPOSAL.md](GRANT_PROPOSAL.md) for grant application details
