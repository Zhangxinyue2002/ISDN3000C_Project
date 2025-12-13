# 🔄 Updated System Logic - December 14, 2025

## ⚡ New Emergency Flow

### 🎯 Two Scenarios for LED2 Flash (Emergency Countdown)

#### Scenario 1: Fall + No Breathing → Immediate Emergency
```
Fall Detected → Check Breathing Immediately
      ↓
No Breathing Detected
      ↓
LED2 FLASHING (10 seconds)
      ↓
LED2 SOLID (Call 999)
```

#### Scenario 2: Fall + Breathing OK, but > 1 Minute → Emergency
```
Fall Detected → Check Breathing Immediately
      ↓
Breathing OK → LED1 ON → Monitor Duration
      ↓
Fall Persists > 1 Minute
      ↓
LED2 FLASHING (10 seconds)
      ↓
LED2 SOLID (Call 999)
```

---

## 🔑 Key Changes from Previous Version

| Feature | Old Logic | New Logic |
|---------|-----------|-----------|
| **Fall Duration** | 2 minutes | **1 minute** |
| **Breathing Check** | After 2 minutes | **Immediately** when fall detected |
| **LED2 Trigger (No Breathing)** | After 2 min + breathing check | **Immediate** after breathing check |
| **LED2 Trigger (Breathing OK)** | No trigger if breathing | **1 minute** of fall |
| **Button 2 Priority** | Cancel countdown only | **HIGHEST - Reset everything anytime** |

---

## 💡 LED States

| State | LED1 | LED2 | Meaning |
|-------|------|------|---------|
| **Normal** | OFF | OFF | Monitoring for falls |
| **Fall Detected** | ON | OFF | Person fallen, checking breathing |
| **Breathing Check** | ON | OFF | Analyzing chest movement (12s) |
| **No Breathing!** | ON | FLASH | Emergency! 10s to cancel |
| **Fall > 1 min** | ON | FLASH | Person fallen too long! 10s to cancel |
| **Emergency Active** | ON | SOLID | Calling 999 |

---

## 🔘 Button Functions

### Button 1: Manual Emergency Call
- **When**: Press anytime
- **Effect**: LED2 goes SOLID immediately
- **Action**: Call 999 directly (no countdown)

### Button 2: SYSTEM RESET (Highest Priority)
- **When**: Press anytime - during any state
- **Effect**: 
  - Turn OFF LED1
  - Turn OFF LED2
  - Stop all monitoring
  - Stop countdown
  - Cancel emergency
- **Action**: Reset to normal fall detection mode
- **Priority**: HIGHEST - overrides everything

---

## 📊 Complete Flow Diagram

```
                    [IDLE - Monitoring]
                           ↓
                    [Fall Detected]
                           ↓
                    LED1 ON + Check Breathing
                    (12 seconds analysis)
                           ↓
            ┌──────────────┴──────────────┐
            ↓                             ↓
    [Breathing Detected]          [No Breathing Detected]
            ↓                             ↓
    LED1 ON (monitoring)          LED2 FLASHING immediately
    Start 1-minute timer                  ↓
            ↓                      10-second countdown
            │                             ↓
    Person  │  Fall                Button 2?
    stands  │  persists                   ↓
    up?     │  > 1 min          ┌─────────┴─────────┐
            ↓                   ↓                   ↓
    ┌───────┴────────┐   LED2 FLASHING          LED2 SOLID
    ↓                ↓   (emergency)            (Call 999!)
LED1 OFF      LED2 FLASHING
(Reset)       10s countdown
                    ↓
            Button 2 pressed?
                    ↓
            ┌───────┴────────┐
            ↓                ↓
        Both LEDs OFF    LED2 SOLID
        (Reset)          (Call 999!)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🟢 BUTTON 2 (ANYTIME) → ALL LEDs OFF, RESET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎬 Example Scenarios

### Example 1: Person Falls, Not Breathing
```
Time  | Event                          | LED1  | LED2   | State
------|--------------------------------|-------|--------|------------------
00:00 | Normal monitoring              | OFF   | OFF    | IDLE
00:05 | Fall detected                  | ON    | OFF    | FALL_DETECTED
00:05 | Start breathing check (12s)    | ON    | OFF    | CHECKING_BREATHING
00:17 | No breathing detected!         | ON    | FLASH  | NO_BREATHING
00:17 | 10s countdown starts           | ON    | FLASH  | COUNTDOWN_ACTIVE
00:27 | Countdown expires              | ON    | SOLID  | EMERGENCY_ACTIVE
      | Calling 999!                   |       |        |
```

### Example 2: Person Falls, Breathing OK, Falls > 1 Min
```
Time  | Event                          | LED1  | LED2   | State
------|--------------------------------|-------|--------|------------------
00:00 | Normal monitoring              | OFF   | OFF    | IDLE
00:05 | Fall detected                  | ON    | OFF    | FALL_DETECTED
00:05 | Start breathing check (12s)    | ON    | OFF    | CHECKING_BREATHING
00:17 | Breathing detected!            | ON    | OFF    | FALL_DETECTED
00:17 | Monitoring fall duration...    | ON    | OFF    | FALL_DETECTED
01:05 | Fall duration > 1 minute!      | ON    | FLASH  | COUNTDOWN_ACTIVE
01:05 | 10s countdown starts           | ON    | FLASH  | COUNTDOWN_ACTIVE
01:15 | Countdown expires              | ON    | SOLID  | EMERGENCY_ACTIVE
      | Calling 999!                   |       |        |
```

### Example 3: Person Falls, Breathing OK, Stands Up
```
Time  | Event                          | LED1  | LED2   | State
------|--------------------------------|-------|--------|------------------
00:00 | Normal monitoring              | OFF   | OFF    | IDLE
00:05 | Fall detected                  | ON    | OFF    | FALL_DETECTED
00:05 | Start breathing check (12s)    | ON    | OFF    | CHECKING_BREATHING
00:17 | Breathing detected!            | ON    | OFF    | FALL_DETECTED
00:17 | Monitoring fall duration...    | ON    | OFF    | FALL_DETECTED
00:40 | Person stands up               | OFF   | OFF    | IDLE
      | System reset to monitoring     |       |        |
```

### Example 4: Button 2 Pressed During Countdown
```
Time  | Event                          | LED1  | LED2   | State
------|--------------------------------|-------|--------|------------------
00:00 | (Any state with LEDs on)       | ON    | FLASH  | COUNTDOWN_ACTIVE
00:03 | Button 2 pressed!              | OFF   | OFF    | IDLE
      | System reset                   |       |        |
```

---

## 🔧 Configuration

**File:** `config/config.yaml`

```yaml
emergency:
  countdown_duration: 10           # 10 seconds LED2 flashing
  fall_duration_threshold: 60      # 1 minute (changed from 120)
  contact_number: "999"
  enable_actual_call: false        # Set true for production

breathing_detection:
  capture_duration: 12             # 12 seconds video capture
  fps: 30                          # 30 frames per second
```

---

## 🚀 Testing the New Logic

### Test Scenario 1: No Breathing Detection
1. Start system: `python3 src/main.py`
2. Lie down in camera view (trigger fall)
3. Hold breath during 12s breathing check
4. LED2 should start FLASHING immediately after check
5. Wait 10s or press Button 2 to cancel

### Test Scenario 2: Breathing OK but > 1 Min Fall
1. Start system: `python3 src/main.py`
2. Lie down in camera view
3. Breathe normally during 12s check
4. Stay lying down for > 1 minute
5. LED2 should start FLASHING at 1 minute mark
6. Press Button 2 to cancel or wait 10s

### Test Scenario 3: Button 2 Reset
1. During any scenario above
2. Press Button 2 at any time
3. Both LEDs should turn OFF immediately
4. System returns to normal monitoring

### Test Breathing Detection Separately
```bash
python3 test_breathing_rdk.py
```

---

## 📋 Summary of Changes

### Code Files Modified:
1. **config/config.yaml**
   - `fall_duration_threshold: 120` → `60` (1 minute)

2. **src/emergency_controller.py**
   - Updated `fall_duration_threshold` to read from config
   - Modified `_monitor_fall_duration()` to trigger countdown after 1 min
   - Modified `handle_breathing_result()`:
     - If breathing: Continue monitoring (don't reset)
     - If no breathing: Trigger countdown immediately
   - Added `reset_to_idle()` method for Button 2 highest priority reset

3. **src/main.py**
   - Modified fall detection to check breathing immediately
   - Updated `_on_cancel_emergency()` to call `reset_to_idle()`

---

## ⚠️ Important Notes

1. **Breathing Check is Immediate**: When fall is detected, breathing check starts right away (no 2-minute wait)

2. **Two Paths to LED2 Flash**:
   - Path 1: No breathing detected → Immediate LED2 flash
   - Path 2: Breathing OK but fall > 1 min → LED2 flash at 1 min

3. **Button 2 is Supreme**: Can reset system from ANY state at ANY time

4. **LED1 Stays ON**: Once fall detected, LED1 stays ON until:
   - Person stands up (fall no longer detected)
   - Button 2 pressed (system reset)

---

## 🎓 Quick Reference

| Condition | LED1 | LED2 | Action |
|-----------|------|------|--------|
| Fall + No breath | ON | FLASH | Countdown 10s |
| Fall + Breath + >1min | ON | FLASH | Countdown 10s |
| Fall + Breath + <1min | ON | OFF | Keep monitoring |
| Button 1 pressed | - | SOLID | Call 999 now |
| Button 2 pressed | OFF | OFF | Reset everything |

---

**Updated:** 2025-12-14  
**Previous Version:** 2-minute wait with breathing check  
**Current Version:** Immediate breathing check + 1-minute threshold
