# Demo Data Generator - Complete Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Demo Scenarios](#demo-scenarios)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)
8. [API Reference](#api-reference)

## Quick Start

Get the demo running in 3 simple steps:

```bash
# 1. Navigate to the ResonaAI directory
cd ResonaAI

# 2. Generate demo data and launch
python scripts/demo_data_generator.py launch --preset quick --auto-browser

# 3. Access the demo at http://localhost:3000
```

That's it! The demo will automatically:
- Generate realistic test data
- Start the mock API server
- Launch the React frontend
- Open your browser to the demo

## Installation

### Prerequisites

- **Python 3.8+** (tested with 3.8, 3.9, 3.10, 3.11)
- **Node.js 16+** (for frontend)
- **npm or yarn** (package manager)

### System Requirements

- **Disk Space**: 100MB for generated data (varies by preset)
- **Memory**: 512MB RAM minimum
- **Network**: Ports 3000 and 8001 available (configurable)

### Dependencies

All Python dependencies are included in the main `requirements.txt`:

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Key dependencies:
- `fastapi==0.104.1` - Mock API server
- `pydantic==2.5.0+` - Data validation
- `hypothesis==6.88.1` - Property-based testing
- `uvicorn` - ASGI server
- `websockets` - Real-time communication

### Frontend Dependencies

The system will automatically detect and install frontend dependencies:

```bash
# Manual installation (optional)
cd apps/frontend
npm install  # or yarn install
```

## Configuration

### Environment Variables

Configure the demo using environment variables or `.env` file:

```bash
# Create .env file in ResonaAI directory
cat > .env << EOF
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

### Configuration Presets

Three built-in presets for different use cases:

| Preset | Users | Conversations | Use Case |
|--------|-------|---------------|----------|
| `quick` | 3 | 2 per user | Fast demos, testing |
| `comprehensive` | 20 | 10 per user | Full feature showcase |
| `development` | 5 | 5 per user | Development, debugging |

## Usage Examples

### Basic Commands

```bash
# Show current configuration
python scripts/demo_data_generator.py show-config

# Validate configuration and dependencies
python scripts/demo_data_generator.py validate

# Generate data only (no launch)
python scripts/demo_data_generator.py generate --preset comprehensive

# Launch with existing data
python scripts/demo_data_generator.py launch --skip-generation

# Clean up all demo data
python scripts/demo_data_generator.py cleanup
```

### Advanced Commands

```bash
# Custom data generation
python scripts/demo_data_generator.py generate \
  --users 15 \
  --conversations 8 \
  --cultural-scenarios 30 \
  --include-crisis \
  --output-dir custom_demo_data

# Launch with custom ports
python scripts/demo_data_generator.py launch \
  --api-port 8002 \
  --frontend-port 3001 \
  --no-browser

# Debug mode with verbose logging
DEMO_DEBUG=true DEMO_VERBOSE=true \
python scripts/demo_data_generator.py launch --preset development
```

### Programmatic Usage

```python
from scripts.demo_data_generator import DemoDataGenerator
from scripts.demo_data_generator.config import DemoConfig

# Create configuration
config = DemoConfig(
    num_users=10,
    conversations_per_user=5,
    include_crisis=True,
    auto_browser=False
)

# Initialize generator
generator = DemoDataGenerator(config)

# Generate data
result = generator.generate_all_data()
print(f"Generated data for {result.users_created} users")

# Launch services
generator.launch_demo()
```

## Demo Scenarios

### Scenario 1: Quick Demo (5 minutes)

Perfect for stakeholder presentations:

```bash
python scripts/demo_data_generator.py launch --preset quick --auto-browser
```

**What you'll see:**
- 3 diverse user profiles
- 6 realistic conversations
- Emotional progression examples
- Cultural context detection
- Voice-truth dissonance patterns

### Scenario 2: Comprehensive Showcase (15 minutes)

Full feature demonstration:

```bash
python scripts/demo_data_generator.py launch --preset comprehensive --auto-browser
```

**What you'll see:**
- 20 diverse user profiles
- 200 conversations with varied scenarios
- Crisis detection examples
- Cultural deflection patterns
- Baseline tracking over time
- All 7 emotions represented

### Scenario 3: Development Testing

For developers and QA:

```bash
DEMO_DEBUG=true python scripts/demo_data_generator.py launch --preset development
```

**Features:**
- Debug logging enabled
- Detailed error messages
- Performance metrics
- Test data validation
- API response inspection

### Scenario 4: Cultural Context Focus

Emphasizing East African cultural elements:

```bash
python scripts/demo_data_generator.py generate \
  --users 10 \
  --conversations 5 \
  --cultural-scenarios 50 \
  --swahili-patterns 100 \
  --crisis-percentage 0.05

python scripts/demo_data_generator.py launch --skip-generation
```

**Highlights:**
- Rich Swahili pattern examples
- Cultural deflection detection
- Traditional vs. modern therapy scenarios
- Family/community pressure situations

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Port 3000 is already in use`

**Solutions:**
```bash
# Option 1: Use different ports
python scripts/demo_data_generator.py launch --frontend-port 3001 --api-port 8002

# Option 2: Kill existing processes
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9
```

#### 2. Node.js/npm Not Found

**Error:** `Node.js not found` or `npm command not found`

**Solutions:**
```bash
# Install Node.js
# Windows: Download from nodejs.org
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm

# Verify installation
node --version
npm --version
```

#### 3. Python Dependencies Missing

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solutions:**
```bash
# Install dependencies
pip install -r requirements.txt

# Or install specific packages
pip install fastapi pydantic hypothesis uvicorn
```

#### 4. Permission Errors

**Error:** `Permission denied` when creating files

**Solutions:**
```bash
# Check directory permissions
ls -la demo_data/

# Create directory with proper permissions
mkdir -p demo_data
chmod 755 demo_data

# Run with different output directory
python scripts/demo_data_generator.py generate --output-dir ~/demo_data
```

#### 5. Frontend Build Failures

**Error:** Frontend fails to start or build

**Solutions:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
cd apps/frontend
rm -rf node_modules package-lock.json
npm install

# Check Node.js version compatibility
node --version  # Should be 16+
```

### Performance Issues

#### Slow Data Generation

**Symptoms:** Generation takes longer than expected

**Solutions:**
```bash
# Use smaller preset
python scripts/demo_data_generator.py launch --preset quick

# Reduce data volume
python scripts/demo_data_generator.py generate --users 5 --conversations 3

# Disable crisis scenarios (computationally intensive)
DEMO_INCLUDE_CRISIS=false python scripts/demo_data_generator.py generate
```

#### High Memory Usage

**Symptoms:** System becomes slow during generation

**Solutions:**
```bash
# Generate data in smaller batches
python scripts/demo_data_generator.py generate --users 5
python scripts/demo_data_generator.py generate --users 5 --append

# Monitor memory usage
# Windows: Task Manager
# macOS: Activity Monitor
# Linux: htop or top
```

### Network Issues

#### API Server Won't Start

**Error:** `Failed to start API server`

**Solutions:**
```bash
# Check if port is available
netstat -an | grep 8001

# Try different port
python scripts/demo_data_generator.py launch --api-port 8002

# Check firewall settings
# Windows: Windows Defender Firewall
# macOS: System Preferences > Security & Privacy > Firewall
# Linux: ufw status
```

#### Browser Won't Open

**Error:** Browser doesn't launch automatically

**Solutions:**
```bash
# Disable auto-browser and open manually
python scripts/demo_data_generator.py launch --no-browser
# Then open http://localhost:3000 manually

# Set default browser
# Windows: Settings > Apps > Default apps
# macOS: System Preferences > General > Default web browser
# Linux: update-alternatives --config x-www-browser
```

### Data Issues

#### Generated Data Looks Unrealistic

**Symptoms:** Conversations seem artificial or repetitive

**Solutions:**
```bash
# Regenerate with different seed
python scripts/demo_data_generator.py cleanup
python scripts/demo_data_generator.py generate --preset comprehensive

# Increase cultural scenario diversity
python scripts/demo_data_generator.py generate --cultural-scenarios 50

# Enable debug mode to inspect generation
DEMO_DEBUG=true python scripts/demo_data_generator.py generate
```

#### Missing Cultural Context

**Symptoms:** No Swahili patterns or cultural elements

**Solutions:**
```bash
# Verify cultural knowledge database
python -c "from scripts.demo_data_generator.cultural_knowledge import CULTURAL_PATTERNS; print(len(CULTURAL_PATTERNS))"

# Regenerate with more cultural focus
python scripts/demo_data_generator.py generate --swahili-patterns 100 --cultural-scenarios 30
```

### System-Specific Issues

#### Windows Issues

```bash
# Path separator issues
# Use forward slashes or raw strings in Python
output_dir = r"C:\demo_data"  # or "C:/demo_data"

# PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Long path support
# Enable in Windows 10/11: Group Policy > Computer Configuration > Administrative Templates > System > Filesystem
```

#### macOS Issues

```bash
# Homebrew permissions
sudo chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions

# Python path issues
export PATH="/usr/local/bin:$PATH"

# Xcode command line tools
xcode-select --install
```

#### Linux Issues

```bash
# Missing system dependencies
sudo apt update
sudo apt install python3-dev python3-pip nodejs npm

# Permission issues with npm global packages
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

## Advanced Usage

### Custom Data Generation

Create your own data generation scripts:

```python
from scripts.demo_data_generator.generators import (
    ConversationSimulator, 
    EmotionGenerator,
    CulturalGenerator
)

# Custom conversation scenarios
simulator = ConversationSimulator()
conversation = simulator.generate_conversation_thread({
    'scenario_type': 'academic_pressure',
    'user_profile': user_profile,
    'emotional_arc': ['neutral', 'stressed', 'anxious', 'hopeful']
})

# Custom emotion patterns
emotion_gen = EmotionGenerator()
emotion_data = emotion_gen.generate_emotion_analysis(
    text="Nimechoka na masomo",
    context={'cultural_background': 'Kikuyu', 'age': 22}
)
```

### API Integration

Extend the mock API with custom endpoints:

```python
from scripts.demo_data_generator.api.mock_api_server import MockAPIServer

server = MockAPIServer()

@server.app.get("/custom/endpoint")
async def custom_endpoint():
    return {"message": "Custom functionality"}

server.start_server(port=8001)
```

### Testing Integration

Use the demo data generator in your tests:

```python
import pytest
from scripts.demo_data_generator import DemoDataGenerator

@pytest.fixture
def demo_data():
    config = DemoConfig(num_users=3, conversations_per_user=2)
    generator = DemoDataGenerator(config)
    return generator.generate_all_data()

def test_conversation_analysis(demo_data):
    conversations = demo_data.conversations
    assert len(conversations) == 6  # 3 users * 2 conversations
```

## API Reference

### Command Line Interface

```bash
python scripts/demo_data_generator.py <command> [options]
```

#### Commands

- `generate` - Generate demo data
- `launch` - Launch demo environment
- `cleanup` - Clean up demo data
- `validate` - Validate configuration
- `show-config` - Display current configuration

#### Global Options

- `--config FILE` - Configuration file path
- `--verbose` - Enable verbose logging
- `--debug` - Enable debug mode
- `--help` - Show help message

#### Generate Options

- `--preset {quick,comprehensive,development}` - Use preset configuration
- `--users N` - Number of users to generate
- `--conversations N` - Conversations per user
- `--cultural-scenarios N` - Number of cultural scenarios
- `--swahili-patterns N` - Number of Swahili patterns
- `--output-dir DIR` - Output directory for data
- `--include-crisis` - Include crisis scenarios
- `--crisis-percentage FLOAT` - Percentage of crisis conversations
- `--append` - Append to existing data

#### Launch Options

- `--preset {quick,comprehensive,development}` - Use preset configuration
- `--api-port PORT` - Mock API server port (default: 8001)
- `--frontend-port PORT` - Frontend server port (default: 3000)
- `--auto-browser` - Automatically open browser
- `--no-browser` - Don't open browser
- `--skip-generation` - Use existing data
- `--processing-delay MS` - API response delay in milliseconds

### Python API

#### DemoDataGenerator Class

```python
class DemoDataGenerator:
    def __init__(self, config: DemoConfig)
    def generate_all_data(self) -> GenerationResult
    def launch_demo(self) -> LaunchResult
    def cleanup_data(self) -> bool
    def validate_setup(self) -> ValidationResult
```

#### Configuration Classes

```python
class DemoConfig:
    num_users: int = 10
    conversations_per_user: int = 5
    cultural_scenarios: int = 20
    swahili_patterns: int = 50
    output_dir: str = "demo_data"
    include_crisis: bool = True
    crisis_percentage: float = 0.1

class ServiceConfig:
    api_port: int = 8001
    frontend_port: int = 3000
    auto_browser: bool = True
    processing_delay: int = 500
```

---

## Support

For additional help:

1. **Check the logs**: Enable debug mode with `DEMO_DEBUG=true`
2. **Review the test suite**: Run `python -m pytest scripts/demo_data_generator/tests/ -v`
3. **Validate your setup**: Run `python scripts/demo_data_generator.py validate`
4. **Check system requirements**: Ensure Python 3.8+, Node.js 16+, and required ports are available

The demo data generator is designed to be robust and self-diagnosing. Most issues can be resolved by following the troubleshooting steps above.