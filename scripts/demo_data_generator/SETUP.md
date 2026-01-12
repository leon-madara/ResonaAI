# Demo Data Generator - Setup and Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Memory**: 512 MB RAM
- **Disk Space**: 100 MB for demo data
- **Network**: Ports 3000 and 8001 available

### Recommended Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Memory**: 2 GB RAM
- **Disk Space**: 500 MB for comprehensive demos
- **Network**: Stable internet connection for initial setup

## Installation Steps

### Step 1: Verify Prerequisites

#### Check Python Version
```bash
python --version
# Should show Python 3.8.0 or higher

# If python command not found, try:
python3 --version
```

#### Check Node.js Version
```bash
node --version
# Should show v16.0.0 or higher

npm --version
# Should show 8.0.0 or higher
```

### Step 2: Install Python Dependencies

Navigate to the ResonaAI directory and install dependencies:

```bash
cd ResonaAI

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, pydantic, hypothesis; print('Dependencies installed successfully')"
```

### Step 3: Install Frontend Dependencies

The demo system will automatically handle frontend dependencies, but you can pre-install them:

```bash
cd apps/frontend

# Install frontend dependencies
npm install

# Verify installation
npm list --depth=0
```

### Step 4: Verify Installation

Run the validation command to check your setup:

```bash
cd ResonaAI

python scripts/demo_data_generator.py validate
```

Expected output:
```
✓ Python version: 3.10.0 (compatible)
✓ Node.js version: 18.0.0 (compatible)
✓ Python dependencies: All installed
✓ Frontend directory: Found
✓ Ports 3000, 8001: Available
✓ Write permissions: demo_data directory
✓ Configuration: Valid

Setup validation completed successfully!
```

## Platform-Specific Setup

### Windows Setup

#### Install Python
1. Download Python from [python.org](https://python.org)
2. Run installer with "Add Python to PATH" checked
3. Verify installation: `python --version`

#### Install Node.js
1. Download Node.js from [nodejs.org](https://nodejs.org)
2. Run installer with default options
3. Verify installation: `node --version`

#### Windows-Specific Commands
```cmd
# Use Command Prompt or PowerShell
cd ResonaAI
python scripts\demo_data_generator.py validate

# If you get execution policy errors in PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS Setup

#### Install Python
```bash
# Using Homebrew (recommended)
brew install python@3.10

# Or download from python.org
```

#### Install Node.js
```bash
# Using Homebrew
brew install node

# Or download from nodejs.org
```

#### macOS-Specific Commands
```bash
# Ensure proper PATH
export PATH="/usr/local/bin:$PATH"

# If you get permission errors:
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

### Linux Setup (Ubuntu/Debian)

#### Install Python
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create alias for python command
echo 'alias python=python3' >> ~/.bashrc
source ~/.bashrc
```

#### Install Node.js
```bash
# Using NodeSource repository (recommended)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or using snap
sudo snap install node --classic
```

#### Linux-Specific Commands
```bash
# If you get permission errors with npm:
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## Configuration

### Environment Variables

Create a `.env` file in the ResonaAI directory:

```bash
# Navigate to ResonaAI directory
cd ResonaAI

# Create .env file
cat > .env << 'EOF'
# Demo Data Generator Configuration

# Data Generation Settings
DEMO_NUM_USERS=10
DEMO_CONVERSATIONS_PER_USER=5
DEMO_CULTURAL_SCENARIOS=20
DEMO_SWAHILI_PATTERNS=50
DEMO_OUTPUT_DIR=demo_data
DEMO_INCLUDE_CRISIS=true
DEMO_CRISIS_PERCENTAGE=0.1

# Service Configuration
DEMO_API_PORT=8001
DEMO_FRONTEND_PORT=3000
DEMO_AUTO_BROWSER=true
DEMO_PROCESSING_DELAY=500

# Development Settings
DEMO_DEBUG=false
DEMO_VERBOSE=false
DEMO_SKIP_BROWSER=false
EOF
```

### Directory Structure

Ensure the following directory structure exists:

```
ResonaAI/
├── scripts/
│   └── demo_data_generator/
│       ├── __init__.py
│       ├── config.py
│       ├── models.py
│       ├── interfaces.py
│       ├── generators/
│       ├── storage/
│       ├── api/
│       ├── launcher/
│       └── tests/
├── apps/
│   └── frontend/
│       ├── package.json
│       ├── src/
│       └── public/
├── demo_data/          # Created automatically
├── requirements.txt
└── .env               # Created in configuration step
```

## First Run

### Quick Test

Run a quick test to ensure everything works:

```bash
cd ResonaAI

# Generate minimal test data and launch demo
python scripts/demo_data_generator.py launch --preset quick --auto-browser
```

This should:
1. Generate test data for 3 users
2. Start the mock API server on port 8001
3. Start the frontend server on port 3000
4. Open your browser to http://localhost:3000

### Expected Output

```
🚀 Demo Data Generator Starting...

📊 Generating demo data...
✓ Created 3 user profiles
✓ Generated 6 conversations
✓ Added cultural context data
✓ Created emotion analysis data
✓ Generated voice simulation data

🔧 Starting services...
✓ Mock API server started on port 8001
✓ Frontend server starting on port 3000
✓ Frontend dependencies installed
✓ Frontend server ready

🌐 Demo ready!
   Frontend: http://localhost:3000
   API: http://localhost:8001
   
🎯 Demo includes:
   • 3 diverse user profiles
   • 6 realistic conversations
   • Emotional progression examples
   • Cultural context detection
   • Voice-truth dissonance patterns

Press Ctrl+C to stop the demo
```

## Troubleshooting Installation

### Common Issues

#### Python Not Found
```bash
# Error: 'python' is not recognized
# Solution: Add Python to PATH or use python3
python3 scripts/demo_data_generator.py validate
```

#### Permission Denied
```bash
# Error: Permission denied when installing packages
# Solution: Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Error: Port 3000 is already in use
# Solution: Use different ports
python scripts/demo_data_generator.py launch --frontend-port 3001 --api-port 8002
```

#### Node.js Version Too Old
```bash
# Error: Node.js version 14.x is not supported
# Solution: Update Node.js
# Windows/macOS: Download from nodejs.org
# Linux: Use NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Validation Failures

If `python scripts/demo_data_generator.py validate` fails:

#### Missing Dependencies
```bash
# Install missing Python packages
pip install fastapi pydantic hypothesis uvicorn websockets

# Install missing Node.js packages
cd apps/frontend
npm install
```

#### Directory Permissions
```bash
# Create demo data directory with proper permissions
mkdir -p demo_data
chmod 755 demo_data

# On Windows, ensure user has write access to the directory
```

#### Port Conflicts
```bash
# Check what's using the ports
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8001

# macOS/Linux
lsof -i :3000
lsof -i :8001

# Kill conflicting processes or use different ports
```

## Advanced Setup

### Virtual Environment (Recommended)

Use a virtual environment to isolate dependencies:

```bash
cd ResonaAI

# Create virtual environment
python -m venv demo_env

# Activate virtual environment
# Windows
demo_env\Scripts\activate
# macOS/Linux
source demo_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python scripts/demo_data_generator.py validate
```

### Docker Setup (Optional)

For containerized deployment:

```bash
# Build Docker image (will be created in task 12.3)
docker build -t resona-demo .

# Run container
docker run -p 3000:3000 -p 8001:8001 resona-demo
```

### Development Setup

For development and testing:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8

# Install pre-commit hooks (if available)
pre-commit install

# Run tests
python -m pytest scripts/demo_data_generator/tests/ -v

# Run with coverage
python -m pytest scripts/demo_data_generator/tests/ --cov=scripts.demo_data_generator
```

## Next Steps

After successful installation:

1. **Read the Usage Guide**: See `USAGE_GUIDE.md` for detailed usage instructions
2. **Try Different Presets**: Test `quick`, `comprehensive`, and `development` presets
3. **Explore Configuration**: Modify `.env` file to customize the demo
4. **Run Tests**: Execute the test suite to ensure everything works correctly

## Support

If you encounter issues during setup:

1. **Check System Requirements**: Ensure you meet minimum requirements
2. **Run Validation**: Use `python scripts/demo_data_generator.py validate`
3. **Check Logs**: Enable debug mode with `DEMO_DEBUG=true`
4. **Review Troubleshooting**: See the troubleshooting section in `USAGE_GUIDE.md`

The setup process is designed to be straightforward and self-diagnosing. Most issues can be resolved by following the steps above.