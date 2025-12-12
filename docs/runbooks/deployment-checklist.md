# Deployment Checklist

This checklist should be followed for every deployment to production.

## Pre-Deployment

- [ ] All tests passing (unit, integration, e2e)
- [ ] Code review completed and approved
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Performance benchmarks met
- [ ] Database migrations tested and ready
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment window
- [ ] Backup of current production database completed
- [ ] Monitoring dashboards verified and accessible

## Deployment Steps

### 1. Staging Deployment
- [ ] Deploy to staging environment
- [ ] Run smoke tests on staging
- [ ] Verify all services are healthy
- [ ] Check logs for errors
- [ ] Verify database migrations applied correctly
- [ ] Test critical user flows

### 2. Production Deployment
- [ ] Create deployment branch/tag
- [ ] Update version numbers
- [ ] Run Terraform plan (review changes)
- [ ] Apply Terraform changes (if infrastructure changes)
- [ ] Build and push Docker images
- [ ] Update ECS task definitions (if needed)
- [ ] Deploy services (blue-green or rolling update)
- [ ] Verify health checks passing
- [ ] Monitor error rates and response times

### 3. Post-Deployment Verification

- [ ] All services showing healthy in monitoring
- [ ] No increase in error rates
- [ ] Response times within acceptable limits
- [ ] Database connections stable
- [ ] Redis cache functioning
- [ ] Critical user flows tested
- [ ] SSL certificates valid
- [ ] CDN cache cleared (if applicable)

## Rollback Criteria

Immediately rollback if:
- Error rate increases by > 5%
- Response time increases by > 50%
- Any critical service becomes unavailable
- Database connection issues
- Data integrity concerns
- Security vulnerabilities detected

## Rollback Procedure

1. Identify the last known good version
2. Revert to previous task definition/image
3. Update ECS services to previous version
4. Verify services return to healthy state
5. Investigate root cause
6. Document incident

## Communication

- Notify team of deployment start
- Notify team of successful deployment
- Notify team immediately if rollback required
- Update status page (if applicable)
- Document any issues encountered

## Post-Deployment

- [ ] Monitor for 1 hour after deployment
- [ ] Review logs for any anomalies
- [ ] Update deployment documentation
- [ ] Conduct post-mortem if issues occurred
- [ ] Update runbooks based on lessons learned

