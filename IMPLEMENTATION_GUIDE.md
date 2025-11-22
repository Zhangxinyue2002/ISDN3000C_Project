# Elderly Fall Detection System - Implementation Guide

**Step-by-Step Implementation Plan**

This document provides a comprehensive, sequential guide for implementing the elderly fall detection system. Follow these steps in order to build the complete system.

---

## Table of Contents
1. [Phase 0: Setup & Preparation](#phase-0-setup--preparation)
2. [Phase 1: Hardware Setup](#phase-1-hardware-setup)
3. [Phase 2: Basic Infrastructure](#phase-2-basic-infrastructure)
4. [Phase 3: Camera Service](#phase-3-camera-service)
5. [Phase 4: Fall Detection](#phase-4-fall-detection)
6. [Phase 5: Breathing Detection](#phase-5-breathing-detection)
7. [Phase 6: Emergency System](#phase-6-emergency-system)
8. [Phase 7: Web Interface](#phase-7-web-interface)
9. [Phase 8: WiFi Access Point](#phase-8-wifi-access-point)
10. [Phase 9: Integration & Testing](#phase-9-integration--testing)
11. [Phase 10: Deployment](#phase-10-deployment)

---

## Phase 0: Setup & Preparation

### Step 0.1: Hardware Checklist
Gather all required components:
- [ ] RDK X5 Development Kit (Horizon Robotics)
- [ ] SD Card or eMMC storage (32GB+)
- [ ] Power Supply (12V DC, as per RDK X5 specs), as per RDK X5 specs)
- [ ] Camera Module (MIPI CSI camera or USB webcam)
- [ ] 2× Push buttons
- [ ] 2× LEDs (any color, recommend red and green)
- [ ] 2× 220Ω resistors (for LEDs)
- [ ] 2× 10kΩ resistors (for buttons, pull-down)
- [ ] Breadboard
- [ ] Jumper wires (Male-to-Female)
- [ ] Computer for development
- [ ] HDMI cable & monitor (for initial setup)
- [ ] Keyboard & mouse (for initial setup)

### Step 0.2: Software Preparation
**On your computer:**
1. Download Ubuntu 20.04/22.04 image for RDK X5 from Horizon Robotics
2. Prepare SD card or eMMC storage
3. Flash OS to storage:
   - Use balenaEtcher or dd command
   - Flash the RDK X5 Ubuntu image
   - Safely eject storage
4. Enable SSH (optional but recommended):
   - Create empty file named `ssh` in boot partition
5. Configure WiFi (optional):
   - Create `wpa_supplicant.conf` in boot partition

### Step 0.3: First Boot
1. Insert SD card or use eMMC on RDK X5
2. Connect monitor, keyboard, mouse
3. Connect camera module to MIPI CSI port
4. Power on RDK X5
5. Complete initial setup:
   - Set country, language, timezone
   - Change default password
   - Update software (may take 10-20 minutes)
6. Configure interfaces:
   ```bash
   # Enable camera and other interfaces as needed
   # Check RDK X5 documentation for specific GPIO/camera setup
   ```
7. Reboot:
   ```bash
   sudo reboot
   ```

### Step 0.4: System Update
```bash
# Update package list
sudo apt-get update

# Upgrade installed packages
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y git vim nano curl wget build-essential
```

### Step 0.5: Install Python Dependencies
```bash
# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Install system libraries for OpenCV
sudo apt-get install -y libopencv-dev python3-opencv \
    libatlas-base-dev libhdf5-dev libhdf5-serial-dev \
    libjasper-dev libqtgui4 libqt4-test

# Install additional libraries
sudo apt-get install -y libavcodec-dev libavformat-dev \
    libswscale-dev libv4l-dev libxvidcore-dev libx264-dev
```

---

## Phase 1: Hardware Setup

### Step 1.1: GPIO Pin Planning
| Component | GPIO Pin | Physical Pin | Notes |
|-----------|----------|--------------|-------|
| Button 1 (Call 999) | GPIO 17 | Pin 11 | Pull-down with 10kΩ |
| Button 2 (Stop Call) | GPIO 27 | Pin 13 | Pull-down with 10kΩ |
| LED 1 (Fall) | GPIO 22 | Pin 15 | 220Ω resistor |
| LED 2 (Emergency) | GPIO 23 | Pin 16 | 220Ω resistor |
| Ground | GND | Pin 6, 9, 14, 20 | Multiple available |
| 3.3V Power | 3.3V | Pin 1, 17 | For button pull-up (if used) |

### Step 1.2: Wiring Diagram

**Button Circuit (Repeat for both buttons):**
```
GPIO Pin -----> Button -----> GND
         |
         +-----> 10kΩ Resistor -----> GND (Pull-down)
```

**LED Circuit (Repeat for both LEDs):**
```
GPIO Pin -----> 220Ω Resistor -----> LED Anode (+)
                                      |
                                    LED Cathode (-) -----> GND
```

### Step 1.3: Physical Wiring
1. **Power off RDK X5 completely**
2. **Connect Button 1 (Call 999):**
   - One leg to GPIO 17 (Pin 11)
   - Other leg to GND (Pin 9)
   - 10kΩ resistor from GPIO 17 to GND (pull-down)
3. **Connect Button 2 (Stop Call):**
   - One leg to GPIO 27 (Pin 13)
   - Other leg to GND (Pin 14)
   - 10kΩ resistor from GPIO 27 to GND
4. **Connect LED 1 (Fall Indicator):**
   - 220Ω resistor from GPIO 22 (Pin 15) to LED anode (+, longer leg)
   - LED cathode (-, shorter leg) to GND (Pin 20)
5. **Connect LED 2 (Emergency Status):**
   - 220Ω resistor from GPIO 23 (Pin 16) to LED anode (+)
   - LED cathode (-) to GND (Pin 6)
6. **Connect Camera:**
   - Align ribbon cable correctly (blue side toward Ethernet port)
   - Insert into CSI port firmly
   - Close the clasp

### Step 1.4: Test Hardware
```bash
# Power on RDK X5

# Test camera
# For MIPI CSI camera:
v4l2-ctl --list-devices
v4l2-ctl --device=/dev/video0 --all

# Test with Python OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('Camera OK' if ret else 'Error'); cap.release()"

# Install GPIO library
pip3 install RPi.GPIO gpiozero

# Test GPIO (create test script)
cat > test_gpio.py << 'EOF'
from gpiozero import LED, Button
from time import sleep

# Define components
button1 = Button(17)
button2 = Button(27)
led1 = LED(22)
led2 = LED(23)

print("Testing LEDs...")
led1.on()
sleep(1)
led1.off()
led2.on()
sleep(1)
led2.off()

print("Test buttons (press Ctrl+C to exit)...")
print("Press Button 1 to light LED 1")
print("Press Button 2 to light LED 2")

try:
    while True:
        if button1.is_pressed:
            led1.on()
            print("Button 1 pressed!")
        else:
            led1.off()
        
        if button2.is_pressed:
            led2.on()
            print("Button 2 pressed!")
        else:
            led2.off()
        
        sleep(0.1)
except KeyboardInterrupt:
    print("\nTest complete!")
    led1.off()
    led2.off()
EOF

python3 test_gpio.py
```

---

## Phase 2: Basic Infrastructure

### Step 2.1: Create Project Structure
```bash
# Navigate to home directory
cd ~

# Create project directory
mkdir -p elderly-fall-detection
cd elderly-fall-detection

# Create directory structure
mkdir -p config src webapp/templates webapp/static/css webapp/static/js webapp/static/images webapp/api models data/images data/logs tests scripts

# Create __init__.py files
touch src/__init__.py webapp/__init__.py webapp/api/__init__.py

# Verify structure
tree -L 2
```

### Step 2.2: Create Configuration Files

**Create `config/config.yaml`:**
```bash
cat > config/config.yaml << 'EOF'
# System Configuration

camera:
  resolution: [1280, 720]
  framerate: 30
  rotation: 0
  flip_horizontal: false
  flip_vertical: false

gpio:
  button_capture: 17
  button_emergency: 27
  led_fall: 22
  led_emergency: 23
  bounce_time: 200  # milliseconds

fall_detection:
  model_path: "models/fall_detection.pt"
  confidence_threshold: 0.75
  check_interval: 0.1  # seconds between frames
  enabled: true

breathing_detection:
  analysis_duration: 12  # seconds
  sift_threshold: 0.3
  breathing_rate_range: [12, 20]  # breaths per minute
  min_motion_amplitude: 2.0  # pixels
  enabled: true

emergency:
  countdown_duration: 10  # seconds
  contact_number: "999"
  enable_actual_call: false  # Set true for production
  notification_methods:
    - "log"
    - "web_alert"
    # - "sms"  # Uncomment when configured
    # - "call"  # Uncomment when configured

storage:
  images_directory: "data/images"
  database_path: "data/database.db"
  max_images: 1000
  auto_cleanup: true
  cleanup_days: 30
  image_quality: 85
  image_format: "jpg"

network:
  wifi_ssid: "ElderlyMonitor-RDK"
  wifi_password: "elderly2024"
  wifi_channel: 6
  mdns_name: "elderlysystem"
  flask_host: "0.0.0.0"
  flask_port: 5000
  flask_debug: false

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  log_file: "data/logs/system.log"
  max_log_size: 10485760  # 10 MB
  backup_count: 5
EOF
```

**Create `config/camera_settings.json`:**
```bash
cat > config/camera_settings.json << 'EOF'
{
  "camera_type": "picamera2",
  "resolution": [1280, 720],
  "framerate": 30,
  "iso": 400,
  "exposure_mode": "auto",
  "awb_mode": "auto",
  "brightness": 50,
  "contrast": 0,
  "saturation": 0,
  "sharpness": 0
}
EOF
```

### Step 2.3: Create Requirements File
```bash
cat > requirements.txt << 'EOF'
# Core dependencies
Flask==3.0.0
Flask-SocketIO==5.3.5
Flask-CORS==4.0.0

# Database
SQLAlchemy==2.0.23

# Computer Vision & AI
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.1.0
torch==2.1.1
torchvision==0.16.1
ultralytics==8.0.227

# GPIO
RPi.GPIO==0.7.1
gpiozero==2.0.1

# Networking
python-socketio==5.10.0
requests==2.31.0

# Configuration
PyYAML==6.0.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Camera (Raspberry Pi specific)
picamera2==0.3.16
EOF
```

### Step 2.4: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Note: Some packages may fail on RDK, install alternatives:
# If torch fails, use:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# If picamera2 fails, install system package:
# sudo apt-get install python3-picamera2
```

### Step 2.5: Create Database Schema
**Create `src/database.py`:**
```python
# We'll implement this in the next step
# For now, create placeholder
cat > src/database.py << 'EOF'
"""Database operations for elderly fall detection system."""
import sqlite3
from datetime import datetime
import yaml

# Implementation will be added in Phase 3
EOF
```

---

## Phase 3: Camera Service

### Step 3.1: Implement Camera Service
**Create `src/camera_service.py`:**
This will be implemented when you're ready to code. For now, here's the structure:

**Required Functionality:**
- Initialize camera with settings from config (use OpenCV VideoCapture for RDK X5)
- **Continuous capture mode**: Capture photos every N seconds (configurable)
- Save image with sequential naming (1.jpg, 2.jpg, etc.)
- Get current frame for AI processing
- **Automatic cleanup**: Delete old photos to prevent storage full
- Track storage usage and trigger cleanup
- Preserve important images (falls, emergencies)
- Handle camera errors gracefully

**Key Functions:**
```python
class CameraService:
    def __init__(self, config_path):
        """Initialize camera with configuration."""
        pass
    
    def start_continuous_capture(self):
        """Start continuous photo capture mode."""
        pass
    
    def stop_continuous_capture(self):
        """Stop continuous capture."""
        pass
    
    def capture_and_save(self):
        """Capture one photo and save with sequential number."""
        pass
    
    def get_current_frame(self):
        """Get current frame as numpy array."""
        pass
    
    def save_image(self, image, category='normal'):
        """Save image with sequential numbering."""
        pass
    
    def cleanup_old_images(self):
        """Delete old images to free storage space."""
        pass
    
    def get_storage_info(self):
        """Get current storage usage statistics."""
        pass
```

### Step 3.2: Implement Database
**Create complete `src/database.py`:**

**Database Schema:**
- `images` table: id, filename, filepath, timestamp, category, fall_detected, breathing_detected, emergency_triggered, confidence
- `events` table: id, event_type, timestamp, image_id, details

**Key Functions:**
- `init_database()`: Create tables
- `add_image()`: Insert image record
- `add_event()`: Log system event
- `get_images()`: Query images with filters
- `get_recent_events()`: Get event history
- `cleanup_old_images()`: Remove old records

### Step 3.3: Implement GPIO Handler
**Create `src/gpio_handler.py`:**

**Required Functionality:**
- Initialize GPIO pins from config
- Setup button callbacks
- LED control methods (on, off, blink)
- Cleanup on shutdown

**Key Functions:**
```python
class GPIOHandler:
    def __init__(self, config):
        """Initialize GPIO pins."""
        pass
    
    def setup_buttons(self, call_999_callback, stop_call_callback):
        """Setup button event handlers."""
        pass
    
    def led_fall_on(self):
        """Turn on fall detection LED."""
        pass
    
    def led_fall_off(self):
        """Turn off fall detection LED."""
        pass
    
    def led_emergency_flash(self):
        """Flash emergency LED."""
        pass
    
    def led_emergency_solid(self):
        """Solid emergency LED."""
        pass
    
    def led_emergency_off(self):
        """Turn off emergency LED."""
        pass
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        pass
```

---

## Phase 4: Fall Detection

### Step 4.1: Model Integration Interface
**Create `src/fall_detector.py`:**

This is where your teammate's model will be integrated.

**Requirements for Teammate:**
1. **Model File Format**: PyTorch (.pt) or ONNX (.onnx)
2. **Input Specification**: 
   - Image size: Configurable (default 640×640)
   - Format: RGB numpy array or PIL Image
   - Preprocessing: Normalization values
3. **Output Specification**:
   - Class labels: ['standing', 'sitting', 'fallen']
   - Confidence score: 0.0 to 1.0
   - Bounding box: [x1, y1, x2, y2] for person detection
4. **Performance**: 
   - Inference time < 100ms on Raspberry Pi 4
   - Accuracy > 90%

**Integration Interface:**
```python
class FallDetector:
    def __init__(self, model_path, config):
        """Load YOLO model from file."""
        # Load model
        # Configure inference parameters
        pass
    
    def detect(self, image):
        """
        Detect fall in image.
        
        Args:
            image: numpy array (H, W, 3) RGB
        
        Returns:
            dict: {
                'fall_detected': bool,
                'confidence': float,
                'class': str ('standing'|'sitting'|'fallen'),
                'bbox': [x1, y1, x2, y2],
                'person_detected': bool
            }
        """
        pass
    
    def preprocess(self, image):
        """Preprocess image for model input."""
        pass
    
    def postprocess(self, output):
        """Process model output to detection result."""
        pass
```

### Step 4.2: Model Testing Framework
**Create `tests/test_fall_detection.py`:**

**Test Cases:**
- Load model successfully
- Process single image
- Detect standing person
- Detect sitting person
- Detect fallen person
- Handle no person in frame
- Measure inference time
- Test with various image sizes
- Test error handling

### Step 4.3: Collecting Training Data for Teammate
**Create script to capture test images:**
```bash
cat > scripts/capture_training_data.sh << 'EOF'
#!/bin/bash
# Script to capture images for training

echo "Capturing training images..."
mkdir -p training_data/{standing,sitting,fallen}

echo "Capture STANDING positions (press Enter between captures, 'q' to finish)"
counter=1
while true; do
    read -p "Press Enter to capture standing $counter (or 'q' to quit): " input
    if [ "$input" = "q" ]; then break; fi
    python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); cv2.imwrite('training_data/standing/standing_$counter.jpg',frame) if ret else None; cap.release()"
    echo "Captured standing_$counter.jpg"
    ((counter++))
done

echo "Capture SITTING positions"
counter=1
while true; do
    read -p "Press Enter to capture sitting $counter (or 'q' to quit): " input
    if [ "$input" = "q" ]; then break; fi
    python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); cv2.imwrite('training_data/sitting/sitting_$counter.jpg',frame) if ret else None; cap.release()"
    echo "Captured sitting_$counter.jpg"
    ((counter++))
done

echo "Capture FALLEN positions"
counter=1
while true; do
    read -p "Press Enter to capture fallen $counter (or 'q' to quit): " input
    if [ "$input" = "q" ]; then break; fi
    python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); cv2.imwrite('training_data/fallen/fallen_$counter.jpg',frame) if ret else None; cap.release()"
    echo "Captured fallen_$counter.jpg"
    ((counter++))
done

echo "Training data collection complete!"
echo "Data saved in training_data/"
tar -czf training_data.tar.gz training_data/
echo "Archive created: training_data.tar.gz"
echo "Share this with your teammate for model training."
EOF

chmod +x scripts/capture_training_data.sh
```

---

## Phase 5: Breathing Detection

### Step 5.1: Implement SIFT Breathing Detector
**Create `src/breathing_detector.py`:**

**Algorithm Overview:**
1. Extract chest region from fallen person bounding box
2. Convert frames to grayscale
3. Detect SIFT keypoints in chest area
4. Track keypoint movement across frames
5. Apply motion analysis to detect periodic chest movement
6. Determine breathing based on motion frequency and amplitude

**Key Functions:**
```python
class BreathingDetector:
    def __init__(self, config):
        """Initialize SIFT detector."""
        self.sift = cv2.SIFT_create()
        self.config = config
    
    def analyze_breathing(self, video_frames, chest_bbox):
        """
        Analyze breathing from video frames.
        
        Args:
            video_frames: list of numpy arrays (frames)
            chest_bbox: [x1, y1, x2, y2] chest region
        
        Returns:
            dict: {
                'breathing_detected': bool,
                'confidence': float,
                'breathing_rate': float (breaths/min),
                'motion_amplitude': float
            }
        """
        pass
    
    def extract_chest_roi(self, frame, bbox):
        """Extract region of interest (chest area)."""
        pass
    
    def detect_keypoints(self, frame_roi):
        """Detect SIFT keypoints in frame."""
        pass
    
    def track_motion(self, keypoints_sequence):
        """Track keypoint motion over time."""
        pass
    
    def analyze_periodic_motion(self, motion_data):
        """Apply FFT to detect breathing frequency."""
        pass
```

### Step 5.2: Breathing Detection Algorithm Details

**Detailed Steps:**
```python
def analyze_breathing_detailed(self, video_frames, chest_bbox):
    """
    Step 1: Extract chest ROI from each frame
    """
    chest_rois = []
    for frame in video_frames:
        x1, y1, x2, y2 = chest_bbox
        roi = frame[y1:y2, x1:x2]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        chest_rois.append(gray_roi)
    
    """
    Step 2: Detect SIFT keypoints in first frame
    """
    keypoints_first, descriptors_first = self.sift.detectAndCompute(
        chest_rois[0], None
    )
    
    """
    Step 3: Track keypoints across frames using BFMatcher
    """
    motion_vectors = []
    for i in range(1, len(chest_rois)):
        kp, desc = self.sift.detectAndCompute(chest_rois[i], None)
        
        # Match keypoints
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_first, desc, k=2)
        
        # Apply ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
        
        # Calculate motion
        if len(good_matches) > 10:
            motion = self.calculate_average_motion(
                keypoints_first, kp, good_matches
            )
            motion_vectors.append(motion)
    
    """
    Step 4: Analyze motion for periodicity
    """
    if len(motion_vectors) < 10:
        return {'breathing_detected': False, 'confidence': 0.0}
    
    # Apply FFT to detect frequency
    motion_array = np.array(motion_vectors)
    fft = np.fft.fft(motion_array)
    frequencies = np.fft.fftfreq(len(motion_array), d=1/30)  # 30 fps
    
    # Find dominant frequency
    magnitude = np.abs(fft)
    peak_freq = frequencies[np.argmax(magnitude[1:len(magnitude)//2])]
    breathing_rate = peak_freq * 60  # Convert to breaths per minute
    
    """
    Step 5: Determine if breathing detected
    """
    min_rate, max_rate = self.config['breathing_rate_range']
    amplitude = np.max(motion_array) - np.min(motion_array)
    
    breathing_detected = (
        min_rate <= breathing_rate <= max_rate and
        amplitude > self.config['min_motion_amplitude']
    )
    
    confidence = min(1.0, amplitude / 10.0)  # Normalize to 0-1
    
    return {
        'breathing_detected': breathing_detected,
        'confidence': confidence,
        'breathing_rate': breathing_rate,
        'motion_amplitude': amplitude
    }
```

### Step 5.3: Testing Breathing Detection
**Create test script:**
```bash
cat > tests/test_breathing.py << 'EOF'
"""
Test breathing detection algorithm.

Test cases:
1. Simulated breathing motion (sine wave)
2. No motion (static image)
3. Random motion (non-periodic)
4. Actual video footage
"""
# Implementation details when ready to code
EOF
```

---

## Phase 6: Emergency System

### Step 6.1: Implement Emergency Controller
**Create `src/emergency_controller.py`:**

**State Machine:**
```
States:
- IDLE: Normal monitoring
- FALL_DETECTED: Fall detected, checking breathing
- NO_BREATHING: No breathing, countdown started
- COUNTDOWN_ACTIVE: 10s countdown running
- COUNTDOWN_CANCELLED: User cancelled
- EMERGENCY_ACTIVE: Emergency call initiated
```

**Key Functions:**
```python
class EmergencyController:
    def __init__(self, config, gpio_handler, database):
        """Initialize emergency controller."""
        self.state = "IDLE"
        self.countdown_timer = None
        self.config = config
        self.gpio = gpio_handler
        self.db = database
    
    def on_manual_emergency_trigger(self):
        """Handle manual Button 1 press (Call 999)."""
        self.start_emergency_countdown(manual=True)
    
    def on_fall_detected(self, image, detection_result):
        """Handle automatic fall detection event."""
        self.state = "FALL_DETECTED"
        self.gpio.led_fall_on()
        # Start breathing check
        pass
    
    def on_breathing_check_complete(self, breathing_result):
        """Handle breathing check result."""
        if breathing_result['breathing_detected']:
            # False alarm, return to normal
            self.reset_to_idle()
        else:
            # No breathing, start countdown
            self.start_emergency_countdown()
    
    def start_emergency_countdown(self):
        """Start 10-second countdown."""
        self.state = "COUNTDOWN_ACTIVE"
        self.countdown_remaining = self.config['countdown_duration']
        self.gpio.led_emergency_flash()
        # Start timer
        pass
    
    def cancel_countdown(self):
        """Cancel emergency countdown (button pressed)."""
        if self.state == "COUNTDOWN_ACTIVE":
            self.state = "COUNTDOWN_CANCELLED"
            self.gpio.led_emergency_off()
            self.reset_to_idle()
    
    def countdown_expired(self):
        """Countdown reached zero, trigger emergency."""
        self.state = "EMERGENCY_ACTIVE"
        self.gpio.led_emergency_solid()
        self.trigger_emergency_call()
    
    def trigger_emergency_call(self):
        """Trigger emergency call/notification."""
        # Log to database
        # Send notification
        # Call 999 (if enabled)
        pass
    
    def reset_to_idle(self):
        """Reset to idle state."""
        self.state = "IDLE"
        self.gpio.led_fall_off()
        self.gpio.led_emergency_off()
```

### Step 6.2: Emergency Notification System
**Create `src/notifications.py`:**

**Methods:**
- Log to database
- Display on web interface
- Send SMS (via Twilio - optional)
- Make phone call (via Twilio - optional)
- Send email (optional)

**Implementation:**
```python
class NotificationService:
    def __init__(self, config):
        """Initialize notification service."""
        self.config = config
    
    def send_emergency_alert(self, event_details):
        """Send emergency alert via configured methods."""
        methods = self.config['notification_methods']
        
        if 'log' in methods:
            self.log_emergency(event_details)
        
        if 'web_alert' in methods:
            self.trigger_web_alert(event_details)
        
        if 'sms' in methods:
            self.send_sms(event_details)
        
        if 'call' in methods:
            self.make_call(event_details)
    
    def log_emergency(self, details):
        """Log emergency to file and database."""
        pass
    
    def trigger_web_alert(self, details):
        """Trigger real-time web alert."""
        # Use Flask-SocketIO to push to web clients
        pass
    
    def send_sms(self, details):
        """Send SMS via Twilio."""
        # Requires Twilio account
        pass
    
    def make_call(self, details):
        """Make automated call via Twilio."""
        # Requires Twilio account
        pass
```

---

## Phase 7: Web Interface

### Step 7.1: Flask Application Structure
**Create `webapp/app.py`:**

**Routes:**
- `/` - Home page (gallery)
- `/gallery` - Image gallery with filters
- `/status` - System status page
- `/api/images` - JSON image list
- `/api/download_all` - Download all images
- `/api/status` - Current system status
- `/api/events` - Recent events
- `/stream` - Live camera stream (optional)

### Step 7.2: Create Templates
**Create `webapp/templates/base.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Elderly Fall Detection System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">Elderly Monitor</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Gallery</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/status">Status</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="{{ url_for('static', filename='js/gallery.js') }}"></script>
</body>
</html>
```

**Create `webapp/templates/index.html`:**
```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>Image Gallery</h1>
        
        <!-- Filters -->
        <div class="btn-group mb-3" role="group">
            <button type="button" class="btn btn-outline-primary active" data-filter="all">All</button>
            <button type="button" class="btn btn-outline-warning" data-filter="fall">Falls</button>
            <button type="button" class="btn btn-outline-danger" data-filter="emergency">Emergency</button>
            <button type="button" class="btn btn-outline-success" data-filter="normal">Normal</button>
        </div>
        
        <a href="/api/download_all" class="btn btn-primary mb-3">Download All Images</a>
        
        <!-- Gallery Grid -->
        <div id="gallery" class="row row-cols-1 row-cols-md-3 g-4">
            <!-- Images will be loaded here via JavaScript -->
        </div>
    </div>
</div>
{% endblock %}
```

**Create `webapp/templates/status.html`:**
```html
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>System Status</h1>
        
        <div class="card">
            <div class="card-body">
                <h5>Current State: <span id="current-state" class="badge bg-success">IDLE</span></h5>
                <hr>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6>Fall Detection</h6>
                        <p>Status: <span id="fall-status">Active</span></p>
                        <p>LED 1: <span id="led1-status" class="badge bg-secondary">OFF</span></p>
                    </div>
                    <div class="col-md-6">
                        <h6>Emergency System</h6>
                        <p>Status: <span id="emergency-status">Ready</span></p>
                        <p>LED 2: <span id="led2-status" class="badge bg-secondary">OFF</span></p>
                    </div>
                </div>
                
                <hr>
                
                <h6>Recent Events</h6>
                <div id="recent-events">
                    <!-- Events will be loaded via JavaScript -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 7.3: Create Static Files
**Create `webapp/static/css/style.css`:**
```css
/* Custom styles */
body {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.gallery-item {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
}

.gallery-item img {
    width: 100%;
    height: 250px;
    object-fit: cover;
    transition: transform 0.3s;
}

.gallery-item:hover img {
    transform: scale(1.05);
}

.gallery-item .badge {
    position: absolute;
    top: 10px;
    right: 10px;
}

.status-card {
    margin-bottom: 20px;
}

.event-item {
    padding: 10px;
    border-left: 3px solid #007bff;
    margin-bottom: 10px;
    background-color: #f8f9fa;
}

.event-item.fall {
    border-left-color: #ffc107;
}

.event-item.emergency {
    border-left-color: #dc3545;
}
```

**Create `webapp/static/js/gallery.js`:**
```javascript
// Gallery functionality
document.addEventListener('DOMContentLoaded', function() {
    loadGallery('all');
    
    // Filter buttons
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', function() {
            // Update active button
            document.querySelectorAll('[data-filter]').forEach(b => 
                b.classList.remove('active')
            );
            this.classList.add('active');
            
            // Load filtered images
            loadGallery(this.dataset.filter);
        });
    });
    
    // Real-time updates via Socket.IO
    const socket = io();
    socket.on('new_image', function(data) {
        prependImage(data);
    });
    
    socket.on('status_update', function(data) {
        updateStatus(data);
    });
});

function loadGallery(filter) {
    fetch(`/api/images?filter=${filter}`)
        .then(response => response.json())
        .then(images => {
            const gallery = document.getElementById('gallery');
            gallery.innerHTML = '';
            
            images.forEach(img => {
                gallery.innerHTML += createImageCard(img);
            });
        });
}

function createImageCard(img) {
    const badgeColor = getBadgeColor(img.category);
    return `
        <div class="col">
            <div class="card gallery-item">
                <img src="/data/images/${img.filename}" class="card-img-top" alt="${img.category}">
                <span class="badge bg-${badgeColor}">${img.category}</span>
                <div class="card-body">
                    <p class="card-text small">
                        <strong>Time:</strong> ${img.timestamp}<br>
                        <strong>Confidence:</strong> ${(img.confidence * 100).toFixed(1)}%
                    </p>
                </div>
            </div>
        </div>
    `;
}

function getBadgeColor(category) {
    const colors = {
        'normal': 'success',
        'fall_detected': 'warning',
        'emergency': 'danger'
    };
    return colors[category] || 'secondary';
}

function prependImage(imageData) {
    const gallery = document.getElementById('gallery');
    gallery.insertAdjacentHTML('afterbegin', createImageCard(imageData));
}

function updateStatus(statusData) {
    // Update status page elements
    if (document.getElementById('current-state')) {
        document.getElementById('current-state').textContent = statusData.state;
    }
}
```

---

## Phase 8: WiFi Access Point

### Step 8.1: Install Required Packages
```bash
sudo apt-get install -y hostapd dnsmasq
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
```

### Step 8.2: Configure DHCP (dnsmasq)
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup

cat | sudo tee /etc/dnsmasq.conf << 'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=local
address=/elderlysystem.local/192.168.4.1
EOF
```

### Step 8.3: Configure Static IP for wlan0
```bash
cat | sudo tee -a /etc/dhcpcd.conf << 'EOF'

# Static IP for AP mode
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOF
```

### Step 8.4: Configure hostapd
```bash
cat | sudo tee /etc/hostapd/hostapd.conf << 'EOF'
interface=wlan0
driver=nl80211
ssid=ElderlyMonitor-RDK
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=elderly2024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

sudo chmod 600 /etc/hostapd/hostapd.conf
```

### Step 8.5: Enable hostapd
```bash
# Tell hostapd where config is
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee -a /etc/default/hostapd

# Unmask and enable services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
```

### Step 8.6: Enable IP Forwarding (Optional - for internet sharing)
```bash
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sysctl -p

# Add NAT rules (if you want to share internet)
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# Save iptables rules
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Load on boot
echo 'iptables-restore < /etc/iptables.ipv4.nat' | sudo tee -a /etc/rc.local
```

### Step 8.7: Create WiFi AP Setup Script
```bash
cat > scripts/setup_wifi_ap.sh << 'EOF'
#!/bin/bash
# WiFi Access Point Setup Script

echo "Setting up WiFi Access Point..."

# Restart services
sudo systemctl restart dhcpcd
sudo systemctl restart dnsmasq
sudo systemctl restart hostapd

# Check status
echo "Checking hostapd status..."
sudo systemctl status hostapd --no-pager

echo "Checking dnsmasq status..."
sudo systemctl status dnsmasq --no-pager

echo ""
echo "WiFi AP should be active!"
echo "SSID: ElderlyMonitor-RDK"
echo "Password: elderly2024"
echo "Access web interface at: http://elderlysystem.local or http://192.168.4.1"
EOF

chmod +x scripts/setup_wifi_ap.sh
```

### Step 8.8: Test WiFi AP
```bash
# Run setup script
sudo bash scripts/setup_wifi_ap.sh

# Verify AP is broadcasting
iwconfig wlan0

# From another device:
# 1. Search for WiFi networks
# 2. Connect to "ElderlyMonitor-RDK"
# 3. Enter password: elderly2024
# 4. Open browser to http://elderlysystem.local
```

---

## Phase 9: Integration & Testing

### Step 9.1: Create Main Application
**Create `src/main.py`:**

This is the entry point that brings everything together:
```python
#!/usr/bin/env python3
"""
Main application for Elderly Fall Detection System.
Integrates all components and runs the monitoring loop.
"""

import sys
import signal
import threading
import time
import yaml
from pathlib import Path

# Import our modules (will be created in coding phase)
from camera_service import CameraService
from fall_detector import FallDetector
from breathing_detector import BreathingDetector
from emergency_controller import EmergencyController
from gpio_handler import GPIOHandler
from database import Database
from notifications import NotificationService

# Import Flask app
sys.path.append('webapp')
from app import create_app, socketio

class ElderlyMonitorSystem:
    def __init__(self, config_path='config/config.yaml'):
        """Initialize the monitoring system."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.camera = CameraService(self.config)
        self.fall_detector = FallDetector(
            self.config['fall_detection']['model_path'],
            self.config['fall_detection']
        )
        self.breathing_detector = BreathingDetector(
            self.config['breathing_detection']
        )
        self.gpio = GPIOHandler(self.config['gpio'])
        self.database = Database(self.config['storage']['database_path'])
        self.notifications = NotificationService(self.config)
        self.emergency = EmergencyController(
            self.config['emergency'],
            self.gpio,
            self.database,
            self.notifications
        )
        
        # Setup button callbacks
        self.gpio.setup_buttons(
            capture_callback=self.on_capture_button,
            emergency_callback=self.on_emergency_button
        )
        
        # Control flags
        self.running = False
        self.monitoring_thread = None
        
        # Flask app
        self.flask_app = create_app(self.config, self)
    
    def on_capture_button(self):
        """Handle manual capture button press."""
        print("Capture button pressed!")
        self.gpio.led_fall_on()
        image = self.camera.capture_image(save=True)
        self.gpio.led_fall_off()
        print("Image captured manually.")
    
    def on_emergency_button(self):
        """Handle emergency cancel button press."""
        print("Emergency button pressed!")
        self.emergency.cancel_countdown()
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        self.running = True
        self.camera.start_monitoring()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.start()
        print("Monitoring started.")
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.running = False
        self.camera.stop_monitoring()
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("Monitoring stopped.")
    
    def _monitoring_loop(self):
        """Main monitoring loop - runs continuously."""
        while self.running:
            try:
                # Get current frame
                frame = self.camera.get_current_frame()
                if frame is None:
                    continue
                
                # Run fall detection
                detection = self.fall_detector.detect(frame)
                
                if detection['fall_detected']:
                    print(f"FALL DETECTED! Confidence: {detection['confidence']:.2f}")
                    
                    # Save image
                    image_id = self.camera.save_image(
                        frame,
                        category='fall_detected',
                        metadata=detection
                    )
                    
                    # Trigger emergency controller
                    self.emergency.on_fall_detected(frame, detection)
                    
                    # Start breathing check
                    self._check_breathing(frame, detection['bbox'])
                
                # Sleep according to check interval
                time.sleep(self.config['fall_detection']['check_interval'])
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _check_breathing(self, frame, person_bbox):
        """Perform breathing check using SIFT."""
        print("Checking breathing...")
        
        # Capture video for breathing analysis
        duration = self.config['breathing_detection']['analysis_duration']
        fps = self.config['camera']['framerate']
        num_frames = int(duration * fps)
        
        frames = []
        for _ in range(num_frames):
            frame = self.camera.get_current_frame()
            if frame is not None:
                frames.append(frame)
            time.sleep(1/fps)
        
        # Analyze breathing
        result = self.breathing_detector.analyze_breathing(frames, person_bbox)
        
        print(f"Breathing detected: {result['breathing_detected']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        # Notify emergency controller
        self.emergency.on_breathing_check_complete(result)
    
    def start_web_server(self):
        """Start Flask web server."""
        socketio.run(
            self.flask_app,
            host=self.config['network']['flask_host'],
            port=self.config['network']['flask_port'],
            debug=self.config['network']['flask_debug']
        )
    
    def shutdown(self):
        """Cleanup and shutdown."""
        print("\nShutting down...")
        self.stop_monitoring()
        self.gpio.cleanup()
        print("Goodbye!")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nReceived interrupt signal...")
    if 'system' in globals():
        system.shutdown()
    sys.exit(0)

if __name__ == '__main__':
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("="*50)
    print("Elderly Fall Detection System")
    print("="*50)
    
    # Create system
    system = ElderlyMonitorSystem()
    
    # Start monitoring in background
    system.start_monitoring()
    
    # Start web server (blocking)
    print(f"Starting web server on port {system.config['network']['flask_port']}...")
    print(f"Access at: http://elderlysystem.local or http://192.168.4.1")
    system.start_web_server()
```

### Step 9.2: Create Startup Script
```bash
cat > scripts/run.sh << 'EOF'
#!/bin/bash
# Startup script for Elderly Fall Detection System

cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Export Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src:$(pwd)/webapp"

# Run application
python3 src/main.py
EOF

chmod +x scripts/run.sh
```

### Step 9.3: Create Auto-start Service
```bash
cat > scripts/setup_autostart.sh << 'EOF'
#!/bin/bash
# Setup systemd service for auto-start

SERVICE_FILE="/etc/systemd/system/elderly-monitor.service"
PROJECT_DIR="$HOME/elderly-fall-detection"

echo "Creating systemd service..."

sudo tee $SERVICE_FILE > /dev/null << SERVICEEOF
[Unit]
Description=Elderly Fall Detection System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/scripts/run.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable elderly-monitor.service

echo "Service created and enabled!"
echo "Start: sudo systemctl start elderly-monitor"
echo "Stop: sudo systemctl stop elderly-monitor"
echo "Status: sudo systemctl status elderly-monitor"
echo "Logs: sudo journalctl -u elderly-monitor -f"
EOF

chmod +x scripts/setup_autostart.sh
```

### Step 9.4: Integration Testing
```bash
cat > tests/test_integration.py << 'EOF'
"""
Integration tests for the complete system.

Test scenarios:
1. System startup and initialization
2. Manual capture with button
3. Fall detection flow
4. Breathing detection
5. Emergency countdown and cancellation
6. Web interface access
7. Database operations
8. Image storage and retrieval
"""

import pytest
import time
import sys
sys.path.append('../src')

# Tests will be implemented during coding phase
EOF
```

---

## Phase 10: Deployment

### Step 10.1: Pre-Deployment Checklist
```markdown
Hardware:
- [ ] All GPIO connections secure
- [ ] Camera focused and positioned correctly
- [ ] LEDs working
- [ ] Buttons responsive
- [ ] Power supply adequate (5V 3A minimum)

Software:
- [ ] All Python dependencies installed
- [ ] Virtual environment activated
- [ ] Configuration file updated (WiFi password, etc.)
- [ ] Fall detection model in place
- [ ] Database initialized
- [ ] Logs directory created with write permissions

Network:
- [ ] WiFi AP broadcasting
- [ ] mDNS resolution working
- [ ] Web interface accessible
- [ ] DHCP assigning IPs correctly

Testing:
- [ ] Camera capture working
- [ ] GPIO buttons trigger actions
- [ ] LEDs respond correctly
- [ ] Fall detection functional
- [ ] Breathing detection tested
- [ ] Emergency controller tested
- [ ] Web gallery displays images
- [ ] Image download working
```

### Step 10.2: Performance Optimization
```bash
cat > scripts/optimize_performance.sh << 'EOF'
#!/bin/bash
# Performance optimization for RDK X5

echo "Optimizing system performance..."

# Note: RDK X5 has dedicated BPU (Brain Processing Unit) for AI inference
# Optimize model to use BPU for best performance

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Set CPU governor to performance
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Optimize swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

echo "Optimization complete! Reboot recommended."
EOF

chmod +x scripts/optimize_performance.sh
```

### Step 10.3: Monitoring and Logging
```bash
cat > scripts/monitor_system.sh << 'EOF'
#!/bin/bash
# Monitor system resources and logs

echo "=== System Resources ==="
echo "CPU Temperature:"
cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "N/A"

echo -e "\nCPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1"%"}'

echo -e "\nMemory Usage:"
free -h

echo -e "\nDisk Usage:"
df -h | grep -E "Filesystem|/dev/root"

echo -e "\n=== Process Status ==="
ps aux | grep "python3 src/main.py" | grep -v grep

echo -e "\n=== Recent Logs (last 20 lines) ==="
tail -n 20 data/logs/system.log

echo -e "\n=== Systemd Service Status ==="
sudo systemctl status elderly-monitor --no-pager
EOF

chmod +x scripts/monitor_system.sh
```

### Step 10.4: Backup and Recovery
```bash
cat > scripts/backup_data.sh << 'EOF'
#!/bin/bash
# Backup important data

BACKUP_DIR="$HOME/elderly-monitor-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR

echo "Creating backup..."

# Backup database, images, and config
tar -czf $BACKUP_FILE \
    data/database.db \
    data/images/ \
    config/ \
    data/logs/

echo "Backup created: $BACKUP_FILE"

# Keep only last 10 backups
cd $BACKUP_DIR
ls -t | tail -n +11 | xargs rm -f --

echo "Old backups cleaned up."
EOF

chmod +x scripts/backup_data.sh

# Setup automatic daily backup
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/elderly-fall-detection/scripts/backup_data.sh") | crontab -
```

### Step 10.5: Deployment Commands
```bash
# Final deployment sequence:

# 1. Optimize system
sudo bash scripts/optimize_performance.sh

# 2. Setup WiFi AP
sudo bash scripts/setup_wifi_ap.sh

# 3. Initialize database
python3 src/database.py --init

# 4. Test all components
python3 -m pytest tests/ -v

# 5. Setup auto-start
sudo bash scripts/setup_autostart.sh

# 6. Start service
sudo systemctl start elderly-monitor

# 7. Monitor logs
sudo journalctl -u elderly-monitor -f
```

---

## Summary of Implementation Steps

### Quick Reference Order:
1. **Phase 0**: Prepare hardware and flash OS
2. **Phase 1**: Wire GPIO components, test camera
3. **Phase 2**: Create project structure, configs, virtual environment
4. **Phase 3**: Implement camera service, database, GPIO handler
5. **Phase 4**: Integrate fall detection model (with teammate)
6. **Phase 5**: Implement SIFT breathing detection
7. **Phase 6**: Build emergency controller and notification system
8. **Phase 7**: Create Flask web interface
9. **Phase 8**: Setup WiFi access point and mDNS
10. **Phase 9**: Integrate all components, test system
11. **Phase 10**: Deploy and optimize

---

## Key Decision Points

### Image Transfer Method (Phase 3)
**Decision**: Use Flask API endpoint for download
**Rationale**: Integrated with web interface, no extra setup required
**Alternative**: SFTP if needed for large bulk transfers

### Fall Detection Model (Phase 4)
**Decision**: Wait for teammate's trained model
**Temporary**: Use placeholder or pre-trained YOLO person detector
**Integration**: Provide clear interface specification to teammate

### Emergency Calling (Phase 6)
**Decision**: Start with logging only, add Twilio later
**Rationale**: Requires paid account and testing
**Production**: Integrate SMS/call when system validated

### WiFi AP vs Infrastructure Mode (Phase 8)
**Decision**: Use Access Point mode
**Rationale**: Meets project requirements, no external network needed
**Alternative**: Could connect to existing WiFi and use mDNS

---

## Troubleshooting Common Issues

### Camera Not Working
- Check CSI cable connection
- Enable camera in raspi-config
- Test with libcamera-hello
- Check permissions

### GPIO Not Responding
- Verify wiring with multimeter
- Check pin numbers (GPIO vs Physical)
- Test with simple LED blink script
- Ensure correct resistor values

### Model Loading Slow/Fails
- Use TensorFlow Lite instead of full PyTorch
- Reduce model size
- Check RAM usage
- Consider model quantization

### WiFi AP Not Visible
- Check hostapd service status
- Verify wlan0 interface exists
- Check for conflicting WiFi processes
- Review hostapd logs

### Web Interface Slow
- Optimize image sizes
- Use thumbnail generation
- Implement pagination
- Enable browser caching

---

## Next Steps for Coding

When ready to implement code, follow this order:

1. **Start with `src/database.py`** - Foundation for everything
2. **Then `src/gpio_handler.py`** - Test hardware independently
3. **Then `src/camera_service.py`** - Get image capture working
4. **Then `src/fall_detector.py`** - Model integration (with teammate)
5. **Then `src/breathing_detector.py`** - SIFT algorithm
6. **Then `src/emergency_controller.py`** - State machine logic
7. **Then `webapp/app.py`** - Web interface
8. **Finally `src/main.py`** - Bring it all together

Each module can be tested independently before integration!

---

**Document Version**: 1.0  
**Last Updated**: November 23, 2025  
**Ready for Implementation**: Yes
