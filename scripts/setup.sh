#!/bin/bash
#
# Setup script for Elderly Fall Detection System
# Run this once to set up the complete environment
#
# Usage: sudo ./setup.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Elderly Fall Detection System Setup${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if running as root for system packages
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠  This script should be run with sudo for system package installation${NC}"
    echo -e "   Some steps may be skipped. Run as: ${GREEN}sudo ./setup.sh${NC}"
    echo ""
fi

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${GREEN}1. Updating system packages...${NC}"
apt-get update || echo -e "${YELLOW}  Skipped (no sudo)${NC}"

echo ""
echo -e "${GREEN}2. Installing system dependencies...${NC}"
apt-get install -y python3 python3-pip python3-venv python3-dev \
    libopencv-dev python3-opencv \
    libatlas-base-dev libhdf5-dev \
    v4l-utils \
    git wget curl || echo -e "${YELLOW}  Skipped (no sudo)${NC}"

echo ""
echo -e "${GREEN}3. Installing GPIO libraries (RDK X5)...${NC}"
# Try Hobot GPIO for RDK X5
pip3 install Hobot.GPIO 2>/dev/null || {
    echo -e "${YELLOW}  Hobot.GPIO not available, trying RPi.GPIO...${NC}"
    apt-get install -y python3-rpi.gpio python3-gpiozero 2>/dev/null || echo -e "${YELLOW}  Skipped${NC}"
}

echo ""
echo -e "${GREEN}4. Creating directory structure...${NC}"
mkdir -p data/images data/logs models
mkdir -p webapp/templates webapp/static/css webapp/static/js
echo -e "  ✓ Directories created"

echo ""
echo -e "${GREEN}5. Creating Python virtual environment...${NC}"
python3 -m venv venv
echo -e "  ✓ Virtual environment created"

echo ""
echo -e "${GREEN}6. Installing Python packages...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "  ✓ Python packages installed"

echo ""
echo -e "${GREEN}7. Setting up permissions...${NC}"
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "  ✓ Scripts made executable"

echo ""
echo -e "${GREEN}8. Checking camera...${NC}"
v4l2-ctl --list-devices 2>/dev/null || echo -e "${YELLOW}  No camera detected (install v4l-utils or connect camera)${NC}"

echo ""
echo -e "${GREEN}9. Testing imports...${NC}"
python3 << EOF
import sys
try:
    import flask
    print("  ✓ Flask")
    import cv2
    print("  ✓ OpenCV")
    import yaml
    print("  ✓ PyYAML")
    import numpy
    print("  ✓ NumPy")
    print("  ✓ All core packages available")
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)
EOF

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  1. Connect hardware:"
echo -e "     - Camera to MIPI CSI port"
echo -e "     - Buttons and LEDs to GPIO pins"
echo -e ""
echo -e "  2. Test components:"
echo -e "     ${YELLOW}python3 test_components.py${NC}"
echo -e ""
echo -e "  3. Start system:"
echo -e "     ${YELLOW}./scripts/run.sh${NC}"
echo -e ""
echo -e "  4. Access web interface:"
echo -e "     ${YELLOW}http://localhost:5000${NC}"
echo -e ""
echo -e "For more information, see:"
echo -e "  - README.md"
echo -e "  - QUICK_START.md"
echo -e "  - RDK_SETUP.md"
echo ""
