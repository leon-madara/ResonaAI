#!/bin/bash
# Installation script for ResonaAI Demo Data Generator (Linux/macOS)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
NODE_MIN_VERSION="16"
INSTALL_DIR="$HOME/.resona-demo"

echo -e "${BLUE}🚀 ResonaAI Demo Data Generator Installation${NC}"
echo "=============================================="

# Function to compare versions
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Check Python version
echo -e "${YELLOW}🐍 Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    version_compare $PYTHON_VERSION $PYTHON_MIN_VERSION
    if [[ $? -eq 2 ]]; then
        echo -e "${RED}❌ Python $PYTHON_VERSION found, but $PYTHON_MIN_VERSION or higher is required${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    fi
else
    echo -e "${RED}❌ Python 3 not found. Please install Python $PYTHON_MIN_VERSION or higher${NC}"
    exit 1
fi

# Check Node.js version
echo -e "${YELLOW}📦 Checking Node.js version...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    if [[ $NODE_MAJOR -lt $NODE_MIN_VERSION ]]; then
        echo -e "${RED}❌ Node.js $NODE_VERSION found, but v$NODE_MIN_VERSION or higher is required${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"
    fi
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js v$NODE_MIN_VERSION or higher${NC}"
    exit 1
fi

# Check npm
echo -e "${YELLOW}📦 Checking npm...${NC}"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm $NPM_VERSION found${NC}"
else
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi

# Create installation directory
echo -e "${YELLOW}📁 Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download or copy demo data generator
echo -e "${YELLOW}📥 Installing Demo Data Generator...${NC}"
if [[ -n "$1" && -d "$1" ]]; then
    # Install from local directory
    echo "Installing from local directory: $1"
    cp -r "$1"/* .
else
    # Install from current directory (assuming script is run from demo_data_generator directory)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    DEMO_DIR="$(dirname "$SCRIPT_DIR")"
    cp -r "$DEMO_DIR"/* .
fi

# Install Python dependencies
echo -e "${YELLOW}🔧 Installing Python dependencies...${NC}"
if [[ -f "requirements.txt" ]]; then
    python3 -m pip install --user -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Create symlink for easy access
echo -e "${YELLOW}🔗 Creating command symlink...${NC}"
SYMLINK_DIR="$HOME/.local/bin"
mkdir -p "$SYMLINK_DIR"

cat > "$SYMLINK_DIR/resona-demo" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 demo_data_generator.py "\$@"
EOF

chmod +x "$SYMLINK_DIR/resona-demo"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}📝 Adding $HOME/.local/bin to PATH...${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
    export PATH="$HOME/.local/bin:$PATH"
fi

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"
cd "$INSTALL_DIR"
if python3 demo_data_generator.py validate; then
    echo -e "${GREEN}✅ Installation successful!${NC}"
    echo ""
    echo -e "${BLUE}🎉 ResonaAI Demo Data Generator is now installed!${NC}"
    echo ""
    echo "Usage:"
    echo "  resona-demo generate --preset quick"
    echo "  resona-demo launch --auto-browser"
    echo "  resona-demo validate"
    echo ""
    echo "Or use the full path:"
    echo "  cd $INSTALL_DIR"
    echo "  python3 demo_data_generator.py launch --preset quick"
    echo ""
    echo -e "${YELLOW}Note: You may need to restart your terminal or run 'source ~/.bashrc' to use the 'resona-demo' command.${NC}"
else
    echo -e "${RED}❌ Installation validation failed${NC}"
    exit 1
fi