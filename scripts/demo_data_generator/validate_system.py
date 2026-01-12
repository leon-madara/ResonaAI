#!/usr/bin/env python3
"""
System validation script for Demo Data Generator
Tests compatibility across different environments
"""

import sys
import platform
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Any

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
    }

def check_python_version() -> Dict[str, Any]:
    """Check Python version compatibility"""
    version_info = sys.version_info
    is_compatible = version_info >= (3, 8)
    
    return {
        "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
        "compatible": is_compatible,
        "minimum_required": "3.8.0",
        "recommended": "3.10.0+",
        "status": "✅ Compatible" if is_compatible else "❌ Incompatible"
    }

def check_node_version() -> Dict[str, Any]:
    """Check Node.js version compatibility"""
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip('v')
            major_version = int(version.split('.')[0])
            is_compatible = major_version >= 16
            
            return {
                "version": version,
                "compatible": is_compatible,
                "minimum_required": "16.0.0",
                "recommended": "18.0.0+",
                "status": "✅ Compatible" if is_compatible else "❌ Incompatible"
            }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    
    return {
        "version": "Not found",
        "compatible": False,
        "minimum_required": "16.0.0",
        "recommended": "18.0.0+",
        "status": "❌ Not installed"
    }

def check_npm_version() -> Dict[str, Any]:
    """Check npm version"""
    try:
        result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            major_version = int(version.split('.')[0])
            is_compatible = major_version >= 8
            
            return {
                "version": version,
                "compatible": is_compatible,
                "minimum_required": "8.0.0",
                "status": "✅ Compatible" if is_compatible else "❌ Incompatible"
            }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    
    return {
        "version": "Not found",
        "compatible": False,
        "minimum_required": "8.0.0",
        "status": "❌ Not installed"
    }

def check_python_dependencies() -> Dict[str, Any]:
    """Check Python dependencies"""
    required_packages = [
        "fastapi",
        "pydantic", 
        "hypothesis",
        "uvicorn",
        "websockets"
    ]
    
    results = {}
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package)
            results[package] = {"installed": True, "status": "✅ Installed"}
        except ImportError:
            results[package] = {"installed": False, "status": "❌ Missing"}
            all_installed = False
    
    return {
        "packages": results,
        "all_installed": all_installed,
        "status": "✅ All dependencies installed" if all_installed else "❌ Missing dependencies"
    }

def check_port_availability() -> Dict[str, Any]:
    """Check if required ports are available"""
    import socket
    
    ports_to_check = [3000, 8001]
    results = {}
    all_available = True
    
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                is_available = result != 0
                results[port] = {
                    "available": is_available,
                    "status": "✅ Available" if is_available else "❌ In use"
                }
                if not is_available:
                    all_available = False
        except Exception as e:
            results[port] = {
                "available": False,
                "status": f"❌ Error: {str(e)}"
            }
            all_available = False
    
    return {
        "ports": results,
        "all_available": all_available,
        "status": "✅ All ports available" if all_available else "⚠️ Some ports in use"
    }

def check_file_permissions() -> Dict[str, Any]:
    """Check file system permissions"""
    test_dir = Path("demo_data_test")
    
    try:
        # Test directory creation
        test_dir.mkdir(exist_ok=True)
        
        # Test file creation
        test_file = test_dir / "test.json"
        test_file.write_text('{"test": true}')
        
        # Test file reading
        content = test_file.read_text()
        data = json.loads(content)
        
        # Test file deletion
        test_file.unlink()
        test_dir.rmdir()
        
        return {
            "can_create_directory": True,
            "can_write_files": True,
            "can_read_files": True,
            "can_delete_files": True,
            "status": "✅ All permissions OK"
        }
        
    except Exception as e:
        # Cleanup on error
        try:
            if test_file.exists():
                test_file.unlink()
            if test_dir.exists():
                test_dir.rmdir()
        except:
            pass
            
        return {
            "can_create_directory": False,
            "can_write_files": False,
            "can_read_files": False,
            "can_delete_files": False,
            "status": f"❌ Permission error: {str(e)}"
        }

def test_demo_functionality() -> Dict[str, Any]:
    """Test core demo functionality"""
    try:
        # Test imports
        from scripts.demo_data_generator.config import DemoConfig
        from scripts.demo_data_generator.storage.local_storage import LocalStorageManager
        from scripts.demo_data_generator.generators.user_generator import UserGenerator
        
        # Test configuration
        config = DemoConfig(num_users=1, conversations_per_user=1)
        
        # Test storage
        storage = LocalStorageManager("demo_data_test")
        
        # Test user generation
        user_gen = UserGenerator()
        user = user_gen.generate_user_profile()
        
        # Cleanup
        import shutil
        if Path("demo_data_test").exists():
            shutil.rmtree("demo_data_test")
        
        return {
            "imports": True,
            "configuration": True,
            "storage": True,
            "generation": True,
            "status": "✅ Core functionality working"
        }
        
    except Exception as e:
        return {
            "imports": False,
            "configuration": False,
            "storage": False,
            "generation": False,
            "status": f"❌ Error: {str(e)}"
        }

def run_validation() -> Dict[str, Any]:
    """Run complete system validation"""
    print("🔍 Running Demo Data Generator System Validation...")
    print("=" * 60)
    
    results = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "system_info": get_system_info(),
        "python_version": check_python_version(),
        "node_version": check_node_version(),
        "npm_version": check_npm_version(),
        "python_dependencies": check_python_dependencies(),
        "port_availability": check_port_availability(),
        "file_permissions": check_file_permissions(),
        "demo_functionality": test_demo_functionality()
    }
    
    # Print results
    print(f"🖥️  System: {results['system_info']['platform']}")
    print(f"🐍 Python: {results['python_version']['status']}")
    print(f"📦 Node.js: {results['node_version']['status']}")
    print(f"📦 npm: {results['npm_version']['status']}")
    print(f"📚 Dependencies: {results['python_dependencies']['status']}")
    print(f"🔌 Ports: {results['port_availability']['status']}")
    print(f"📁 Permissions: {results['file_permissions']['status']}")
    print(f"⚙️  Demo Functions: {results['demo_functionality']['status']}")
    
    # Overall status
    all_checks = [
        results['python_version']['compatible'],
        results['node_version']['compatible'],
        results['npm_version']['compatible'],
        results['python_dependencies']['all_installed'],
        results['file_permissions']['can_write_files'],
        results['demo_functionality']['imports']
    ]
    
    overall_status = all(all_checks)
    results['overall_status'] = overall_status
    
    print("=" * 60)
    if overall_status:
        print("✅ VALIDATION PASSED - System ready for Demo Data Generator")
    else:
        print("❌ VALIDATION FAILED - Please address the issues above")
        
        # Provide specific recommendations
        print("\n🔧 Recommendations:")
        if not results['python_version']['compatible']:
            print("   - Upgrade Python to 3.8 or higher")
        if not results['node_version']['compatible']:
            print("   - Install Node.js 16.0 or higher")
        if not results['npm_version']['compatible']:
            print("   - Update npm to version 8.0 or higher")
        if not results['python_dependencies']['all_installed']:
            print("   - Install missing Python packages: pip install -r requirements.txt")
        if not results['file_permissions']['can_write_files']:
            print("   - Check file system permissions for the current directory")
    
    return results

if __name__ == "__main__":
    validation_results = run_validation()
    
    # Save results to file
    results_file = Path("validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if validation_results['overall_status'] else 1)