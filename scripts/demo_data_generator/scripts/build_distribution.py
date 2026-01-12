#!/usr/bin/env python3
"""
Build distribution packages for ResonaAI Demo Data Generator
"""

import os
import sys
import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path
from typing import List

def run_command(cmd: List[str], cwd: Path = None) -> bool:
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False

def create_source_distribution(source_dir: Path, dist_dir: Path) -> bool:
    """Create source distribution"""
    print("📦 Creating source distribution...")
    
    # Files to include in distribution
    include_files = [
        "*.py",
        "requirements.txt",
        "setup.py",
        "README.md",
        "USAGE_GUIDE.md",
        "SETUP.md", 
        "TROUBLESHOOTING.md",
        "Dockerfile",
        "docker-compose.yml",
        "generators/",
        "storage/",
        "api/",
        "launcher/",
        "tests/",
        "examples/",
        "scripts/",
    ]
    
    # Create temporary directory for packaging
    temp_dir = dist_dir / "temp"
    package_dir = temp_dir / "resona-demo-data-generator"
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    package_dir.mkdir(parents=True)
    
    # Copy files
    for pattern in include_files:
        if pattern.endswith("/"):
            # Directory
            src_path = source_dir / pattern.rstrip("/")
            if src_path.exists():
                shutil.copytree(src_path, package_dir / pattern.rstrip("/"))
        else:
            # File or glob pattern
            if "*" in pattern:
                import glob
                for file_path in glob.glob(str(source_dir / pattern)):
                    rel_path = Path(file_path).relative_to(source_dir)
                    dest_path = package_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
            else:
                src_path = source_dir / pattern
                if src_path.exists():
                    dest_path = package_dir / pattern
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
    
    # Create archives
    version = "1.0.0"
    
    # ZIP archive (Windows)
    zip_path = dist_dir / f"resona-demo-data-generator-{version}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arc_path = file_path.relative_to(temp_dir)
                zf.write(file_path, arc_path)
    
    # TAR.GZ archive (Linux/macOS)
    tar_path = dist_dir / f"resona-demo-data-generator-{version}.tar.gz"
    with tarfile.open(tar_path, 'w:gz') as tf:
        tf.add(package_dir, arcname=f"resona-demo-data-generator-{version}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    print(f"✅ Created {zip_path}")
    print(f"✅ Created {tar_path}")
    return True

def create_wheel_distribution(source_dir: Path, dist_dir: Path) -> bool:
    """Create Python wheel distribution"""
    print("🎡 Creating wheel distribution...")
    
    # Build wheel
    wheel_dist_dir = dist_dir / "wheels"
    wheel_dist_dir.mkdir(exist_ok=True)
    
    return run_command([
        sys.executable, "setup.py", 
        "bdist_wheel", 
        "--dist-dir", str(wheel_dist_dir)
    ], cwd=source_dir)

def create_docker_image(source_dir: Path) -> bool:
    """Build Docker image"""
    print("🐳 Building Docker image...")
    
    # Build Docker image
    success = run_command([
        "docker", "build", 
        "-t", "resona-demo-data-generator:latest",
        "-t", "resona-demo-data-generator:1.0.0",
        "."
    ], cwd=source_dir)
    
    if success:
        print("✅ Docker image built successfully")
        print("   Run with: docker run -p 3000:3000 -p 8001:8001 resona-demo-data-generator:latest")
    
    return success

def create_installation_packages(source_dir: Path, dist_dir: Path) -> bool:
    """Create platform-specific installation packages"""
    print("📋 Creating installation packages...")
    
    install_dir = dist_dir / "installers"
    install_dir.mkdir(exist_ok=True)
    
    # Copy installation scripts
    scripts_dir = source_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.glob("install.*"):
            shutil.copy2(script, install_dir)
    
    # Create quick install script for Unix
    unix_installer = install_dir / "quick-install.sh"
    unix_installer.write_text("""#!/bin/bash
# Quick installer for ResonaAI Demo Data Generator

set -e

echo "🚀 ResonaAI Demo Data Generator Quick Install"
echo "============================================"

# Download and extract
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Downloading..."
curl -L -o resona-demo.tar.gz "https://github.com/resonaai/demo-data-generator/releases/latest/download/resona-demo-data-generator-1.0.0.tar.gz"

echo "📦 Extracting..."
tar -xzf resona-demo.tar.gz
cd resona-demo-data-generator-1.0.0

echo "🔧 Installing..."
bash scripts/install.sh

echo "🧹 Cleaning up..."
cd /
rm -rf "$TEMP_DIR"

echo "✅ Installation complete!"
""")
    unix_installer.chmod(0o755)
    
    # Create quick install script for Windows
    windows_installer = install_dir / "quick-install.ps1"
    windows_installer.write_text("""# Quick installer for ResonaAI Demo Data Generator

Write-Host "🚀 ResonaAI Demo Data Generator Quick Install" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Blue

# Create temp directory
$TempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }

try {
    Set-Location $TempDir
    
    Write-Host "📥 Downloading..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://github.com/resonaai/demo-data-generator/releases/latest/download/resona-demo-data-generator-1.0.0.zip" -OutFile "resona-demo.zip"
    
    Write-Host "📦 Extracting..." -ForegroundColor Yellow
    Expand-Archive -Path "resona-demo.zip" -DestinationPath "."
    Set-Location "resona-demo-data-generator-1.0.0"
    
    Write-Host "🔧 Installing..." -ForegroundColor Yellow
    & PowerShell -ExecutionPolicy Bypass -File "scripts\\install.ps1"
    
    Write-Host "✅ Installation complete!" -ForegroundColor Green
} finally {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    Set-Location $env:USERPROFILE
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}
""")
    
    print(f"✅ Created installation packages in {install_dir}")
    return True

def main():
    """Main build function"""
    print("🏗️  Building ResonaAI Demo Data Generator Distribution")
    print("=" * 60)
    
    # Get paths
    script_dir = Path(__file__).parent
    source_dir = script_dir.parent
    dist_dir = source_dir / "dist"
    
    # Create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    success = True
    
    # Create source distribution
    if not create_source_distribution(source_dir, dist_dir):
        success = False
    
    # Create wheel distribution
    if not create_wheel_distribution(source_dir, dist_dir):
        success = False
    
    # Create installation packages
    if not create_installation_packages(source_dir, dist_dir):
        success = False
    
    # Build Docker image (optional)
    if shutil.which("docker"):
        create_docker_image(source_dir)
    else:
        print("⚠️  Docker not found, skipping Docker image build")
    
    print("=" * 60)
    if success:
        print("✅ Distribution build completed successfully!")
        print(f"📁 Distribution files created in: {dist_dir}")
        print("\nCreated files:")
        for file_path in dist_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(dist_dir)
                size = file_path.stat().st_size
                print(f"   {rel_path} ({size:,} bytes)")
    else:
        print("❌ Distribution build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())