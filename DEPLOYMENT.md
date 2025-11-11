# Deployment Guide

## Prerequisites

- Python 3.9 or higher
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

- `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/botfather) on Telegram
- `WHATSAPP_API_KEY`: From WhatsApp Business API
- `WHATSAPP_PHONE_NUMBER_ID`: From WhatsApp Business API
- `OPENAI_API_KEY`: Optional, for AI analysis

### 3. Initialize Database

```bash
python -m app.db.init_db
```

### 4. Run Application

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

2. Run with environment variables:

```bash
docker run -d \
  -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e WHATSAPP_API_KEY=your_key \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  athlethia
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

### SQLite (Default)

No additional setup needed. Database file will be created automatically.

### PostgreSQL (Production)

1. Install PostgreSQL
2. Create database:

```sql
CREATE DATABASE athlethia;
```

3. Update `DATABASE_URL`:

```
DATABASE_URL=postgresql://user:password@localhost/athlethia
```

4. Run migrations:

```bash
alembic upgrade head
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
