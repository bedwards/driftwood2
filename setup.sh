#!/bin/bash

# Philosophical Dialogue System Setup Script
# For Mac/Linux systems

set -e

echo "════════════════════════════════════════════════════════════════"
echo "   Philosophical Dialogue System - Setup"
echo "════════════════════════════════════════════════════════════════"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check Ollama
echo
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    print_status "Ollama found"
    
    # Start Ollama service if not running
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
        print_status "Ollama service started"
    else
        print_status "Ollama service already running"
    fi
else
    print_error "Ollama not found"
    echo "Please install Ollama from: https://ollama.com/download"
    echo "Or run: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo
    echo "Creating data directory..."
    mkdir -p data
    print_status "Data directory created"
fi

# Create virtual environment
echo
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo
echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
print_status "Dependencies installed"

# Check and download Ollama models
echo
echo "Checking Ollama models..."
echo "This may take a while on first run..."

MODELS=(
    "llama3.2:3b"
    "mistral:7b"
    "qwen2.5:7b"
    "gemma2:9b"
)

for model in "${MODELS[@]}"; do
    echo -n "Checking $model... "
    if ollama list 2>/dev/null | grep -q "$model"; then
        print_status "already installed"
    else
        print_warning "not found, downloading..."
        ollama pull "$model"
        print_status "$model downloaded"
    fi
done

# Optional: Check for DeepSeek R1
echo
echo -n "Checking for DeepSeek R1 model... "
if ollama list 2>/dev/null | grep -q "deepseek"; then
    print_status "DeepSeek model found"
else
    print_warning "DeepSeek R1 not found (optional)"
    echo "  To install: ollama pull deepseek-r1:7b (if available)"
fi

echo
echo "════════════════════════════════════════════════════════════════"
echo "   Setup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python app.py"
echo "  3. Open browser to: http://localhost:5001"
echo
echo "For Speechify integration:"
echo "  - Install Speechify Chrome extension"
echo "  - Each philosopher tab can use different voices"
echo
echo "════════════════════════════════════════════════════════════════"