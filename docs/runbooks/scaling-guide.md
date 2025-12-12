# Scaling Guide

This guide explains how to scale the Mental Health Platform to handle increased load.

## Scaling Strategies

### Horizontal Scaling (Recommended)
- Add more service instances
- Distribute load across instances
- Better fault tolerance

### Vertical Scaling
- Increase CPU/memory of instances
- Quick but limited
- May require downtime

## Auto-Scaling Configuration

### ECS Auto-Scaling

**Target Tracking Scaling:**
- CPU utilization: 70%
- Memory utilization: 80%
- Request count: 1000 requests/minute

**Scaling Policies:**
```hcl
resource "aws_appautoscaling_target" "api_gateway_target" {
  max_capacity       = 20
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.kenya_cluster.name}/${aws_ecs_service.api_gateway.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_gateway_cpu" {
  name               = "api-gateway-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api_gateway_target.resource_id
  scalable_dimension = aws_appautoscaling_target.api_gateway_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api_gateway_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### Kubernetes Auto-Scaling

**Horizontal Pod Autoscaler:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: mental-health-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Manual Scaling

### Docker Compose

```bash
# Scale specific service
docker-compose up -d --scale api-gateway=5

# Scale all services
docker-compose up -d --scale api-gateway=5 --scale speech-processing=3
```

### ECS

```bash
# Update service desired count
aws ecs update-service \
  --cluster mental-health-platform-kenya-cluster \
  --service api-gateway \
  --desired-count 5
```

### Kubernetes

```bash
# Scale deployment
kubectl scale deployment api-gateway --replicas=5 -n mental-health-platform

# Or edit deployment
kubectl edit deployment api-gateway -n mental-health-platform
```

## Service-Specific Scaling

### API Gateway
- **Min replicas**: 2
- **Max replicas**: 20
- **Scale on**: CPU > 70%, Memory > 80%, Request rate > 1000/min
- **Priority**: High (entry point)

### Speech Processing
- **Min replicas**: 2
- **Max replicas**: 10
- **Scale on**: CPU > 75%, Queue depth > 50
- **Priority**: Medium (CPU intensive)

### Conversation Engine
- **Min replicas**: 2
- **Max replicas**: 15
- **Scale on**: CPU > 70%, Response time > 2s
- **Priority**: High (core functionality)

### Crisis Detection
- **Min replicas**: 3 (always available)
- **Max replicas**: 10
- **Scale on**: CPU > 70%, Queue depth > 20
- **Priority**: Critical (safety)

### Emotion Analysis
- **Min replicas**: 2
- **Max replicas**: 10
- **Scale on**: CPU > 75%, Response time > 1s
- **Priority**: Medium

### Safety Moderation
- **Min replicas**: 2
- **Max replicas**: 8
- **Scale on**: CPU > 70%, Queue depth > 30
- **Priority**: Medium

### Sync Service
- **Min replicas**: 2
- **Max replicas**: 5
- **Scale on**: Queue depth > 100
- **Priority**: Low (background processing)

### Cultural Context
- **Min replicas**: 2
- **Max replicas**: 5
- **Scale on**: CPU > 70%, Response time > 1s
- **Priority**: Low

## Database Scaling

### Read Replicas

```hcl
resource "aws_db_instance" "kenya_rds_replica" {
  replicate_source_db = aws_db_instance.kenya_rds.identifier
  instance_class      = "db.t3.micro"
}
```

### Connection Pooling

- Use PgBouncer for connection pooling
- Configure max connections per service
- Monitor connection usage

### Query Optimization

- Add indexes for frequently queried columns
- Optimize slow queries
- Use query caching where appropriate

## Redis Scaling

### Cluster Mode

```hcl
resource "aws_elasticache_replication_group" "kenya_redis_cluster" {
  replication_group_id       = "${var.project_name}-kenya-redis-cluster"
  description                = "Redis cluster"
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7.cluster.on"
  num_node_groups            = 2
  replicas_per_node_group    = 1
  automatic_failover_enabled = true
}
```

### Memory Management

- Set appropriate maxmemory policy
- Monitor memory usage
- Scale up when > 80% memory usage

## Load Balancer Configuration

### ALB Target Groups

- Health check interval: 30s
- Healthy threshold: 2
- Unhealthy threshold: 3
- Timeout: 5s

### Sticky Sessions

- Not required (stateless services)
- If needed, enable for specific services

## Monitoring Scaling

### Key Metrics

- **CPU Utilization**: Target 60-70%
- **Memory Utilization**: Target 70-80%
- **Request Rate**: Monitor per service
- **Response Time**: P95 < 200ms
- **Error Rate**: < 1%

### Scaling Triggers

1. **CPU > 70%** for 5 minutes → Scale up
2. **Memory > 80%** for 5 minutes → Scale up
3. **Response time > 2s** for 5 minutes → Scale up
4. **Error rate > 5%** → Investigate (may need scaling)
5. **CPU < 30%** for 15 minutes → Scale down
6. **Memory < 50%** for 15 minutes → Scale down

## Cost Optimization

### Spot Instances

- Use Fargate Spot for non-critical services
- Can save up to 70% on compute costs
- Configure for: sync-service, cultural-context

### Reserved Instances

- Purchase reserved instances for predictable workloads
- 1-year or 3-year terms
- Significant cost savings

### Right-Sizing

- Regularly review instance sizes
- Downsize if consistently underutilized
- Upsize if hitting limits frequently

## Scaling Checklist

Before scaling:
- [ ] Review current metrics
- [ ] Identify bottleneck
- [ ] Check cost implications
- [ ] Verify capacity limits
- [ ] Test scaling in staging

During scaling:
- [ ] Monitor service health
- [ ] Verify load distribution
- [ ] Check for errors
- [ ] Monitor costs

After scaling:
- [ ] Verify performance improvement
- [ ] Review cost impact
- [ ] Update documentation
- [ ] Adjust auto-scaling policies if needed

## Troubleshooting Scaling Issues

### Services Not Scaling

1. Check auto-scaling policies
2. Verify resource limits
3. Check for capacity constraints
4. Review CloudWatch metrics

### Uneven Load Distribution

1. Check load balancer configuration
2. Verify health checks
3. Review session affinity settings
4. Check for network issues

### Scaling Too Aggressively

1. Adjust cooldown periods
2. Increase scale-down thresholds
3. Review scaling policies
4. Add scale-down delays

