# Quick Reference - File Transfer & Testing

## 📦 Files to Transfer to RDK X5

Copy these from your Windows PC to RDK X5:

```
ISDN3000C_Project/
├── config/config.yaml          ← Configuration
├── requirements.txt            ← Python dependencies
├── src/
│   ├── __init__.py
│   ├── database.py            ← Database with cleanup
│   ├── gpio_handler.py        ← Button & LED control
│   └── camera_service.py      ← Camera capture
└── test_components.py         ← Test script
```

## 🔧 One-Time Setup (On RDK X5)

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv python3-opencv \
    libopencv-dev v4l-utils python3-gpiozero python3-rpi.gpio

# 3. Create directories
cd ~/ISDN3000C_Project
mkdir -p data/images data/logs models

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ⚡ Quick Test (Run Every Time)

```bash
# Navigate to project
cd ~/ISDN3000C_Project

# Activate environment
source venv/bin/activate

# Run tests
python3 test_components.py
```

## 🔌 GPIO Wiring Reminder

```
Button 1 (Call 999):    GPIO 17 (Pin 11) → Button → GND
Button 2 (Stop Call):   GPIO 27 (Pin 13) → Button → GND
LED 1 (Fall):          GPIO 22 (Pin 15) → 220Ω → LED → GND
LED 2 (Emergency):     GPIO 23 (Pin 16) → 220Ω → LED → GND
Camera:                MIPI CSI port (ribbon cable, blue side toward Ethernet)
```

## 🎯 Test Sequence

The test script will automatically:
1. ✅ Test LED 1 & LED 2 (on/off/flash)
2. ✅ Test camera capture
3. ✅ Test continuous capture (15 seconds)
4. ✅ Show storage statistics
5. ✅ Test buttons (press buttons to verify)

## 🐛 Quick Troubleshooting

### Camera not working?
```bash
# Find your camera device
ls -l /dev/video*

# Test camera
v4l2-ctl --device=/dev/video0 --all
```

### GPIO not working?
```bash
# Check GPIO group
groups

# Add user to GPIO group if missing
sudo usermod -a -G gpio $USER
sudo reboot
```

### Import errors?
```bash
# Ensure virtual environment is active
source venv/bin/activate

# Check installations
pip list | grep -E "opencv|gpiozero|gpio"
```

## 📊 Expected Output

When test passes, you should see:
```
✓ Database ready
✓ GPIO ready  
✓ Camera ready
✓ LED test complete!
✓ Camera test complete!
✓ Continuous capture test complete!
✓ Storage stats test complete!
✓ Button test complete!
```

## 🚀 After Tests Pass

Report back with:
1. ✅ All tests passed
2. 📸 Screenshot of test output (optional)
3. 📝 Any warnings or issues

Then we'll proceed to:
- Fall detection integration (with teammate's model)
- Breathing detection (SIFT)
- Emergency controller
- Web interface

## 💾 Important Files Location

- **Images**: `data/images/` (numbered: 1.jpg, 2.jpg, ...)
- **Database**: `data/database.db`
- **Logs**: `data/logs/system.log`
- **Config**: `config/config.yaml`

## 🔄 Config Adjustments

If needed, edit `config/config.yaml`:

```yaml
camera:
  capture_interval: 2        # Seconds between captures
  resolution: [1280, 720]    # Lower if too slow: [640, 480]
  
storage:
  max_images: 5000          # Maximum images to keep
  cleanup_threshold: 0.85   # Start cleanup at 85% full
  
gpio:
  button_call_999: 17       # GPIO pin for button 1
  button_stop_call: 27      # GPIO pin for button 2
  led_fall: 22             # GPIO pin for LED 1
  led_emergency: 23        # GPIO pin for LED 2
```

---

**Need Help?** Check `RDK_SETUP.md` for detailed instructions!
