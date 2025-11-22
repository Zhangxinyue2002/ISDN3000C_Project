# Implementation Checklist

## Phase 1: Hardware & Basic Setup ✅ IN PROGRESS

### Files Created
- [x] `src/database.py` - Database with automatic cleanup
- [x] `src/gpio_handler.py` - GPIO control for buttons and LEDs
- [x] `src/camera_service.py` - Camera with continuous capture
- [x] `test_components.py` - Component testing script
- [x] `RDK_SETUP.md` - Setup instructions

### Your Tasks (On RDK X5)
- [ ] Transfer project files to RDK X5
- [ ] Install system dependencies (Python, OpenCV, GPIO libraries)
- [ ] Create virtual environment
- [ ] Install Python packages from requirements.txt
- [ ] Wire GPIO components (2 buttons, 2 LEDs)
- [ ] Connect camera to MIPI CSI port
- [ ] Run `python3 test_components.py`
- [ ] Verify all 5 tests pass:
  - [ ] LED test passes
  - [ ] Camera test passes
  - [ ] Continuous capture test passes
  - [ ] Storage stats test passes
  - [ ] Button test passes

## Phase 2: Fall Detection (Waiting for Teammate)

### What We Need
- [ ] Fall detection model file (.pt format)
- [ ] Model input specifications (image size, preprocessing)
- [ ] Model output format (classes, confidence scores)
- [ ] Expected inference time

### Files to Create (After receiving model)
- [ ] `src/fall_detector.py` - YOLO fall detection wrapper
- [ ] `tests/test_fall_detection.py` - Test fall detection
- [ ] Copy model to `models/fall_detection.pt`

## Phase 3: Breathing Detection

### Files to Create
- [ ] `src/breathing_detector.py` - SIFT breathing analysis
- [ ] `tests/test_breathing.py` - Test breathing detection

### Algorithm Steps
- [ ] Extract chest ROI from fall detection bbox
- [ ] Detect SIFT keypoints
- [ ] Track keypoint motion over 12 seconds
- [ ] Apply FFT to detect breathing frequency
- [ ] Validate 12-20 breaths/min range

## Phase 4: Emergency System

### Files to Create
- [ ] `src/emergency_controller.py` - State machine
- [ ] `src/notifications.py` - Alert system
- [ ] `tests/test_emergency.py` - Test emergency logic

### Features to Implement
- [ ] Manual trigger (Button 1)
- [ ] Automatic trigger (fall + no breathing)
- [ ] 10-second countdown
- [ ] Countdown cancellation (Button 2)
- [ ] Emergency call logging
- [ ] LED status indicators

## Phase 5: Web Interface

### Files to Create
- [ ] `webapp/app.py` - Flask application
- [ ] `webapp/templates/base.html` - Base template
- [ ] `webapp/templates/index.html` - Gallery page
- [ ] `webapp/templates/status.html` - Status page
- [ ] `webapp/static/css/style.css` - Stylesheet
- [ ] `webapp/static/js/gallery.js` - JavaScript

### Features to Implement
- [ ] Image gallery with filters (all/falls/emergency/normal)
- [ ] Real-time status updates
- [ ] Download all images (ZIP)
- [ ] Event log display
- [ ] Live camera stream (optional)

## Phase 6: WiFi Access Point

### Setup Tasks
- [ ] Install hostapd and dnsmasq
- [ ] Configure static IP (192.168.4.1)
- [ ] Setup DHCP (192.168.4.2-20)
- [ ] Configure mDNS (elderlysystem.local)
- [ ] Test connection from phone/laptop
- [ ] Verify web interface accessible

## Phase 7: Integration

### Files to Create
- [ ] `src/main.py` - Main application
- [ ] `scripts/run.sh` - Startup script
- [ ] `scripts/setup_autostart.sh` - Systemd service

### Integration Tasks
- [ ] Connect all modules together
- [ ] Implement monitoring loop
- [ ] Setup button callbacks
- [ ] Start Flask in background thread
- [ ] Test complete workflow

## Phase 8: Testing & Deployment

### Testing Tasks
- [ ] Unit tests for each module
- [ ] Integration tests
- [ ] End-to-end workflow test
- [ ] Performance testing
- [ ] Stress testing (24-hour run)

### Deployment Tasks
- [ ] Setup auto-start service
- [ ] Configure logging
- [ ] Setup automatic backups
- [ ] Performance optimization
- [ ] Documentation final review

---

## Current Status: Phase 1 - Component Development ✅

**Next Immediate Steps:**
1. Transfer files to RDK X5
2. Run setup instructions from RDK_SETUP.md
3. Test components with test_components.py
4. Report back results

**Waiting For:**
- Your confirmation that Phase 1 tests pass
- Teammate's fall detection model
