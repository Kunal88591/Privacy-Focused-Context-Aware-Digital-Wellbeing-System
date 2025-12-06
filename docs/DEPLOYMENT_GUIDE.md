# 🚀 Deployment Guide

## Overview

This guide covers deploying the Privacy-Focused Digital Wellbeing System to production.

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Self-Hosting)

**Prerequisites:**
- Docker & Docker Compose installed
- 2GB RAM minimum
- Open ports: 8000 (API), 1883 (MQTT), 9001 (MQTT WebSocket)

**Steps:**

```bash
# Clone the repository
git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
cd Privacy-Focused-Context-Aware-Digital-Wellbeing-System

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

**Access:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MQTT Broker: mqtt://localhost:1883
- MQTT WebSocket: ws://localhost:9001

---

### Option 2: Heroku (Easy Cloud Deployment)

**Prerequisites:**
- Heroku account (free tier available)
- Heroku CLI installed

**Steps:**

```bash
# Login to Heroku
heroku login

# Create app
cd backend-api
heroku create your-wellbeing-app

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open app
heroku open

# View logs
heroku logs --tail
```

**Your API will be at:** `https://your-wellbeing-app.herokuapp.com`

---

### Option 3: AWS/GCP/Azure

**AWS EC2 Deployment:**

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose -y

# Clone and deploy
git clone https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System.git
cd Privacy-Focused-Context-Aware-Digital-Wellbeing-System
sudo docker-compose up -d
```

**Open Security Group Ports:**
- 8000 (HTTP)
- 1883 (MQTT)
- 9001 (MQTT WebSocket)

---

## Mobile App Configuration

After deploying backend, update mobile app:

**File:** `mobile-app/src/config/api.js`

```javascript
export const API_CONFIG = {
  // Update with your deployed backend URL
  BASE_URL: 'https://your-wellbeing-app.herokuapp.com',
  MQTT_BROKER: 'your-mqtt-broker-url',
  MQTT_PORT: 1883,
  TIMEOUT: 10000,
};
```

Then rebuild mobile app:

```bash
cd mobile-app
npm install
npx expo start
```

---

## Environment Variables

Create `.env` file in `backend-api/`:

```env
# Production settings
ENVIRONMENT=production
DEBUG=false

# MQTT Configuration
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://your-frontend-url.com

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free):

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Update docker-compose.yml:

```yaml
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
```

---

## Monitoring & Logging

### Health Check Endpoint:

```bash
curl http://your-api-url/health
```

### Docker Logs:

```bash
# View backend logs
docker-compose logs -f backend

# View MQTT logs
docker-compose logs -f mosquitto
```

### Production Monitoring Tools:
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation

---

## Scaling

### Horizontal Scaling:

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config
```

### Load Balancer (Nginx):

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

---

## Security Checklist

- [ ] Enable HTTPS/SSL
- [ ] Set strong SECRET_KEY
- [ ] Configure MQTT authentication
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitor logs for suspicious activity

---

## Backup & Recovery

### Automated Backup Script:

```bash
#!/bin/bash
# backup.sh

# Backup MQTT data
docker-compose exec mosquitto tar czf /backup/mqtt-$(date +%Y%m%d).tar.gz /mosquitto/data

# Backup database (if applicable)
docker-compose exec backend pg_dump > backup-$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp backup-$(date +%Y%m%d).sql s3://your-bucket/backups/
```

---

## Troubleshooting

### Backend won't start:

```bash
# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend

# Rebuild
docker-compose up --build backend
```

### MQTT connection issues:

```bash
# Test MQTT connection
mosquitto_sub -h localhost -t test/topic

# Check MQTT logs
docker-compose logs mosquitto
```

### Port already in use:

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

---

## Performance Optimization

### Backend:

```python
# app/main.py
app = FastAPI()

# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
```

### Database Connection Pooling:

```python
# Increase pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

---

## Cost Estimates

### Self-Hosting (AWS EC2):
- t2.micro (free tier): $0/month for 1 year
- t2.small: ~$17/month
- Storage: ~$1/month

### Heroku:
- Free tier: $0 (limited hours)
- Hobby: $7/month
- Standard: $25/month

### Cloud MQTT:
- CloudMQTT: Free - $5/month
- AWS IoT: Pay per message (~$1/month for low traffic)

---

## Production Checklist

Before going live:

- [ ] All tests passing
- [ ] Environment variables set
- [ ] SSL/HTTPS enabled
- [ ] Monitoring configured
- [ ] Backup system in place
- [ ] Security hardening done
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Mobile app updated with production API
- [ ] DNS configured
- [ ] Error tracking enabled

---

## Support & Maintenance

### Regular Tasks:
- Weekly: Check logs, review metrics
- Monthly: Security updates, dependency updates
- Quarterly: Performance review, capacity planning

### Updates:

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

---

## Next Steps

1. **Deploy backend** using preferred method
2. **Update mobile app** with production API URL
3. **Test end-to-end** functionality
4. **Set up monitoring** and alerts
5. **Configure backups**
6. **Launch!** 🚀

---

**Your system is production-ready!** Follow this guide to deploy and make it accessible to users.
