#!/usr/bin/env python3
"""
Generate test coverage report for ResonaAI
"""

import subprocess
import sys
import os

def main():
    """Generate coverage report"""
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print("=" * 60)
    print("Generating Test Coverage Report")
    print("=" * 60)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=apps/backend",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=json:coverage.json",
        "-v",
        "--tb=short"
    ]
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        print("\n" + "=" * 60)
        print("Coverage Report Generated")
        print("=" * 60)
        print("\nCoverage reports:")
        print("  - Terminal: Shown above")
        print("  - HTML: htmlcov/index.html")
        print("  - JSON: coverage.json")
        print("\nTo view HTML report:")
        print("  - Open htmlcov/index.html in your browser")
        
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nCoverage generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError generating coverage: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

