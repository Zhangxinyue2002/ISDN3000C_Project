# 🎨 Visual System Flow - Integrated Fall + Breathing Detection

## 📊 Complete System State Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SYSTEM STARTUP                                │
│                         Camera Monitoring                             │
│                              (IDLE)                                   │
│                          LED1: OFF                                    │
│                          LED2: OFF                                    │
└─────────────┬────────────────────────────────────────────────────────┘
              │
              ↓
      ┌───────────────┐
      │ Fall Detected? │
      └───┬───────┬───┘
          │ No    │ Yes
          ↓       ↓
    Continue   ┌─────────────────────────────────────────┐
    Monitor    │     FALL DETECTED (State 1)             │
               │     LED1: ON (Solid Red)                │
               │     LED2: OFF                           │
               │     Duration Timer: 0s → 120s           │
               └─────────────┬───────────────────────────┘
                             │
                             ↓
                     ┌───────────────┐
                     │ Wait 2 minutes │
                     │  (120 seconds) │
                     └───┬───────┬───┘
                         │       │
                Person   │       │  Fall persists
              Recovers   │       │  for 2+ minutes
                (stands  │       │
                  up)    │       │
                         ↓       ↓
                  ┌──────────┐  ┌────────────────────────────────┐
                  │  IDLE    │  │  CHECKING_BREATHING (State 2)  │
                  │ LED1 OFF │  │  LED1: ON                      │
                  │ LED2 OFF │  │  LED2: OFF                     │
                  └──────────┘  │  Capturing: 12 seconds @ 30fps │
                                │  Analyzing chest movement      │
                                └─────────────┬──────────────────┘
                                              │
                                              ↓
                                    ┌──────────────────┐
                                    │ Breathing Result │
                                    └────┬────────┬────┘
                                         │        │
                            Breathing    │        │   No Breathing
                             Detected    │        │    Detected
                              (Normal)   │        │   (Emergency!)
                                         ↓        ↓
                          ┌──────────────────┐  ┌──────────────────────────────┐
                          │  FALSE ALARM     │  │  NO_BREATHING (State 3)      │
                          │  LED1: OFF       │  │  LED1: ON                    │
                          │  LED2: OFF       │  │  LED2: OFF                   │
                          │  Back to IDLE    │  │  Preparing countdown...      │
                          └──────────────────┘  └────────────┬─────────────────┘
                                                              │
                                                              ↓
                                              ┌────────────────────────────────┐
                                              │ COUNTDOWN_ACTIVE (State 4)     │
                                              │ LED1: ON                       │
                                              │ LED2: FLASHING (1 Hz)          │
                                              │ Timer: 10 → 9 → 8 → ... → 0   │
                                              │ "Press Button 2 to Cancel!"    │
                                              └───┬────────────────────┬───────┘
                                                  │                    │
                                      Button 2    │                    │  No Cancel
                                       Pressed    │                    │  (Timeout)
                                                  ↓                    ↓
                                  ┌─────────────────────┐  ┌─────────────────────────┐
                                  │ COUNTDOWN_CANCELLED │  │ EMERGENCY_ACTIVE        │
                                  │ LED1: OFF           │  │ LED1: ON                │
                                  │ LED2: OFF           │  │ LED2: SOLID (Bright)    │
                                  │ Back to IDLE        │  │ 🚨 CALLING 999! 🚨      │
                                  └─────────────────────┘  └───────┬─────────────────┘
                                                                   │
                                                       Button 2    │
                                                        Pressed    │
                                                                   ↓
                                                      ┌──────────────────────┐
                                                      │ EMERGENCY_RESOLVED   │
                                                      │ LED1: OFF            │
                                                      │ LED2: OFF            │
                                                      │ Back to IDLE         │
                                                      └──────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    MANUAL EMERGENCY PATH                              │
│                    (Anytime, from any state)                          │
└──────────────────────────────────────────────────────────────────────┘
                                │
                    Button 1 Pressed (Call 999 Button)
                                │
                                ↓
                    ┌───────────────────────────┐
                    │  EMERGENCY_ACTIVE         │
                    │  LED1: OFF (or kept ON)   │
                    │  LED2: SOLID (Immediate)  │
                    │  NO COUNTDOWN             │
                    │  🚨 CALLING 999 NOW! 🚨   │
                    └───────────┬───────────────┘
                                │
                    Button 2 Pressed to Stop
                                │
                                ↓
                    ┌───────────────────────────┐
                    │  EMERGENCY_RESOLVED       │
                    │  LED1: OFF                │
                    │  LED2: OFF                │
                    │  Back to IDLE             │
                    └───────────────────────────┘
```

---

## 🎬 Timeline View

### Scenario A: Fall with Breathing (False Alarm)
```
Time  │ State                   │ LED1  │ LED2      │ Action
──────┼─────────────────────────┼───────┼───────────┼─────────────────────
00:00 │ IDLE                    │ OFF   │ OFF       │ Monitoring...
00:05 │ FALL_DETECTED           │ ON    │ OFF       │ Person fell!
00:30 │ FALL_DETECTED           │ ON    │ OFF       │ Still fallen (30s)
01:00 │ FALL_DETECTED           │ ON    │ OFF       │ Still fallen (1min)
01:30 │ FALL_DETECTED           │ ON    │ OFF       │ Still fallen (1.5min)
02:05 │ CHECKING_BREATHING      │ ON    │ OFF       │ 2min passed, checking...
02:17 │ Breathing Result        │ ON    │ OFF       │ Analysis complete
02:17 │ IDLE (False Alarm)      │ OFF   │ OFF       │ ✓ Breathing detected
02:17 │ Continue monitoring...  │ OFF   │ OFF       │ Back to normal
```

### Scenario B: Fall WITHOUT Breathing (Real Emergency)
```
Time  │ State                   │ LED1  │ LED2      │ Action
──────┼─────────────────────────┼───────┼───────────┼─────────────────────
00:00 │ IDLE                    │ OFF   │ OFF       │ Monitoring...
00:05 │ FALL_DETECTED           │ ON    │ OFF       │ Person fell!
02:05 │ CHECKING_BREATHING      │ ON    │ OFF       │ 2min passed, checking...
02:17 │ NO_BREATHING            │ ON    │ OFF       │ ✗ No breathing!
02:17 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 10s countdown starts
02:18 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 9 seconds...
02:19 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 8 seconds...
02:20 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 7 seconds...
02:21 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 6 seconds...
02:22 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 5 seconds!
02:23 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 4 seconds!
02:24 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 3 seconds!
02:25 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 2 seconds!
02:26 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 1 second!
02:27 │ EMERGENCY_ACTIVE        │ ON    │ SOLID     │ 🚨 CALLING 999!
```

### Scenario C: Cancelled During Countdown
```
Time  │ State                   │ LED1  │ LED2      │ Action
──────┼─────────────────────────┼───────┼───────────┼─────────────────────
00:00 │ IDLE                    │ OFF   │ OFF       │ Monitoring...
00:05 │ FALL_DETECTED           │ ON    │ OFF       │ Person fell!
02:05 │ CHECKING_BREATHING      │ ON    │ OFF       │ Checking...
02:17 │ NO_BREATHING            │ ON    │ OFF       │ ✗ No breathing!
02:17 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 10s countdown
02:20 │ COUNTDOWN_ACTIVE        │ ON    │ FLASH     │ 7 seconds...
02:22 │ Button 2 Pressed! ──────┼──────→│           │ USER CANCELS
02:22 │ COUNTDOWN_CANCELLED     │ OFF   │ OFF       │ ✓ Cancelled
02:22 │ IDLE                    │ OFF   │ OFF       │ Back to normal
```

### Scenario D: Manual Emergency (Button 1)
```
Time  │ State                   │ LED1  │ LED2      │ Action
──────┼─────────────────────────┼───────┼───────────┼─────────────────────
00:00 │ IDLE                    │ OFF   │ OFF       │ Monitoring...
00:15 │ Button 1 Pressed! ──────┼──────→│           │ MANUAL EMERGENCY
00:15 │ EMERGENCY_ACTIVE        │ OFF   │ SOLID     │ 🚨 CALLING 999!
00:15 │ (No countdown, immediate)│      │           │ Direct call
```

---

## 🎯 Decision Tree

```
                            ┌─────────────┐
                            │ Fall Detected│
                            └──────┬──────┘
                                   │
                                   ↓
                        ┌──────────────────────┐
                        │ Wait 2 minutes       │
                        │ Does person recover? │
                        └────┬────────────┬────┘
                             │            │
                         YES │            │ NO
                             │            │
                             ↓            ↓
                     ┌──────────┐   ┌─────────────┐
                     │ LED OFF  │   │ Check       │
                     │ No Alert │   │ Breathing   │
                     └──────────┘   └──────┬──────┘
                                           │
                                           ↓
                              ┌────────────────────────┐
                              │ Is person breathing?   │
                              └────┬──────────────┬────┘
                                   │              │
                               YES │              │ NO
                                   │              │
                                   ↓              ↓
                          ┌───────────┐    ┌────────────┐
                          │ LED OFF   │    │ LED2 FLASH │
                          │False Alarm│    │ Countdown  │
                          └───────────┘    └─────┬──────┘
                                                  │
                                                  ↓
                                    ┌─────────────────────────┐
                                    │ User cancels (Button 2)?│
                                    └─────┬───────────────┬───┘
                                          │               │
                                      YES │               │ NO
                                          │               │
                                          ↓               ↓
                                  ┌──────────┐    ┌────────────┐
                                  │ LED OFF  │    │ LED2 SOLID │
                                  │Cancelled │    │ CALL 999!  │
                                  └──────────┘    └────────────┘
```

---

## 📱 LED Behavior Guide

### LED1 (Fall Indicator) - GPIO Pin 22
```
STATE: IDLE              ●───────  OFF (dark)
STATE: FALL_DETECTED     ●███████  ON (solid red)
STATE: CHECKING_BREATHING●███████  ON (solid red)
STATE: NO_BREATHING      ●███████  ON (solid red)
STATE: COUNTDOWN_ACTIVE  ●███████  ON (solid red)
STATE: EMERGENCY_ACTIVE  ●███████  ON (solid red)
```

### LED2 (Emergency Indicator) - GPIO Pin 33
```
STATE: IDLE              ●───────  OFF (dark)
STATE: FALL_DETECTED     ●───────  OFF (dark)
STATE: CHECKING_BREATHING●───────  OFF (dark)
STATE: NO_BREATHING      ●───────  OFF (dark)
STATE: COUNTDOWN_ACTIVE  ●█●█●█●█  FLASHING (1 Hz)
STATE: EMERGENCY_ACTIVE  ●███████  SOLID (bright red)
```

### Combined LED States
```
Both OFF        ●─────── ●───────  IDLE (normal monitoring)
LED1 only       ●███████ ●───────  Fall detected/checking
LED1 + LED2 flash●██████ ●█●█●█●  No breathing! 10s to cancel
LED2 only solid ●─────── ●███████  Emergency active (999)
```

---

## 🔘 Button Functions

### Button 1 (Call 999 - GPIO Pin 11)
```
┌──────────────────────────────────────────┐
│  BUTTON 1: MANUAL EMERGENCY              │
│  ┌────────┐                              │
│  │ [CALL] │ ← Press for immediate help   │
│  │ [ 999] │                              │
│  └────────┘                              │
│                                          │
│  Effect:                                 │
│  ✓ LED2 goes SOLID immediately           │
│  ✓ Calls 999 directly                    │
│  ✓ No countdown, no checks               │
│  ✓ Use when immediate help needed        │
└──────────────────────────────────────────┘
```

### Button 2 (Cancel - GPIO Pin 13)
```
┌──────────────────────────────────────────┐
│  BUTTON 2: CANCEL/STOP                   │
│  ┌────────┐                              │
│  │[CANCEL]│ ← Press to stop emergency    │
│  │ [STOP] │                              │
│  └────────┘                              │
│                                          │
│  Effect:                                 │
│  ✓ Stops countdown (LED2 flashing)       │
│  ✓ Stops emergency (LED2 solid)          │
│  ✓ Both LEDs turn OFF                    │
│  ✓ System returns to IDLE                │
└──────────────────────────────────────────┘
```

---

## 📊 Timing Summary

| Event                  | Duration       | Purpose                          |
|------------------------|----------------|----------------------------------|
| Camera capture         | Every 2s       | Continuous monitoring            |
| Fall detection         | ~100ms         | AI analysis per frame            |
| Fall monitoring        | 120s (2 min)   | Recovery grace period            |
| Breathing capture      | 12s            | Video collection                 |
| Breathing analysis     | ~3s            | SIFT motion detection            |
| Emergency countdown    | 10s            | User cancellation window         |
| LED2 flash rate        | 1 Hz (1s)      | Visual countdown indicator       |

**Total time from fall to 999 call:** ~142 seconds (2:22)
- 120s fall monitoring
- 12s breathing capture
- 10s countdown

---

## 🎓 Quick Troubleshooting Guide

| Issue | Check | Solution |
|-------|-------|----------|
| LED1 won't light | Fall detected? | Trigger fall (lie down) |
| LED2 won't flash | Breathing check done? | Wait 2min after fall |
| Countdown stops | Button 2 pressed? | Don't press during test |
| No emergency call | enable_actual_call? | Set to true in config |
| Button not working | GPIO wired correctly? | Check wiring diagram |
| Camera not working | /dev/video* exists? | Check camera connection |

---

**Last Updated:** 2025-12-14  
**System Version:** Integrated Fall + Breathing Detection v1.0  
**Documentation:** See INTEGRATED_SYSTEM_GUIDE.md for complete details
