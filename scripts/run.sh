#!/bin/bash
#
# Startup script for Elderly Fall Detection System
# 
# This script starts both the main detection system and web interface
#
# Usage: ./run.sh [--web-only] [--main-only]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Elderly Fall Detection System${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Parse arguments
WEB_ONLY=false
MAIN_ONLY=false

for arg in "$@"; do
    case $arg in
        --web-only)
            WEB_ONLY=true
            shift
            ;;
        --main-only)
            MAIN_ONLY=true
            shift
            ;;
    esac
done

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "  Please run setup first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}→ Activating virtual environment...${NC}"
source venv/bin/activate

# Check Python packages
echo -e "${GREEN}→ Checking dependencies...${NC}"
python3 -c "import flask, cv2, yaml, numpy" 2>/dev/null || {
    echo -e "${RED}✗ Missing dependencies!${NC}"
    echo -e "  Installing from requirements.txt..."
    pip install -r requirements.txt
}

# Create necessary directories
echo -e "${GREEN}→ Checking directories...${NC}"
mkdir -p data/images data/logs models

# Clear all images and reset database
echo -e "${YELLOW}→ Clearing previous session data...${NC}"
rm -f data/images/*.jpg 2>/dev/null || true
rm -f data/database.db 2>/dev/null || true
echo -e "${GREEN}✓ Gallery cleared, starting fresh${NC}"

# Check configuration
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}✗ Configuration file not found: config/config.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Pre-checks complete${NC}"
echo ""

# Function to start web interface
start_web() {
    echo -e "${BLUE}→ Starting web interface...${NC}"
    cd webapp
    python3 app.py &
    WEB_PID=$!
    cd ..
    echo -e "${GREEN}✓ Web interface started (PID: $WEB_PID)${NC}"
    echo -e "  Access at: ${YELLOW}http://localhost:5000${NC}"
    echo ""
}

# Function to start main system
start_main() {
    echo -e "${BLUE}→ Starting main detection system...${NC}"
    echo -e "${YELLOW}  Note: GPIO requires root access. Using sudo with venv...${NC}"
    # Use sudo with the venv's python directly to preserve packages
    sudo -E "$PROJECT_DIR/venv/bin/python3" src/main.py &
    MAIN_PID=$!
    echo -e "${GREEN}✓ Main system started (PID: $MAIN_PID)${NC}"
    echo ""
}

# Trap Ctrl+C
cleanup() {
    echo ""
    echo -e "${YELLOW}→ Shutting down...${NC}"
    
    if [ ! -z "$WEB_PID" ]; then
        echo -e "  Stopping web interface (PID: $WEB_PID)..."
        kill $WEB_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$MAIN_PID" ]; then
        echo -e "  Stopping main system (PID: $MAIN_PID)..."
        kill $MAIN_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Shutdown complete${NC}"
    exit 0
}

trap cleanup INT TERM

# Start components based on arguments
if [ "$MAIN_ONLY" = true ]; then
    start_main
elif [ "$WEB_ONLY" = true ]; then
    start_web
else
    # Start both
    start_web
    sleep 2
    start_main
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  System Running${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Web Interface: ${YELLOW}http://localhost:5000${NC}"
echo -e "  Log File: ${YELLOW}data/logs/system.log${NC}"
echo ""
echo -e "  Press ${RED}Ctrl+C${NC} to stop"
echo ""

# Wait for processes
wait
