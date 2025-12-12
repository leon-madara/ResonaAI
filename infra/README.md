# Infrastructure

Infrastructure as Code (IaC) for ResonaAI deployment.

## 📁 Directory Structure

```
infra/
├── README.md              # This file
├── docker/                # Docker configurations
│   └── docker-compose.yml # Main compose file
├── kubernetes/            # Kubernetes manifests
│   ├── base/              # Base configurations
│   │   ├── namespace.yaml
│   │   ├── configmaps/
│   │   ├── deployments/
│   │   ├── services/
│   │   └── ingress/
│   ├── overlays/          # Environment-specific
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── helm/              # Helm charts
│       └── mental-health-platform/
├── terraform/             # Cloud infrastructure
│   ├── environments/      # Terraform configs
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── acm.tf
│   │   ├── ecs-tasks.tf
│   │   └── secrets.tf
│   └── modules/           # Reusable modules
└── nginx/                 # Reverse proxy configs
    ├── nginx.conf
    └── ssl/
```

## 🚀 Quick Start

### Local Development (Docker)
```bash
cd infra/docker
docker-compose up -d
```

### Kubernetes Deployment
```bash
cd infra/kubernetes
kubectl apply -k base/
```

### Terraform (Cloud)
```bash
cd infra/terraform/environments
terraform init
terraform plan
terraform apply
```

## 🐳 Docker

### Services Defined
The `docker-compose.yml` includes:
- API Gateway
- All microservices (15 services)
- PostgreSQL database
- Redis cache
- Nginx reverse proxy

### Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

## ☸️ Kubernetes

### Base Resources
- `namespace.yaml` - ResonaAI namespace
- `configmaps/` - Application configuration
- `deployments/` - Service deployments
- `services/` - Service networking
- `ingress/` - External access

### Using Kustomize
```bash
# Development
kubectl apply -k overlays/dev/

# Staging
kubectl apply -k overlays/staging/

# Production
kubectl apply -k overlays/prod/
```

### Using Helm
```bash
helm install resona-ai helm/mental-health-platform \
  --values helm/mental-health-platform/values-prod.yaml
```

## 🏗️ Terraform

### Resources Managed
- ACM certificates
- ECS task definitions
- Secrets Manager
- VPC networking (in modules)

### Usage
```bash
cd terraform/environments
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

## 🔧 Nginx

### Configuration
- `nginx.conf` - Main Nginx configuration
- `ssl/` - SSL certificate storage

### Features
- TLS 1.3 termination
- Reverse proxy to services
- Rate limiting
- Security headers

## 🔄 Migration Notes

This directory consolidates:
- `docker-compose.yml` → `infra/docker/`
- `infrastructure/kubernetes/` → `infra/kubernetes/base/`
- `infrastructure/helm/` → `infra/kubernetes/helm/`
- `infrastructure/terraform/` → `infra/terraform/environments/`
- `nginx/` → `infra/nginx/`

## 🔧 Environments

| Environment | Purpose | Location |
|-------------|---------|----------|
| dev | Development | `overlays/dev/` |
| staging | Pre-production | `overlays/staging/` |
| prod | Production | `overlays/prod/` |

## 📋 Deployment Checklist

### Before Deployment
- [ ] All tests pass
- [ ] Security scan complete
- [ ] Config reviewed
- [ ] Secrets rotated if needed
- [ ] Monitoring alerts configured

### After Deployment
- [ ] Health checks passing
- [ ] Smoke tests successful
- [ ] Metrics flowing
- [ ] Alerts working
