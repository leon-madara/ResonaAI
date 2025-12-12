# Monitoring and Alerts Guide

This guide explains the monitoring setup and how to respond to alerts.

## Monitoring Stack

- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notification
- **ELK Stack**: Log aggregation and analysis

## Access URLs

- **Grafana**: http://localhost:3000 (admin/admin - change in production)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **Kibana**: http://localhost:5601

## Key Dashboards

### Service Health Dashboard
- Service status (up/down)
- Response times (p50, p95, p99)
- Request rates
- Error rates

### API Metrics Dashboard
- Total requests
- Error rate percentage
- Average and P95 response times
- Requests by status code
- Response time distribution

### System Resources Dashboard
- CPU usage
- Memory usage
- Disk usage
- Network I/O
- Disk I/O

## Alert Categories

### Critical Alerts

#### ServiceDown
**Description:** A service is not responding to health checks

**Response:**
1. Check service logs: `docker-compose logs <service-name>`
2. Check if container is running: `docker-compose ps`
3. Restart service if needed: `docker-compose restart <service-name>`
4. If persistent, check resource constraints
5. Escalate if unable to resolve

#### CrisisDetectionServiceDown
**Description:** Crisis detection service is down (HIGHEST PRIORITY)

**Response:**
1. **IMMEDIATE ACTION REQUIRED** - This affects user safety
2. Check service status and logs
3. Restart service immediately
4. Verify service is processing crisis detection
5. Check for missed crisis events
6. Notify on-call engineer immediately

#### DatabaseConnectionFailure
**Description:** Cannot connect to PostgreSQL database

**Response:**
1. Check database status: `docker-compose ps postgres`
2. Check database logs: `docker-compose logs postgres`
3. Verify database is accessible: `docker-compose exec postgres psql -U postgres -d mental_health -c "SELECT 1;"`
4. Check connection pool settings
5. Restart database if needed (with caution)
6. Escalate if database is corrupted

#### RedisDown
**Description:** Redis cache is not responding

**Response:**
1. Check Redis status: `docker-compose ps redis`
2. Check Redis logs: `docker-compose logs redis`
3. Test Redis connection: `docker-compose exec redis redis-cli ping`
4. Restart Redis if needed
5. Verify cache is functioning after restart

### Warning Alerts

#### HighErrorRate
**Description:** Error rate exceeds 5% threshold

**Response:**
1. Check error logs in Grafana/Kibana
2. Identify which endpoints are failing
3. Check for recent deployments
4. Review error patterns
5. Check database connectivity
6. Consider rolling back if recent deployment

#### HighResponseTime
**Description:** 95th percentile response time exceeds 2 seconds

**Response:**
1. Identify slow endpoints
2. Check database query performance
3. Check Redis cache hit rates
4. Review resource utilization (CPU, memory)
5. Check for external API delays
6. Consider scaling up if persistent

#### HighDatabaseConnections
**Description:** Database has > 80 active connections

**Response:**
1. Check connection pool settings
2. Identify services with high connection usage
3. Review for connection leaks
4. Consider increasing connection limits
5. Optimize connection pooling

#### HighRedisMemory
**Description:** Redis memory usage > 90%

**Response:**
1. Check Redis memory usage: `docker-compose exec redis redis-cli INFO memory`
2. Identify large keys: `docker-compose exec redis redis-cli --bigkeys`
3. Review cache TTL settings
4. Consider increasing Redis memory
5. Implement cache eviction if needed

#### HighCrisisDetectionRate
**Description:** Unusually high crisis detection rate (> 5 per minute)

**Response:**
1. Review crisis detection logs
2. Verify detections are legitimate
3. Check for false positives
4. Review detection thresholds
5. Notify crisis response team if legitimate

### System Resource Alerts

#### HighCPUUsage
**Description:** CPU usage > 80% for 10 minutes

**Response:**
1. Identify services with high CPU usage
2. Check for CPU-intensive operations
3. Review recent code changes
4. Consider scaling horizontally
5. Optimize code if needed

#### HighMemoryUsage
**Description:** Memory usage > 85% for 10 minutes

**Response:**
1. Identify services with high memory usage
2. Check for memory leaks
3. Review memory limits
4. Consider scaling up or out
5. Restart services if needed

#### DiskSpaceLow
**Description:** Disk space < 15% available

**Response:**
1. Identify what's using disk space
2. Clean up old logs
3. Remove unused Docker images: `docker system prune -a`
4. Archive old data
5. Consider increasing disk size

## Alert Response Workflow

1. **Acknowledge Alert**
   - Alert received via email/Slack/Discord
   - Acknowledge in AlertManager

2. **Investigate**
   - Check relevant dashboards
   - Review logs
   - Identify root cause

3. **Resolve**
   - Apply fix
   - Verify resolution
   - Monitor for recurrence

4. **Document**
   - Document issue and resolution
   - Update runbooks if needed
   - Conduct post-mortem for critical issues

## Alert Escalation

### Escalation Path

1. **Level 1**: On-call engineer (first 15 minutes)
2. **Level 2**: Team lead (if unresolved after 15 minutes)
3. **Level 3**: Engineering manager (if unresolved after 30 minutes)
4. **Level 4**: CTO/VP Engineering (for critical production issues)

### Escalation Criteria

- Service down for > 15 minutes
- Database unavailable
- Crisis detection service down (immediate escalation)
- Security breach suspected
- Data loss detected
- Unable to resolve after 30 minutes

## Alert Tuning

### Reducing False Positives

- Adjust thresholds based on historical data
- Add alert grouping to reduce noise
- Use alert inhibition rules
- Review and update alert rules quarterly

### Adding New Alerts

1. Identify metric to monitor
2. Define threshold
3. Create alert rule in Prometheus
4. Configure AlertManager routing
5. Test alert
6. Document in this guide

## Maintenance

### Weekly
- Review alert history
- Check for alert fatigue
- Verify all alerts are working

### Monthly
- Review and tune thresholds
- Update alert rules
- Review escalation procedures

### Quarterly
- Comprehensive alert review
- Update documentation
- Train team on new alerts

