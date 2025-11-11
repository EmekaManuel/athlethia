# Athlethia - AI-Powered Link Scam Detection

A comprehensive, AI-driven link scanning service that detects scam websites and provides real-time warnings through WhatsApp and Telegram integrations. Built for grant applications and production deployment.

## 🎯 Features

- **AI-Powered Detection**: Multi-layered scam detection using:

  - URL pattern analysis
  - Content analysis with AI models
  - Domain reputation checking
  - SSL certificate validation
  - Phishing pattern recognition
  - Known scam database lookup

- **Multi-Platform Integration**:

  - WhatsApp Business API integration
  - Telegram Bot integration
  - RESTful API for custom integrations

- **Real-Time Scanning**: Fast, asynchronous link analysis
- **Database**: Persistent storage of scan results and known scams
- **Scalable Architecture**: Built with FastAPI for high performance

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐
│  WhatsApp   │────▶│             │
│   Client    │     │             │
└─────────────┘     │   FastAPI   │     ┌──────────────┐
                    │   Backend   │────▶│   Scam      │
┌─────────────┐     │             │     │  Detection  │
│  Telegram   │────▶│             │     │   Engine    │
│     Bot     │     │             │     └──────────────┘
└─────────────┘     └─────────────┘            │
                                              ▼
                                       ┌──────────────┐
                                       │  Database    │
                                       │  (MongoDB)   │
                                       └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB 4.4+ (local installation or Docker)
- WhatsApp Business API credentials (or use WhatsApp Web API)
- Telegram Bot Token
- OpenAI API key (optional, for advanced AI analysis)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd athlethia
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and tokens
```

4. Initialize the database:

```bash
python -m app.db.init_db
```

5. Run the application:

```bash
uvicorn app.main:app --reload
```

## 📋 Environment Variables

Create a `.env` file with the following:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=athlethia

# Security
SECRET_KEY=your_secret_key_here
```

## 🔧 Usage

### WhatsApp Integration

The service automatically scans links sent in WhatsApp messages and responds with scam warnings when detected.

### Telegram Integration

Add the bot to your Telegram group or chat, and it will automatically scan links and provide warnings.

### API Endpoints

- `POST /api/v1/scan` - Scan a URL
- `GET /api/v1/scan/{scan_id}` - Get scan results
- `GET /api/v1/stats` - Get scanning statistics

## 🧪 Testing

```bash
pytest tests/
```

## 📊 Grant Application Highlights

- **Innovation**: AI-powered multi-signal detection approach
- **Impact**: Protects users from financial fraud and phishing
- **Scalability**: Built for high-volume usage
- **Open Source**: Contributes to cybersecurity community
- **Multi-Platform**: Reaches users where they communicate

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
