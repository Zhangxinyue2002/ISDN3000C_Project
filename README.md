# Elderly Fall Detection System

An AI-powered monitoring system that detects falls, monitors breathing, and provides emergency response capabilities for elderly care.

![System Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Platform](https://img.shields.io/badge/Platform-RDK%20X5-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

---

## 🎯 Project Overview

This system uses a Raspberry Pi (RDK) with camera, AI models, and sensors to:
- ✅ **Detect falls** using YOLOv8 pose detection
- ✅ **Monitor breathing** using SIFT motion detection (integrated verification)
- ✅ **Trigger emergency calls** with 10-second countdown and manual override
- ✅ **Provide web gallery** for captured images with WiFi access
- ✅ **Real-time alerts** using LEDs and buttons

### 🔄 **NEW: Integrated Fall + Breathing Detection**
The system now performs automatic breathing checks after detecting a 1-minute fall, preventing false alarms before triggering emergency calls. See [INTEGRATED_SYSTEM_GUIDE.md](INTEGRATED_SYSTEM_GUIDE.md) for complete details.

---

## 📖 Table of Contents

1. [Quick Start Guide](#-quick-start-guide)
2. [Step-by-Step Operation](#-step-by-step-operation)
3. [System Architecture](#-system-architecture)
4. [Features](#-features)
5. [Installation](#-installation)
6. [Troubleshooting](#-troubleshooting)
7. [Advanced Usage](#-advanced-usage)

---

## 🚀 Quick Start Guide

### Prerequisites
- RDK X5 with Ubuntu installed
- Camera connected (USB or CSI)
- Internet connection for initial setup

### 1-Minute Setup
```bash
# Clone the repository
git clone https://github.com/Zhangxinyue2002/ISDN3000C_Project.git
cd ISDN3000C_Project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the system
./scripts/run.sh
```

### Access the System
- **Web Interface**: http://localhost:5000
- **From other devices**: http://192.168.50.8:5000

---

## 📚 Step-by-Step Operation

### Step 1: Initial Setup (First Time Only)

#### 1.1 Connect Hardware
```bash
# Check if camera is detected
ls /dev/video*
# Should show: /dev/video0 or /dev/video1
```

#### 1.2 Activate Virtual Environment
```bash
cd /home/sunrise/Project/ISDN3000C_Project
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

#### 1.3 Verify Installation
```bash
# Check Python version (should be 3.10+)
python3 --version

# Check if all packages are installed
pip list | grep -E "(opencv|flask|ultralytics|yaml)"
```

Expected output:
```
opencv-python         4.8.1.78
Flask                 3.0.0
ultralytics           8.0.227
PyYAML                6.0.1
```

---

### Step 2: Starting the System

#### 2.1 Start Everything
```bash
# Make sure you're in the project directory
cd /home/sunrise/Project/ISDN3000C_Project

# Activate virtual environment (if not already)
source venv/bin/activate

# Start the system
./scripts/run.sh
```

#### 2.2 What You'll See
```
============================================
  Elderly Fall Detection System
============================================

✓ Pre-checks complete
✓ Web interface started (PID: XXXX)
  Access at: http://localhost:5000
✓ Main system started (PID: XXXX)

============================================
  System Running
============================================

  Web Interface: http://localhost:5000
  Log File: data/logs/system.log
```

#### 2.3 Verify System is Running
```bash
# Check if processes are running
ps aux | grep python | grep -E "(main.py|app.py)"

# Check camera status
tail -20 data/logs/system.log | grep Camera
```

You should see:
- `Camera opened successfully on /dev/video0`
- `Camera running: True`
- `Continuous capture started`

---

### Step 3: Using the Web Interface

#### 3.1 Access the Gallery
1. Open your browser
2. Go to: **http://localhost:5000**
3. You should see the image gallery

#### 3.2 Understanding the Interface

**Top Bar - Filters:**
- **Category**: Filter by Normal, Fall, or Emergency
- **Sort**: Show newest or oldest first
- **Images Per Page**: 20, 50, 100, or 500
- **Reset**: Clear all filters
- **Auto-Refresh ON/OFF**: Toggle automatic updates (updates every 3 seconds)

**Statistics Cards:**
- **Total Images**: Number of photos captured
- **Falls Detected**: Number of fall events detected
- **Emergencies**: Number of emergency calls triggered
- **Storage**: Disk space used

**Image Grid:**
- Each image shows timestamp
- **Red "FALL" badge**: Fall detected in this image
- **Yellow "EMERGENCY" badge**: Emergency triggered
- Click any image to see details

#### 3.3 Key Features

**Auto-Refresh:**
- Click the green "Auto-Refresh ON" button to enable/disable
- When ON: New images appear automatically every 3 seconds
- When OFF: Click browser refresh to update manually

**Download Images:**
- Click "Download All" button
- System creates ZIP file of all images
- Downloads automatically to your computer

**Filter by Falls:**
- Select "fall" from Category dropdown
- See only images where falls were detected

---

### Step 4: Stopping the System

#### 6.1 Graceful Shutdown
```bash
# Step 1: Press Ctrl+C in the terminal where run.sh is running

# Step 2: Kill processes
pkill -f "python.*main.py"
pkill -f "python.*webapp/app.py"
```

---

## ⚡ Hardware Wiring Guide

### Components Needed

| Component | Quantity | Specification |
|-----------|----------|---------------|
| Push Buttons | 2 | Normally-open momentary switches |
| LEDs | 2 | Any color |
| Resistors | 4 | 220Ω |
| Jumper Wires | At least 10 | Male-to-female |
| Breadboard | 1 | / |

### GPIO Pin Assignment

| Component | Physical Pin | GPIO Number | Function |
|-----------|--------------|-------------|----------|
| Button 1 | Pin 11 | GPIO 17 | Manual emergency call (Call 999) |
| Button 2 | Pin 13 | GPIO 27 | Cancel emergency |
| LED 1 | Pin 31 | GPIO 6 | Fall detection indicator |
| LED 2 | Pin 33 | GPIO 13 | Emergency status (flash/solid) |
| GND | Pin 6, 9, 14, 25, 30, 34, 39 | Ground | Common ground |
| 3.3V | Pin 1, 17 | 3.3V Power | Power for buttons |

### Wiring Instructions

#### LED 1 (Fall Indicator) - Pin 31
```
RDK Pin 31 (GPIO 6) ──→ [220Ω Resistor] ──→ LED (+) ──→ LED (-) ──→ GND (Pin 6)
```

**Steps:**
1. Connect Pin 31 to one end of a 220Ω resistor
2. Connect the other end of resistor to LED's positive leg (longer leg)
3. Connect LED's negative leg (shorter leg) to GND (Pin 6)

#### LED 2 (Emergency Indicator) - Pin 33
```
RDK Pin 33 (GPIO 13) ──→ [220Ω Resistor] ──→ LED (+) ──→ LED (-) ──→ GND (Pin 9)
```

**Steps:**
1. Connect Pin 33 to one end of a 220Ω resistor
2. Connect the other end of resistor to LED's positive leg (longer leg)
3. Connect LED's negative leg (shorter leg) to GND (Pin 9)

#### Button 1 (Call 999) - Pin 11
```
3.3V (Pin 1) ──→ Button Terminal 1 ──→ Button Terminal 2 ──→ RDK Pin 11 (GPIO 17)
                                            └──→ [220Ω] ──→ GND (Pin 14)
```

**Steps:**
1. Connect Pin 1 (3.3V) to one terminal of Button 1
2. Connect the other terminal of Button 1 to Pin 11
3. Connect Pin 11 to one end of 220Ω resistor (pull-down)
4. Connect the other end of resistor to GND (Pin 14)

#### Button 2 (Cancel) - Pin 13
```
3.3V (Pin 1) ──→ Button Terminal 1 ──→ Button Terminal 2 ──→ RDK Pin 13 (GPIO 27)
                                            └──→ [220Ω] ──→ GND (Pin 20)
```

**Steps:**
1. Connect Pin 1 (3.3V) to one terminal of Button 2
2. Connect the other terminal of Button 2 to Pin 13
3. Connect Pin 13 to one end of 220Ω resistor (pull-down)
4. Connect the other end of resistor to GND (Pin 20)



### LED Behavior

#### LED 1 (Fall Indicator)
- **OFF**: Normal operation, no fall detected
- **ON**: Fall detected

#### LED 2 (Emergency Indicator)
- **OFF**: Normal operation
- **FLASHING**: Emergency countdown active (10 seconds) - Press Button 2 to cancel!
- **SOLID**: Emergency call activated (calling 999)

### Button Functions

#### Button 1 (Manual Emergency)
- **Press**: Immediately trigger emergency call
- **Result**: LED 1 & LED 2 goes SOLID (no flashing), calls 999 directly

#### Button 2 (Cancel)
- **During countdown (LED2 flashing)**: Cancel emergency, both LEDs turn OFF
- **During active call (LED2 solid)**: Stop emergency call, both LEDs turn OFF
- **Otherwise**: Indicate system is working or not (when program start runing --> Turn off)

### System Scenarios

#### Scenario 1: Fall with Breathing
1. **Fall detected** → LED 1 turns **ON**
2. System detect breath → Is breathing → Back to fall detect mode
3. System monitors fall duration (1 minutes) 
4. **After 1 minutes** → LED 2 **FLASHING** for 10-sec 
5. User not pressing Button 2 → Emergency mode (LED 2 **SOLID** )
6. User pressing Button 2 → Back to normal (LED 1 & LED 2 **OFF** )

#### Scenario 2: Fall WITHOUT Breathing
1. **Fall detected** → LED 1 turns **ON**
2. System detect breath → **NOT** breathing → Emergency mode (LED 2 **SOLID** )

#### Scenario 3: Manual Emergency
1. **User presses Button 1** → LED 1 AND LED 2 **SOLID** immediately (no countdown)
2. Calling 999 directly
3. **Press Button 2** → LED 1 & LED 2 **OFF**, emergency cancelled



### Troubleshooting Hardware

#### LEDs Not Lighting
- **Check polarity**: Long leg (+) to resistor, short leg (-) to GND
- **Check resistor**: Use 220-330Ω, not too high (1kΩ+)
- **Test LED directly**: Connect LED to 3.3V via resistor to verify it works
- **Check GPIO pin**: Run test script to verify GPIO output

#### Buttons Not Working
- **Check connections**: Ensure button is pressed to close circuit
- **Check pull-down resistor**: Must have 10kΩ to GND
- **Test button**: Use multimeter in continuity mode
- **Check bounce time**: Ensure proper debouncing in config.yaml

#### System Not Detecting Button Press
```bash
# Check GPIO states
python3 -c "import Hobot.GPIO as GPIO; GPIO.setmode(GPIO.BOARD); GPIO.setup(11, GPIO.IN); print('Button 1:', GPIO.input(11))"
```

### Safety Notes

⚠️ **Important:**
- Never connect LEDs without resistors (will damage LED or GPIO)
- Use 3.3V power, NOT 5V (RDK X5 GPIO is 3.3V)
- Double-check polarity before powering on
- Use pull-down resistors for buttons to prevent floating inputs
- Test components individually before final assembly

---

## 🏗️ System Architecture

### Hardware Components
- **RDK Device**: RDK X5 (Horizon Robotics Development Kit)
- **Camera**: USB webcam or CSI camera (continuous 2-second capture)
- **2 Buttons**:
  - Button 1: GPIO 11 - Call 999 (emergency call)
  - Button 2: GPIO 13 - Stop calling 999 (cancel emergency)
- **2 LEDs**:
  - LED 1: GPIO 31 - Fall detection indicator
  - LED 2: GPIO 33 - Emergency status (flashing/solid)

### Software Components
```
Camera → Capture (every 2s) → Database
          ↓
    YOLOv8 Detection → Fall? → Yes → Emergency Controller → Call 999
          ↓                             ↓
         No → Mark Normal         Breathing Check → LED Flash
                                        ↓
                                   Button 2 Cancel
```

### Data Flow

#### Integrated Fall + Breathing Detection Flow
1. **Camera captures** image every 2 seconds
2. Image saved to database as "normal"
3. **YOLOv8 analyzes** image for falls
4. If **fall detected**:
   - Database updated to category="fall"
   - **LED 1 turns ON**
   - System monitors fall duration (2 minutes)
5. If fall persists for **2+ minutes**:
   - **Breathing check** automatically triggered (12 seconds)
   - System captures video and analyzes chest movement
   - **If breathing detected**: 
     - LED 1 turns **OFF** (false alarm)
     - Return to normal monitoring
   - **If NO breathing detected**:
     - **LED 2 starts FLASHING** (10-second countdown)
     - Press **Button 2** to cancel
     - If not cancelled: **LED 2 goes SOLID** → Calling 999
6. During emergency:
   - Press **Button 2** to stop call → Both LEDs **OFF**

#### Manual Emergency Flow
1. User presses **Button 1** (emergency button)
2. **LED 2 goes SOLID immediately** (no countdown, bypasses all checks)
3. Calling 999 directly
4. Press **Button 2** to cancel → LED 2 **OFF**

---

## 🚀 Features

### Core Functionality
1. **Continuous Photo Capture**: Camera captures photos every 2 seconds automatically
2. **Fall Detection**: YOLO AI model analyzes each photo for falls
3. **Breathing Analysis**: SIFT algorithm checks for chest movement
4. **Emergency Response**: Manual 999 call via Button 1, cancel via Button 2
5. **Automatic Cleanup**: Old photos deleted automatically to prevent storage full
6. **Web Gallery**: Browse all captured images via WiFi

### Smart Alert System
- **LED 1** (Fall Indicator):
  - ON: Fall detected
  - OFF: Normal operation
- **LED 2** (Emergency Status):
  - FLASHING: Emergency call pending (10s countdown)
  - SOLID: Emergency call activated
  - OFF: Normal operation

### Button Controls
- **Button 1**: Call 999 immediately (triggers emergency)
- **Button 2**: Stop/cancel calling 999 (during countdown or active call)

---

## 📋 Requirements

### Hardware Requirements
- RDK X5 Development Kit (Horizon Robotics)
- Camera Module (MIPI CSI camera or USB webcam)
- 2× Push buttons
- 2× LEDs (any color)
- Resistors (220Ω for LEDs, 10kΩ for buttons)
- Jumper wires
- Power supply (5V 3A minimum)
- SD Card (32GB minimum, Class 10)

### Software Requirements
- Ubuntu 20.04/22.04 (64-bit) for RDK X5
- Python 3.9 or higher
- 20GB free storage space
- Internet connection (for initial setup)

---

## 📦 Installation

### 1. Prepare RDK X5
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y python3-pip python3-venv git \
    libopencv-dev python3-opencv libatlas-base-dev \
    hostapd dnsmasq
```

### 2. Clone Repository
```bash
cd ~
git clone https://github.com/yourusername/elderly-fall-detection.git
cd elderly-fall-detection
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Hardware Setup
Connect components to GPIO pins:

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| Button 1  | GPIO 17  | Pin 11       |
| Button 2  | GPIO 27  | Pin 13       |
| LED 1     | GPIO 22  | Pin 31       |
| LED 2     | GPIO 23  | Pin 33       |
| Camera    | CSI Port | Camera Port  |

*Use appropriate resistors: 220Ω for LEDs, 10kΩ pull-down for buttons*

### 6. Configure System
```bash
# Edit configuration file
nano config/config.yaml

# Set WiFi AP credentials
nano config/wifi_ap.conf

# Configure camera settings
nano config/camera_settings.json
```

### 7. Setup WiFi Access Point
```bash
# Run setup script
sudo bash scripts/setup_wifi_ap.sh

# Restart networking
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

### 8. Initialize Database
```bash
python src/database.py --init
```

### 9. Load AI Model
```bash
# Place your trained model in models/
cp /path/to/your/model.pt models/fall_detection.pt
```

---

## 🎮 Usage

### Starting the System

#### Manual Start
```bash
cd ~/elderly-fall-detection
source venv/bin/activate
python src/main.py
```

#### Auto-start on Boot
```bash
# Enable startup script
sudo bash scripts/setup_autostart.sh

# Reboot to test
sudo reboot
```

### Accessing the Web Interface

1. **Connect to WiFi**:
   - SSID: `ElderlyMonitor-RDK`
   - Password: (from `config/wifi_ap.conf`)

2. **Open Browser**:
   - Navigate to: `http://elderlysystem.local`
   - Or use IP: `http://192.168.4.1`

3. **View Gallery**:
   - Browse captured images
   - Filter by category (normal, fall detected, emergency)
   - Download individual or bulk images

### Operating the System

#### Normal Monitoring Mode
- Camera captures photos every 2 seconds
- Each photo analyzed by AI automatically
- Falls detected in real-time
- Photos stored with sequential numbering
- Old photos cleaned up automatically
- LED 1 remains off

#### Manual Emergency Call
1. Press **Button 1** to call 999
2. LED 2 starts flashing (10-second countdown)
3. Press **Button 2** to cancel if false alarm
4. If not cancelled: LED 2 solid, emergency call made

#### Fall Detected Scenario
1. **Fall Detected**:
   - LED 1 turns ON
   - Image captured and saved
   - Breathing analysis starts

2. **Breathing Check** (10-15 seconds):
   - SIFT analyzes chest movement
   - If breathing detected: LED 1 OFF, return to monitoring
   - If no breathing: Proceed to emergency

3. **Emergency Mode**:
   - LED 2 starts FLASHING
   - 10-second countdown begins
   - User can press **Button 2** to cancel
   - If not cancelled: LED 2 goes SOLID, emergency call triggered

4. **Cancelling False Alarm**:
   - Press **Button 2** during countdown
   - LED 2 turns OFF
   - System returns to monitoring

---

## 🌐 Web Interface Features

### Gallery Page
- **Timeline View**: All captured images in chronological order
- **Filters**: 
  - All images
  - Fall detected only
  - Emergency events only
  - Manual captures only
- **Image Details**: Timestamp, category, AI confidence
- **Download Options**: Individual or bulk ZIP download

### Status Dashboard
- Current system state
- Fall detection status
- Emergency alert status
- Recent events log
- System health metrics

### API Endpoints
- `GET /api/images` - List all images (JSON)
- `GET /api/download_all` - Download all images as ZIP
- `GET /api/status` - Current system status
- `GET /api/events` - Recent events log
- `GET /stream` - Live camera feed (optional)

---

## 📊 Image Transfer Methods

### Method 1: Web Interface (Recommended)
1. Connect to RDK WiFi
2. Open `http://elderlysystem.local`
3. Click "Download All Images" button
4. ZIP file downloads to your computer

### Method 2: SCP/SFTP
```bash
# From your computer
scp -r pi@192.168.4.1:~/elderly-fall-detection/data/images/ ./downloaded_images/
```

### Method 3: SMB Share (Windows)
1. Access `\\192.168.4.1\elderly-monitor`
2. Copy images folder to your computer

---

## 🔧 Troubleshooting

### Problem: Camera Not Working

**Error**: `ERROR: Failed to open camera!`

**Solutions**:
```bash
# 1. Check if camera is connected
ls /dev/video*

# 2. Check camera permissions
sudo chmod 666 /dev/video0

# 3. Test camera with simple capture
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed'); cap.release()"

# 4. Try different video device numbers
# Edit src/camera_service.py and change the camera index
```

---

### Problem: Web Interface Not Loading

**Error**: Cannot access http://localhost:5000

**Solutions**:
```bash
# 1. Check if Flask is running
ps aux | grep "webapp/app.py"

# 2. Check Flask logs
tail -50 data/logs/system.log | grep Flask

# 3. Try different port
# Edit webapp/app.py, change port to 5001

# 4. Check firewall
sudo ufw allow 5000
```

---

### Problem: Images Not Appearing in Gallery

**Error**: Gallery shows "No Images" even though system is running

**Solutions**:
```bash
# 1. Check database has images
python3 -c "from src.database import Database; db = Database('data/database.db'); print(f'Images: {db.get_image_count()}')"

# 2. Check image files exist
ls -lh data/images/ | tail -10

# 3. Clear browser cache and refresh

# 4. Check API endpoint directly
curl http://localhost:5000/api/images?limit=5
```

---

### Problem: Falls Not Being Detected

**Error**: Camera sees fall image but no detection

**Solutions**:
```bash
# 1. Verify YOLOv8 model is loaded
grep "YOLOv8" data/logs/system.log

# 2. Test fall detector directly
python3 test_fall_batch.py

# 3. Check if detector is in MOCK mode
grep "MOCK" data/logs/system.log

# 4. Restart system
pkill -f python; sleep 2; ./scripts/run.sh
```

---

### Problem: Auto-Refresh Not Working

**Error**: New images don't appear automatically

**Solutions**:
1. Click "Auto-Refresh ON" button (should be green)
2. Check browser console for JavaScript errors (F12)
3. Refresh page manually (Ctrl+R)
4. Clear browser cache

---

### Problem: System Crashes or Freezes

**Solutions**:
```bash
# 1. Check system resources
htop  # Press 'q' to quit

# 2. Check disk space
df -h

# 3. Check memory usage
free -h

# 4. Review error logs
tail -100 data/logs/system.log | grep -i error

# 5. Restart system
sudo reboot
```

---

### Problem: Storage Full

**Error**: `No space left on device`

**Solutions**:
```bash
# 1. Check storage usage
du -sh data/images/
df -h

# 2. Delete old images manually
cd data/images
rm $(ls | head -1000)  # Delete oldest 1000 images

# 3. Reduce image quality
# Edit config/config.yaml, set image_quality: 70

# 4. Enable auto-cleanup
# Check config/config.yaml storage.max_images setting
```

---

### Problem: Virtual Environment Issues

**Error**: `command not found: pip` or package import errors

**Solutions**:
```bash
# 1. Ensure virtual environment is activated
source venv/bin/activate
# Should see (venv) in prompt

# 2. Reinstall virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Check Python version
python3 --version  # Should be 3.10+
```

---

## 💡 Tips and Best Practices

### Daily Operation
1. **Start system in the morning**: `./scripts/run.sh`
2. **Check web interface**: Verify images are being captured
3. **Monitor storage**: Keep below 80% capacity
4. **Stop system at night**: `Ctrl+C` or `pkill -f python`

### Performance Optimization
- **Reduce image quality** if storage is limited (config.yaml)
- **Increase capture interval** to 3-4 seconds for slower systems
- **Limit images per page** to 20 for faster loading
- **Enable auto-cleanup** in config to delete old images

### Security
- **Change default WiFi password** in config/wifi_ap.conf
- **Enable authentication** for web interface (optional)
- **Keep system updated**: `sudo apt update && sudo apt upgrade`
- **Backup database** regularly: `cp data/database.db backup/`

### Maintenance
```bash
# Weekly: Check log file size
ls -lh data/logs/system.log

# Monthly: Clean up old logs
> data/logs/system.log  # Clear log file

# Monthly: Backup important fall images
python3 -c "from src.database import Database; db = Database('data/database.db'); falls = db.get_images(category='fall'); print(f'Backup {len(falls)} fall images')"
```

---

## 📖 Additional Documentation

- **ARCHITECTURE.md**: Detailed system design and component interaction
- **IMPLEMENTATION_GUIDE.md**: Step-by-step development guide
- **FALL_DETECTION_MODEL_GUIDE.md**: How YOLOv8 pose detection works
- **CAMERA_WEB_TEST_GUIDE.md**: Camera integration testing
- **RDK_SETUP.md**: RDK X5 hardware setup instructions

---

## 🎓 Common Questions

### Q: How often does the camera take photos?
**A**: Every 2 seconds by default (configurable in config.yaml)

### Q: How long are images kept?
**A**: Until storage limit is reached, then oldest images are deleted automatically

### Q: Can I access the system from my phone?
**A**: Yes! Connect to the RDK's WiFi and open http://192.168.50.8:5000

### Q: What happens if I press Button 1?
**A**: Emergency call to 999 is triggered immediately (simulated in current version)

### Q: Can I change the fall detection sensitivity?
**A**: Yes, edit `config.yaml` and adjust `confidence_threshold` (0.0-1.0)

### Q: How do I know if a fall was detected?
**A**: Check web interface for images with red "FALL" badge, or check logs

### Q: Can the system run 24/7?
**A**: Yes, but consider storage capacity and periodic maintenance

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

---

## 📄 License

This project is for educational purposes (ISDN3000C Course Project).

---

## 👥 Authors

- **Project Team**: ISDN3000C Fall 2025
- **GitHub**: https://github.com/Zhangxinyue2002/ISDN3000C_Project

---

## 🙏 Acknowledgments

- Ultralytics for YOLOv8
- OpenCV community
- Flask framework
- RDK X5 development team

---

**Last Updated**: December 11, 2025  
**Version**: 2.0 - Production Ready

storage:
  max_images: 1000
  auto_cleanup: true
  image_quality: 85

network:
  wifi_ssid: "ElderlyMonitor-RDK"
  wifi_password: "elderly2024"
  mdns_name: "elderlysystem"
```

### GPIO Pin Configuration
Edit in `src/gpio_handler.py`:
```python
BUTTON_1_PIN = 17  # Manual capture
BUTTON_2_PIN = 27  # Emergency cancel
LED_1_PIN = 22     # Fall indicator
LED_2_PIN = 23     # Emergency status
```

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Test Individual Components
```bash
# Test camera (use appropriate camera interface for RDK X5)
python src/camera_service.py --test

# Test fall detection
python src/fall_detector.py --test --image test_images/fall.jpg

# Test breathing detection
python src/breathing_detector.py --test --video test_videos/breathing.mp4

# Test GPIO
python src/gpio_handler.py --test
```

### Integration Test
```bash
python tests/test_integration.py
```

---

## 🤝 Team Collaboration

### For Teammate Testing Fall Detection Models

Your teammate should provide:
1. **Model File**: `fall_detection.pt` (PyTorch) or `fall_detection.onnx`
2. **Config File**: `model_config.yaml` with:
   ```yaml
   model_type: "yolo"
   input_size: [640, 640]
   classes: ["standing", "sitting", "fallen"]
   preprocessing:
     normalize: true
     mean: [0.485, 0.456, 0.406]
     std: [0.229, 0.224, 0.225]
   ```
3. **Performance Metrics**: Accuracy, FPS, false positive rate

### Integration Steps
1. Place model in `models/` directory
2. Update `config/config.yaml` with model path
3. Test with sample images: `python src/fall_detector.py --test`
4. Validate performance on RDK hardware
5. Adjust confidence thresholds if needed

### Sharing Test Data
- Provide sample images from RDK camera to teammate
- Include various scenarios: standing, sitting, falling, lying
- Different lighting conditions and angles

---

## 📁 Project Structure

```
elderly-fall-detection/
├── README.md                   # This file
├── ARCHITECTURE.md             # Detailed architecture documentation
├── IMPLEMENTATION_GUIDE.md     # Step-by-step implementation guide
├── requirements.txt            # Python dependencies
├── config/                     # Configuration files
├── src/                        # Source code
│   ├── main.py                # Entry point
│   ├── camera_service.py      # Camera operations
│   ├── fall_detector.py       # Fall detection AI
│   ├── breathing_detector.py  # Breathing analysis
│   ├── emergency_controller.py # Emergency logic
│   ├── gpio_handler.py        # Hardware control
│   └── database.py            # Database operations
├── webapp/                     # Flask web application
│   ├── app.py                 # Flask app
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, images
├── models/                     # AI models
├── data/                       # Images and database
│   ├── images/                # Captured images
│   └── database.db            # SQLite database
├── tests/                      # Test files
└── scripts/                    # Setup and utility scripts
```

---

## 🐛 Troubleshooting

### Camera Not Working
```bash
# Check camera device
ls -l /dev/video*

# Test camera with v4l2
v4l2-ctl --list-devices

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error')"
```

### WiFi AP Not Starting
```bash
# Check hostapd status
sudo systemctl status hostapd

# Check logs
sudo journalctl -u hostapd -f

# Restart services
sudo systemctl restart hostapd dnsmasq
```

### Model Loading Errors
```bash
# Verify model file exists
ls -lh models/fall_detection.pt

# Check model compatibility
python -c "import torch; print(torch.__version__)"

# Test model loading
python src/fall_detector.py --validate-model
```

### GPIO Not Responding
```bash
# Check GPIO permissions
sudo usermod -aG gpio $USER

# Test GPIO
python -c "import RPi.GPIO as GPIO; print(GPIO.VERSION)"

# Run GPIO test
python src/gpio_handler.py --test
```

### Web Interface Not Accessible
```bash
# Check Flask is running
ps aux | grep python

# Check firewall
sudo ufw status

# Test locally
curl http://localhost:5000

# Check WiFi connection
iwconfig
```

---

## 🔒 Security Notes

- Change default WiFi password before deployment
- Enable HTTPS for web interface (production)
- Regularly update system and dependencies
- Implement user authentication for web access
- Configure automatic image cleanup
- Secure emergency contact information
- Regular backup of database

---

## 📝 Development Roadmap

### Phase 1: Core System (Current)
- [x] Hardware setup
- [ ] Camera capture service
- [ ] Fall detection integration
- [ ] Breathing detection (SIFT)
- [ ] Emergency controller
- [ ] Basic web interface

### Phase 2: Enhancement
- [ ] Advanced filtering (Black & White, Vintage)
- [ ] Real-time video streaming
- [ ] Mobile-responsive design
- [ ] Improved breathing algorithm
- [ ] Multi-person detection

### Phase 3: Production
- [ ] Actual emergency calling (Twilio)
- [ ] Cloud backup integration
- [ ] Remote monitoring access
- [ ] Analytics dashboard
- [ ] Mobile app development

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational purposes as part of ISDN3000C coursework.

---

## 👥 Team

- **Project Lead**: [Your Name]
- **AI/ML Developer**: [Teammate Name]
- **Hardware Integration**: [Your Name]
- **Web Development**: [Your Name]

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]
- Documentation: See `ARCHITECTURE.md` and `IMPLEMENTATION_GUIDE.md`

---

## 🙏 Acknowledgments

- Ultralytics YOLOv8 for object detection
- OpenCV for computer vision algorithms
- Flask community for web framework
- Horizon Robotics for RDK X5 platform

---

**Version**: 1.0  
**Last Updated**: November 23, 2025  
**Status**: In Development

---

## 📚 Additional Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Step-by-step implementation
- [API Documentation](docs/API.md) - Web API reference
- [Hardware Setup Guide](docs/HARDWARE.md) - Detailed wiring diagrams

---

Made with ❤️ for elderly care and safety
