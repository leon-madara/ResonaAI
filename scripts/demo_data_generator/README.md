# Demo Data Generator

The Demo Data Generator is a comprehensive testing and demonstration system for the ResonaAI platform. It creates realistic test data, provides local storage capabilities, and launches the frontend application to showcase the autonomous building software's capabilities.

## Project Structure

```
demo_data_generator/
├── __init__.py                 # Package initialization
├── models.py                   # Pydantic data models
├── interfaces.py               # Abstract interfaces and protocols
├── config.py                   # Configuration management
├── generators/                 # Data generation components
│   └── __init__.py
├── storage/                    # Local storage management
│   └── __init__.py
├── api/                        # Mock API server
│   └── __init__.py
├── launcher/                   # Frontend launcher
│   └── __init__.py
└── tests/                      # Test suite
    ├── __init__.py
    └── test_setup.py           # Setup and basic functionality tests
```

## Features

### ✅ Completed (Task 1)
- **Project Structure**: Complete directory structure with proper Python packages
- **Data Models**: Comprehensive Pydantic models for all data types
- **Interfaces**: Abstract base classes defining contracts for all components
- **Configuration Management**: Environment variable support with validation
- **CLI Interface**: Command-line tool for managing the demo system
- **Testing Framework**: Basic test suite with Hypothesis for property-based testing

### 🚧 Pending Implementation (Future Tasks)
- Data generation components (conversations, emotions, cultural context)
- Local storage management
- Mock API server
- Frontend launcher
- Complete demo orchestration

## Installation

The required dependencies are already included in the main `requirements.txt`:

- `fastapi==0.104.1` - Web framework for mock API
- `pydantic==2.5.0+` - Data validation and settings
- `pydantic-settings==2.1.0` - Settings management
- `hypothesis==6.88.1` - Property-based testing

## Usage

### Command Line Interface

The demo data generator provides a comprehensive CLI:

```bash
# Show current configuration
python scripts/demo_data_generator.py show-config

# Generate data with preset
python scripts/demo_data_generator.py generate --preset quick
python scripts/demo_data_generator.py generate --preset comprehensive
python scripts/demo_data_generator.py generate --preset development

# Launch demo environment
python scripts/demo_data_generator.py launch --auto-browser

# Validate configuration
python scripts/demo_data_generator.py validate

# Clean up demo data
python scripts/demo_data_generator.py cleanup
```

### Configuration Presets

- **Quick**: 3 users, 2 conversations each, minimal data for fast demos
- **Comprehensive**: 20 users, 10 conversations each, full feature demonstration
- **Development**: 5 users, debug mode enabled, optimized for development

### Environment Variables

Configure the demo using environment variables:

```bash
# Data Generation
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

# Development
DEMO_DEBUG=false
DEMO_VERBOSE=false
DEMO_SKIP_BROWSER=false
```

## Data Models

### Core Models
- `DemoConfig`: Configuration for data generation
- `ServiceConfig`: Configuration for services
- `UserProfile`: User demographics and baseline data
- `ConversationThread`: Complete conversation with emotional arc
- `EmotionResult`: Emotion analysis with confidence scores
- `CulturalContext`: Cultural patterns and deflection detection

### Enums
- `EmotionType`: Seven-emotion model (neutral, happy, sad, angry, fear, surprise, disgust)
- `CrisisLevel`: Crisis severity levels (none, low, medium, high, critical)
- `ConversationScenarioType`: Types of conversation scenarios
- `CulturalScenarioType`: Types of cultural scenarios

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest scripts/demo_data_generator/tests/ -v

# Run specific test file
python -m pytest scripts/demo_data_generator/tests/test_setup.py -v
```

The test suite includes:
- Import validation
- Model creation and validation
- Configuration management
- Interface abstraction verification
- Property-based testing setup (using Hypothesis)

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **Data Models**: Pydantic models ensure type safety and validation
2. **Interfaces**: Abstract base classes define contracts for all components
3. **Configuration**: Centralized configuration with environment variable support
4. **Generators**: Modular data generation components (to be implemented)
5. **Storage**: Local JSON file storage for test data (to be implemented)
6. **API**: Mock API server compatible with frontend (to be implemented)
7. **Launcher**: Frontend application launcher (to be implemented)

## Development

### Adding New Components

1. Define interfaces in `interfaces.py`
2. Create data models in `models.py`
3. Implement components in appropriate subdirectories
4. Add configuration options to `config.py`
5. Write tests in `tests/` directory

### Configuration Management

The `ConfigurationManager` class provides:
- Environment variable loading
- Configuration validation
- Preset application
- JSON config file support

### Property-Based Testing

The system is designed for property-based testing using Hypothesis:
- Generate random test data
- Validate universal properties
- Catch edge cases automatically
- Ensure robust implementations

## Documentation

### Complete Documentation Suite

- **[SETUP.md](SETUP.md)** - Detailed setup and installation instructions
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive usage guide with examples
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Links

- **Getting Started**: See [SETUP.md](SETUP.md) for installation
- **Usage Examples**: See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage
- **Having Issues?**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions

## Implementation Status

### ✅ Completed Features
- **Project Structure**: Complete directory structure with proper Python packages
- **Data Models**: Comprehensive Pydantic models for all data types
- **Interfaces**: Abstract base classes defining contracts for all components
- **Configuration Management**: Environment variable support with validation
- **CLI Interface**: Command-line tool for managing the demo system
- **Testing Framework**: Complete test suite with Hypothesis for property-based testing
- **Data Generation**: All data generators (users, conversations, emotions, cultural context)
- **Local Storage**: JSON file storage and management
- **Mock API Server**: FastAPI-based server with WebSocket support
- **Frontend Launcher**: Automatic frontend setup and launching
- **Demo Orchestration**: Complete demo automation and management
- **Documentation**: Comprehensive setup, usage, and troubleshooting guides

## Requirements Validation

This implementation satisfies the following requirements:

- **6.1**: Easy setup and execution with command-line interface
- **6.5**: Cross-platform compatibility with proper path handling and environment detection

The project structure and core interfaces are now ready for implementing the remaining components in subsequent tasks.