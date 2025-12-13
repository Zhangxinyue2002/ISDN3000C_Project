# Implementation Summary: Emergency System with LEDs and Buttons

## Date: December 13, 2025

## Overview
Implemented complete emergency response system with 2 LEDs and 2 buttons supporting:
- Automatic emergency (2+ minute fall detection)
- Manual emergency (Button 1 press)
- Cancellation capability (Button 2)

---

## What Was Implemented

### 1. Emergency Controller Updates
**File:** `src/emergency_controller.py`

**New Features:**
- ✅ 2-minute fall duration monitoring
- ✅ Fall monitoring thread that tracks fall persistence
- ✅ Manual emergency trigger (direct call, no countdown)
- ✅ Enhanced countdown with 10-second LED flashing
- ✅ Cancel functionality for both countdown and active emergency

**Key Methods Added:**
- `_monitor_fall_duration()`: Tracks if fall persists for 2+ minutes
- `stop_fall_monitoring()`: Stops monitoring when person recovers
- `trigger_emergency(manual=True/False)`: Handles both manual and automatic triggers
- Enhanced `cancel_countdown()`: Cancels countdown and turns off both LEDs
- Enhanced `resolve_emergency()`: Resolves active emergency from Button 2

### 2. LED Behavior Implementation
**LED 1 (Fall Indicator) - GPIO Pin 22:**
- OFF: Normal operation
- ON: Fall detected

**LED 2 (Emergency Indicator) - GPIO Pin 33:**
- OFF: Normal operation
- FLASHING: Emergency countdown (10 seconds)
- SOLID: Emergency call active

### 3. Button Behavior Implementation
**Button 1 (Manual Emergency) - GPIO Pin 11:**
- Press → LED 2 goes SOLID immediately (no flashing)
- Calls 999 directly
- Press Button 2 to cancel

**Button 2 (Cancel) - GPIO Pin 13:**
- During countdown → Cancel countdown, both LEDs OFF
- During emergency → Stop call, both LEDs OFF

### 4. System Scenarios

#### Scenario A: 2+ Minute Fall (Automatic)
```
Fall detected → LED1 ON → Wait 2 min → LED2 FLASHING (10s) → LED2 SOLID (call 999)
                                            ↓
                                     Button 2 cancels
```

#### Scenario B: Manual Emergency
```
Button 1 press → LED2 SOLID (immediate, no flash) → Call 999
                        ↓
                 Button 2 cancels
```

### 5. Configuration Updates
**File:** `config/config.yaml`

Added parameters:
```yaml
emergency:
  countdown_duration: 10  # LED2 flash time
  fall_duration_threshold: 120  # 2 minutes
  manual_trigger: true
  auto_trigger: true
```

### 6. Documentation Created

#### README.md
- ✅ Complete hardware wiring guide with diagrams
- ✅ Pin assignment table
- ✅ Breadboard layout
- ✅ Component list with specifications
- ✅ Step-by-step wiring instructions
- ✅ LED behavior descriptions
- ✅ Button function explanations
- ✅ System scenarios with timelines
- ✅ Testing procedures
- ✅ Troubleshooting section

#### EMERGENCY_SYSTEM_GUIDE.md (NEW)
- ✅ Comprehensive operation guide
- ✅ LED state reference table
- ✅ Button action reference
- ✅ Detailed scenarios with logs
- ✅ Configuration guide
- ✅ Troubleshooting specific to emergency system

#### test_emergency_logic.py (NEW)
- ✅ Automated test scenarios
- ✅ Manual emergency test
- ✅ Fall duration test (simulated)
- ✅ Countdown expiration test
- ✅ Interactive test with real hardware

---

## File Changes Summary

### Modified Files
1. **src/emergency_controller.py**
   - Added fall duration monitoring (2 minutes)
   - Added manual vs automatic trigger distinction
   - Enhanced LED control logic
   - Improved cancellation handling

2. **config/config.yaml**
   - Added `fall_duration_threshold: 120`
   - Added detailed comments explaining LED and button behavior

3. **README.md**
   - Added complete "Hardware Wiring Guide" section
   - Added GPIO pin tables
   - Added wiring diagrams (ASCII art)
   - Added LED behavior descriptions
   - Added button function explanations
   - Added breadboard layout guide
   - Added component specifications
   - Updated system architecture section

### New Files Created
1. **test_emergency_logic.py**
   - Complete test suite for emergency system
   - 4 test scenarios
   - Interactive mode for hardware testing

2. **EMERGENCY_SYSTEM_GUIDE.md**
   - Standalone operation guide
   - Reference tables for LED/button states
   - Detailed scenario walkthroughs
   - Troubleshooting guide

---

## Hardware Requirements

### Components Needed
- 2× Push buttons (momentary, normally-open)
- 2× LEDs (any color, red recommended)
- 2× 220Ω resistors (for LEDs)
- 2× 10kΩ resistors (for button pull-down)
- Jumper wires (12 minimum)
- Breadboard (optional but recommended)

### Connections

| Component | Physical Pin | GPIO | Connection |
|-----------|--------------|------|------------|
| Button 1 | Pin 11 | GPIO 17 | 3.3V → Button → Pin 11 → 10kΩ → GND |
| Button 2 | Pin 13 | GPIO 27 | 3.3V → Button → Pin 13 → 10kΩ → GND |
| LED 1 | Pin 22 | GPIO 25 | Pin 22 → 220Ω → LED+ → LED- → GND |
| LED 2 | Pin 33 | GPIO 13 | Pin 33 → 220Ω → LED+ → LED- → GND |

---

## Testing Instructions

### Step 1: Hardware Test
```bash
python3 test_components.py
```
Verify:
- LED 1 blinks
- LED 2 goes solid
- LED 2 flashes
- Buttons detected when pressed

### Step 2: Logic Test
```bash
python3 test_emergency_logic.py
```
Select option:
- 1: Manual emergency test
- 2: Fall duration test (2min → 10s simulated)
- 3: Countdown expiration test
- 4: Interactive test (real hardware)

### Step 3: Full System Test
```bash
# Start system
./scripts/run.sh

# In another terminal, watch logs
tail -f data/logs/system.log | grep -E "FALL|EMERGENCY|Button"

# Test scenarios:
# 1. Press Button 1 → LED 2 should go solid
# 2. Press Button 2 → LED 2 should turn off
# 3. Wait for fall detection → LED 1 ON → wait → LED 2 flash → LED 2 solid
```

---

## What's NOT Implemented Yet

The following will be added when breathing detection is tested:

1. **Breathing Integration**:
   - Fall detected → Check breathing → If no breathing → Countdown
   - Currently: Only 2-minute duration implemented

2. **Actual Phone Calls**:
   - Twilio/SMS gateway integration
   - Currently: Simulated calls only

3. **Remote Notifications**:
   - Web dashboard alerts
   - Mobile app notifications

---

## How to Use

### Daily Operation

1. **Start System:**
   ```bash
   cd /home/sunrise/Project/ISDN3000C_Project
   source venv/bin/activate
   ./scripts/run.sh
   ```

2. **Monitor Status:**
   - Watch LEDs for fall/emergency indicators
   - Check web interface: http://localhost:5000

3. **In Emergency:**
   - **Automatic**: System detects fall → Wait 2 min → LED 2 flashes → Press Button 2 to cancel
   - **Manual**: Press Button 1 → LED 2 solid → Calling 999

4. **Cancel Emergency:**
   - Press Button 2 anytime → Both LEDs OFF

### Wiring Your Hardware

Follow the comprehensive guide in:
- **README.md** → Section: "⚡ Hardware Wiring Guide"
- **EMERGENCY_SYSTEM_GUIDE.md** → Section: "Hardware Components"

Key steps:
1. Connect LEDs with 220Ω resistors
2. Connect buttons with 10kΩ pull-down resistors
3. Use 3.3V power (NOT 5V)
4. Test each component individually

---

## Code Architecture

### Flow Diagram

```
main.py
  ├─ CameraService (captures every 2s)
  ├─ FallDetectorEnhanced (analyzes images)
  ├─ EmergencyController
  │    ├─ handle_fall_detected()
  │    │    └─ _monitor_fall_duration() [2 min timer]
  │    ├─ trigger_emergency(manual=True/False)
  │    ├─ start_countdown() [10s LED2 flash]
  │    └─ cancel_countdown() / resolve_emergency()
  └─ GPIOHandler
       ├─ Button 1 → on_manual_emergency()
       ├─ Button 2 → on_cancel_emergency()
       ├─ LED 1 (Fall)
       └─ LED 2 (Emergency)
```

### State Machine

```
IDLE
  ↓ (fall detected)
FALL_DETECTED
  ↓ (2 minutes elapsed)
COUNTDOWN_ACTIVE (LED2 flashing)
  ↓ (10s elapsed OR Button 1 pressed)
EMERGENCY_ACTIVE (LED2 solid)
  ↓ (Button 2 pressed)
IDLE
```

---

## Configuration Reference

### Adjust Timing
Edit `config/config.yaml`:

```yaml
emergency:
  # How long LED2 flashes before triggering call
  countdown_duration: 10
  
  # How long fall must persist before starting countdown
  fall_duration_threshold: 120  # 2 minutes
  
  # Enable/disable triggers
  manual_trigger: true   # Button 1 works
  auto_trigger: true     # Fall detection works
  
  # Actual calls (set to true in production)
  enable_actual_call: false
```

### Adjust GPIO Pins
If your wiring is different, edit `config/config.yaml`:

```yaml
gpio:
  button_call_999: 11   # Physical pin for Button 1
  button_stop_call: 13  # Physical pin for Button 2
  led_fall: 22          # Physical pin for LED 1
  led_emergency: 33     # Physical pin for LED 2
```

---

## Troubleshooting Quick Reference

| Problem | Check | Solution |
|---------|-------|----------|
| LED 1 not ON when fall detected | Logs, wiring | Run test_fall_model.py |
| LED 2 not flashing | Countdown active? | Check logs for "Countdown started" |
| Button 1 no response | Wiring, pull-down | Test with test_components.py |
| Button 2 not cancelling | Button wiring | Check logs for "CANCEL BUTTON PRESSED" |
| Fall not detected | Camera, model | Check test_fall_batch.py |
| 2-min timer not working | Fall persistent? | Check "Fall duration: X/120s" in logs |

---

## Support Files

| File | Purpose |
|------|---------|
| README.md | Complete system documentation with wiring |
| EMERGENCY_SYSTEM_GUIDE.md | Detailed operation guide |
| test_emergency_logic.py | Automated testing suite |
| test_components.py | Hardware component testing |
| config/config.yaml | System configuration |

---

## Next Steps (For You)

1. **Wire the Hardware:**
   - Follow README.md → "⚡ Hardware Wiring Guide"
   - Use breadboard for easier connections
   - Double-check polarity and resistor values

2. **Test Hardware:**
   ```bash
   python3 test_components.py
   ```

3. **Test Emergency Logic:**
   ```bash
   python3 test_emergency_logic.py
   # Choose option 4 for interactive test
   ```

4. **Run Full System:**
   ```bash
   ./scripts/run.sh
   ```

5. **Verify Scenarios:**
   - Test Button 1 → LED 2 solid
   - Test Button 2 → LEDs off
   - Simulate fall (use test image) → Wait → Observe LED sequence

6. **When Breathing Detection Ready:**
   - Let me know
   - I'll integrate breathing check into the flow
   - Flow will be: Fall → Check breathing → If no breathing → Countdown

---

## Questions?

Refer to:
1. **Wiring**: README.md → Hardware Wiring Guide
2. **Operation**: EMERGENCY_SYSTEM_GUIDE.md
3. **Testing**: Run test_emergency_logic.py
4. **Troubleshooting**: Both README.md and EMERGENCY_SYSTEM_GUIDE.md

---

**Implementation Complete! ✅**

The emergency system is now ready for hardware testing. Follow the wiring guide, connect your components, and test each scenario using the provided test scripts.
