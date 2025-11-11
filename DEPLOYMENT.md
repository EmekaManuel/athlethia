# Deployment Guide

## Prerequisites

- Python 3.9 or higher
- MongoDB 4.4+ (local installation or Docker)
- WhatsApp Business API account (for WhatsApp integration)
- Telegram Bot Token (for Telegram integration)
- OpenAI API key (optional, for advanced AI analysis)

## Local Development Setup

### 1. Clone and Install

```bash
git clone <repository-url>
cd athlethia
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DATABASE`: Database name (default: `athlethia`)
- `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/botfather) on Telegram
- `WHATSAPP_API_KEY`: From WhatsApp Business API
- `WHATSAPP_PHONE_NUMBER_ID`: From WhatsApp Business API
- `OPENAI_API_KEY`: Optional, for AI analysis

### 3. Start MongoDB

**Option 1: Using Docker**

```bash
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

**Option 2: Local Installation**
Make sure MongoDB is installed and running:

```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
# Start MongoDB service from Services
```

### 4. Initialize Database

```bash
python -m app.db.init_db
```

This creates the necessary indexes for optimal performance.

### 5. Run Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Build and Run

```bash
docker-compose up -d
```

### Environment Variables

Set environment variables in `docker-compose.yml` or use a `.env` file.

## Production Deployment

### Using Docker

1. Build the image:

```bash
docker build -t athlethia .
```

2. Run with environment variables (ensure MongoDB is accessible):

```bash
docker run -d \
  -p 8000:8000 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -e MONGODB_DATABASE=athlethia \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e WHATSAPP_API_KEY=your_key \
  --network="host" \
  athlethia
```

Or use `docker-compose up` which includes MongoDB:

```bash
docker-compose up -d
```

### Using Cloud Platforms

#### Heroku

1. Create `Procfile`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:

```bash
heroku create athlethia
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
```

#### AWS/GCP/Azure

Use container services (ECS, Cloud Run, Container Instances) with the Dockerfile provided.

## WhatsApp Webhook Setup

1. Set webhook URL in WhatsApp Business API dashboard:

   ```
   https://your-domain.com/whatsapp/webhook
   ```

2. Set verify token to match `WHATSAPP_VERIFY_TOKEN` in your `.env`

3. Subscribe to webhook events: `messages`

## Telegram Bot Setup

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get bot token
3. Set `TELEGRAM_BOT_TOKEN` in environment
4. Bot will automatically start when application runs

## Database Setup

### MongoDB (Default)

MongoDB is the default database. The application will automatically create the database and collections on first run.

#### Local MongoDB

1. Install MongoDB:

   - **macOS**: `brew install mongodb-community`
   - **Linux**: Follow [MongoDB installation guide](https://www.mongodb.com/docs/manual/installation/)
   - **Windows**: Download from [MongoDB website](https://www.mongodb.com/try/download/community)

2. Start MongoDB:

   ```bash
   # macOS/Linux
   mongod --dbpath /path/to/data

   # Or as a service
   brew services start mongodb-community  # macOS
   sudo systemctl start mongod            # Linux
   ```

3. Update `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DATABASE=athlethia
   ```

#### MongoDB Atlas (Cloud)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster (free tier available)
3. Get connection string
4. Update `.env`:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/athlethia?retryWrites=true&w=majority
   MONGODB_DATABASE=athlethia
   ```

#### Docker MongoDB

The `docker-compose.yml` includes a MongoDB service. Just run:

```bash
docker-compose up -d
```

#### Initialize Database

After MongoDB is running, initialize indexes:

```bash
python -m app.db.init_db
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Security Considerations

1. **Environment Variables**: Never commit `.env` file
2. **HTTPS**: Use HTTPS in production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Database**: Use strong passwords and encrypted connections
5. **API Keys**: Rotate keys regularly

## Scaling

### Horizontal Scaling

- Use load balancer (nginx, AWS ALB)
- Multiple application instances
- Shared database (PostgreSQL)

### Performance Optimization

- Enable database connection pooling
- Use Redis for caching
- CDN for static assets
- Database indexing on frequently queried fields

## Troubleshooting

### Telegram Bot Not Responding

- Check bot token is correct
- Verify bot is not blocked
- Check application logs

### WhatsApp Webhook Not Working

- Verify webhook URL is accessible
- Check verify token matches
- Review webhook logs in WhatsApp dashboard

### Database Errors

- Ensure database is initialized
- Check database connection string
- Verify database permissions

## Support

For issues or questions:

- GitHub Issues: [repository URL]/issues
- Documentation: See README.md
- Email: [support email]
