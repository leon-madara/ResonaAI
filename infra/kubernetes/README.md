# Kubernetes Configuration

Kubernetes manifests for ResonaAI deployment.

## Structure

```
kubernetes/
├── base/              # Base configurations (shared)
│   ├── namespace.yaml
│   ├── configmaps/
│   ├── deployments/
│   ├── services/
│   └── ingress/
├── overlays/          # Environment-specific overrides
│   ├── dev/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── prod/
│       └── kustomization.yaml
└── helm/              # Helm charts
    └── mental-health-platform/
```

## Usage

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

## Migration Notes
Will contain files from `infrastructure/kubernetes/` and `infrastructure/helm/`.

