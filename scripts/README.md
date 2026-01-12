# ResonaAI Scripts

**Automation scripts for development, testing, and deployment**

---

## 📁 Script Categories

### Setup Scripts (`setup/`)
**Environment setup and initialization**

| Script | Platform | Description |
|--------|----------|-------------|
| `setup_and_run.ps1` | Windows | Complete environment setup and startup |
| `setup_and_run.sh` | Linux/Mac | Complete environment setup and startup |
| `QUICK_RESTART.ps1` | Windows | Quick restart of backend services |

### Development Scripts (`development/`)
**Development workflow automation**

| Script | Description |
|--------|-------------|
| `create_fake_user_data.py` | Generate test user data for development |
| `generate_ui_for_user.py` | Generate UI configuration for testing |
| `get_auth_token.ps1` | Get JWT token for API testing |

---

## 🚀 Quick Start

### Complete Environment Setup

**Windows:**
```powershell
.\scripts\setup\setup_and_run.ps1
```

**Linux/Mac:**
```bash
./scripts/setup/setup_and_run.sh
```

### Quick Restart (Development)

**Windows:**
```powershell
.\scripts\setup\QUICK_RESTART.ps1
```

### Generate Test Data

```bash
cd scripts/development
python create_fake_user_data.py --yes
```

### Get Authentication Token

```powershell
.\scripts\development\get_auth_token.ps1
```

---

## 📋 Script Details

### Setup Scripts

#### `setup_and_run.ps1` / `setup_and_run.sh`
**Complete environment setup and startup**

**What it does:**
- Sets up environment variables
- Starts PostgreSQL and Redis
- Runs database migrations
- Starts backend services
- Starts frontend development server
- Opens browser to application

**Prerequisites:**
- Docker and Docker Compose installed
- Node.js 18+ installed
- Python 3.8+ installed

**Usage:**
```powershell
# Windows
.\scripts\setup\setup_and_run.ps1

# Linux/Mac  
./scripts/setup/setup_and_run.sh
```

#### `QUICK_RESTART.ps1`
**Quick restart of backend services**

**What it does:**
- Stops running backend services
- Restarts API Gateway
- Restarts key microservices
- Verifies services are healthy

**Usage:**
```powershell
.\scripts\setup\QUICK_RESTART.ps1
```

### Development Scripts

#### `create_fake_user_data.py`
**Generate test user data for development**

**What it does:**
- Creates test user accounts
- Generates fake voice sessions
- Creates pattern analysis data
- Generates UI configurations

**Usage:**
```bash
python scripts/development/create_fake_user_data.py --yes
```

**Options:**
- `--yes`: Skip confirmation prompts
- `--users N`: Number of users to create (default: 1)
- `--sessions N`: Sessions per user (default: 10)

#### `generate_ui_for_user.py`
**Generate UI configuration for specific user**

**What it does:**
- Analyzes user patterns
- Generates personalized UI config
- Saves encrypted configuration
- Updates interface database

**Usage:**
```bash
python scripts/development/generate_ui_for_user.py --user-id USER_ID
```

#### `get_auth_token.ps1`
**Get JWT token for API testing**

**What it does:**
- Registers or logs in test user
- Extracts JWT token
- Saves token for API testing
- Provides curl examples

**Usage:**
```powershell
.\scripts\development\get_auth_token.ps1
```

---

## 🔧 Script Configuration

### Environment Variables

Scripts use these environment variables (set in `.env`):

```bash
# Database
DATABASE_URL=postgresql://postgres:9009@localhost:5432/mental_health

# JWT
JWT_SECRET_KEY=test-secret-key-dev-only

# API
REACT_APP_API_URL=http://localhost:8000

# External Services
OPENAI_API_KEY=your_openai_key
AZURE_SPEECH_KEY=your_azure_key
```

### Default Ports

| Service | Port | URL |
|---------|------|-----|
| **API Gateway** | 8000 | http://localhost:8000 |
| **Frontend** | 3000 | http://localhost:3000 |
| **PostgreSQL** | 5432 | localhost:5432 |
| **Redis** | 6379 | localhost:6379 |

---

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F

# Kill process (Linux/Mac)
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check database exists
psql -U postgres -h localhost -c "\l"
```

#### Services Not Starting
```bash
# Check Docker is running
docker --version

# Check Docker Compose
docker-compose --version

# View service logs
docker-compose logs -f [service-name]
```

#### Frontend Build Errors
```bash
# Clear node modules
rm -rf apps/frontend/node_modules
cd apps/frontend && npm install

# Clear npm cache
npm cache clean --force
```

---

## 📖 Related Documentation

### Development Setup
- [Development Setup Guide](../docs/development/setup-guide.md)
- [Testing Guide](../docs/development/testing-guide.md)
- [Troubleshooting](../docs/development/troubleshooting.md)

### API Testing
- [API Documentation](../docs/api/overview.md)
- [Authentication Guide](../docs/api/authentication.md)
- [JWT Token Guide](../docs/development/jwt-token-guide.md)

### Project Status
- [Current Status](../docs/project-status/current-status.md)
- [Critical Path](../docs/project-status/critical-path.md)

---

**Scripts Maintained By**: Development Team  
**Last Updated**: January 11, 2025  
**Platform Support**: Windows (PowerShell), Linux/Mac (Bash)