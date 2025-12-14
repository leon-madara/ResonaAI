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
    print("Running unit tests (isolated suites)...")
    try:
        repo_root = Path(__file__).resolve().parents[1]
        tests_root = repo_root / "tests"

        suites: list[list[str]] = []

        # Core/unit tests at repo root (exclude integration folder; run separately).
        suites.append([str(tests_root / "test_audio_processor.py")])
        suites.append([str(tests_root / "test_emotion_detector.py")])
        suites.append([str(tests_root / "test_streaming_processor.py")])
        suites.append([str(tests_root / "test_api.py")])

        # Database schema tests
        suites.append([str(tests_root / "database")])

        # Service suites (one subprocess per service to avoid module cache collisions)
        services_dir = tests_root / "services"
        if services_dir.exists():
            for child in sorted(services_dir.iterdir()):
                if child.is_dir():
                    suites.append([str(child)])

        # Run each suite in a fresh Python process
        for suite in suites:
            print(f"\n--- Running: pytest {' '.join(suite)} ---")
            subprocess.run([sys.executable, "-m", "pytest", *suite], check=True)

        print("\nUnit test suites passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Unit tests failed: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    try:
        repo_root = Path(__file__).resolve().parents[1]
        tests_root = repo_root / "tests"
        result = subprocess.run([sys.executable, "-m", "pytest", str(tests_root / "integration")], check=True)
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
        repo_root = Path(__file__).resolve().parents[1]
        # Run flake8
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            str(repo_root / "src"),
            str(repo_root / "tests"),
            str(repo_root / "main.py"),
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
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run([
            sys.executable, "-m", "black", 
            "--check", 
            str(repo_root / "src"),
            str(repo_root / "tests"),
            str(repo_root / "main.py"),
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
    
    # Style gates are opt-in locally (CI should enforce once baseline is clean).
    if os.getenv("RUN_STYLE", "0") == "1":
        if not run_linting():
            all_passed = False
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
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
