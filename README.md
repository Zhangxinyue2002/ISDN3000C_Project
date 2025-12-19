# Elderly Fall Detection System

**Authors:** Selina & Amy (ISDN3000C Project Team)  
**Date:** December 2025  
**Version:** 1.0

A comprehensive real-time monitoring system for elderly care that combines computer vision, hardware controls, and web interface to detect falls, check breathing, and trigger emergency alerts automatically.

---

## 📋 Quick Links

- [Installation Guide](#-installation)
- [System Workflow](#-system-workflow)
- [Web Interface](#-web-interface)
- [Technical Details](TECHNICAL_EXPLANATION.md)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 System Overview

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

## 🏗️ System Architecture

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

## 👥 Authors

- **Selina** - System architecture, fall detection, web interface
- **Amy** - Breathing detection, emergency controller, hardware

**Course:** ISDN3000C  
**Institution:** [Your University]  
**Date:** December 2025

---

## 📧 Support

For detailed technical explanations and design decisions, see:
- [TECHNICAL_EXPLANATION.md](TECHNICAL_EXPLANATION.md) - Architecture and algorithms
- System logs: `data/logs/system.log`
- Configuration: `config/config.yaml`

---

**Last Updated:** December 18, 2025  
**Version:** 1.0.0
