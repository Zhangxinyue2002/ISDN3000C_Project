# 🚀 Quick Reference Card - Integrated Fall Detection System

## ⚡ Emergency Flow (Quick Overview)

```
FALL → WAIT 2 MIN → CHECK BREATHING → COUNTDOWN → CALL 999
 ↓         ↓             ↓               ↓           ↓
LED1     LED1         LED1+12s        LED2        LED2
 ON       ON          analyzing       FLASH      SOLID
          
         Can          Breathing         Can
        Recover         OK?           Cancel
          ↓              ↓              ↓
        LED OFF       LED OFF        LED OFF
```

---

## 💡 LED States

| LED(s) | State | Meaning | What's Happening |
|--------|-------|---------|------------------|
| Both OFF | Normal | System monitoring | Watching for falls |
| LED1 ON | Fall detected | Person fallen | Waiting 2 minutes |
| LED1 ON | Checking | Analyzing breathing | 12 seconds analysis |
| LED1+LED2 FLASH | Countdown | No breathing! | 10s to cancel |
| LED2 SOLID | Emergency | Calling 999 | Active emergency |

---

## 🔘 Buttons

| Button | Action | When | Result |
|--------|--------|------|--------|
| **Button 1** | Call 999 | Anytime | LED2 solid, immediate call |
| **Button 2** | Cancel | LED2 flashing | Both LEDs off, cancel |
| **Button 2** | Stop | LED2 solid | Both LEDs off, stop call |

---

## ⏱️ Timing

| Event | Duration | Purpose |
|-------|----------|---------|
| Camera capture | Every 2s | Continuous monitoring |
| Fall monitoring | 2 minutes | Wait for recovery |
| Breathing check | 12 seconds | Verify if help needed |
| Emergency countdown | 10 seconds | Time to cancel |

---

## 🎯 Decision Points

### After Fall Detected (2 min):
- ✅ **Breathing detected** → LED OFF → No emergency
- ❌ **No breathing** → LED2 flash → 10s countdown

### During Countdown (10s):
- ✅ **Button 2 pressed** → Cancel → LED OFF
- ❌ **No button press** → LED2 solid → Call 999

---

## 🚨 Quick Actions

### Start System
```bash
cd ~/Project/ISDN3000C_Project
source venv/bin/activate
python3 src/main.py
```

### Stop System
Press `Ctrl+C` in terminal

### View Logs
```bash
tail -f data/logs/system.log
```

### Test Breathing
```bash
python3 test_breathing_rdk.py
```

### Web Interface
```
http://YOUR_RDK_IP:5000
```

---

## 📊 System States

1. **IDLE** - Normal monitoring
2. **FALL_DETECTED** - Fall detected, monitoring duration
3. **CHECKING_BREATHING** - Analyzing breathing (12s)
4. **NO_BREATHING** - No breathing detected
5. **COUNTDOWN_ACTIVE** - 10s countdown (LED2 flashing)
6. **EMERGENCY_ACTIVE** - Calling 999 (LED2 solid)

---

## 🔧 Configuration Quick Edit

```bash
nano config/config.yaml
```

**Key Settings:**
- `fall_duration_threshold: 120` - Time before breathing check (seconds)
- `countdown_duration: 10` - Cancel window (seconds)
- `capture_duration: 12` - Breathing analysis time (seconds)

---

## 📞 Emergency Number

Default: **999** (UK Emergency Services)

To change:
```yaml
emergency:
  contact_number: "999"  # Change this
```

---

## 🎓 Testing Checklist

- [ ] Camera working? → `ls /dev/video*`
- [ ] LEDs wired? → `python3 test_components.py`
- [ ] Buttons working? → Press during test_components.py
- [ ] Fall detection? → Lie down in camera view
- [ ] Breathing detection? → `python3 test_breathing_rdk.py`
- [ ] Web interface? → Open browser to RDK IP:5000

---

## 🆘 Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Camera not found | `ls /dev/video*`, check connection |
| LEDs not lighting | Check wiring, polarity, resistors |
| Buttons not responding | Check GPIO pins, test with script |
| No fall detection | Check camera view, person visible? |
| Breathing check fails | Run `test_breathing_rdk.py` alone |
| Web page blank | Check Flask running, firewall open |

---

## 📖 Full Documentation

- **Complete System Flow**: [INTEGRATED_SYSTEM_GUIDE.md](INTEGRATED_SYSTEM_GUIDE.md)
- **Hardware Wiring**: [WIRING_DIAGRAM.md](WIRING_DIAGRAM.md) or README.md
- **Breathing Detection**: [BREATHING_MODULE_COMPLETE.md](BREATHING_MODULE_COMPLETE.md)
- **Emergency System**: [EMERGENCY_SYSTEM_GUIDE.md](EMERGENCY_SYSTEM_GUIDE.md)
- **Main README**: [README.md](README.md)

---

## 🎯 Remember

1. **LED1 = Fall detected** (person on ground)
2. **LED2 Flash = Cancel now** (10 seconds to press Button 2)
3. **LED2 Solid = Emergency active** (calling 999)
4. **Button 1 = Immediate emergency** (no wait, no checks)
5. **Button 2 = Cancel/Stop** (press anytime during flash or solid)

---

## 💾 File Locations

```
System Logs:    data/logs/system.log
Captured Images: data/images/
Config File:    config/config.yaml
Test Results:   test_results.csv
Database:       data/elderly_monitoring.db
```

---

## 🔑 Key Features

✅ Automatic breathing verification prevents false alarms  
✅ 2-minute grace period for recovery  
✅ 10-second countdown allows cancellation  
✅ Manual emergency button for immediate help  
✅ Visual LED feedback shows system state  
✅ Web interface for image gallery and statistics  

---

**Last Updated:** 2025-12-14  
**System Version:** Fall Detection + Breathing Integration v1.0
