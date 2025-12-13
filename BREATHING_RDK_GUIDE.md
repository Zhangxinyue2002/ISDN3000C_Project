# RDK Camera Breathing Detection Guide

## 🎯 Overview

This guide explains how to test breathing detection using a camera connected to RDK X5 (instead of a webcam). The test uses the existing `CameraService` class which handles RDK-specific camera configuration.

---

## 📋 Prerequisites

### Hardware Requirements
- ✅ RDK X5 development board
- ✅ Camera connected to RDK X5:
  - MIPI CSI camera (preferred), OR
  - USB webcam
- ✅ Monitor/display for interactive ROI selection (optional)

### Software Requirements
- ✅ Ubuntu on RDK X5
- ✅ Python 3.x
- ✅ OpenCV with contrib modules
- ✅ Project files transferred to RDK X5

---

## 🚀 Quick Start

### Step 1: Transfer Files to RDK X5

From your Windows PC:
```powershell
# Transfer the new test script
scp test_breathing_rdk.py user@rdkx5-ip:~/ISDN3000C_Project/
```

Or transfer the entire updated project:
```powershell
scp -r f:\ISDN3000C_Project/* user@rdkx5-ip:~/ISDN3000C_Project/
```

### Step 2: SSH to RDK X5

```bash
ssh user@rdkx5-ip
cd ~/ISDN3000C_Project
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 4: Run Camera Test

```bash
# First, test basic camera capture
python3 test_breathing_rdk.py --test-capture
```

**Expected output:**
```
======================================================================
RDK X5 BREATHING DETECTION TEST
======================================================================

CAMERA CAPTURE TEST
Trying /dev/video0...
✓ Camera opened successfully on /dev/video0

Capturing 5 test frames...
  Frame 1: (720, 1280, 3) - ✓
  Frame 2: (720, 1280, 3) - ✓
  Frame 3: (720, 1280, 3) - ✓
  Frame 4: (720, 1280, 3) - ✓
  Frame 5: (720, 1280, 3) - ✓

✅ Camera capture test PASSED
```

---

## 🧪 Testing Breathing Detection

### Option 1: Interactive Mode (with Display)

If you have a monitor connected to RDK X5:

```bash
python3 test_breathing_rdk.py
```

**What happens:**
1. Camera test runs automatically
2. Live camera preview opens
3. Draw a box around the chest area
4. Press SPACE to confirm
5. System captures 12 seconds of video
6. Breathing analysis runs automatically
7. Results displayed

### Option 2: Manual Bounding Box (Headless)

If you DON'T have a display (SSH only):

```bash
# Manually specify chest bounding box coordinates
python3 test_breathing_rdk.py --bbox 200,100,400,300
```

**How to determine bbox coordinates:**
1. Take a test photo first: `python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); cv2.imwrite('test.jpg',frame)"`
2. Download the image: `scp user@rdkx5-ip:~/ISDN3000C_Project/test.jpg .`
3. Open on PC and note the chest region coordinates
4. Use those coordinates with `--bbox X1,Y1,X2,Y2`

### Option 3: Custom Duration

```bash
# Capture for 15 seconds instead of 12
python3 test_breathing_rdk.py --duration 15
```

### Option 4: Lower FPS (if needed)

```bash
# Use 20 FPS instead of 30 (faster processing)
python3 test_breathing_rdk.py --fps 20 --duration 10
```

---

## 📊 Understanding the Results

### Successful Detection Example

```
BREATHING DETECTION RESULTS
======================================================================

  Breathing Detected:  YES ✓
  Confidence:          85.0%
  Breathing Rate:      16.2 breaths/min
  Breathing Amplitude: 5.4 pixels
  Frames Analyzed:     360
  Keypoints Tracked:   145

INTERPRETATION:
  ✅ High confidence - Person is breathing normally
  ✓ Breathing rate of 16.2 bpm is within normal range
```

**What this means:**
- ✅ Breathing detected successfully
- ✅ Rate is normal (12-20 bpm)
- ✅ Algorithm working correctly
- ✅ Ready for integration

---

### No Breathing Detected Example

```
BREATHING DETECTION RESULTS
======================================================================

  Breathing Detected:  NO ✗
  Confidence:          30.0%
  Breathing Rate:      5.2 breaths/min
  Motion Amplitude:    0.8 pixels
  Frames Analyzed:     360
  Keypoints Tracked:   78

INTERPRETATION:
  ❌ No breathing detected!
  → Breathing rate too low: 5.2 bpm
  → Motion amplitude too small: 0.8 pixels
  → Person may be too still or too far from camera
```

**Possible causes:**
- Person is too far from camera
- Lighting is poor
- Clothing is too plain (no texture for SIFT)
- Camera is not stable
- Person is actually not breathing (emergency!)

---

### False Positive (Motion Detected)

```
BREATHING DETECTION RESULTS
======================================================================

  Breathing Detected:  NO ✗
  Confidence:          40.0%
  Breathing Rate:      35.8 breaths/min
  Motion Amplitude:    18.2 pixels
  Frames Analyzed:     360
  Keypoints Tracked:   122

INTERPRETATION:
  ❌ No breathing detected!
  → Motion too fast (not breathing): 35.8 bpm
  → Possible causes: camera shake, person moving, etc.
```

**Possible causes:**
- Camera is not mounted securely (shaking)
- Person is moving (not just breathing)
- Background movement
- This is actually GOOD - algorithm correctly rejected non-breathing motion!

---

## 🔧 Troubleshooting

### Problem: Camera not opening

```bash
# Check available cameras
ls -l /dev/video*

# Test camera manually
v4l2-ctl --list-devices

# Try different camera index
python3 -c "import cv2; cap=cv2.VideoCapture(0); print('Video0:', cap.isOpened()); cap.release()"
python3 -c "import cv2; cap=cv2.VideoCapture(8); print('Video8:', cap.isOpened()); cap.release()"
```

The `CameraService` automatically tries indices [0, 1, 8, 10].

### Problem: "Insufficient keypoints"

**Solution:**
- Ensure person wears textured clothing (not plain solid colors)
- Improve lighting
- Move person closer to camera
- Clean camera lens

### Problem: Low FPS / Slow capture

**Solution:**
```bash
# Reduce FPS and duration
python3 test_breathing_rdk.py --fps 20 --duration 10

# Or reduce resolution in config.yaml
camera:
  resolution: [640, 480]  # Instead of [1280, 720]
```

### Problem: Can't select ROI (no display)

**Solution:** Use manual bbox:
```bash
python3 test_breathing_rdk.py --bbox 200,150,450,400
```

---

## 🎯 Integration with Fall Detection

Once breathing detection is tested, here's how it integrates:

```python
# In your main application on RDK X5

from src.camera_service import CameraService
from src.breathing_detector import BreathingDetector
from src.fall_detector import FallDetector
from src.database import Database

# Initialize
db = Database()
camera = CameraService(config, db)
fall_detector = FallDetector()
breathing_detector = BreathingDetector()

# Main loop
camera.start_continuous_capture()

while True:
    # Get latest frame
    ret, frame = camera.cap.read()
    
    # Detect fall
    fall_result = fall_detector.detect(frame)
    
    if fall_result['fall_detected']:
        print("Fall detected!")
        
        # Calculate chest region (upper half of person)
        x1, y1, x2, y2 = fall_result['bbox']
        chest_bbox = (x1, y1, x2, y1 + (y2-y1)//2)
        
        # Analyze breathing (captures 12 seconds of video)
        breathing_result = breathing_detector.capture_and_analyze(
            camera.cap, 
            chest_bbox
        )
        
        if breathing_result['breathing_detected']:
            print("✓ Breathing OK - False alarm")
            # Continue monitoring
        else:
            print("⚠️ NO BREATHING - Emergency!")
            # Start emergency countdown
            start_emergency_protocol()
```

---

## 📝 Command Reference

### Basic Commands

```bash
# Test camera only
python3 test_breathing_rdk.py --test-capture

# Full test (interactive)
python3 test_breathing_rdk.py

# Headless with manual bbox
python3 test_breathing_rdk.py --bbox 200,100,400,300

# Custom duration
python3 test_breathing_rdk.py --duration 15

# Lower FPS
python3 test_breathing_rdk.py --fps 20

# Combined options
python3 test_breathing_rdk.py --bbox 200,100,400,300 --duration 10 --fps 25
```

### Helper Commands

```bash
# Capture test photo
python3 -c "import cv2; cap=cv2.VideoCapture(0); ret,frame=cap.read(); cv2.imwrite('test.jpg',frame); cap.release()"

# Check camera resolution
python3 -c "import cv2; cap=cv2.VideoCapture(0); print(f'Resolution: {int(cap.get(3))}x{int(cap.get(4))}'); cap.release()"

# List video devices
ls -l /dev/video*

# Check camera details
v4l2-ctl --device=/dev/video0 --all
```

---

## 🎓 Best Practices

### For Testing
1. ✅ Test camera capture first (`--test-capture`)
2. ✅ Use good lighting
3. ✅ Person should wear textured clothing
4. ✅ Camera should be stable/mounted
5. ✅ Person sits/lies still during capture
6. ✅ Clear view of chest area

### For Production
1. ✅ Mount camera securely
2. ✅ Use optimal resolution (640x480 or 1280x720)
3. ✅ Test in actual deployment environment
4. ✅ Adjust config parameters if needed
5. ✅ Monitor performance (FPS, accuracy)

---

## 📈 Performance Optimization

### If processing is slow:

1. **Reduce FPS:**
   ```yaml
   # config.yaml
   breathing_detection:
     fps: 20  # Instead of 30
   ```

2. **Reduce duration:**
   ```yaml
   breathing_detection:
     capture_duration: 10  # Instead of 12
   ```

3. **Lower camera resolution:**
   ```yaml
   camera:
     resolution: [640, 480]  # Instead of [1280, 720]
   ```

4. **Reduce keypoint threshold:**
   ```yaml
   breathing_detection:
     min_keypoints: 5  # Instead of 10
   ```

---

## ✅ Success Checklist

Before moving to integration:

- [ ] Camera opens successfully on RDK X5
- [ ] Can capture frames reliably
- [ ] Breathing detection works with test subject
- [ ] Results make sense (12-20 bpm when breathing)
- [ ] No breathing correctly detected when person holds breath
- [ ] Performance is acceptable (2-5 seconds processing time)

---

## 📞 Need Help?

Common issues and solutions:
1. **Camera not opening** → Check `/dev/video*` devices
2. **Low keypoints** → Better lighting, textured clothing
3. **Slow processing** → Reduce FPS/resolution
4. **Can't select ROI** → Use `--bbox` parameter
5. **Wrong breathing rate** → Adjust config thresholds

---

**Created:** 2025-12-13  
**For:** RDK X5 Platform  
**Status:** Ready for Testing
