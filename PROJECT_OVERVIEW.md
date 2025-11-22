# Elderly Fall Detection System - Project Overview

## Quick Reference for Development

### Project Goal
Build an AI-powered elderly fall detection system on RDK that:
- Detects falls using YOLO
- Monitors breathing using SIFT
- Provides emergency calling with manual override
- Hosts a web gallery via WiFi access point

---

## System Components at a Glance

### Hardware
- **RDK X5** (Horizon Robotics)
- **Camera** (MIPI CSI camera or USB webcam) → Continuous capture
- **Button 1** (GPIO 17) → Call 999 (emergency)
- **Button 2** (GPIO 27) → Stop calling 999
- **LED 1** (GPIO 22) → Fall indicator
- **LED 2** (GPIO 23) → Emergency status

### Software Modules
1. **camera_service.py** - Image capture and storage
2. **fall_detector.py** - YOLO fall detection (teammate's model)
3. **breathing_detector.py** - SIFT breathing analysis
4. **emergency_controller.py** - State machine for emergency response
5. **gpio_handler.py** - Button/LED control
6. **database.py** - SQLite operations
7. **app.py** - Flask web interface
8. **main.py** - Integration and main loop

---

## Workflow Overview

### Normal Operation
```
Continuous Capture (every 2s) → Save Photo → YOLO Detection → [No Fall] → Continue
                                                              ↓ [Fall Detected]
                                                         LED1 ON → SIFT Analysis
                                                              ↓
                                                    [Breathing Detected]
                                                              ↓
                                                        LED1 OFF → Resume
                                      
Automatic Cleanup: Delete old photos when storage > 85% threshold
```

### Emergency Flow
```
SIFT Analysis → [No Breathing] → LED2 Flash (10s countdown)
                                          ↓
                              ┌───────────┴──────────┐
                              ↓                      ↓
                      Button2 Pressed           Timeout
                              ↓                      ↓
                        Cancel Alert           LED2 Solid
                        Return Normal          Call 999
```

---

## Key Design Decisions

### 1. Image Transfer (RDK → Computer)
**Method**: Flask API endpoint `/api/download_all`
- Returns ZIP file of all images
- Accessible via web interface
- Images named sequentially (1.jpg, 2.jpg, ...)

### 2. Fall Detection Model Integration
**Interface**: Your teammate provides `fall_detection.pt`
**Input**: RGB image (numpy array)
**Output**: 
```python
{
    'fall_detected': bool,
    'confidence': float,
    'class': 'standing' | 'sitting' | 'fallen',
    'bbox': [x1, y1, x2, y2]
}
```

### 3. Breathing Detection Algorithm
**Method**: SIFT keypoint tracking + FFT analysis
**Steps**:
1. Extract chest ROI from fallen person
2. Detect SIFT keypoints
3. Track motion across frames (10-15 seconds)
4. Apply FFT to detect periodic motion
5. Validate breathing rate (12-20 breaths/min)

### 4. Emergency System
**States**: IDLE → FALL_DETECTED → NO_BREATHING → COUNTDOWN → EMERGENCY
**Cancel Window**: 10 seconds with LED2 flashing
**Action**: Log event + Web alert (actual 999 call optional)

### 5. Web Interface
**Access**: `http://elderlysystem.local` or `http://192.168.4.1`
**Features**:
- Image gallery with filters
- Real-time status dashboard
- Bulk download
- Event logs

---

## Database Schema

### images table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| filename | TEXT | Image filename (1.jpg, 2.jpg, ...) |
| filepath | TEXT | Full path |
| timestamp | DATETIME | Capture time |
| category | TEXT | 'normal', 'fall_detected', 'emergency' |
| fall_detected | BOOLEAN | Fall flag |
| breathing_detected | BOOLEAN | Breathing result |
| emergency_triggered | BOOLEAN | Emergency flag |
| confidence | REAL | AI confidence score |

### events table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_type | TEXT | 'fall', 'breathing_check', 'emergency_call' |
| timestamp | DATETIME | Event time |
| image_id | INTEGER | Foreign key to images |
| details | TEXT | JSON details |

---

## Implementation Priority Order

### Phase 1: Foundation (Week 1)
1. ✅ Project structure created
2. Hardware wiring and GPIO testing
3. Camera capture working
4. Database operational

### Phase 2: Core AI (Week 2)
5. Fall detection integration (with teammate)
6. SIFT breathing detection
7. Image sequential storage

### Phase 3: Emergency System (Week 3)
8. Emergency controller state machine
9. Button/LED coordination
10. Notification system

### Phase 4: Web Interface (Week 4)
11. Flask app with gallery
12. API endpoints
13. Real-time updates (SocketIO)

### Phase 5: Deployment (Week 5)
14. WiFi AP setup
15. mDNS configuration
16. Auto-start service
17. Testing and optimization

---

## Critical Integration Points

### With Teammate (AI/ML Developer)
**What you need from them:**
- Trained YOLO model file (`fall_detection.pt`)
- Model configuration (input size, classes, preprocessing)
- Performance metrics (accuracy, FPS)

**What they need from you:**
- Training images from RDK camera
- Model interface specification (see ARCHITECTURE.md)
- Testing feedback on RDK hardware

### Image Naming Convention
Sequential numbering starting from 1:
```
data/images/
├── 1.jpg
├── 2.jpg
├── 3.jpg
└── ...
```

Counter maintained in database or file.

### Automatic Cleanup Strategy
- **Trigger**: When image count > 85% of max (5000 images)
- **Method**: FIFO (First-In-First-Out)
- **Preserve**: Always keep fall detection and emergency images
- **Age-based**: Delete normal images older than 7 days
- **Disk monitoring**: Cleanup if disk usage > 90%

---

## Testing Strategy

### Unit Tests
- Each module tested independently
- Mock hardware components (GPIO, Camera)
- Database operations
- AI model loading

### Integration Tests
- Full workflow: capture → detect → breathing → emergency
- GPIO button events trigger correct actions
- Web interface displays correct data

### Field Tests
- Actual fall scenarios
- Different lighting conditions
- False positive handling
- Network connectivity

---

## Common Pitfalls to Avoid

1. **GPIO Pin Confusion**: Use GPIO numbering, not physical pin numbers
2. **Camera Permissions**: Ensure user in `video` group
3. **Model Size**: Large models slow on RDK, use TFLite if needed
4. **WiFi Conflicts**: Disable wpa_supplicant on wlan0 for AP mode
5. **Image Storage**: Implement auto-cleanup to prevent disk full
6. **Thread Safety**: Use locks when accessing shared resources
7. **Error Handling**: Camera/network failures should be recoverable

---

## Quick Commands Reference

### Development
```bash
# Activate environment
source venv/bin/activate

# Run system
python3 src/main.py

# Run tests
pytest tests/ -v

# Check logs
tail -f data/logs/system.log
```

### Deployment
```bash
# Start service
sudo systemctl start elderly-monitor

# View logs
sudo journalctl -u elderly-monitor -f

# Restart
sudo systemctl restart elderly-monitor
```

### Maintenance
```bash
# Backup data
bash scripts/backup_data.sh

# Monitor resources
bash scripts/monitor_system.sh

# Check WiFi AP
iwconfig wlan0
```

---

## Key Configuration Files

### Primary Config
`config/config.yaml` - All system settings

### Important Values
- Button GPIO: 17, 27
- LED GPIO: 22, 23
- WiFi SSID: ElderlyMonitor-RDK
- Web port: 5000
- Fall threshold: 0.75
- Countdown: 10 seconds

---

## Web Interface Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Gallery home page |
| `/gallery` | GET | Image gallery |
| `/status` | GET | System status page |
| `/api/images` | GET | JSON image list |
| `/api/download_all` | GET | Download ZIP |
| `/api/status` | GET | Current status JSON |
| `/api/events` | GET | Event log JSON |
| `/stream` | GET | Live camera feed |

---

## Resources for Each Phase

### Hardware Setup
- RDK X5 GPIO documentation: Check Horizon Robotics documentation
- Camera setup: MIPI CSI or USB camera with OpenCV

### Python Libraries
- gpiozero: https://gpiozero.readthedocs.io/
- OpenCV: https://docs.opencv.org/
- Flask: https://flask.palletsprojects.com/
- YOLOv8: https://docs.ultralytics.com/

### Networking
- hostapd config: `/etc/hostapd/hostapd.conf`
- DHCP config: `/etc/dnsmasq.conf`

---

## Documentation Files

1. **README.md** - User-facing documentation, installation, usage
2. **ARCHITECTURE.md** - Technical architecture, detailed design
3. **IMPLEMENTATION_GUIDE.md** - Step-by-step implementation instructions
4. **PROJECT_OVERVIEW.md** (this file) - Quick reference for developers

---

## Next Steps

When ready to start coding:

1. Read through all documentation
2. Wire up hardware and test GPIO
3. Start with `database.py` (foundation)
4. Then `gpio_handler.py` (test buttons/LEDs)
5. Then `camera_service.py` (get images capturing)
6. Coordinate with teammate on fall detection model
7. Implement breathing detection
8. Build emergency controller
9. Create web interface
10. Integrate everything in `main.py`

**Remember**: You can implement step-by-step and test each component independently!

---

## Contact and Collaboration

### Your Role
- Hardware integration
- Camera service
- Breathing detection (SIFT)
- Emergency system
- Web interface
- System integration

### Teammate's Role
- Fall detection model training
- Model optimization for RDK
- Performance tuning
- Testing various fall scenarios

### Integration Meeting Points
- Share training data
- Test model on RDK
- Validate inference speed
- Adjust confidence thresholds
- Final system testing

---

**Quick Start**: Read README.md → Follow IMPLEMENTATION_GUIDE.md → Code step-by-step

**Document Version**: 1.0  
**Last Updated**: November 23, 2025
