# Elderly Fall Detection System - Architecture Document

## Project Overview
An AI-powered elderly fall detection system running on RDK (Raspberry Pi or similar SBC) that detects falls, monitors breathing using SIFT, and provides emergency calling functionality with a web-based gallery interface.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RDK DEVICE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────┐        ┌──────────────────┐                    │
│  │  Camera    │───────>│  Image Capture   │                    │
│  │  Module    │        │    Service       │                    │
│  └────────────┘        └────────┬─────────┘                    │
│                                 │                               │
│                                 ▼                               │
│                        ┌─────────────────┐                      │
│  ┌────────────┐        │  Fall Detection │                     │
│  │  Button 1  │───────>│   AI Model      │                     │
│  │  (Capture) │        │   (YOLO-based)  │                     │
│  └────────────┘        └────────┬────────┘                     │
│                                 │                               │
│  ┌────────────┐                 ▼                               │
│  │  Button 2  │        ┌─────────────────┐                     │
│  │(Emergency) │───────>│ SIFT Breathing  │                     │
│  └────────────┘        │    Detection    │                     │
│                        └────────┬────────┘                     │
│  ┌────────────┐                 │                               │
│  │  LED 1     │<────────────────┘                               │
│  │(Fall Alert)│                                                 │
│  └────────────┘        ┌─────────────────┐                     │
│                        │  Emergency Call │                     │
│  ┌────────────┐        │    Controller   │                     │
│  │  LED 2     │<───────│  (999 Dialer)   │                     │
│  │(Emergency) │        └────────┬────────┘                     │
│  └────────────┘                 │                               │
│                                 ▼                               │
│                        ┌─────────────────┐                      │
│                        │  Flask Web App  │                      │
│                        │   + Gallery     │                      │
│                        └────────┬────────┘                     │
│                                 │                               │
│                        ┌─────────────────┐                      │
│                        │  SQLite Database│                      │
│                        │  (Image + Meta) │                      │
│                        └─────────────────┘                      │
│                                                                 │
│                        ┌─────────────────┐                      │
│                        │  WiFi AP        │                      │
│                        │  + mDNS         │                      │
│                        └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ WiFi Connection
                                 ▼
                     ┌──────────────────────┐
                     │  User Device         │
                     │  (Phone/Computer)    │
                     │  Browser Access      │
                     └──────────────────────┘
```

---

## Component Breakdown

### 1. Hardware Components (RDK)
- **Camera Module**: Continuously captures images of elderly person
- **Button 1 (Emergency Call)**: Trigger emergency call to 999
- **Button 2 (Emergency Stop)**: Stop/cancel emergency call
- **LED 1 (Fall Detection Indicator)**: Lights up when fall detected
- **LED 2 (Emergency Status)**: 
  - Flashing: Emergency call pending (10s countdown)
  - Solid: Emergency call made
- **WiFi Module**: Creates access point for web interface

### 2. Software Components

#### A. Image Capture Service
**Purpose**: Manages camera operations and image storage
**Technologies**: Python, OpenCV
**Functions**:
- Continuous photo capture mode (not just monitoring)
- Automated capture at regular intervals (e.g., 1-2 seconds)
- Image preprocessing and storage
- Sequential naming (1.jpg, 2.jpg, 3.jpg...)
- Automatic cleanup of old photos to prevent storage full
- Transfer images to computer via:
  - **Recommended**: Flask endpoint for bulk download
  - **Alternative**: SFTP/SCP server
  - **Alternative**: SMB/Samba file share

#### B. Fall Detection AI Model
**Purpose**: Detect elderly person falling
**Technologies**: YOLO (YOLOv8 or YOLOv5), PyTorch/TensorFlow
**Process**:
1. Continuous frame analysis from camera
2. Person detection + pose estimation
3. Fall classification (standing/sitting/fallen)
4. Trigger alert when fall detected
5. Start breathing detection sequence

**Integration Points**:
- Your teammate trains model separately
- Model format: PyTorch (.pt) or ONNX (.onnx)
- Integration: Load model file into detection service
- Interface: `detect_fall(image) -> bool, confidence, bbox`

#### C. SIFT Breathing Detection
**Purpose**: Detect chest movement indicating breathing
**Technologies**: OpenCV SIFT, optical flow analysis
**Process**:
1. Activated after fall detection
2. Captures 10-15 seconds of video
3. Extract chest region using YOLO bounding box
4. Apply SIFT feature detection on chest area
5. Track feature point movement over time
6. Determine breathing based on periodic motion
7. If no breathing detected → initiate emergency call

**Algorithm**:
```
1. Detect person in fallen position
2. Extract chest ROI (region of interest)
3. Detect SIFT keypoints in ROI
4. Track keypoint movement frame-by-frame
5. Apply FFT to detect periodic motion (12-20 breaths/min)
6. Threshold: Motion amplitude > threshold = breathing
```

#### D. Emergency Call Controller
**Purpose**: Manage emergency response workflow
**States**:
- **IDLE**: Normal monitoring
- **FALL_DETECTED**: LED1 on, start breathing check
- **NO_BREATHING**: LED2 flashing, 10s countdown
- **COUNTDOWN_CANCELLED**: User pressed Button2, return to monitoring
- **EMERGENCY_ACTIVE**: LED2 solid, call 999 (simulate with notification)

**State Machine**:
```
IDLE → [Fall Detected] → FALL_DETECTED
                              ↓
                     [Check Breathing]
                              ↓
                    [Breathing: Yes] → IDLE
                              ↓
                    [Breathing: No] → NO_BREATHING
                              ↓
                    [Start 10s Timer + LED2 Flash]
                              ↓
                    [Button2 Pressed] → COUNTDOWN_CANCELLED → IDLE
                              ↓
                    [Timer Expired] → EMERGENCY_ACTIVE → Call 999
```

#### E. Flask Web Application
**Purpose**: Web interface for gallery and monitoring
**Endpoints**:
- `/` - Home/Gallery page
- `/gallery` - Image gallery with filters
- `/api/images` - JSON list of images
- `/api/download_all` - Bulk download images
- `/api/status` - System status (fall detected, emergency state)
- `/stream` - Live camera feed (optional)
- `/image/<id>` - Individual image view

**Features**:
- Responsive web design
- Filter by category (fall detected, normal, emergency)
- Timeline view
- Download individual/bulk images
- Real-time status updates (WebSocket or polling)

#### F. Database (SQLite)
**Schema**:
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    category TEXT, -- 'normal', 'fall_detected', 'emergency'
    fall_detected BOOLEAN DEFAULT 0,
    breathing_detected BOOLEAN,
    emergency_triggered BOOLEAN DEFAULT 0,
    confidence REAL
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT, -- 'fall', 'breathing_check', 'emergency_call', 'manual_capture'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_id INTEGER,
    details TEXT,
    FOREIGN KEY(image_id) REFERENCES images(id)
);
```

#### G. WiFi Access Point + mDNS
**Purpose**: Provide network access to web interface
**Configuration**:
- SSID: `ElderlyMonitor-RDK`
- Password: Configurable
- IP Range: `192.168.4.1/24`
- mDNS: `elderlysystem.local`
- Access: `http://elderlysystem.local` or `http://192.168.4.1`

---

## Data Flow Diagrams

### 1. Normal Capture Flow (Button 1 Pressed)
```
User Press Button1 → Capture Image → Blink LED1 → 
Save to DB → Display in Gallery
```

### 2. Fall Detection Flow
```
Camera Feed → YOLO Detection → Fall Detected? 
                                    ↓ YES
                            LED1 ON → Save Image → 
                            Start SIFT Analysis → Breathing Check
                                    ↓
                        ┌───────────┴───────────┐
                        ↓                       ↓
                   Breathing YES           Breathing NO
                        ↓                       ↓
                    LED1 OFF              LED2 Flash (10s)
                    Return Monitor         Wait for Button2
                                                ↓
                                    ┌───────────┴──────────┐
                                    ↓                      ↓
                              Button2 Pressed         Timeout
                                    ↓                      ↓
                              Cancel Alert           LED2 Solid
                              LED2 OFF              Call 999
                              Return Monitor         Log Event
```

### 3. Image Transfer Flow (RDK → Computer)
```
RDK (Flask Server)
    ↓
    └─> /api/download_all endpoint
            ↓
    Computer sends GET request
            ↓
    RDK packages all images → ZIP file
            ↓
    Transfer via HTTP
            ↓
    Computer extracts images
```

---

## Technology Stack

### Hardware
- **RDK**: RDK X5 (Horizon Robotics)
- **Camera**: MIPI CSI camera or USB webcam
- **GPIO**: 2 buttons + 2 LEDs (or LED strip)
- **WiFi**: Built-in WiFi module

### Software Stack
- **OS**: Ubuntu 20.04/22.04 (64-bit) for RDK X5
- **Language**: Python 3.9+
- **AI Framework**: 
  - PyTorch or TensorFlow Lite
  - OpenCV for SIFT
  - Ultralytics YOLOv8
- **Web Framework**: Flask + Flask-SocketIO
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap)
- **Networking**: hostapd (WiFi AP), dnsmasq (DHCP + mDNS)

---

## Directory Structure

```
elderly-fall-detection/
├── README.md                      # User-facing documentation
├── ARCHITECTURE.md                # This file
├── IMPLEMENTATION_GUIDE.md        # Step-by-step implementation
├── requirements.txt               # Python dependencies
├── config/
│   ├── config.yaml               # System configuration
│   ├── wifi_ap.conf              # WiFi AP settings
│   └── camera_settings.json      # Camera parameters
├── src/
│   ├── main.py                   # Entry point
│   ├── camera_service.py         # Camera capture logic
│   ├── fall_detector.py          # YOLO fall detection
│   ├── breathing_detector.py     # SIFT breathing analysis
│   ├── emergency_controller.py   # Emergency state machine
│   ├── gpio_handler.py           # Button/LED control
│   ├── database.py               # Database operations
│   └── utils.py                  # Helper functions
├── webapp/
│   ├── app.py                    # Flask application
│   ├── templates/
│   │   ├── index.html           # Gallery page
│   │   ├── status.html          # System status
│   │   └── base.html            # Base template
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── gallery.js
│   │   └── images/
│   └── api/
│       └── routes.py            # API endpoints
├── models/
│   ├── fall_detection.pt        # YOLO model (your teammate provides)
│   └── model_config.yaml        # Model metadata
├── data/
│   ├── images/                  # Captured images (1.jpg, 2.jpg, ...)
│   ├── database.db              # SQLite database
│   └── logs/                    # System logs
├── tests/
│   ├── test_fall_detection.py
│   ├── test_breathing.py
│   └── test_integration.py
└── scripts/
    ├── setup_wifi_ap.sh         # WiFi AP setup script
    ├── install_dependencies.sh  # Installation script
    └── run.sh                   # Startup script
```

---

## Integration with Teammate's Model

Your teammate is testing different fall detection models. Here's how to integrate:

### Model Requirements Document (Share with Teammate)
```yaml
Model Specifications:
  Task: Fall Detection
  Input: RGB image (640x640 or 1280x720)
  Output: 
    - Class: 'standing', 'sitting', 'fallen'
    - Confidence score: float (0-1)
    - Bounding box: [x1, y1, x2, y2]
  Format: PyTorch (.pt) or ONNX (.onnx)
  
Performance Requirements:
  - Inference time: < 100ms on RDK
  - Minimum accuracy: 90%
  - False positive rate: < 5%

Testing Dataset:
  - Provide your teammate with sample images from RDK
  - Include various angles, lighting conditions
  - Test cases: actual falls, sitting, lying in bed

Delivery:
  - Model file: fall_detection.pt
  - Config file: model_config.yaml
  - Class labels mapping
  - Preprocessing requirements (normalization, resize)
```

### Integration Code Interface
```python
# fall_detector.py - Your code
class FallDetector:
    def __init__(self, model_path):
        # Load model provided by teammate
        self.model = torch.load(model_path)
        
    def detect(self, image):
        """
        Interface function for teammate's model
        Returns: {
            'fall_detected': bool,
            'confidence': float,
            'class': str,
            'bbox': [x1, y1, x2, y2]
        }
        """
        pass
```

---

## Image Transfer Methods (RDK → Computer)

### Recommended: Flask API Endpoint
**Pros**: Integrated with web interface, no extra setup
**Implementation**:
```python
@app.route('/api/download_all')
def download_all():
    # Create ZIP of all images
    # Return as download
    pass
```

### Alternative 1: SFTP/SCP
**Pros**: Standard protocol, secure
**Setup**: 
```bash
# On RDK
sudo apt-get install openssh-server

# On computer
scp -r pi@192.168.4.1:/home/pi/elderly-fall-detection/data/images/ ./
```

### Alternative 2: SMB/Samba Share
**Pros**: Easy for Windows users
**Setup**: Install Samba on RDK, share data folder

---

## Network Architecture

```
┌─────────────────────────────────────┐
│         RDK WiFi AP                 │
│    SSID: ElderlyMonitor-RDK         │
│    IP: 192.168.4.1                  │
│    mDNS: elderlysystem.local        │
└──────────────┬──────────────────────┘
               │
               │ WiFi Connection
               │
┌──────────────┴──────────────────────┐
│     User Device (Phone/Laptop)      │
│     IP: 192.168.4.2-254             │
│     Browser: http://elderlysystem.local │
└─────────────────────────────────────┘
```

---

## State Machine Diagram

```
        ┌──────────────┐
        │     IDLE     │
        │  Monitoring  │
        └──────┬───────┘
               │
               │ Fall Detected (YOLO)
               ▼
        ┌──────────────┐
        │FALL_DETECTED │
        │  LED1: ON    │
        └──────┬───────┘
               │
               │ Start SIFT Analysis
               ▼
        ┌──────────────┐
        │  BREATHING   │
        │    CHECK     │
        └──────┬───────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
  Breathing         No Breathing
       │                │
       ▼                ▼
   ┌──────┐      ┌──────────────┐
   │ IDLE │      │ NO_BREATHING │
   └──────┘      │  LED2: Flash │
                 │  Timer: 10s  │
                 └──────┬───────┘
                        │
                ┌───────┴────────┐
                │                │
                ▼                ▼
          Button2          Timer Expired
          Pressed               │
                │               ▼
                ▼        ┌─────────────┐
           ┌──────┐      │ EMERGENCY   │
           │ IDLE │      │LED2: Solid  │
           └──────┘      │ Call 999    │
                         └─────────────┘
```

---

## Performance Considerations

### Real-time Requirements
- Fall detection: Process frame every 100-200ms
- Breathing detection: Analyze 10-15 second window
- Emergency countdown: Precise 10-second timer
- Web interface: Responsive (<500ms page load)

### Resource Management
- **CPU**: YOLO inference is CPU-intensive
  - Consider using TensorFlow Lite or ONNX Runtime
  - Use threading for concurrent operations
- **Memory**: Store max 1000 images, auto-cleanup older ones
- **Storage**: Compress images to JPEG (quality 85)
- **Power**: Optimize for continuous operation

---

## Security Considerations

1. **WiFi AP**: Use WPA2 encryption
2. **Web Interface**: Optional basic authentication
3. **Database**: Encrypt sensitive data
4. **Emergency Contacts**: Store securely
5. **Image Privacy**: Auto-delete after X days (configurable)

---

## Testing Strategy

### Unit Tests
- Camera capture functionality
- Fall detection accuracy
- SIFT breathing detection
- GPIO button/LED responses
- Database operations

### Integration Tests
- Full workflow: Fall → Breathing → Emergency
- Web gallery functionality
- Image transfer methods
- State machine transitions

### Field Tests
- Various lighting conditions
- Different fall scenarios
- False positive handling
- Network connectivity

---

## Deployment Checklist

- [ ] RDK OS installed and updated
- [ ] Python 3.9+ with all dependencies
- [ ] Camera module connected and tested
- [ ] GPIO buttons and LEDs wired correctly
- [ ] WiFi AP configured with mDNS
- [ ] Fall detection model trained and loaded
- [ ] Database initialized
- [ ] Flask app tested locally
- [ ] Emergency contact configured
- [ ] System startup script enabled
- [ ] Monitoring and logging configured

---

## Future Enhancements

1. **Multi-person detection**: Track multiple elderly individuals
2. **Cloud backup**: Sync images to cloud storage
3. **Mobile app**: Native iOS/Android app
4. **Voice alerts**: Audio notifications
5. **Integration with smart home**: Connect to existing systems
6. **Advanced analytics**: Fall pattern analysis
7. **Remote monitoring**: Family member access via internet

---

## Emergency Call Implementation

Since actual 999 calling requires telecom integration, implement as:

### Phase 1 (Development)
- Log to database
- Send notification to web interface
- Display alert on gallery page
- Email/SMS simulation (if credentials available)

### Phase 2 (Production)
- Integrate with Twilio API for SMS
- Use VoIP service for automated call
- Send to monitoring center/caregiver app

---

## Glossary

- **RDK**: Raspberry Development Kit (Raspberry Pi)
- **YOLO**: You Only Look Once (object detection model)
- **SIFT**: Scale-Invariant Feature Transform
- **mDNS**: Multicast DNS (for .local domain resolution)
- **GPIO**: General Purpose Input/Output
- **Access Point (AP)**: WiFi hotspot mode
- **Flask**: Python web framework
- **SQLite**: Lightweight database engine

---

## References & Resources

- YOLO: https://github.com/ultralytics/ultralytics
- OpenCV SIFT: https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html
- Flask: https://flask.palletsprojects.com/
- Raspberry Pi GPIO: https://gpiozero.readthedocs.io/
- WiFi AP Setup: https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

---

**Document Version**: 1.0  
**Last Updated**: November 23, 2025  
**Authors**: Project Team
