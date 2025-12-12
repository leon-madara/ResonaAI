# Disaster Recovery Plan

This document outlines procedures for recovering from various disaster scenarios.

## Recovery Objectives

- **RTO (Recovery Time Objective)**: 4 hours for critical services
- **RPO (Recovery Point Objective)**: 1 hour maximum data loss
- **Priority Services**: Crisis Detection, API Gateway, Database

## Backup Strategy

### Database Backups

**Automated Backups:**
- RDS automated backups: Daily at 3:00 AM UTC
- Retention: 7 days
- Point-in-time recovery: Enabled

**Manual Snapshots:**
- Before major deployments
- Before schema changes
- Weekly manual snapshots (retained for 30 days)

**Backup Verification:**
- Monthly restore tests
- Verify data integrity
- Test recovery procedures

### Application Backups

**Container Images:**
- All images stored in GitHub Container Registry
- Tagged with version numbers
- Previous versions retained

**Configuration:**
- Terraform state in S3 with versioning
- Configuration files in Git
- Secrets in AWS Secrets Manager

## Disaster Scenarios

### Scenario 1: Single Region Failure (Kenya)

**Impact:** Complete service outage in primary region

**Recovery Steps:**

1. **Activate DR Region (South Africa):**
   ```bash
   cd infrastructure/terraform
   terraform workspace select south-africa
   terraform apply
   ```

2. **Update DNS:**
   - Point domain to South Africa ALB
   - TTL set to 5 minutes for quick failover

3. **Restore Database:**
   ```bash
   # Restore from latest snapshot
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier mental-health-platform-sa-rds \
     --db-snapshot-identifier mental-health-platform-kenya-rds-snapshot-YYYY-MM-DD \
     --region af-south-1
   ```

4. **Deploy Services:**
   - Deploy all services to South Africa ECS cluster
   - Update service configurations
   - Verify health checks

5. **Verify Functionality:**
   - Test critical user flows
   - Verify database connectivity
   - Check monitoring

**Estimated Recovery Time:** 2-3 hours

### Scenario 2: Database Corruption

**Impact:** Data integrity issues, potential data loss

**Recovery Steps:**

1. **Immediate Actions:**
   - Stop all writes (disable API Gateway)
   - Isolate affected database
   - Assess extent of corruption

2. **Restore from Backup:**
   ```bash
   # Identify last known good snapshot
   aws rds describe-db-snapshots \
     --db-instance-identifier mental-health-platform-kenya-rds
   
   # Restore to new instance
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier mental-health-platform-kenya-rds-restored \
     --db-snapshot-identifier <snapshot-id>
   ```

3. **Point Services to Restored Database:**
   - Update ECS task definitions
   - Update connection strings
   - Restart services

4. **Data Recovery:**
   - Identify data lost since last backup
   - Restore from sync queue if available
   - Replay transactions if possible

5. **Verification:**
   - Verify data integrity
   - Test critical functionality
   - Monitor for issues

**Estimated Recovery Time:** 1-2 hours

### Scenario 3: Complete AWS Region Failure

**Impact:** Complete infrastructure loss

**Recovery Steps:**

1. **Activate DR Region:**
   - Provision infrastructure in South Africa
   - Use Terraform to recreate resources

2. **Restore Data:**
   - Restore database from cross-region snapshot
   - Restore S3 data from backup

3. **Deploy Applications:**
   - Pull images from container registry
   - Deploy all services
   - Configure monitoring

4. **Update DNS:**
   - Point to new region
   - Verify propagation

**Estimated Recovery Time:** 3-4 hours

### Scenario 4: Security Breach

**Impact:** Potential data exposure, service compromise

**Recovery Steps:**

1. **Immediate Containment:**
   - Isolate affected services
   - Revoke compromised credentials
   - Enable additional logging

2. **Assess Impact:**
   - Identify compromised data
   - Review access logs
   - Determine breach scope

3. **Remediate:**
   - Rotate all secrets
   - Patch vulnerabilities
   - Update security groups

4. **Restore Services:**
   - Deploy patched versions
   - Verify security controls
   - Monitor for anomalies

5. **Post-Incident:**
   - Notify affected users (if required)
   - Document incident
   - Implement additional security measures

**Estimated Recovery Time:** 2-6 hours (depending on scope)

## Recovery Procedures by Component

### Database Recovery

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier mental-health-platform-kenya-rds

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mental-health-platform-kenya-rds-restored \
  --db-snapshot-identifier <snapshot-id>

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier mental-health-platform-kenya-rds \
  --target-db-instance-identifier mental-health-platform-kenya-rds-restored \
  --restore-time 2024-01-01T12:00:00Z
```

### Redis Recovery

```bash
# Redis data is ephemeral, but can restore from backup if available
# Restore from RDB file if backup exists
redis-cli --rdb /path/to/backup.rdb

# Or restore from AOF file
redis-server --appendonly yes
redis-cli --aof-load /path/to/backup.aof
```

### S3 Data Recovery

```bash
# List object versions
aws s3api list-object-versions \
  --bucket mental-health-platform-kenya-audio-storage \
  --prefix audio/

# Restore specific version
aws s3api restore-object \
  --bucket mental-health-platform-kenya-audio-storage \
  --key audio/file.wav \
  --version-id <version-id>
```

## Testing Disaster Recovery

### Quarterly DR Tests

1. **Test Database Restore:**
   - Restore to test instance
   - Verify data integrity
   - Test application connectivity

2. **Test Regional Failover:**
   - Simulate primary region failure
   - Activate DR region
   - Verify service functionality

3. **Test Backup Restoration:**
   - Restore from various backup points
   - Verify data completeness
   - Test recovery procedures

### Monthly Backup Verification

- Verify backups are completing successfully
- Test restore procedures
- Document any issues
- Update procedures as needed

## Communication Plan

### During Disaster

1. **Immediate Notification:**
   - Alert on-call engineer
   - Notify team leads
   - Update status page

2. **Status Updates:**
   - Every 30 minutes during recovery
   - Document progress
   - Communicate ETA

3. **Post-Recovery:**
   - Notify stakeholders
   - Conduct post-mortem
   - Document lessons learned

## Prevention Measures

1. **Regular Backups:**
   - Automated daily backups
   - Manual backups before changes
   - Cross-region replication

2. **Monitoring:**
   - Health checks on all services
   - Alerting on failures
   - Regular backup verification

3. **Documentation:**
   - Keep procedures up to date
   - Document all changes
   - Maintain runbooks

4. **Testing:**
   - Regular DR drills
   - Backup restoration tests
   - Failover testing

