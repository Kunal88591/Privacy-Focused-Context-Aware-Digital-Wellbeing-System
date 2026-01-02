# Launch Guide - Production Deployment

**Project:** Privacy-Focused Context-Aware Digital Wellbeing System  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026

---

## 🚀 QUICK START - PRODUCTION DEPLOYMENT

This guide walks you through deploying the system to production. Follow these steps in order.

---

## 📋 PREREQUISITES

Before starting the deployment:

- [ ] Docker and Docker Compose installed
- [ ] PostgreSQL database available (RDS, managed DB, or self-hosted)
- [ ] Redis instance available (ElastiCache, managed Redis, or self-hosted)
- [ ] Domain name registered
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Production server provisioned (AWS EC2, DigitalOcean, etc.)

---

## 🔐 STEP 1: SECURITY CONFIGURATION (15 minutes)

### 1.1 Generate Production Secrets

```bash
# Generate a secure SECRET_KEY for JWT tokens
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Save the output - you'll need it for environment variables
```

### 1.2 Create Production Environment File

Create `.env.production` in the root directory:

```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_generated_secret_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@your-db-host:5432/wellbeing_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis Configuration
REDIS_URL=redis://your-redis-host:6379/0
REDIS_PASSWORD=your_redis_password

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# CORS Settings - IMPORTANT: Restrict to your domain
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# MQTT Settings (for IoT devices)
MQTT_BROKER_URL=mqtt://your-mqtt-broker:1883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password

# ML Model Settings
ML_MODEL_PATH=/app/ai-models/models
MODEL_VERSION=1.0.0

# Monitoring (optional but recommended)
SENTRY_DSN=your_sentry_dsn_here
```

### 1.3 Update CORS Configuration

Edit `backend-api/app/main.py`:

```python
# PRODUCTION: Restrict CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],  # Change from ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐳 STEP 2: BUILD DOCKER IMAGES (20 minutes)

### 2.1 Build Production Images

```bash
# Build backend API image
cd backend-api
docker build -t wellbeing-api:1.0.0 -f Dockerfile .

# Tag for registry (if using)
docker tag wellbeing-api:1.0.0 your-registry/wellbeing-api:1.0.0

# Push to registry (optional)
docker push your-registry/wellbeing-api:1.0.0
```

### 2.2 Update Docker Compose for Production

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  api:
    image: wellbeing-api:1.0.0
    container_name: wellbeing-api
    restart: always
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: wellbeing-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: wellbeing-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api

volumes:
  redis-data:
    driver: local
```

---

## 🌐 STEP 3: NGINX CONFIGURATION (15 minutes)

### 3.1 Create Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API Proxy
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health Check (no rate limit)
        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

---

## 🗄️ STEP 4: DATABASE SETUP (20 minutes)

### 4.1 Create Production Database

```bash
# Connect to PostgreSQL
psql -h your-db-host -U postgres

# Create database and user
CREATE DATABASE wellbeing_db;
CREATE USER wellbeing_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE wellbeing_db TO wellbeing_user;
\q
```

### 4.2 Run Database Migrations

```bash
# Install alembic if not already installed
pip install alembic psycopg2-binary

# Initialize alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 4.3 Create Database Indexes

```sql
-- Connect to database
\c wellbeing_db

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_timestamp ON notifications(timestamp);
CREATE INDEX idx_analytics_user ON analytics(user_id);
CREATE INDEX idx_analytics_date ON analytics(date);
CREATE INDEX idx_devices_user ON devices(user_id);
```

---

## 🚀 STEP 5: DEPLOY TO PRODUCTION (30 minutes)

### 5.1 Transfer Files to Server

```bash
# Copy files to production server
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  . user@your-server:/opt/wellbeing-system/

# SSH to server
ssh user@your-server
cd /opt/wellbeing-system
```

### 5.2 Start Services

```bash
# Load environment variables
export $(cat .env.production | xargs)

# Start services with docker compose
docker-compose -f docker-compose.production.yml up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 5.3 Verify Deployment

```bash
# Check API health
curl https://yourdomain.com/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-01-04T..."}

# Check database connection
curl https://yourdomain.com/api/v1/health/db

# Check Redis connection
curl https://yourdomain.com/api/v1/health/redis
```

---

## 📱 STEP 6: MOBILE APP DEPLOYMENT

### 6.1 Update API Endpoint

Edit `mobile-app/src/config.js`:

```javascript
const config = {
  API_BASE_URL: 'https://yourdomain.com/api/v1',
  WS_URL: 'wss://yourdomain.com/ws',
  ENVIRONMENT: 'production'
};

export default config;
```

### 6.2 Build Android APK

```bash
cd mobile-app

# Install dependencies
npm install

# Build production APK
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

### 6.3 Sign APK (Required for Play Store)

```bash
# Generate keystore (first time only)
keytool -genkeypair -v -keystore wellbeing-release.keystore \
  -alias wellbeing -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore wellbeing-release.keystore \
  app/build/outputs/apk/release/app-release-unsigned.apk wellbeing

# Align APK
zipalign -v 4 app-release-unsigned.apk app-release.apk
```

---

## 📊 STEP 7: MONITORING SETUP (30 minutes)

### 7.1 Set Up Error Tracking (Sentry)

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

Add to `backend-api/app/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### 7.2 Set Up Uptime Monitoring

**Option 1: UptimeRobot (Free)**
1. Sign up at uptimerobot.com
2. Create HTTP(S) monitor for: `https://yourdomain.com/health`
3. Set check interval: 5 minutes
4. Configure alert contacts

**Option 2: Pingdom**
1. Sign up at pingdom.com
2. Create uptime check
3. Configure SMS/email alerts

### 7.3 Set Up Log Aggregation

**Simple Solution: Centralized Logging**

```yaml
# Add to docker-compose.production.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
        labels: "service=api"
```

**Advanced Solution: ELK Stack (Optional)**
- Elasticsearch for log storage
- Logstash for log processing
- Kibana for visualization

---

## ✅ STEP 8: POST-DEPLOYMENT VERIFICATION (30 minutes)

### 8.1 Run Smoke Tests

```bash
# Test user registration
curl -X POST https://yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Test user login
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Test protected endpoint
TOKEN="your_access_token"
curl -H "Authorization: Bearer $TOKEN" \
  https://yourdomain.com/api/v1/profile
```

### 8.2 Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://yourdomain.com/api/v1/health

# Expected results:
# - Requests per second: >100
# - Time per request: <100ms (mean)
# - No failed requests
```

### 8.3 Security Verification

```bash
# Check SSL certificate
curl -vI https://yourdomain.com

# Check security headers
curl -I https://yourdomain.com | grep -E 'Strict-Transport|X-Frame|X-Content'

# Verify CORS restrictions
curl -H "Origin: https://malicious-site.com" \
  -I https://yourdomain.com/api/v1/health
```

---

## 🔧 STEP 9: OPERATIONAL PROCEDURES

### 9.1 Backup Procedures

**Database Backup (Daily):**
```bash
# Create backup script
cat > /opt/wellbeing-system/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h your-db-host -U wellbeing_user wellbeing_db \
  | gzip > /backups/wellbeing_db_$DATE.sql.gz

# Keep only last 30 days
find /backups -name "wellbeing_db_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /opt/wellbeing-system/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/wellbeing-system/backup.sh
```

**Redis Backup:**
```bash
# Redis automatically creates dump.rdb with appendonly mode
# Copy to backup location daily
0 3 * * * cp /var/lib/redis/dump.rdb /backups/redis_$(date +%Y%m%d).rdb
```

### 9.2 Monitoring Checklist

**Daily:**
- [ ] Check error rates in Sentry
- [ ] Review application logs
- [ ] Verify uptime status
- [ ] Check response times

**Weekly:**
- [ ] Review performance trends
- [ ] Check disk space
- [ ] Review security logs
- [ ] Update dependencies (if needed)

**Monthly:**
- [ ] Review backup integrity
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Cost optimization review

### 9.3 Rollback Procedure

```bash
# If deployment fails, rollback:

# 1. Stop current services
docker-compose -f docker-compose.production.yml down

# 2. Switch to previous version
docker tag wellbeing-api:previous wellbeing-api:1.0.0

# 3. Restart services
docker-compose -f docker-compose.production.yml up -d

# 4. Verify rollback
curl https://yourdomain.com/health
```

---

## 🚨 TROUBLESHOOTING

### Common Issues

**Issue: Database connection fails**
```bash
# Check database connectivity
psql -h your-db-host -U wellbeing_user -d wellbeing_db

# Check DATABASE_URL in .env.production
# Verify firewall rules allow connection
```

**Issue: Redis connection fails**
```bash
# Check Redis connectivity
redis-cli -h your-redis-host ping

# Check REDIS_URL in .env.production
# Verify Redis password if set
```

**Issue: High response times**
```bash
# Check Redis cache hit rate
curl https://yourdomain.com/api/v1/cache/stats

# Check database pool status
curl https://yourdomain.com/api/v1/db/stats

# Review slow query logs
docker logs wellbeing-api | grep "Slow request"
```

**Issue: Out of memory**
```bash
# Check container memory usage
docker stats

# Increase container memory limit in docker-compose
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📞 SUPPORT

### Getting Help

- **Documentation:** [GitHub README](../README.md)
- **Issues:** [GitHub Issues](https://github.com/Kunal88591/Privacy-Focused-Context-Aware-Digital-Wellbeing-System/issues)
- **Email:** support@yourdomain.com

### Emergency Contacts

- **Primary On-Call:** [To be assigned]
- **Secondary On-Call:** [To be assigned]
- **Escalation:** [To be defined]

---

## ✅ LAUNCH COMPLETION CHECKLIST

- [ ] All services running and healthy
- [ ] Database accessible and backed up
- [ ] Redis cache operational
- [ ] SSL certificate valid
- [ ] CORS properly configured
- [ ] Monitoring and alerts configured
- [ ] Error tracking operational
- [ ] Backups scheduled
- [ ] Mobile app deployed
- [ ] Documentation updated
- [ ] Team notified

**Congratulations! Your system is now live! 🎉**

---

**Developed by:** Kunal Meena (@Kunal88591)  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026
