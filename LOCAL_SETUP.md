# Local Development Setup (Without Docker)

This guide will help you run Athlethia locally without Docker.

## Prerequisites

1. **Python 3.9+** - Already installed ✓
2. **MongoDB** - You'll need to install and run MongoDB locally
3. **API Keys** (optional):
   - OpenAI API key (for AI-powered scam detection)
   - Telegram Bot Token (for Telegram integration)
   - WhatsApp API credentials (for WhatsApp integration)

## Step 1: Install MongoDB Locally

### macOS (using Homebrew)
```bash
# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Or run manually
mongod --config /usr/local/etc/mongod.conf
```

### macOS (using MacPorts)
```bash
sudo port install mongodb
sudo port load mongodb
```

### Linux (Ubuntu/Debian)
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Windows
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Run the installer
3. MongoDB will start as a Windows service automatically

### Verify MongoDB is Running
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Or check the port
lsof -i :27017  # macOS/Linux
netstat -an | findstr 27017  # Windows
```

## Step 2: Create Environment File

Create a `.env` file in the project root:

```bash
cp .env.example .env  # If .env.example exists
# Or create manually:
```

```env
# API Keys (optional - app will work without them, but some features will be disabled)
OPENAI_API_KEY=your_openai_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
WHATSAPP_API_KEY=your_whatsapp_api_key_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_VERIFY_TOKEN=athlethia_verify_token

# Database Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=athlethia

# Security
SECRET_KEY=change-this-in-production-use-a-random-string

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# Scam Detection Settings
SCAM_DETECTION_THRESHOLD=0.7
ENABLE_AI_ANALYSIS=true
CACHE_TTL_SECONDS=3600
```

**Note:** You can run the app without API keys, but:
- AI-powered scam detection will be disabled without `OPENAI_API_KEY`
- Telegram bot won't work without `TELEGRAM_BOT_TOKEN`
- WhatsApp integration won't work without WhatsApp credentials

## Step 3: Install Python Dependencies

```bash
# Make sure you're in the project directory
cd /Users/manuelofthenorth/Documents/athlethia

# Install dependencies (already done, but if you need to reinstall)
pip3 install -r requirements.txt
```

## Step 4: Initialize Database

The database will be automatically initialized when you start the app, but you can also initialize it manually:

```bash
python3 -m app.db.init_db
```

## Step 5: Run the Application

```bash
# Run the application
python3 run.py
```

The app will start on `http://localhost:8000`

## Step 6: Verify It's Working

1. **Check health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Visit API documentation:**
   Open your browser and go to: `http://localhost:8000/docs`

3. **Test link scanning:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/scan" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
   ```

## Troubleshooting

### MongoDB Connection Issues

**Error: "Failed to connect to MongoDB"**

1. Make sure MongoDB is running:
   ```bash
   # macOS/Linux
   brew services list  # Check if mongodb-community is started
   # Or
   ps aux | grep mongod
   
   # Start if not running
   brew services start mongodb-community
   ```

2. Check MongoDB is listening on port 27017:
   ```bash
   lsof -i :27017
   ```

3. Verify connection string in `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   ```

### Port Already in Use

If port 8000 is already in use, you can change it:

```bash
# Edit run.py and change port=8000 to your desired port
# Or set environment variable
export PORT=8001
python3 run.py
```

### Missing Dependencies

If you get import errors:
```bash
pip3 install -r requirements.txt
```

### Telegram Bot Not Starting

- Check that `TELEGRAM_BOT_TOKEN` is set in `.env`
- Verify the token is valid
- The app will continue to run even if Telegram bot fails to start

## Running in Development Mode

For development with auto-reload:

```bash
# Install uvicorn if not already installed
pip3 install uvicorn[standard]

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** When running with `uvicorn` directly, the Telegram bot won't start automatically. Use `python3 run.py` for full functionality.

## Next Steps

- See [QUICKSTART.md](QUICKSTART.md) for more examples
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [README.md](README.md) for full documentation

