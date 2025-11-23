#!/usr/bin/env python3
"""
Test runner script for ResonaAI Voice Emotion Detection Pipeline
"""

import subprocess
import sys
import os
from pathlib import Path

def run_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--cov=src",
            "--cov-report=term-missing"
        ], check=True)
        print("Unit tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Unit tests failed: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "-m", "integration",
            "--tb=short"
        ], check=True)
        print("Integration tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Integration tests failed: {e}")
        return False

def run_performance_tests():
    """Run performance tests"""
    print("Running performance tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "-m", "slow",
            "--tb=short"
        ], check=True)
        print("Performance tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Performance tests failed: {e}")
        return False

def run_linting():
    """Run code linting"""
    print("Running code linting...")
    try:
        # Run flake8
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            "src/", 
            "tests/", 
            "main.py"
        ], check=True)
        print("Linting passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Linting failed: {e}")
        return False

def run_formatting_check():
    """Check code formatting"""
    print("Checking code formatting...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "black", 
            "--check", 
            "src/", 
            "tests/", 
            "main.py"
        ], check=True)
        print("Code formatting is correct!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Code formatting check failed: {e}")
        print("Run 'black .' to fix formatting issues")
        return False

def main():
    """Main test runner function"""
    print("Running ResonaAI Voice Emotion Detection Pipeline Tests...")
    
    all_passed = True
    
    # Run linting
    if not run_linting():
        all_passed = False
    
    # Run formatting check
    if not run_formatting_check():
        all_passed = False
    
    # Run unit tests
    if not run_unit_tests():
        all_passed = False
    
    # Run integration tests (if any)
    # if not run_integration_tests():
    #     all_passed = False
    
    # Run performance tests (if any)
    # if not run_performance_tests():
    #     all_passed = False
    
    if all_passed:
        print("\nAll tests passed! ✅")
        return 0
    else:
        print("\nSome tests failed! ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
