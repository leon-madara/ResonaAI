# Terraform Configuration

Infrastructure as Code for cloud resources.

## Structure

```
terraform/
├── modules/           # Reusable modules
│   ├── networking/
│   ├── database/
│   ├── kubernetes/
│   └── monitoring/
└── environments/      # Environment configurations
    ├── dev/
    ├── staging/
    └── prod/
```

## Usage

### Initialize
```bash
cd environments/dev
terraform init
```

### Plan Changes
```bash
terraform plan -out=tfplan
```

### Apply Changes
```bash
terraform apply tfplan
```

### Destroy (careful!)
```bash
terraform destroy
```

## State Management
- State stored in remote backend (S3/GCS)
- State locking enabled
- Never commit `.tfstate` files

## Migration Notes
Will contain files from `infrastructure/terraform/`.

