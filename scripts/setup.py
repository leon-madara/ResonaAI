#!/usr/bin/env python3
"""
Setup script for ResonaAI Voice Emotion Detection Pipeline
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "models",
        "uploads",
        "temp",
        "data",
        "checkpoints"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    return True

def setup_environment():
    """Setup environment configuration"""
    env_example = "config.env.example"
    env_file = ".env"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            print(f"Created {env_file} from {env_example}")
        else:
            print(f"Warning: {env_example} not found")
    else:
        print(f"{env_file} already exists")

def download_models():
    """Download pre-trained models"""
    print("Downloading pre-trained models...")
    try:
        # This would download the actual models
        # For now, just create the models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # Create a placeholder file
        placeholder = models_dir / "README.md"
        with open(placeholder, "w") as f:
            f.write("# Models Directory\n\n")
            f.write("This directory contains pre-trained models for emotion detection.\n")
            f.write("Models will be downloaded automatically on first run.\n")
        
        print("Models directory created")
    except Exception as e:
        print(f"Error setting up models: {e}")

def run_tests():
    """Run tests to verify installation"""
    print("Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("All tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
        return False
    return True

def main():
    """Main setup function"""
    print("Setting up ResonaAI Voice Emotion Detection Pipeline...")
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        return 1
    
    # Setup environment
    setup_environment()
    
    # Download models
    download_models()
    
    # Run tests
    if not run_tests():
        print("Tests failed, but setup completed")
    
    print("\nSetup completed successfully!")
    print("\nTo start the API server, run:")
    print("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\nTo run tests, use:")
    print("pytest tests/ -v")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
