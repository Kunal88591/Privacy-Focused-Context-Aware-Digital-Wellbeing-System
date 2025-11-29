#!/bin/bash

# Setup script for Privacy-Focused Digital Wellbeing System
# This script helps set up the development environment

set -e  # Exit on error

echo "🚀 Privacy-Focused Digital Wellbeing System - Setup Script"
echo "=========================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print colored message
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

MISSING_DEPS=0

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python 3 found (version $PYTHON_VERSION)"
else
    print_error "Python 3 not found. Please install Python 3.9 or higher"
    MISSING_DEPS=1
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "Node.js found (version $NODE_VERSION)"
else
    print_error "Node.js not found. Please install Node.js 18 or higher"
    MISSING_DEPS=1
fi

if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "npm found (version $NPM_VERSION)"
else
    print_error "npm not found. Please install npm"
    MISSING_DEPS=1
fi

if command_exists mosquitto; then
    print_status "Mosquitto MQTT broker found"
else
    print_warning "Mosquitto not found. Installing is recommended for full functionality"
    echo "  Install with: sudo apt install mosquitto (Ubuntu/Debian)"
    echo "               brew install mosquitto (macOS)"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    print_error "Missing required dependencies. Please install them and run this script again."
    exit 1
fi

echo ""
echo "=========================================================="
echo "Setting up project components..."
echo ""

# Setup Backend API
echo "📡 Setting up Backend API..."
cd backend-api
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
fi

source venv/bin/activate 2>/dev/null || . venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_status "Installed backend dependencies"

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env file from template"
else
    print_warning ".env already exists, skipping"
fi
deactivate
cd ..

echo ""

# Setup IoT Device
echo "🤖 Setting up IoT Device..."
cd iot-device
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
fi

source venv/bin/activate 2>/dev/null || . venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_status "Installed IoT device dependencies"

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env file from template"
else
    print_warning ".env already exists, skipping"
fi
deactivate
cd ..

echo ""

# Setup AI Models
echo "🧠 Setting up AI Models..."
cd ai-models
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created virtual environment"
fi

source venv/bin/activate 2>/dev/null || . venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_status "Installed AI/ML dependencies"
deactivate
cd ..

echo ""

# Setup Mobile App
echo "📱 Setting up Mobile App..."
cd mobile-app
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
    print_status "Installed mobile app dependencies"
else
    print_warning "node_modules already exists, skipping npm install"
fi
cd ..

echo ""
echo "=========================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start MQTT broker: mosquitto"
echo "2. Start backend API: cd backend-api && source venv/bin/activate && python app/main.py"
echo "3. Start IoT device: cd iot-device && source venv/bin/activate && python mqtt_client.py"
echo "4. Start mobile app: cd mobile-app && npm start"
echo ""
echo "For detailed instructions, see: docs/setup/QUICK_START.md"
echo ""
