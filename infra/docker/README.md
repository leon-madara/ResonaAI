# Docker Configuration

Docker and Docker Compose configurations for ResonaAI.

## 📁 Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main orchestration file |

## 🚀 Quick Start

### Start All Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f api-gateway
```

### Stop Services
```bash
docker-compose down
```

### Rebuild and Start
```bash
docker-compose up -d --build
```

## 🏗️ Services

The compose file defines these services:

| Service | Port | Description |
|---------|------|-------------|
| api-gateway | 8000 | Main API entry point |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| nginx | 80/443 | Reverse proxy |

Plus all 15 microservices on ports 8001-8015.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in this directory:
```env
POSTGRES_PASSWORD=your_password
REDIS_PASSWORD=your_password
JWT_SECRET=your_secret
OPENAI_API_KEY=your_key
```

### Volumes
- `postgres_data` - Database persistence
- `redis_data` - Cache persistence

## 📊 Resource Limits

Default resource limits per service:
- Memory: 512MB
- CPU: 0.5 cores

Adjust in `docker-compose.yml` as needed.

## 🔍 Health Checks

All services include health checks:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🔄 Development Workflow

1. Make code changes in `apps/`
2. Rebuild affected service: `docker-compose build [service]`
3. Restart: `docker-compose up -d [service]`
4. Check logs: `docker-compose logs -f [service]`

