# ⏱️ System Timing - Quick Reference

## 🎯 Scenario 1: Fall + No Breathing → Emergency

### Timeline
```
00:00  [IDLE] Normal monitoring
       Camera capturing every 2 seconds
       
00:05  🚨 FALL DETECTED!
       LED1: ON
       Start breathing check immediately
       
00:05  Capturing 12 seconds of video @ 30 fps
       Total frames: 360
       
00:17  Analyzing chest movement...
       SIFT motion detection
       
00:17  ❌ NO BREATHING DETECTED!
       LED2: FLASHING (immediately!)
       10-second countdown starts
       
00:18  Countdown: 9...
00:19  Countdown: 8...
00:20  Countdown: 7...
00:21  Countdown: 6...
00:22  Countdown: 5... ⚠️
00:23  Countdown: 4... ⚠️
00:24  Countdown: 3... ⚠️
00:25  Countdown: 2... ⚠️
00:26  Countdown: 1... ⚠️
       
00:27  ⏰ COUNTDOWN EXPIRED!
       LED2: SOLID
       🚨 CALLING 999!

Total time from fall to emergency: ~22 seconds
(5s detect + 12s breathing + 0s analysis + 10s countdown - 5s overlap)
```

---

## 🎯 Scenario 2: Fall + Breathing OK → Monitor 1 Minute

### Timeline (Person Stands Up)
```
00:00  [IDLE] Normal monitoring
       
00:05  🚨 FALL DETECTED!
       LED1: ON
       Start breathing check immediately
       
00:05  Capturing 12 seconds of video @ 30 fps
       
00:17  Analyzing chest movement...
       
00:17  ✅ BREATHING DETECTED!
       LED1: ON (continue monitoring)
       LED2: OFF
       Start 1-minute fall duration timer
       
00:30  Fall persists (30 seconds)
       LED1: ON (monitoring...)
       
00:47  Person stands up!
       Fall no longer detected
       LED1: OFF
       System reset to IDLE
       
Total monitoring time: 42 seconds (didn't reach 1 minute)
```

### Timeline (Fall Persists > 1 Minute)
```
00:00  [IDLE] Normal monitoring
       
00:05  🚨 FALL DETECTED!
       LED1: ON
       Start breathing check immediately
       
00:17  ✅ BREATHING DETECTED!
       LED1: ON (continue monitoring)
       LED2: OFF
       Start 1-minute fall duration timer
       
00:30  Fall persists (30 seconds)
       LED1: ON (monitoring...)
       
01:00  Fall persists (1 minute)
       LED1: ON (monitoring...)
       
01:17  ⚠️ FALL DURATION > 1 MINUTE!
       LED2: FLASHING
       10-second countdown starts
       
01:18  Countdown: 9...
01:19  Countdown: 8...
01:20  Countdown: 7...
01:21  Countdown: 6...
01:22  Countdown: 5... ⚠️
01:23  Countdown: 4... ⚠️
01:24  Countdown: 3... ⚠️
01:25  Countdown: 2... ⚠️
01:26  Countdown: 1... ⚠️
       
01:27  ⏰ COUNTDOWN EXPIRED!
       LED2: SOLID
       🚨 CALLING 999!

Total time from fall to emergency: ~1 minute 22 seconds
(5s detect + 12s breathing + 60s monitoring + 10s countdown - 5s overlap)
```

---

## 🔘 Button 2: Instant Reset

### During Countdown
```
00:17  LED2: FLASHING (countdown active)
       10 seconds remaining
       
00:20  🟢 BUTTON 2 PRESSED!
       LED1: OFF (immediately)
       LED2: OFF (immediately)
       System: IDLE
       All monitoring stopped
       Back to normal fall detection
       
Reset time: <0.1 seconds (instant)
```

### During Emergency
```
01:27  LED2: SOLID (emergency active)
       Calling 999...
       
01:30  🟢 BUTTON 2 PRESSED!
       LED1: OFF (immediately)
       LED2: OFF (immediately)
       System: IDLE
       Emergency cancelled
       Back to normal fall detection
       
Reset time: <0.1 seconds (instant)
```

### During Fall Monitoring
```
00:30  LED1: ON (fall monitoring)
       LED2: OFF
       Waiting for 1 minute threshold...
       
00:35  🟢 BUTTON 2 PRESSED!
       LED1: OFF (immediately)
       LED2: OFF (immediately)
       System: IDLE
       Monitoring stopped
       Back to normal fall detection
       
Reset time: <0.1 seconds (instant)
```

---

## 📊 Timing Summary

| Event | Duration | Cumulative Time |
|-------|----------|-----------------|
| Fall detection | ~0s (instant) | 0:00 |
| Breathing check | 12s | 0:12 |
| Breathing analysis | ~0s (instant) | 0:12 |
| **Path A: No Breathing** | | |
| → LED2 flash | immediate | 0:12 |
| → Countdown | 10s | 0:22 |
| → Emergency call | N/A | 0:22 |
| **Path B: Breathing OK** | | |
| → Monitor duration | up to 60s | 0:12 - 1:12 |
| → LED2 flash (if >1min) | immediate | 1:12 |
| → Countdown | 10s | 1:22 |
| → Emergency call | N/A | 1:22 |

---

## ⚡ Quick Actions

| Action | Time to Complete |
|--------|-----------------|
| Fall detection | Instant (~0.1s) |
| Breathing check | 12 seconds |
| No breathing → LED2 flash | Instant after check |
| 1 min fall → LED2 flash | Instant at 1:00 mark |
| Button 2 → Reset | Instant (<0.1s) |
| Countdown → Emergency | 10 seconds |

---

## 🎯 User Response Windows

| Situation | How Long to Respond |
|-----------|---------------------|
| No breathing detected | 10 seconds (countdown) |
| Fall > 1 minute | 10 seconds (countdown) |
| Emergency active | Anytime (Button 2) |

---

## 📝 Key Times to Remember

- **Breathing check**: 12 seconds after fall
- **Fall threshold**: 1 minute (60 seconds)
- **Countdown**: 10 seconds before calling 999
- **Button 2 reset**: Instant (works anytime)

---

## 🚨 Emergency Response Times

### Fastest Emergency (No Breathing)
```
Fall detected → Breathing check (12s) → No breathing → Countdown (10s) → Call 999
Total: ~22 seconds
```

### Slowest Emergency (Breathing OK, Fall > 1min)
```
Fall detected → Breathing check (12s) → Breathing OK → Monitor (60s) → Countdown (10s) → Call 999
Total: ~82 seconds (1 minute 22 seconds)
```

### Manual Emergency (Button 1)
```
Button 1 pressed → Call 999 immediately
Total: <1 second
```

---

**Note:** All times are approximate. Actual times may vary slightly depending on:
- Camera frame rate
- Image processing speed
- System load
- Network latency (for actual 999 calls)
