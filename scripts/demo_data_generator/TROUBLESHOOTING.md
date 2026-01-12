# Demo Data Generator - Troubleshooting Guide

## Quick Diagnosis

Run the built-in diagnostic tool first:

```bash
cd ResonaAI
python scripts/demo_data_generator.py validate --verbose
```

This will check:
- ✓ System requirements
- ✓ Dependencies
- ✓ Port availability
- ✓ File permissions
- ✓ Configuration validity

## Common Issues and Solutions

### 1. Installation Issues

#### Python Not Found
**Error:** `'python' is not recognized as an internal or external command`

**Cause:** Python not installed or not in PATH

**Solutions:**
```bash
# Check if Python is installed with different name
python3 --version
py --version

# Add Python to PATH (Windows)
# Add C:\Python310 and C:\Python310\Scripts to PATH environment variable

# Use full path temporarily
C:\Python310\python.exe scripts/demo_data_generator.py validate

# Install Python if missing
# Windows: Download from python.org
# macOS: brew install python
# Linux: sudo apt install python3
```

#### Node.js Not Found
**Error:** `'node' is not recognized` or `'npm' is not recognized`

**Cause:** Node.js not installed or not in PATH

**Solutions:**
```bash
# Check Node.js installation
node --version
npm --version

# Install Node.js
# Windows/macOS: Download from nodejs.org
# Linux: 
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be v16.0.0 or higher
```

#### Permission Denied
**Error:** `Permission denied` when installing packages

**Cause:** Insufficient permissions or system-wide package conflicts

**Solutions:**
```bash
# Use virtual environment (recommended)
python -m venv demo_env
# Windows
demo_env\Scripts\activate
# macOS/Linux
source demo_env/bin/activate

# Install in virtual environment
pip install -r requirements.txt

# Alternative: User installation
pip install --user -r requirements.txt

# Fix npm permissions (Linux/macOS)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 2. Port and Network Issues

#### Port Already in Use
**Error:** `Port 3000 is already in use` or `Port 8001 is already in use`

**Cause:** Another service is using the required ports

**Solutions:**
```bash
# Find what's using the port
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>

# Use different ports
python scripts/demo_data_generator.py launch --frontend-port 3001 --api-port 8002

# Set environment variables
export DEMO_FRONTEND_PORT=3001
export DEMO_API_PORT=8002
```

#### Firewall Blocking Connections
**Error:** Cannot access http://localhost:3000

**Cause:** Firewall blocking local connections

**Solutions:**
```bash
# Windows: Allow through Windows Defender Firewall
# 1. Open Windows Defender Firewall
# 2. Click "Allow an app or feature through Windows Defender Firewall"
# 3. Add Python and Node.js

# macOS: Check System Preferences > Security & Privacy > Firewall
# Linux: Check ufw status
sudo ufw status
sudo ufw allow 3000
sudo ufw allow 8001
```

#### Network Interface Issues
**Error:** `EADDRNOTAVAIL` or `Cannot bind to address`

**Cause:** Network interface configuration issues

**Solutions:**
```bash
# Check network interfaces
# Windows
ipconfig
# macOS/Linux
ifconfig

# Bind to specific interface
python scripts/demo_data_generator.py launch --host 127.0.0.1

# Use 0.0.0.0 for all interfaces (development only)
python scripts/demo_data_generator.py launch --host 0.0.0.0
```

### 3. Data Generation Issues

#### Slow Data Generation
**Symptoms:** Generation takes much longer than expected

**Cause:** Large dataset, insufficient resources, or inefficient generation

**Solutions:**
```bash
# Use smaller preset
python scripts/demo_data_generator.py launch --preset quick

# Reduce data volume
python scripts/demo_data_generator.py generate --users 3 --conversations 2

# Disable resource-intensive features
DEMO_INCLUDE_CRISIS=false python scripts/demo_data_generator.py generate

# Monitor system resources
# Windows: Task Manager
# macOS: Activity Monitor  
# Linux: htop or top
```

#### Memory Issues
**Error:** `MemoryError` or system becomes unresponsive

**Cause:** Insufficient RAM for large datasets

**Solutions:**
```bash
# Generate smaller batches
python scripts/demo_data_generator.py generate --users 5
python scripts/demo_data_generator.py generate --users 5 --append

# Increase virtual memory (Windows)
# System Properties > Advanced > Performance Settings > Advanced > Virtual Memory

# Monitor memory usage
python -c "
import psutil
print(f'Available memory: {psutil.virtual_memory().available / 1024**3:.1f} GB')
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
```

#### Unrealistic Generated Data
**Symptoms:** Conversations seem artificial, repetitive, or culturally inappropriate

**Cause:** Insufficient randomization, limited cultural knowledge, or generation bugs

**Solutions:**
```bash
# Regenerate with different parameters
python scripts/demo_data_generator.py cleanup
python scripts/demo_data_generator.py generate --preset comprehensive

# Increase cultural diversity
python scripts/demo_data_generator.py generate \
  --cultural-scenarios 50 \
  --swahili-patterns 100

# Enable debug mode to inspect generation
DEMO_DEBUG=true DEMO_VERBOSE=true \
python scripts/demo_data_generator.py generate

# Verify cultural knowledge database
python -c "
from scripts.demo_data_generator.cultural_knowledge import CULTURAL_PATTERNS
print(f'Cultural patterns available: {len(CULTURAL_PATTERNS)}')
"
```

### 4. Frontend Issues

#### Frontend Won't Start
**Error:** `Failed to start frontend server`

**Cause:** Missing dependencies, port conflicts, or Node.js issues

**Solutions:**
```bash
# Check frontend directory
ls -la apps/frontend/

# Install dependencies manually
cd apps/frontend
npm install

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for errors
npm run start

# Use different port
npm run start -- --port 3001
```

#### Build Failures
**Error:** Frontend build fails with compilation errors

**Cause:** Dependency conflicts, TypeScript errors, or missing files

**Solutions:**
```bash
cd apps/frontend

# Check Node.js version compatibility
node --version  # Should be 16+

# Update dependencies
npm update

# Fix TypeScript errors
npm run build

# Check for missing files
ls -la src/

# Reset to clean state
git checkout -- package-lock.json
rm -rf node_modules
npm install
```

#### Browser Won't Open
**Symptoms:** Demo starts but browser doesn't open automatically

**Cause:** No default browser, browser security settings, or system configuration

**Solutions:**
```bash
# Disable auto-browser and open manually
python scripts/demo_data_generator.py launch --no-browser
# Then open http://localhost:3000 manually

# Set environment variable
export DEMO_AUTO_BROWSER=false

# Check default browser settings
# Windows: Settings > Apps > Default apps
# macOS: System Preferences > General > Default web browser
# Linux: update-alternatives --config x-www-browser

# Use specific browser
# Windows
start chrome http://localhost:3000
# macOS
open -a "Google Chrome" http://localhost:3000
# Linux
google-chrome http://localhost:3000
```

### 5. API Server Issues

#### API Server Won't Start
**Error:** `Failed to start API server` or `uvicorn: command not found`

**Cause:** Missing uvicorn, port conflicts, or FastAPI issues

**Solutions:**
```bash
# Install uvicorn
pip install uvicorn

# Check if FastAPI is installed
python -c "import fastapi; print('FastAPI installed')"

# Start API server manually
cd ResonaAI
python -m uvicorn scripts.demo_data_generator.api.mock_api_server:app --port 8001

# Check for port conflicts
netstat -an | grep 8001

# Use different port
python scripts/demo_data_generator.py launch --api-port 8002
```

#### API Responses Are Slow
**Symptoms:** Frontend loads slowly, API calls timeout

**Cause:** High processing delay, insufficient resources, or network issues

**Solutions:**
```bash
# Reduce processing delay
export DEMO_PROCESSING_DELAY=100
python scripts/demo_data_generator.py launch

# Disable artificial delays
export DEMO_PROCESSING_DELAY=0

# Check system resources
python -c "
import psutil
print(f'CPU usage: {psutil.cpu_percent()}%')
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/health
```

#### CORS Issues
**Error:** `CORS policy` errors in browser console

**Cause:** Cross-origin request restrictions

**Solutions:**
```bash
# Check API server CORS configuration
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8001/api/conversations

# Restart with CORS debugging
DEMO_DEBUG=true python scripts/demo_data_generator.py launch

# Check browser console for detailed CORS errors
# Open Developer Tools > Console
```

### 6. File System Issues

#### Permission Denied
**Error:** `Permission denied` when creating or accessing files

**Cause:** Insufficient file system permissions

**Solutions:**
```bash
# Check directory permissions
ls -la demo_data/

# Create directory with proper permissions
mkdir -p demo_data
chmod 755 demo_data

# Change ownership (Linux/macOS)
sudo chown -R $USER:$USER demo_data/

# Use different output directory
python scripts/demo_data_generator.py generate --output-dir ~/demo_data

# Windows: Run as administrator or check folder permissions
```

#### Disk Space Issues
**Error:** `No space left on device` or `Disk full`

**Cause:** Insufficient disk space for generated data

**Solutions:**
```bash
# Check available space
df -h .  # Linux/macOS
dir /-c  # Windows

# Clean up existing demo data
python scripts/demo_data_generator.py cleanup

# Use smaller dataset
python scripts/demo_data_generator.py generate --preset quick

# Use different location with more space
export DEMO_OUTPUT_DIR=/path/to/larger/disk/demo_data
```

#### File Corruption
**Error:** `JSON decode error` or `Invalid data format`

**Cause:** Corrupted data files, interrupted generation, or disk issues

**Solutions:**
```bash
# Validate existing data
python scripts/demo_data_generator.py validate --check-data

# Clean up and regenerate
python scripts/demo_data_generator.py cleanup
python scripts/demo_data_generator.py generate

# Check specific files
python -c "
import json
with open('demo_data/conversations.json') as f:
    data = json.load(f)
    print(f'Loaded {len(data)} conversations')
"

# Backup and restore
cp -r demo_data demo_data_backup
# If corruption occurs:
rm -rf demo_data
mv demo_data_backup demo_data
```

### 7. Platform-Specific Issues

#### Windows Issues

**PowerShell Execution Policy**
```powershell
# Error: Execution policy restriction
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative: Use Command Prompt instead of PowerShell
cmd
cd ResonaAI
python scripts\demo_data_generator.py validate
```

**Path Length Limitations**
```bash
# Error: Path too long
# Enable long path support in Windows 10/11:
# Group Policy > Computer Configuration > Administrative Templates > System > Filesystem > Enable Win32 long paths

# Or use shorter paths
export DEMO_OUTPUT_DIR=C:\demo
```

**Antivirus Interference**
```bash
# If antivirus blocks execution:
# 1. Add ResonaAI directory to antivirus exclusions
# 2. Temporarily disable real-time protection
# 3. Check Windows Defender quarantine
```

#### macOS Issues

**Homebrew Permissions**
```bash
# Fix Homebrew permissions
sudo chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions

# Reinstall packages if needed
brew reinstall python node
```

**Xcode Command Line Tools**
```bash
# Install if missing
xcode-select --install

# Reset if corrupted
sudo xcode-select --reset
```

**Gatekeeper Issues**
```bash
# If Python or Node.js is blocked:
# System Preferences > Security & Privacy > General
# Click "Allow Anyway" for blocked applications
```

#### Linux Issues

**Missing System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev python3-pip nodejs npm build-essential

# CentOS/RHEL
sudo yum install python3-devel python3-pip nodejs npm gcc

# Arch Linux
sudo pacman -S python python-pip nodejs npm base-devel
```

**SELinux Issues**
```bash
# Check SELinux status
sestatus

# Temporarily disable if causing issues
sudo setenforce 0

# Or create proper SELinux policies
sudo setsebool -P httpd_can_network_connect 1
```

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable all debug options
export DEMO_DEBUG=true
export DEMO_VERBOSE=true
python scripts/demo_data_generator.py launch --preset development

# Check debug logs
tail -f demo_data/debug.log
```

### Performance Profiling

Profile performance issues:

```python
# Create performance_test.py
import cProfile
import pstats
from scripts.demo_data_generator import DemoDataGenerator
from scripts.demo_data_generator.config import DemoConfig

def profile_generation():
    config = DemoConfig(num_users=10, conversations_per_user=5)
    generator = DemoDataGenerator(config)
    generator.generate_all_data()

if __name__ == "__main__":
    cProfile.run('profile_generation()', 'profile_stats')
    stats = pstats.Stats('profile_stats')
    stats.sort_stats('cumulative').print_stats(20)
```

### Network Debugging

Debug network issues:

```bash
# Test API connectivity
curl -v http://localhost:8001/health

# Test WebSocket connection
wscat -c ws://localhost:8001/ws

# Monitor network traffic
# Windows: netstat -an
# Linux: ss -tuln
# macOS: netstat -an
```

### Memory Debugging

Debug memory issues:

```python
# Create memory_test.py
import tracemalloc
import psutil
import os

def monitor_memory():
    tracemalloc.start()
    
    # Your code here
    from scripts.demo_data_generator import DemoDataGenerator
    from scripts.demo_data_generator.config import DemoConfig
    
    config = DemoConfig(num_users=5)
    generator = DemoDataGenerator(config)
    generator.generate_all_data()
    
    current, peak = tracemalloc.get_traced_memory()
    process = psutil.Process(os.getpid())
    
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    print(f"Process memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()

if __name__ == "__main__":
    monitor_memory()
```

## Getting Help

If you can't resolve the issue:

1. **Run Full Diagnostics**:
   ```bash
   python scripts/demo_data_generator.py validate --verbose --check-data
   ```

2. **Collect System Information**:
   ```bash
   python --version
   node --version
   pip list | grep -E "(fastapi|pydantic|hypothesis)"
   npm list --depth=0
   ```

3. **Check Logs**:
   ```bash
   # Enable debug mode and check logs
   DEMO_DEBUG=true python scripts/demo_data_generator.py launch
   cat demo_data/debug.log
   ```

4. **Create Minimal Reproduction**:
   ```bash
   # Test with minimal configuration
   python scripts/demo_data_generator.py generate --users 1 --conversations 1
   ```

5. **Test Individual Components**:
   ```python
   # Test data generation
   from scripts.demo_data_generator.generators.user_generator import UserGenerator
   generator = UserGenerator()
   user = generator.generate_user_profile()
   print(user)
   ```

The troubleshooting guide covers the most common issues. Most problems can be resolved by following the appropriate section above.