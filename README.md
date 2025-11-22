# Elderly Fall Detection System

An AI-powered monitoring system that detects falls, monitors breathing, and provides emergency response capabilities for elderly care.

![System Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Platform](https://img.shields.io/badge/Platform-RDK%20X5-red)
![Python](https://img.shields.io/badge/Python-3.9+-blue)

---

## 🎯 Project Overview

This system uses a Raspberry Pi (RDK) with camera, AI models, and sensors to:
- ✅ **Detect falls** using YOLO-based computer vision
- ✅ **Monitor breathing** using SIFT motion detection
- ✅ **Trigger emergency calls** with manual override capability
- ✅ **Provide web gallery** for captured images with WiFi access point
- ✅ **Real-time alerts** using LEDs and buttons

---

## 🏗️ System Architecture

### Hardware Components
- **RDK Device**: RDK X5 (Horizon Robotics Development Kit)
- **Camera**: MIPI CSI camera or USB webcam (continuous capture mode)
- **2 Buttons**:
  - Button 1: Call 999 (emergency call)
  - Button 2: Stop calling 999 (cancel emergency)
- **2+ LEDs**:
  - LED 1: Fall detection indicator
  - LED 2: Emergency status (flashing/solid)
- **WiFi**: Built-in module for access point

### Software Stack
- **Operating System**: Ubuntu 20.04/22.04 (64-bit) for RDK X5
- **Programming Language**: Python 3.9+
- **AI Framework**: PyTorch/TensorFlow Lite, Ultralytics YOLOv8
- **Computer Vision**: OpenCV (SIFT)
- **Web Framework**: Flask + Flask-SocketIO
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap)
- **Networking**: hostapd, dnsmasq (WiFi AP + mDNS)

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
| LED 1     | GPIO 22  | Pin 15       |
| LED 2     | GPIO 23  | Pin 16       |
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

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)
```yaml
camera:
  resolution: [1280, 720]
  framerate: 30
  rotation: 0

fall_detection:
  model_path: "models/fall_detection.pt"
  confidence_threshold: 0.75
  check_interval: 0.1  # seconds

breathing_detection:
  analysis_duration: 12  # seconds
  sift_threshold: 0.3
  breathing_rate_range: [12, 20]  # breaths per minute

emergency:
  countdown_duration: 10  # seconds
  contact_number: "999"
  enable_call: false  # Set true for production

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
