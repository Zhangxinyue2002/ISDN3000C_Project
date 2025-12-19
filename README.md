# Elderly Fall Detection System

**Authors:** Selina & Amy (ISDN3000C Project Team)  
**Date:** December 2025  
**Version:** 1.0

A comprehensive real-time monitoring system for elderly care that combines computer vision, hardware controls, and web interface to detect falls, check breathing, and trigger emergency alerts automatically.

---

## 📋 Quick Links

- [Quick Start Guide](#-quick-start-guide)
- [Installation Guide](#-installation)
- [System Workflow](#-system-workflow)
- [Web Interface](#-web-interface)
- [Technical Details](TECHNICAL_EXPLANATION.md)
- [Troubleshooting](#-troubleshooting)

### 🔄 **NEW: Integrated Fall + Breathing Detection**
The system now performs automatic breathing checks after detecting a 1-minute fall, preventing false alarms before triggering emergency calls. See [INTEGRATED_SYSTEM_GUIDE.md](INTEGRATED_SYSTEM_GUIDE.md) for complete details.

---

## 🎯 System Overview

This system uses a Raspberry Pi (RDK) with camera, AI models, and sensors to:
- ✅ **Detect falls** using YOLOv8 pose detection
- ✅ **Monitor breathing** using SIFT motion detection (integrated verification)
- ✅ **Trigger emergency calls** with 10-second countdown and manual override
- ✅ **Provide web gallery** for captured images with WiFi access
- ✅ **Real-time alerts** using LEDs and buttons

This system provides 24/7 monitoring for elderly individuals, automatically detecting falls and checking breathing to prevent serious injuries or health emergencies.

### What It Does

1. **Continuous Monitoring**: Camera captures images every 2 seconds
2. **Fall Detection**: AI identifies when person has fallen
3. **Breathing Check**: Analyzes chest movement to detect breathing
4. **Emergency Response**: Automatic 999 call after 10-second countdown
5. **Manual Override**: Physical buttons for immediate emergency or cancellation

---

## ✨ Key Features

### 🤖 AI Detection
- **YOLOv8 Pose Estimation**: 17-point skeleton detection
- **SIFT Feature Tracking**: Chest movement analysis
- **FFT Signal Processing**: Breathing rate validation (6-30 BPM)

### 🔴 Hardware Controls
- **Button 1**: Manual emergency trigger
- **Button 2**: Cancel/reset system
- **LED 1**: Fall indicator (ON = fall detected)
- **LED 2**: Emergency status (FLASH = countdown, SOLID = calling 999)

### 🌐 Web Dashboard
- Real-time image gallery with filters
- Live event timeline (1-second refresh)
- Statistics tracking (images, falls, emergencies)

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
3.3V (Pin 17) ──→ Button Terminal 1 ──→ Button Terminal 2 ──→ RDK Pin 13 (GPIO 27)
                                            └──→ [220Ω] ──→ GND (Pin 20)
```

**Steps:**
1. Connect Pin 17 (3.3V) to one terminal of Button 2
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

## 🔄 System Architecture

```
Camera (2s) → Fall Detector (YOLO) → Breathing Detector (SIFT+FFT)
                     ↓                          ↓
              Emergency Controller ← GPIO Handler (Buttons/LEDs)
                     ↓
          Database ← Web Interface (Flask)
```

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
cd ~/Project/ISDN3000C_Project
./scripts/setup.sh

# 2. Start system
./scripts/run.sh

# 3. Access web interface
# Open browser: http://localhost:5000
```

---

## 🔧 Hardware Setup

### Required Components
- Raspberry Pi 4 or RDK X5
- USB Camera (720p minimum)
- 2× Push buttons
- 2× LEDs (red)
- 4× Resistors (2×220Ω for LEDs, 2×10kΩ for buttons)

### GPIO Connections (Physical Pin Numbers)
```
Button 1 → Pin 11 (GPIO17)
Button 2 → Pin 13 (GPIO27)
LED 1    → Pin 31 (GPIO6)
LED 2    → Pin 33 (PWM0)
```

See `WIRING_DIAGRAM.md` for circuit details.

---

## 🔄 System Workflow

### Normal Operation
```
1. Camera captures image every 2s
   ↓
2. Fall detector analyzes pose
   ├→ Normal: Continue monitoring
   └→ Fall detected: LED1 ON, check breathing
      ↓
3. Breathing detection (15s video)
   ├→ Breathing: Keep monitoring
   └→ No breathing: LED2 FLASH, start countdown
      ↓
4. 10-second countdown
   ├→ Button 2 pressed: Cancel (LEDs OFF)
   └→ Timeout: EMERGENCY (LED1+LED2 SOLID, call 999)
```

### Emergency Modes

**Auto Emergency** (Fall + No Breathing):
- LED2 flashes for 10 seconds (countdown)
- Press Button 2 to cancel
- If timeout: Both LEDs solid, call 999

**Manual Emergency** (Button 1):
- Both LEDs solid immediately (no countdown)
- System calls 999 right away

**Reset** (Button 2):
- Both LEDs turn OFF
- System returns to monitoring mode

---

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
camera:
  capture_interval: 2    # Seconds between captures

fall_detection:
  confidence_threshold: 0.75  # 0-1, lower = more sensitive

breathing_detection:
  capture_duration: 15   # Video length in seconds
  min_motion_amplitude: 1.7  # Pixels, lower = more sensitive

emergency:
  countdown_duration: 10  # Countdown seconds
  enable_actual_call: false  # true = real 999 calls
```

---

## 🌐 Web Interface

### Gallery Page (`/`)
- View all captured images
- Filter by category (All/Falls/Emergency/Normal)
- Sort by date
- Download as ZIP
- Auto-refresh every 1 second

### Status Page (`/status`)
- Recent events timeline (live updates)
- Hardware configuration
- System information

### API Endpoints
- `GET /api/images` - List images
- `GET /api/stats` - Get statistics
- `GET /api/events` - Event history
- `GET /api/status` - System status

---

## 📊 Database Structure

### Images Table
- `filename`, `filepath`, `timestamp`
- `category` (normal/fall/emergency)
- `fall_detected`, `emergency_triggered` (boolean)
- `confidence` (detection accuracy)

### Events Table
- `event_type` (fall_detected, emergency_triggered)
- `timestamp`, `image_id`
- `details` (description)

---

## 🐛 Troubleshooting

### Camera Not Working
```bash
# Check camera
ls /dev/video*

# Test camera
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### GPIO Errors
```bash
# Run with sudo (required)
sudo python3 src/main.py

# Or add to gpio group
sudo usermod -a -G gpio $USER
sudo reboot
```

### Web Interface Not Loading
```bash
# Check if running
ps aux | grep app.py

# Restart
pkill -f app.py
cd webapp && python3 app.py
```

### Low Detection Accuracy
1. Adjust `confidence_threshold` (lower = more sensitive)
2. Improve lighting
3. Position camera 1-2m from subject
4. Check logs: `tail -f data/logs/system.log`

---

## 📝 File Structure

```
ISDN3000C_Project/
├── config/
│   └── config.yaml          # System configuration
├── data/
│   ├── images/              # Captured images
│   ├── logs/                # System logs
│   └── database.db          # SQLite database
├── src/
│   ├── main.py              # Main system coordinator
│   ├── camera_service.py    # Camera capture
│   ├── fall_detector_enhanced.py  # YOLOv8 fall detection
│   ├── breathing_detector.py      # SIFT breathing analysis
│   ├── emergency_controller.py    # State machine
│   ├── gpio_handler.py      # Hardware control
│   └── database.py          # Data management
├── webapp/
│   ├── app.py               # Flask server
│   ├── templates/           # HTML pages
│   └── static/              # CSS/JS/images
├── scripts/
│   ├── run.sh               # Start system
│   └── setup.sh             # Installation
├── README.md                # This file
├── TECHNICAL_EXPLANATION.md # Detailed technical docs
└── requirements.txt         # Python dependencies
```

---

## 🎓 Educational Value

This project demonstrates:
- Real-time computer vision with deep learning
- Embedded systems with GPIO
- State machine design
- Full-stack web development
- Database management
- Hardware-software integration

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



## 📄 License

This project is for educational purposes (ISDN3000C Course Project).

---

## 👥 Authors

- **Selina** - System architecture, fall detection, web interface
- **Amy** - Breathing detection, emergency controller, hardware
- **Project Team**: Amy and Selina
- **GitHub**: https://github.com/Zhangxinyue2002/ISDN3000C_Project

**Course:** ISDN3000C  
**Date:** December 2025

---

## 📧 Support

For detailed technical explanations and design decisions, see:
- [TECHNICAL_EXPLANATION.md](TECHNICAL_EXPLANATION.md) - Architecture and algorithms
- System logs: `data/logs/system.log`
- Configuration: `config/config.yaml`

---

## 🙏 Acknowledgments

- Ultralytics for YOLOv8
- OpenCV community
- Flask framework
- RDK X5 development team

---

**Last Updated:** December 18, 2025  
**Version:** 1.0.0

Made with ❤️ for elderly care and safety
