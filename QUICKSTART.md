# Quick Start Guide

Get Athlethia up and running in 5 minutes!

## Prerequisites

- Python 3.9+
- MongoDB (see [LOCAL_SETUP.md](LOCAL_SETUP.md) for installation instructions)
- Telegram Bot Token (optional, for Telegram integration)
- WhatsApp Business API credentials (optional, for WhatsApp integration)

## Installation

### Option 1: Using Docker (Recommended for quick start)

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Start MongoDB with Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 3. Create .env file
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
WHATSAPP_API_KEY=your_whatsapp_api_key_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=athlethia
EOF

# 4. Run the application
python3 run.py
```

### Option 2: Without Docker (Local Setup)

For detailed instructions on running without Docker, see **[LOCAL_SETUP.md](LOCAL_SETUP.md)**.

Quick steps:
```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Install and start MongoDB locally (see LOCAL_SETUP.md)

# 3. Create .env file (see LOCAL_SETUP.md for full template)

# 4. Run the application
python3 run.py
```

**Note:** The database will be automatically initialized when you start the app. You can also initialize it manually:
```bash
python3 -m app.db.init_db
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

- See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed local development setup (without Docker)
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [README.md](README.md) for full documentation
- See [GRANT_PROPOSAL.md](GRANT_PROPOSAL.md) for grant application details
