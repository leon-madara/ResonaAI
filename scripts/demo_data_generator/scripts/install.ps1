# Installation script for ResonaAI Demo Data Generator (Windows PowerShell)

param(
    [string]$InstallPath = "$env:USERPROFILE\.resona-demo",
    [string]$SourcePath = $null
)

# Configuration
$PythonMinVersion = [Version]"3.8.0"
$NodeMinVersion = [Version]"16.0.0"

Write-Host "🚀 ResonaAI Demo Data Generator Installation" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue

# Function to compare versions
function Compare-Version {
    param([Version]$Version1, [Version]$Version2)
    return $Version1.CompareTo($Version2)
}

# Check Python version
Write-Host "🐍 Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
        $currentPythonVersion = [Version]$matches[1]
        if ((Compare-Version $currentPythonVersion $PythonMinVersion) -ge 0) {
            Write-Host "✅ Python $currentPythonVersion found" -ForegroundColor Green
        } else {
            Write-Host "❌ Python $currentPythonVersion found, but $PythonMinVersion or higher is required" -ForegroundColor Red
            exit 1
        }
    } else {
        throw "Could not parse Python version"
    }
} catch {
    Write-Host "❌ Python not found. Please install Python $PythonMinVersion or higher" -ForegroundColor Red
    Write-Host "   Download from: https://python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node.js version
Write-Host "📦 Checking Node.js version..." -ForegroundColor Yellow
try {
    $nodeVersion = & node --version 2>&1
    if ($nodeVersion -match "v(\d+\.\d+\.\d+)") {
        $currentNodeVersion = [Version]$matches[1]
        if ((Compare-Version $currentNodeVersion $NodeMinVersion) -ge 0) {
            Write-Host "✅ Node.js $currentNodeVersion found" -ForegroundColor Green
        } else {
            Write-Host "❌ Node.js $currentNodeVersion found, but v$NodeMinVersion or higher is required" -ForegroundColor Red
            exit 1
        }
    } else {
        throw "Could not parse Node.js version"
    }
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js v$NodeMinVersion or higher" -ForegroundColor Red
    Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check npm
Write-Host "📦 Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = & npm --version 2>&1
    Write-Host "✅ npm $npmVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm" -ForegroundColor Red
    exit 1
}

# Create installation directory
Write-Host "📁 Creating installation directory..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Remove-Item -Path $InstallPath -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

# Copy demo data generator files
Write-Host "📥 Installing Demo Data Generator..." -ForegroundColor Yellow
if ($SourcePath -and (Test-Path $SourcePath)) {
    Write-Host "Installing from: $SourcePath"
    Copy-Item -Path "$SourcePath\*" -Destination $InstallPath -Recurse -Force
} else {
    # Install from current directory (assuming script is run from demo_data_generator directory)
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $DemoDir = Split-Path -Parent $ScriptDir
    Copy-Item -Path "$DemoDir\*" -Destination $InstallPath -Recurse -Force
}

# Install Python dependencies
Write-Host "🔧 Installing Python dependencies..." -ForegroundColor Yellow
$RequirementsFile = Join-Path $InstallPath "requirements.txt"
if (Test-Path $RequirementsFile) {
    Set-Location $InstallPath
    & python -m pip install --user -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ requirements.txt not found" -ForegroundColor Red
    exit 1
}

# Create batch file for easy access
Write-Host "🔗 Creating command script..." -ForegroundColor Yellow
$BatchContent = @"
@echo off
cd /d "$InstallPath"
python demo_data_generator.py %*
"@

$BatchFile = "$env:USERPROFILE\.local\bin\resona-demo.bat"
$BatchDir = Split-Path -Parent $BatchFile
if (!(Test-Path $BatchDir)) {
    New-Item -ItemType Directory -Path $BatchDir -Force | Out-Null
}
$BatchContent | Out-File -FilePath $BatchFile -Encoding ASCII

# Add to PATH if not already there
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$BatchDirPath = Split-Path -Parent $BatchFile
if ($UserPath -notlike "*$BatchDirPath*") {
    Write-Host "📝 Adding $BatchDirPath to PATH..." -ForegroundColor Yellow
    $NewPath = "$UserPath;$BatchDirPath"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    $env:PATH = "$env:PATH;$BatchDirPath"
}

# Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Yellow
Set-Location $InstallPath
$ValidationResult = & python demo_data_generator.py validate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 ResonaAI Demo Data Generator is now installed!" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  resona-demo generate --preset quick"
    Write-Host "  resona-demo launch --auto-browser"
    Write-Host "  resona-demo validate"
    Write-Host ""
    Write-Host "Or use the full path:"
    Write-Host "  cd $InstallPath"
    Write-Host "  python demo_data_generator.py launch --preset quick"
    Write-Host ""
    Write-Host "Note: You may need to restart your terminal to use the 'resona-demo' command." -ForegroundColor Yellow
} else {
    Write-Host "❌ Installation validation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "Installation directory: $InstallPath" -ForegroundColor Cyan