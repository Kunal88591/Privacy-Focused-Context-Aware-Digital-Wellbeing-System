# Post-Launch Maintenance Guide

**Project:** Privacy-Focused Context-Aware Digital Wellbeing System  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026

---

## 📋 OVERVIEW

This guide covers ongoing maintenance, operations, and support after launch. Follow these procedures to keep your system running smoothly.

---

## 🗓️ DAILY OPERATIONS

### Morning Checklist (15 minutes)

**1. System Health Check**
```bash
# Check all services are running
docker ps

# Expected output: all containers "Up" status
# - wellbeing-api
# - wellbeing-redis
# - wellbeing-nginx (if using)
```

**2. Review Overnight Metrics**
```bash
# Check error rates
curl https://yourdomain.com/metrics | jq '.total_errors'

# View recent errors in Sentry
# Go to: sentry.io/your-project/issues

# Check uptime status
# Go to: uptimerobot.com/dashboard
```

**3. Check System Resources**
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -20
```

**4. Review Logs**
```bash
# Check for errors in last 24 hours
docker logs wellbeing-api --since 24h 2>&1 | grep -i error | wc -l

# If errors > 10, investigate:
docker logs wellbeing-api --since 24h 2>&1 | grep -i error | tail -20
```

### Evening Checklist (10 minutes)

**1. Verify Backups Completed**
```bash
# Check last backup timestamp
ls -lht /backups | head -5

# Verify backup file size (should be > 1MB)
du -h /backups/*.sql.gz | tail -1
```

**2. Review Daily Metrics**
```bash
# Get daily statistics
curl https://yourdomain.com/metrics

# Key metrics to check:
# - total_requests should be > 0
# - error_rate should be < 1%
# - avg_response_time should be < 200ms
```

**3. Check User Activity**
```bash
# Check active users today
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://yourdomain.com/api/v1/admin/stats/daily
```

---

## 📅 WEEKLY OPERATIONS

### Monday: Review & Plan (30 minutes)

**1. Weekly Metrics Review**
```bash
# Generate weekly report
curl https://yourdomain.com/api/v1/analytics/weekly-summary
```

Key metrics to review:
- Active users (DAU, WAU, MAU)
- API request volume
- Error rate trends
- Performance metrics
- New user signups
- User retention

**2. Error Analysis**
```bash
# Run weekly error analysis
./scripts/analyze-logs.sh > weekly-report.txt

# Review top errors
cat weekly-report.txt
```

**3. Plan Maintenance**
- Schedule any needed updates
- Plan feature releases
- Review user feedback
- Prioritize bug fixes

### Wednesday: Performance Review (20 minutes)

**1. Check Performance Trends**
```bash
# Review slow queries
docker logs wellbeing-api --since 7d 2>&1 | grep "Slow request"

# Check cache hit rate
curl https://yourdomain.com/api/v1/cache/stats | jq '.hit_rate'
# Should be > 80%
```

**2. Database Maintenance**
```bash
# Check database size
psql $DATABASE_URL -c "
SELECT pg_size_pretty(pg_database_size('wellbeing_db'));
"

# Check for slow queries
psql $DATABASE_URL -c "
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

**3. Optimize if Needed**
```sql
-- Vacuum database
VACUUM ANALYZE;

-- Reindex if needed
REINDEX DATABASE wellbeing_db;
```

### Friday: Security & Updates (30 minutes)

**1. Security Check**
```bash
# Check for security updates
pip list --outdated | grep -E 'security|crypto'

# Review recent access logs
docker logs wellbeing-api --since 7d 2>&1 | grep "401\|403" | wc -l
```

**2. Dependency Updates**
```bash
# Check for dependency updates
cd backend-api
pip list --outdated

# Update non-breaking changes
pip install --upgrade package-name

# Test after updates
pytest
```

**3. Backup Verification**
```bash
# Test database restore (on staging)
gunzip < /backups/latest.sql.gz | psql $STAGING_DATABASE_URL

# Verify data integrity
psql $STAGING_DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

---

## 📆 MONTHLY OPERATIONS

### First Monday: Comprehensive Review (2 hours)

**1. Monthly Metrics Report**
```bash
# Generate monthly report
curl https://yourdomain.com/api/v1/analytics/monthly-summary > monthly-report.json

# Analyze trends
cat monthly-report.json | jq '.'
```

Metrics to analyze:
- User growth rate
- Churn rate
- Feature adoption
- API usage patterns
- Error trends
- Performance trends
- Cost analysis

**2. Capacity Planning**
```bash
# Check resource usage trends
docker stats --no-stream

# Database size growth
psql $DATABASE_URL -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

Plan for:
- Server scaling if CPU/memory > 70% consistently
- Database storage if growing > 10GB/month
- Caching optimization if hit rate < 80%

**3. Security Audit**
```bash
# Run security scan
pip install safety
safety check --file requirements.txt

# Check for exposed secrets
git secrets --scan

# Review access logs for anomalies
./scripts/security-audit.sh
```

### Mid-Month: Feature & Improvements (1 hour)

**1. User Feedback Review**
- Review GitHub issues
- Analyze support emails
- Check user ratings/reviews
- Identify common requests

**2. Bug Triage**
- Categorize open bugs (P1-P4)
- Assign priorities
- Plan fixes
- Update issue tracker

**3. Feature Planning**
- Review feature requests
- Estimate effort required
- Plan sprint/release
- Update roadmap

---

## 🚨 INCIDENT RESPONSE

### Severity Levels

**P1: Critical (< 15 min response)**
- System completely down
- Data loss risk
- Security breach
- Complete database failure

**P2: High (< 1 hour)**
- Major feature broken
- High error rate (> 10%)
- Severe performance degradation
- Partial outage

**P3: Medium (< 4 hours)**
- Minor feature issues
- Moderate error rate (5-10%)
- Performance warnings
- Non-critical failures

**P4: Low (next business day)**
- Cosmetic issues
- Feature requests
- Documentation updates
- Minor improvements

### Incident Response Procedure

**1. Detection & Alert**
```bash
# Acknowledge alert
echo "Incident acknowledged by $(whoami) at $(date)" >> incident.log
```

**2. Initial Assessment**
```bash
# Check service status
docker ps

# Check recent logs
docker logs wellbeing-api --tail 100

# Check system resources
top -bn1
df -h
free -h
```

**3. Immediate Mitigation**

For API down:
```bash
# Restart service
docker-compose restart api

# If fails, check logs
docker logs wellbeing-api

# Check dependencies
docker ps | grep -E "redis|postgres"
```

For high error rate:
```bash
# Check Sentry for error details
# Identify affected endpoint

# If recent deployment, rollback:
docker-compose down
git checkout previous-version
docker-compose up -d
```

For database issues:
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Check connection pool
curl https://yourdomain.com/api/v1/db/stats

# Restart if needed
docker-compose restart db
```

**4. Root Cause Analysis**
```bash
# Gather evidence
docker logs wellbeing-api > incident-logs.txt
docker stats --no-stream > incident-stats.txt

# Document timeline
cat > incident-report.md << EOF
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** X minutes
**Impact:** Users affected, requests failed

## Timeline
- HH:MM - Alert received
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Service restored

## Root Cause
[Describe what happened]

## Resolution
[Describe how it was fixed]

## Prevention
[What will prevent this in future]
EOF
```

**5. Post-Incident**
- Notify stakeholders of resolution
- Complete incident report
- Plan preventive measures
- Update runbooks
- Schedule post-mortem meeting

---

## 🔧 COMMON MAINTENANCE TASKS

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api

# Full rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Clear Cache

```bash
# Clear Redis cache
docker exec wellbeing-redis redis-cli FLUSHALL

# Restart Redis
docker-compose restart redis
```

### Database Maintenance

```bash
# Connect to database
psql $DATABASE_URL

# Vacuum and analyze
VACUUM ANALYZE;

# Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### Log Rotation

```bash
# Manually rotate logs if needed
docker-compose logs --tail=1000 api > archived-logs-$(date +%Y%m%d).log

# Clear docker logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' wellbeing-api)
```

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements
pip freeze > requirements.txt

# Test
pytest

# Deploy if tests pass
docker-compose down
docker-compose up -d --build
```

---

## 📊 MONITORING & METRICS

### Key Metrics to Track

**Application Metrics**
- Requests per second
- Error rate (%)
- Response time (p50, p95, p99)
- Cache hit rate (%)
- Active users

**Infrastructure Metrics**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network I/O
- Database connections

**Business Metrics**
- New user signups
- Daily active users (DAU)
- Weekly active users (WAU)
- Monthly active users (MAU)
- User retention rate

### Setting Up Alerts

**Critical Alerts (SMS + Email)**
- API down (> 2 minutes)
- Error rate > 50%
- Database connection lost
- Disk space > 95%

**High Priority (Email + Slack)**
- Error rate > 10%
- Response time > 2s (p95)
- Memory usage > 90%
- Disk space > 85%

**Medium Priority (Email)**
- Error rate > 5%
- Response time > 1s (p95)
- Cache hit rate < 80%
- Failed backups

---

## 🔐 SECURITY MAINTENANCE

### Weekly Security Tasks

**1. Review Access Logs**
```bash
# Check for suspicious activity
docker logs wellbeing-api --since 7d 2>&1 | grep -E "401|403" | \
  awk '{print $1}' | sort | uniq -c | sort -nr
```

**2. Check Failed Login Attempts**
```bash
# If > 10 failed attempts from same IP, consider blocking
docker logs wellbeing-api --since 7d 2>&1 | grep "Login failed"
```

**3. Review Sentry Errors**
- Check for any security-related errors
- Look for unusual patterns
- Investigate new error types

### Monthly Security Tasks

**1. Dependency Audit**
```bash
# Check for security vulnerabilities
pip install safety
safety check --file requirements.txt

# Update vulnerable packages
pip install --upgrade vulnerable-package
```

**2. SSL Certificate Check**
```bash
# Check certificate expiration
echo | openssl s_client -servername yourdomain.com \
  -connect yourdomain.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

**3. Secrets Rotation**
```bash
# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update in production
# Restart services
```

---

## 📈 SCALING GUIDELINES

### When to Scale

**Vertical Scaling (upgrade server)**
- CPU usage > 70% consistently
- Memory usage > 80% consistently
- Cannot handle traffic spikes

**Horizontal Scaling (add servers)**
- Response time degrading
- Need high availability
- Traffic > 1000 req/sec

**Database Scaling**
- Query performance degrading
- Database size > 50GB
- Connection pool saturated

### Scaling Procedures

**Vertical Scaling**
```bash
# 1. Schedule maintenance window
# 2. Take database backup
# 3. Shutdown services
docker-compose down

# 4. Upgrade server (via hosting provider)
# 5. Start services
docker-compose up -d

# 6. Verify functionality
curl https://yourdomain.com/health
```

**Horizontal Scaling**
```yaml
# 1. Update docker-compose.yml
services:
  api:
    deploy:
      replicas: 3
    
  nginx:
    # Add load balancing config

# 2. Deploy
docker-compose up -d --scale api=3
```

---

## 📞 SUPPORT PROCEDURES

### User Support Tickets

**Priority Assignment**
- **P1 Critical:** Cannot use system, data loss
- **P2 High:** Major feature broken
- **P3 Medium:** Minor feature issue
- **P4 Low:** Enhancement request

**Response Times**
- P1: < 2 hours
- P2: < 8 hours
- P3: < 24 hours
- P4: < 3 business days

**Support Workflow**
1. Ticket received via email/GitHub
2. Categorize and prioritize
3. Acknowledge receipt
4. Investigate and diagnose
5. Provide solution or workaround
6. Follow up to confirm resolution
7. Close ticket

### Common Support Issues

**Issue: Login not working**
```bash
# Check user exists
psql $DATABASE_URL -c "SELECT * FROM users WHERE email='user@example.com';"

# Check password hash
# Verify token generation

# Reset password if needed
psql $DATABASE_URL -c "UPDATE users SET password='new_hash' WHERE email='user@example.com';"
```

**Issue: Notifications not appearing**
```bash
# Check notification service
docker logs wellbeing-api | grep "notification"

# Verify user settings
curl -H "Authorization: Bearer $TOKEN" \
  https://yourdomain.com/api/v1/settings
```

**Issue: Slow performance**
```bash
# Check cache hit rate
curl https://yourdomain.com/api/v1/cache/stats

# Check slow queries
docker logs wellbeing-api | grep "Slow request"

# Check system resources
top -bn1
```

---

## ✅ MAINTENANCE CHECKLIST

### Daily
- [ ] Check service status
- [ ] Review error rates
- [ ] Check system resources
- [ ] Verify backups completed

### Weekly
- [ ] Review weekly metrics
- [ ] Analyze errors
- [ ] Check performance
- [ ] Security scan
- [ ] Update dependencies (minor)

### Monthly
- [ ] Generate monthly report
- [ ] Capacity planning review
- [ ] Security audit
- [ ] Feature planning
- [ ] Cost optimization review

### Quarterly
- [ ] Comprehensive security audit
- [ ] Major version updates
- [ ] Architecture review
- [ ] Disaster recovery test
- [ ] Documentation update

---

## 📚 RESOURCES

### Documentation
- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Launch Guide](LAUNCH_GUIDE.md)
- [Monitoring Setup](MONITORING_SETUP.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

### Tools & Services
- **Monitoring:** Sentry, UptimeRobot
- **Database:** PostgreSQL docs
- **Cache:** Redis docs
- **Container:** Docker docs

### Emergency Contacts
- **Primary On-Call:** [To be assigned]
- **Secondary On-Call:** [To be assigned]
- **Escalation:** [To be defined]

---

**Maintenance Guide Complete! Keep your system healthy! 🛠️**

---

**Developed by:** Kunal Meena (@Kunal88591)  
**Version:** 1.0.0  
**Last Updated:** January 4, 2026
