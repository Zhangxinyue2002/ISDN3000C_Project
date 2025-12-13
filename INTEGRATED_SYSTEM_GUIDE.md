# 🔄 Integrated Fall Detection + Breathing Detection System

## System Overview

The system now integrates fall detection with breathing detection to provide accurate emergency response. The breathing check acts as a **critical verification step** before triggering emergency calls.

---

## 🎯 Complete Emergency Flow

### Flow Diagram
```
[Camera Monitoring]
        ↓
[Fall Detected?] ──No──> Continue Monitoring
        ↓ Yes
        │
[LED1 ON (Fall Indicator)]
        │
[Start 2-Minute Timer]
        │
        ├─> [Person Recovers?] ──Yes──> [LED1 OFF] → [Back to IDLE]
        │
        ↓ After 2 minutes
        │
[Check Breathing for 12 seconds]
        │
        ├─> [Breathing Detected?] ──Yes──> [False Alarm] → [LED1 OFF] → [Back to IDLE]
        │
        ↓ No Breathing
        │
[LED2 FLASHING (10 seconds)]
   "Press Button 2 to Cancel!"
        │
        ├─> [Button 2 Pressed?] ──Yes──> [Cancelled] → [Both LEDs OFF] → [Back to IDLE]
        │
        ↓ No cancellation
        │
[LED2 SOLID ON]
[Call 999 Emergency]
```

---

## 📋 Detailed Step-by-Step Process

### **Step 1: Initial Fall Detection**
- **Camera**: Continuously captures images every 2 seconds
- **Fall Detector**: Analyzes each frame using YOLOv8 pose estimation
- **When Fall Detected**:
  - ✅ LED1 turns ON (solid red)
  - ✅ System logs: "🚨 FALL DETECTED!"
  - ✅ 2-minute monitoring timer starts
  - ✅ Emergency state: `IDLE` → `FALL_DETECTED`

### **Step 2: 2-Minute Monitoring Period**
- **Purpose**: Wait to see if person can recover on their own
- **System Behavior**:
  - LED1 remains ON (solid)
  - System logs progress every 30 seconds
  - Monitors if person stands up
  
**If person recovers (stands up):**
- ✅ LED1 turns OFF
- ✅ State returns to `IDLE`
- ✅ No emergency triggered
- ✅ System logs: "Person recovered"

**If fall persists for 2 minutes:**
- ⏩ Proceed to breathing check

### **Step 3: Breathing Detection (After 2 Minutes)**
- **Automatic Trigger**: System automatically starts breathing check
- **Process**:
  1. System logs: "⚠️ FALL DURATION EXCEEDED 120s!"
  2. System logs: "Performing breathing check after 2-minute fall..."
  3. State changes to `CHECKING_BREATHING`
  4. Captures 12 seconds of video (360 frames at 30 FPS)
  5. Automatically detects chest region using pose estimation
  6. Analyzes chest movement using SIFT algorithm
  7. Determines if person is breathing

**Breathing Check Results:**

#### ✅ **If Breathing Detected:**
```
✓ Breathing detected (confidence: 0.85)
Person appears to be breathing normally - no emergency
```
- LED1 turns OFF
- State returns to `IDLE`
- Logged as false alarm
- **No emergency call**

#### ❌ **If NO Breathing Detected:**
```
✗ NO BREATHING DETECTED!
Starting 10s emergency countdown...
LED2 will flash - Press Button 2 to cancel!
```
- LED1 remains ON
- LED2 starts FLASHING (1 Hz)
- State changes to `NO_BREATHING` → `COUNTDOWN_ACTIVE`
- **10-second countdown begins**

### **Step 4: Emergency Countdown (10 Seconds)**
- **LED2 Behavior**: Flashes rapidly (1 Hz)
- **System Logs**: 
  ```
  ⏱️ Countdown started: 10 seconds
  LED2 flashing... Press Button 2 to cancel!
  🚨 Emergency call in 5...
  🚨 Emergency call in 4...
  🚨 Emergency call in 3...
  🚨 Emergency call in 2...
  🚨 Emergency call in 1...
  ```

**User Can Cancel:**
- Press **Button 2** anytime during countdown
- Both LEDs turn OFF
- State returns to `IDLE`
- System logs: "Countdown cancelled by user"

**If Not Cancelled:**
- After 10 seconds → Emergency activated

### **Step 5: Emergency Activated**
- **LED2**: Changes from FLASHING to SOLID ON (bright)
- **Action**: System calls 999 (emergency services)
- **State**: `EMERGENCY_ACTIVE`
- **System Logs**: 
  ```
  ⏰ COUNTDOWN EXPIRED - TRIGGERING EMERGENCY CALL
  🚨 EMERGENCY ACTIVATED - CALLING 999!
  ```

---

## 🔴 Manual Emergency Button

### Button 1: Manual Emergency Call
- **Purpose**: Manually trigger emergency call (bypass fall/breathing detection)
- **Behavior**:
  - Press Button 1 at any time
  - LED2 turns SOLID ON immediately (no countdown)
  - Emergency call triggered instantly
  - System logs: "🔴 MANUAL EMERGENCY BUTTON PRESSED!"

---

## 🟢 Cancel Button

### Button 2: Cancel/Stop Emergency
- **Can Cancel During**:
  - ✅ 10-second countdown (LED2 flashing)
  - ✅ Active emergency call (LED2 solid)
  
- **Behavior**:
  - Press Button 2
  - Both LEDs turn OFF
  - Emergency cancelled/resolved
  - State returns to `IDLE`
  - System logs: "🟢 CANCEL BUTTON PRESSED"

---

## 💡 LED Status Reference

| LED State | Meaning | Emergency State |
|-----------|---------|-----------------|
| **Both OFF** | Normal operation | `IDLE` |
| **LED1 ON** | Fall detected, monitoring | `FALL_DETECTED` |
| **LED1 ON** | Checking breathing | `CHECKING_BREATHING` |
| **LED1 ON + LED2 FLASHING** | No breathing! Countdown active (10s) | `COUNTDOWN_ACTIVE` |
| **LED2 SOLID ON** | Emergency active, calling 999 | `EMERGENCY_ACTIVE` |

---

## 🧪 System Testing

### Test Complete Emergency Flow

```bash
# 1. Start the system
cd ~/Project/ISDN3000C_Project
python3 src/main.py

# System will start monitoring...
```

### Test Scenarios

#### **Scenario 1: Fall with Recovery**
1. Trigger fall detection (lie down in camera view)
2. Observe LED1 turn ON
3. Wait 30 seconds, then stand up
4. LED1 turns OFF automatically
5. ✅ No emergency triggered

#### **Scenario 2: Fall with Breathing (False Alarm)**
1. Trigger fall detection (lie down)
2. LED1 turns ON
3. Wait 2 minutes (LED1 stays ON)
4. System checks breathing (12 seconds)
5. If breathing detected: LED1 turns OFF
6. ✅ No emergency triggered (false alarm logged)

#### **Scenario 3: Fall with NO Breathing → Emergency**
1. Trigger fall detection (lie down, hold breath)
2. LED1 turns ON
3. Wait 2 minutes
4. System checks breathing (hold breath still)
5. No breathing detected → LED2 starts FLASHING
6. Wait 10 seconds (don't press button)
7. LED2 changes to SOLID ON
8. ✅ Emergency call triggered

#### **Scenario 4: Cancel During Countdown**
1. Follow Scenario 3 steps 1-5
2. LED2 is FLASHING (countdown active)
3. Press Button 2
4. Both LEDs turn OFF
5. ✅ Emergency cancelled

#### **Scenario 5: Manual Emergency**
1. System in any state
2. Press Button 1
3. LED2 turns SOLID ON immediately
4. ✅ Emergency call triggered

---

## 📊 System Logs

Monitor logs in real-time:
```bash
tail -f data/logs/system.log
```

### Example Log Output

```
2025-12-14 10:30:15 - fall_detector_enhanced - WARNING - 🚨 FALL DETECTED! Image ID: 1234, Confidence: 0.85
2025-12-14 10:30:15 - emergency_controller - WARNING - 🚨 FALL DETECTED! Confidence: 0.85
2025-12-14 10:30:15 - emergency_controller - INFO - Starting 2-minute fall monitoring...
2025-12-14 10:30:15 - emergency_controller - INFO - Fall duration monitor started. Will check breathing after 120s

... [2 minutes pass] ...

2025-12-14 10:32:15 - emergency_controller - WARNING - ⚠️ FALL DURATION EXCEEDED 120s!
2025-12-14 10:32:15 - emergency_controller - WARNING - Triggering breathing check...
2025-12-14 10:32:15 - main - INFO - Performing breathing check after 2-minute fall...
2025-12-14 10:32:15 - main - INFO - Starting breathing detection sequence...
2025-12-14 10:32:15 - main - INFO - Capturing 12s of video at 30 FPS...

... [12 seconds of capture] ...

2025-12-14 10:32:27 - main - INFO - Captured 360 frames for breathing analysis
2025-12-14 10:32:30 - main - INFO - Breathing analysis complete:
2025-12-14 10:32:30 - main - INFO -   - Breathing detected: False
2025-12-14 10:32:30 - main - INFO -   - Confidence: 0.15
2025-12-14 10:32:30 - main - INFO -   - Breathing rate: 0.0 BPM
2025-12-14 10:32:30 - emergency_controller - WARNING - ✗ NO BREATHING DETECTED!
2025-12-14 10:32:30 - emergency_controller - WARNING - Starting 10s emergency countdown...
2025-12-14 10:32:30 - emergency_controller - WARNING - LED2 will flash - Press Button 2 to cancel!
2025-12-14 10:32:30 - emergency_controller - INFO - ⏱️ Countdown started: 10 seconds
2025-12-14 10:32:35 - emergency_controller - WARNING - 🚨 Emergency call in 5...
2025-12-14 10:32:36 - emergency_controller - WARNING - 🚨 Emergency call in 4...
2025-12-14 10:32:37 - emergency_controller - WARNING - 🚨 Emergency call in 3...
2025-12-14 10:32:38 - emergency_controller - WARNING - 🚨 Emergency call in 2...
2025-12-14 10:32:39 - emergency_controller - WARNING - 🚨 Emergency call in 1...
2025-12-14 10:32:40 - emergency_controller - WARNING - ⏰ COUNTDOWN EXPIRED - TRIGGERING EMERGENCY CALL
2025-12-14 10:32:40 - emergency_controller - WARNING - 🚨 EMERGENCY ACTIVATED - CALLING 999!
```

---

## ⚙️ Configuration

Key settings in `config/config.yaml`:

```yaml
emergency:
  # 2-minute fall duration before breathing check
  fall_duration_threshold: 120  # seconds
  
  # 10-second countdown before emergency call
  countdown_duration: 10  # seconds
  
  # Emergency contact number
  contact_number: "999"
  
  # Enable/disable features
  auto_trigger: true     # Enable automatic fall detection
  manual_trigger: true   # Enable manual emergency button

breathing_detection:
  # Breathing analysis parameters
  capture_duration: 12   # seconds of video
  fps: 30               # frames per second
  min_breathing_rate: 8  # minimum breaths per minute
  max_breathing_rate: 30 # maximum breaths per minute
```

---

## 🔧 Troubleshooting

### Breathing Detection Not Working
```bash
# Test breathing detection separately
python3 test_breathing_rdk.py

# This will:
# 1. Capture camera frame
# 2. Detect person and chest region
# 3. Save visual results (captured_frame.jpg, chest_detection_result.jpg)
# 4. Run breathing analysis
# 5. Save analysis result (breathing_analysis_result.jpg)
```

### Check System State
```bash
# View system logs
tail -n 100 data/logs/system.log

# Check emergency controller state
grep "Emergency state:" data/logs/system.log | tail -n 10
```

### Camera Issues
```bash
# Verify camera access
ls -l /dev/video*

# Test camera directly
python3 preview_camera.py
```

---

## 📈 System Statistics

Access via web interface: `http://YOUR_RDK_IP:5000`

**Statistics Displayed**:
- Total falls detected
- Emergency calls made
- False alarms (breathing detected after fall)
- System uptime
- Images captured

---

## ✅ Safety Features

1. **False Alarm Prevention**: Breathing check prevents unnecessary emergency calls
2. **User Control**: Button 2 allows cancellation anytime during countdown
3. **Visual Feedback**: LEDs clearly indicate system state
4. **Manual Override**: Button 1 for immediate emergency call when needed
5. **Recovery Detection**: Automatically cancels if person stands up
6. **Comprehensive Logging**: All events logged for review

---

## 📝 Summary

| Event | LED1 | LED2 | Duration | Action |
|-------|------|------|----------|--------|
| Fall detected | ON | OFF | 2 minutes | Monitor for recovery |
| Person recovers | OFF | OFF | - | Cancel, back to IDLE |
| 2 min passed | ON | OFF | 12 seconds | Check breathing |
| Breathing OK | OFF | OFF | - | False alarm, back to IDLE |
| No breathing | ON | FLASH | 10 seconds | Countdown (can cancel) |
| Countdown expires | ON | SOLID | Until resolved | Call 999 |
| Button 2 pressed | OFF | OFF | - | Cancel/resolve |
| Button 1 pressed | OFF | SOLID | Until resolved | Immediate 999 call |

---

## 🚀 Next Steps

1. **Test the integrated system** with various scenarios
2. **Adjust thresholds** if needed (fall duration, breathing parameters)
3. **Monitor false alarm rate** and tune breathing detection sensitivity
4. **Configure actual 999 calling** when ready for production
5. **Add notifications** (SMS, app push) for emergency alerts

---

## 🆘 Emergency Contact

For system issues or questions:
- Check logs: `data/logs/system.log`
- Review test results: `test_results.csv`
- Consult: `README.md`, `EMERGENCY_SYSTEM_GUIDE.md`, `BREATHING_MODULE_COMPLETE.md`
