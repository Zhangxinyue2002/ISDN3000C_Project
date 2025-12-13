# Emergency System Operation Guide

## Overview

The emergency system has two main triggers:
1. **Automatic**: Fall detected for 2+ minutes
2. **Manual**: User presses Button 1

Both scenarios have different LED behaviors to indicate what's happening.

---

## Hardware Components

### LEDs
- **LED 1 (Fall Indicator)**: Connected to GPIO Pin 22
- **LED 2 (Emergency Indicator)**: Connected to GPIO Pin 33

### Buttons
- **Button 1 (Emergency Call)**: Connected to GPIO Pin 11
- **Button 2 (Cancel)**: Connected to GPIO Pin 13

---

## LED States

### LED 1 (Fall Indicator)
| State | Meaning |
|-------|---------|
| OFF | Normal operation - no fall detected |
| ON | Fall detected - system monitoring |

### LED 2 (Emergency Indicator)
| State | Meaning |
|-------|---------|
| OFF | Normal operation |
| **FLASHING** | **Emergency countdown active (10 seconds)** - Press Button 2 to cancel! |
| **SOLID** | **Emergency call active** - Calling 999 |

---

## Operational Scenarios

### Scenario 1: Automatic Fall Detection (2+ Minutes)

**Timeline:**
```
t=0s:     Fall detected
          ↓
          LED 1: ON
          System: Monitoring fall duration
          
t=120s:   Fall persists for 2 minutes
(2 min)   ↓
          LED 2: FLASHING (10-second countdown starts)
          User can press Button 2 to cancel
          
t=130s:   If NOT cancelled
          ↓
          LED 2: SOLID
          System: Calling 999
          
          User can still press Button 2 to stop call
```

**What you'll see:**
1. Person falls → Camera captures → AI detects fall
2. **LED 1 turns ON** (fall indicator)
3. System monitors if person gets up
4. **After 2 minutes of continuous fall**:
   - **LED 2 starts FLASHING** (you have 10 seconds)
   - System announces: "Emergency countdown started"
5. **Two options:**
   - **Cancel**: Press Button 2 → Both LEDs turn OFF
   - **No action**: After 10s → LED 2 goes SOLID → Calling 999

**Logs you'll see:**
```
🚨 FALL DETECTED! Confidence: 0.95
Starting 2-minute fall monitoring...
Fall duration: 30s / 120s
Fall duration: 60s / 120s
Fall duration: 90s / 120s
Fall duration: 120s / 120s
⚠️  FALL DURATION EXCEEDED 120s!
Starting emergency countdown...
⏱️  Countdown started: 10 seconds
🚨 Emergency call in 5...
🚨 Emergency call in 4...
🚨 Emergency call in 3...
🚨 Emergency call in 2...
🚨 Emergency call in 1...
⏰ COUNTDOWN EXPIRED - TRIGGERING EMERGENCY CALL
🚨🚨🚨 EMERGENCY TRIGGERED 🚨🚨🚨
```

---

### Scenario 2: Manual Emergency (Button 1)

**Timeline:**
```
t=0s:     User presses Button 1
          ↓
          LED 2: SOLID (immediately, no flashing)
          System: Calling 999
          
          User can press Button 2 to cancel
```

**What you'll see:**
1. Person presses Button 1 (red emergency button)
2. **LED 2 turns SOLID immediately** (no flashing, no countdown)
3. System: "Manual emergency triggered - Calling 999"
4. **To cancel**: Press Button 2 → LED 2 turns OFF

**Logs you'll see:**
```
🔴 MANUAL EMERGENCY BUTTON PRESSED!
🔴 MANUAL EMERGENCY TRIGGERED - Calling 999 immediately!
[MANUAL] SIMULATED call to 999
```

---

### Scenario 3: False Alarm Cancellation

**During Countdown (LED 2 Flashing):**
```
1. System detects fall → LED 1 ON
2. After 2 minutes → LED 2 FLASHING
3. Person is okay → Press Button 2
4. Result: Both LEDs turn OFF
5. System returns to normal monitoring
```

**During Active Call (LED 2 Solid):**
```
1. Emergency call active → LED 2 SOLID
2. False alarm → Press Button 2
3. Result: LED 2 turns OFF
4. System stops emergency call
5. Returns to normal monitoring
```

**Logs you'll see:**
```
🟢 CANCEL BUTTON PRESSED
Cancelling emergency countdown...
✅ Countdown cancelled: User pressed cancel button
Returned to normal monitoring
```

---

## Testing the System

### Test 1: Hardware Test
```bash
python3 test_components.py
```

**Expected:**
- LED 1 blinks
- LED 2 goes solid
- LED 2 flashes
- Message: "Press buttons to test"

### Test 2: Emergency Logic Test
```bash
python3 test_emergency_logic.py
```

**Menu options:**
1. Test manual emergency (Button 1)
2. Test fall duration (2 min → 10s for testing)
3. Test countdown expiration
4. Interactive test (real hardware)

### Test 3: Full System Test
```bash
# Start the system
./scripts/run.sh

# Watch the logs
tail -f data/logs/system.log | grep -E "FALL|EMERGENCY|Button"
```

---

## Configuration

Edit `config/config.yaml` to adjust behavior:

```yaml
emergency:
  countdown_duration: 10       # Seconds of LED2 flashing before calling 999
  fall_duration_threshold: 120 # Seconds of fall before triggering countdown (2 minutes)
  contact_number: "999"
  enable_actual_call: false    # Set to true for production
  manual_trigger: true         # Enable Button 1 manual emergency
  auto_trigger: true           # Enable automatic fall detection
```

---

## Troubleshooting

### LED 1 not turning ON when fall detected
**Check:**
1. Fall detection working? Run `python3 test_fall_model.py`
2. GPIO connection correct? Run `python3 test_components.py`
3. Check logs: `grep "FALL DETECTED" data/logs/system.log`

### LED 2 not flashing during countdown
**Check:**
1. GPIO wiring to Pin 33
2. Emergency controller state: Check logs for "Countdown started"
3. Test LED directly: `python3 test_components.py`

### Button 1 not triggering emergency
**Check:**
1. Button wiring: 3.3V → Button → Pin 11 → 10kΩ → GND
2. Test button: Press and check logs for "MANUAL EMERGENCY BUTTON PRESSED"
3. Run: `python3 test_emergency_logic.py` → Option 4 (Interactive)

### Button 2 not cancelling
**Check:**
1. Button wiring: 3.3V → Button → Pin 13 → 10kΩ → GND
2. Check logs for "CANCEL BUTTON PRESSED"
3. Ensure countdown is actually active (LED 2 flashing)

### System not detecting 2-minute fall duration
**Check:**
1. Fall detection continuous? Check `grep "FALL DETECTED" data/logs/system.log`
2. System state: Look for "Starting 2-minute fall monitoring"
3. Check config: `fall_duration_threshold: 120` in config.yaml

---

## Safety Notes

⚠️ **IMPORTANT:**

1. **Battery Backup**: Consider UPS for continuous operation
2. **Network**: Emergency calls need internet (for future Twilio integration)
3. **Testing**: Always test after wiring changes
4. **False Alarms**: Adjust `fall_duration_threshold` if too many false alarms
5. **Response Time**: 
   - Manual: Immediate (Button 1)
   - Automatic: 2 minutes + 10 seconds = 2:10 total

---

## Future Enhancements (Not Implemented Yet)

The following features will be added later:

1. **Breathing Detection Integration**:
   - If fall detected + no breathing for 10 seconds → Countdown
   - Currently: Only 2-minute fall duration implemented

2. **Actual Phone Calls**:
   - Integration with Twilio/SMS gateway
   - Currently: Simulated calls only

3. **Remote Monitoring**:
   - Web dashboard notifications
   - Mobile app alerts

---

## Quick Reference

### LED Behaviors
| LED 1 | LED 2 | Meaning |
|-------|-------|---------|
| OFF | OFF | Normal operation |
| ON | OFF | Fall detected, monitoring |
| ON | FLASHING | Emergency countdown (10s) |
| ON | SOLID | Calling 999 (automatic) |
| OFF | SOLID | Calling 999 (manual Button 1) |

### Button Actions
| Button | Action | Result |
|--------|--------|--------|
| Button 1 | Press | LED 2 SOLID → Call 999 immediately |
| Button 2 | During flash | Cancel countdown → Both LEDs OFF |
| Button 2 | During solid | Stop emergency → LED 2 OFF |

---

**Last Updated:** December 13, 2025  
**Version:** 1.0  
**Status:** Production Ready (Breathing integration pending)
