# Monitoring & Alerting Setup Guide

**Project:** Privacy-Focused Context-Aware Digital Wellbeing System  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026

---

## 📊 OVERVIEW

This guide covers setting up comprehensive monitoring and alerting for production deployment.

**Monitoring Goals:**
- **Availability:** Track uptime and service health
- **Performance:** Monitor response times and throughput
- **Errors:** Detect and alert on errors immediately
- **Resources:** Track CPU, memory, disk usage
- **Business Metrics:** User activity, API usage

---

## 🎯 MONITORING STACK OPTIONS

### Option 1: Simple & Free (Recommended for Small Deployments)

**Components:**
- **Uptime Monitoring:** UptimeRobot (free tier)
- **Error Tracking:** Sentry (free tier: 5,000 events/month)
- **Logs:** Docker JSON logs + basic scripts
- **Metrics:** Built-in performance middleware

**Cost:** Free  
**Setup Time:** 1-2 hours  
**Suitable For:** MVP, small teams, <1000 users

### Option 2: Professional (Recommended for Production)

**Components:**
- **APM:** New Relic or DataDog
- **Uptime:** Pingdom or StatusCake
- **Error Tracking:** Sentry (paid tier)
- **Logs:** ELK Stack or Splunk
- **Alerts:** PagerDuty

**Cost:** $50-200/month  
**Setup Time:** 4-8 hours  
**Suitable For:** Production, teams, >1000 users

### Option 3: Enterprise

**Components:**
- **Full observability:** DataDog, New Relic
- **Distributed tracing:** Jaeger, Zipkin
- **Log management:** Splunk, ELK
- **On-call:** PagerDuty, OpsGenie
- **Status page:** StatusPage.io

**Cost:** $500+/month  
**Setup Time:** 1-2 days  
**Suitable For:** Large scale, enterprise

---

## 🚀 QUICK START: SIMPLE MONITORING (Option 1)

### STEP 1: Error Tracking with Sentry (15 minutes)

#### 1.1 Create Sentry Account

1. Go to [sentry.io](https://sentry.io)
2. Sign up for free account
3. Create new project: "Digital Wellbeing API"
4. Copy your DSN (Data Source Name)

#### 1.2 Install Sentry SDK

```bash
cd backend-api
pip install sentry-sdk[fastapi]==1.40.0
pip freeze > requirements.txt
```

#### 1.3 Configure Sentry

Add to `backend-api/app/main.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
import os

# Initialize Sentry
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FastApiIntegration(),
            AsyncioIntegration(),
        ],
        traces_sample_rate=1.0,  # 100% of transactions
        environment=os.getenv("ENVIRONMENT", "production"),
        release=f"wellbeing-api@{os.getenv('VERSION', '1.0.0')}",
        
        # Set performance monitoring
        enable_tracing=True,
        
        # Filter sensitive data
        before_send=filter_sensitive_data,
    )

def filter_sensitive_data(event, hint):
    """Remove sensitive data from Sentry events"""
    # Remove passwords from error context
    if 'request' in event:
        if 'data' in event['request']:
            data = event['request']['data']
            if isinstance(data, dict):
                data.pop('password', None)
                data.pop('token', None)
    return event

# Test Sentry integration
@app.get("/sentry-test")
async def sentry_test():
    """Test endpoint to verify Sentry error tracking"""
    try:
        1 / 0
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
```

Add to `.env.production`:

```bash
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
ENVIRONMENT=production
VERSION=1.0.0
```

#### 1.4 Configure Sentry Alerts

1. Go to Sentry project settings
2. Navigate to **Alerts** → **Create Alert Rule**
3. Create these alert rules:

**High Error Rate Alert:**
- Condition: Errors > 10 in 1 minute
- Action: Email to team
- Severity: Critical

**New Error Alert:**
- Condition: First seen error
- Action: Email to team
- Severity: Warning

**Performance Alert:**
- Condition: Transaction duration > 1s
- Action: Email to team
- Severity: Warning

### STEP 2: Uptime Monitoring with UptimeRobot (10 minutes)

#### 2.1 Create UptimeRobot Account

1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account (50 monitors)
3. Verify email

#### 2.2 Create Monitors

**Monitor 1: API Health Check**
- Type: HTTP(S)
- URL: `https://yourdomain.com/health`
- Name: "Wellbeing API - Health"
- Interval: 5 minutes
- Alert contacts: Your email

**Monitor 2: Database Health**
- Type: HTTP(S)
- URL: `https://yourdomain.com/api/v1/health/db`
- Name: "Wellbeing API - Database"
- Interval: 5 minutes
- Alert contacts: Your email

**Monitor 3: Cache Health**
- Type: HTTP(S)
- URL: `https://yourdomain.com/api/v1/health/redis`
- Name: "Wellbeing API - Redis"
- Interval: 5 minutes
- Alert contacts: Your email

#### 2.3 Configure Alerts

1. Go to **My Settings** → **Alert Contacts**
2. Add email, SMS (optional), Slack (optional)
3. Enable notifications for:
   - Monitor goes down
   - Monitor comes back up

### STEP 3: Application Performance Monitoring (10 minutes)

#### 3.1 Add Custom Metrics

Create `backend-api/app/middleware/metrics.py`:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect application metrics"""
    
    def __init__(self):
        self.request_count = defaultdict(int)
        self.error_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.last_reset = datetime.now()
    
    def record_request(self, path: str, method: str, status: int, duration: float):
        """Record request metrics"""
        endpoint = f"{method} {path}"
        self.request_count[endpoint] += 1
        self.response_times[endpoint].append(duration)
        
        if status >= 400:
            self.error_count[endpoint] += 1
    
    def get_stats(self) -> dict:
        """Get current metrics"""
        stats = {
            "total_requests": sum(self.request_count.values()),
            "total_errors": sum(self.error_count.values()),
            "endpoints": {}
        }
        
        for endpoint, count in self.request_count.items():
            times = self.response_times[endpoint]
            stats["endpoints"][endpoint] = {
                "count": count,
                "errors": self.error_count[endpoint],
                "avg_time": sum(times) / len(times) if times else 0,
                "max_time": max(times) if times else 0,
                "min_time": min(times) if times else 0
            }
        
        return stats
    
    def reset(self):
        """Reset metrics (call hourly/daily)"""
        self.request_count.clear()
        self.error_count.clear()
        self.response_times.clear()
        self.last_reset = datetime.now()

# Global metrics collector
metrics = MetricsCollector()

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Record metrics
        metrics.record_request(
            path=request.url.path,
            method=request.method,
            status=response.status_code,
            duration=duration
        )
        
        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.2f}s"
            )
        
        return response
```

Add metrics endpoint in `main.py`:

```python
from app.middleware.metrics import MetricsMiddleware, metrics

# Add middleware
app.add_middleware(MetricsMiddleware)

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics.get_stats()
```

#### 3.2 Add Health Check Endpoints

Create `backend-api/app/api/health.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.cache import cache_manager
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """Detailed health check with all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        if cache_manager.redis:
            await cache_manager.redis.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check system resources
    health_status["checks"]["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
    
    return health_status

@router.get("/health/db")
async def database_health(db: Session = Depends(get_db)):
    """Check database connectivity"""
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "timestamp": time.time()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}

@router.get("/health/redis")
async def redis_health():
    """Check Redis connectivity"""
    try:
        if cache_manager.redis:
            await cache_manager.redis.ping()
            return {"status": "healthy", "timestamp": time.time()}
        return {"status": "not configured", "timestamp": time.time()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}
```

Register in `main.py`:

```python
from app.api.health import router as health_router

app.include_router(health_router, tags=["health"])
```

### STEP 4: Log Management (15 minutes)

#### 4.1 Configure Structured Logging

Create `backend-api/app/core/logging_config.py`:

```python
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON log formatter"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add level
        log_record['level'] = record.levelname
        
        # Add service name
        log_record['service'] = 'wellbeing-api'
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id

def setup_logging():
    """Setup structured logging"""
    # Create handler
    handler = logging.StreamHandler()
    
    # Use JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Set levels for specific loggers
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
```

Add to `main.py`:

```python
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()
```

#### 4.2 Add Log Rotation

Update `docker-compose.production.yml`:

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"  # Max log file size
        max-file: "5"     # Keep 5 log files
        compress: "true"  # Compress old logs
```

#### 4.3 Create Log Analysis Script

Create `scripts/analyze-logs.sh`:

```bash
#!/bin/bash

# Analyze logs for errors
echo "=== Error Summary (Last Hour) ==="
docker logs wellbeing-api --since 1h 2>&1 | grep -i error | wc -l

echo ""
echo "=== Top 10 Errors ==="
docker logs wellbeing-api --since 24h 2>&1 | \
  grep -i error | \
  sort | uniq -c | sort -nr | head -10

echo ""
echo "=== Slow Requests (>1s) ==="
docker logs wellbeing-api --since 1h 2>&1 | \
  grep "Slow request" | tail -20

echo ""
echo "=== Response Time Stats ==="
docker logs wellbeing-api --since 1h 2>&1 | \
  grep "Request completed" | \
  awk '{print $NF}' | \
  awk '{sum+=$1; count++} END {print "Avg:", sum/count "ms"}'
```

Make it executable:

```bash
chmod +x scripts/analyze-logs.sh
```

### STEP 5: Alerting Rules (10 minutes)

#### 5.1 Create Alert Script

Create `scripts/check-health.sh`:

```bash
#!/bin/bash

# Configuration
API_URL="https://yourdomain.com"
ALERT_EMAIL="alerts@yourdomain.com"
SLACK_WEBHOOK="your_slack_webhook_url"

# Check API health
check_health() {
    response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" != "200" ]; then
        send_alert "API Health Check Failed" "HTTP $http_code: $body"
        return 1
    fi
    return 0
}

# Check database
check_database() {
    response=$(curl -s "$API_URL/health/db")
    status=$(echo "$response" | jq -r '.status')
    
    if [ "$status" != "healthy" ]; then
        send_alert "Database Health Check Failed" "$response"
        return 1
    fi
    return 0
}

# Check Redis
check_redis() {
    response=$(curl -s "$API_URL/health/redis")
    status=$(echo "$response" | jq -r '.status')
    
    if [ "$status" != "healthy" ]; then
        send_alert "Redis Health Check Failed" "$response"
        return 1
    fi
    return 0
}

# Send alert
send_alert() {
    title=$1
    message=$2
    
    # Email alert
    echo "$message" | mail -s "$title" "$ALERT_EMAIL"
    
    # Slack alert
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST "$SLACK_WEBHOOK" \
          -H 'Content-Type: application/json' \
          -d "{\"text\":\"🚨 $title\n$message\"}"
    fi
    
    # Log alert
    echo "[$(date)] ALERT: $title - $message" >> /var/log/wellbeing-alerts.log
}

# Run checks
echo "Running health checks..."
check_health
check_database
check_redis

echo "Health checks complete."
```

#### 5.2 Schedule Health Checks

Add to crontab:

```bash
# Edit crontab
crontab -e

# Add health checks every 5 minutes
*/5 * * * * /opt/wellbeing-system/scripts/check-health.sh

# Add log analysis every hour
0 * * * * /opt/wellbeing-system/scripts/analyze-logs.sh >> /var/log/wellbeing-analysis.log
```

---

## 📈 MONITORING DASHBOARDS

### Built-in Metrics Dashboard

Access at: `https://yourdomain.com/metrics`

Shows:
- Total requests
- Error count and rate
- Average response time per endpoint
- Slowest endpoints
- Most used endpoints

### Example Grafana Dashboard (Optional)

If using Prometheus + Grafana:

```yaml
# Add to docker-compose.production.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

---

## 🔔 ALERT SEVERITY LEVELS

### Critical (P1) - Immediate Action Required
- API completely down
- Database connection lost
- Error rate > 50%
- Data loss risk

**Response Time:** < 15 minutes  
**Notification:** SMS, phone call, Slack

### High (P2) - Action Required Soon
- Performance degradation (>2s response time)
- Error rate > 10%
- Redis cache down
- Disk space > 90%

**Response Time:** < 1 hour  
**Notification:** Email, Slack

### Medium (P3) - Action Required
- Error rate > 5%
- Slow queries (>500ms)
- Memory usage > 80%
- Failed background jobs

**Response Time:** < 4 hours  
**Notification:** Email

### Low (P4) - Informational
- New error types
- Performance warnings
- Deprecated API usage
- Configuration recommendations

**Response Time:** Next business day  
**Notification:** Email digest

---

## 📊 KEY METRICS TO TRACK

### Application Metrics
- **Request Rate:** requests/second
- **Error Rate:** % of failed requests
- **Response Time:** p50, p95, p99
- **Apdex Score:** User satisfaction metric

### Infrastructure Metrics
- **CPU Usage:** % utilization
- **Memory Usage:** % and MB used
- **Disk I/O:** read/write operations
- **Network:** inbound/outbound traffic

### Business Metrics
- **Active Users:** daily/weekly/monthly
- **API Usage:** calls per user
- **Feature Adoption:** usage per feature
- **User Retention:** cohort analysis

---

## ✅ MONITORING CHECKLIST

- [ ] Sentry configured for error tracking
- [ ] UptimeRobot monitors created
- [ ] Health check endpoints working
- [ ] Custom metrics collecting data
- [ ] Structured logging implemented
- [ ] Log rotation configured
- [ ] Alert scripts created
- [ ] Health check cron jobs scheduled
- [ ] Alert notification channels tested
- [ ] Monitoring dashboard accessible
- [ ] Documentation updated with runbooks

---

## 📚 MONITORING BEST PRACTICES

1. **Set meaningful alerts** - Avoid alert fatigue
2. **Monitor user experience** - Not just technical metrics
3. **Create runbooks** - Document response procedures
4. **Regular reviews** - Adjust thresholds based on data
5. **Test alerts** - Ensure notifications work
6. **Track trends** - Not just current values
7. **Correlate events** - Connect metrics for root cause analysis
8. **Document incidents** - Post-mortems for learning

---

## 🆘 INCIDENT RESPONSE PLAYBOOK

### 1. API Down

**Detection:** Uptime monitor alert  
**Steps:**
1. Check service status: `docker ps`
2. Check logs: `docker logs wellbeing-api --tail 100`
3. Restart service: `docker-compose restart api`
4. If persists, check infrastructure
5. Notify users via status page

### 2. High Error Rate

**Detection:** Sentry alert  
**Steps:**
1. Check Sentry for error details
2. Identify affected endpoints
3. Check recent deployments
4. Rollback if caused by new deployment
5. Fix and redeploy

### 3. Database Connection Issues

**Detection:** Database health check failure  
**Steps:**
1. Check database status
2. Verify connection strings
3. Check connection pool status
4. Restart database connections
5. Check database logs for errors

### 4. Performance Degradation

**Detection:** Slow request alerts  
**Steps:**
1. Check cache hit rate
2. Review database query performance
3. Check system resources (CPU, memory)
4. Identify slow queries
5. Optimize or add caching

---

**Setup Complete! Your monitoring system is ready! 📊**

---

**Developed by:** Kunal Meena (@Kunal88591)  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026
