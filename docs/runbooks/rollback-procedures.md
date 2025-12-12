# Rollback Procedures

This document outlines procedures for rolling back deployments in different scenarios.

## Quick Rollback (ECS)

### Using AWS Console

1. Navigate to ECS → Clusters → mental-health-platform-kenya-cluster
2. Select the service to rollback
3. Click "Update Service"
4. Under "Task Definition", select previous revision
5. Click "Update"
6. Monitor service until all tasks are running previous version

### Using AWS CLI

```bash
# Get current task definition
aws ecs describe-services \
  --cluster mental-health-platform-kenya-cluster \
  --services api-gateway \
  --query 'services[0].taskDefinition'

# Update service to previous task definition
aws ecs update-service \
  --cluster mental-health-platform-kenya-cluster \
  --service api-gateway \
  --task-definition mental-health-platform-kenya-api-gateway:XX \
  --force-new-deployment
```

### Using Terraform

```bash
cd infrastructure/terraform
terraform state list | grep task_definition
terraform state show aws_ecs_task_definition.kenya_api_gateway
# Note the previous revision number
# Update terraform to use previous revision
terraform apply
```

## Database Rollback

### If Migration Failed

1. **Stop the deployment immediately**
2. **Identify the migration that failed**
3. **Check database state:**
   ```sql
   SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5;
   ```
4. **Rollback migration:**
   ```bash
   # If using Alembic
   alembic downgrade -1
   
   # If using raw SQL, run rollback script
   psql -h $DB_HOST -U postgres -d mental_health -f migrations/rollback_XXX.sql
   ```
5. **Verify database integrity**
6. **Fix migration script**
7. **Test migration in staging**
8. **Redeploy**

### If Data Corruption Detected

1. **Stop all writes immediately** (disable API Gateway if needed)
2. **Restore from backup:**
   ```bash
   # Restore RDS snapshot
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier mental-health-platform-kenya-rds-restored \
     --db-snapshot-identifier mental-health-platform-kenya-rds-snapshot-YYYY-MM-DD
   ```
3. **Point services to restored database**
4. **Verify data integrity**
5. **Investigate root cause**

## Container Image Rollback

### Using GitHub Container Registry

```bash
# List available tags
gh api /orgs/resonaai/packages/container/resonaai-api-gateway/versions

# Update docker-compose or ECS task definition to use previous tag
# For docker-compose:
docker-compose pull api-gateway:previous-tag
docker-compose up -d api-gateway

# For ECS, update task definition with previous image tag
```

## Infrastructure Rollback (Terraform)

### Partial Rollback

```bash
cd infrastructure/terraform

# Review what will change
terraform plan -out=rollback.tfplan

# Apply rollback
terraform apply rollback.tfplan
```

### Full Infrastructure Rollback

```bash
# Revert to previous Terraform state
git checkout HEAD~1 infrastructure/terraform/
terraform init -upgrade
terraform plan
terraform apply
```

## Kubernetes Rollback

### Using kubectl

```bash
# View deployment history
kubectl rollout history deployment/api-gateway -n mental-health-platform

# Rollback to previous revision
kubectl rollout undo deployment/api-gateway -n mental-health-platform

# Rollback to specific revision
kubectl rollout undo deployment/api-gateway -n mental-health-platform --to-revision=2
```

### Using Helm

```bash
# List releases
helm list -n mental-health-platform

# Rollback to previous release
helm rollback mental-health-platform -n mental-health-platform

# Rollback to specific revision
helm rollback mental-health-platform -n mental-health-platform 2
```

## Verification After Rollback

1. **Check service health:**
   ```bash
   curl https://mentalhealth.ke/health
   ```

2. **Monitor metrics:**
   - Error rates should return to pre-deployment levels
   - Response times should normalize
   - All services should show healthy

3. **Verify functionality:**
   - Test critical user flows
   - Verify database queries work
   - Check cache functionality

4. **Review logs:**
   ```bash
   aws logs tail /aws/ecs/mental-health-platform-kenya --follow
   ```

## Emergency Rollback (All Services)

If multiple services need rollback:

1. **Stop all deployments**
2. **Rollback services in dependency order:**
   - API Gateway (first)
   - Conversation Engine
   - Speech Processing
   - Emotion Analysis
   - Crisis Detection
   - Safety Moderation
   - Sync Service
   - Cultural Context (last)

3. **Monitor each service after rollback**
4. **Verify inter-service communication**
5. **Check end-to-end functionality**

## Post-Rollback Actions

1. **Document the rollback:**
   - What was rolled back
   - Why it was rolled back
   - What version was rolled back to
   - Time of rollback

2. **Investigate root cause:**
   - Review logs
   - Check monitoring data
   - Identify the issue

3. **Fix the issue:**
   - Create fix in separate branch
   - Test thoroughly
   - Get approval

4. **Schedule re-deployment:**
   - Plan deployment window
   - Ensure fix is tested
   - Follow deployment checklist

## Prevention

To minimize rollback needs:
- Always test in staging first
- Use blue-green deployments when possible
- Implement canary deployments for high-risk changes
- Monitor closely during deployment
- Have rollback plan ready before deployment
- Keep previous versions available
- Maintain database backups

