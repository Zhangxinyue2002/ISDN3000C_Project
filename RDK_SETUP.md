# RDK X5 Setup Instructions

## Step 1: Transfer Files to RDK X5

Transfer the following files and folders to your RDK X5:

```
ISDN3000C_Project/
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── gpio_handler.py
│   └── camera_service.py
├── test_components.py
└── requirements.txt
```

**Methods to transfer:**
- Using SCP: `scp -r ISDN3000C_Project/ user@rdkx5:~/`
- Using USB drive
- Using SFTP client (FileZilla, WinSCP)

## Step 2: Initial RDK X5 Setup

SSH into your RDK X5:
```bash
ssh user@your-rdkx5-ip
```

Navigate to project directory:
```bash
cd ~/ISDN3000C_Project
```

## Step 3: Install System Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and essential tools
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Install OpenCV dependencies
sudo apt-get install -y libopencv-dev python3-opencv \
    libatlas-base-dev libhdf5-dev libhdf5-serial-dev

# Install video libraries
sudo apt-get install -y libavcodec-dev libavformat-dev \
    libswscale-dev libv4l-dev v4l-utils

# Install GPIO libraries
sudo apt-get install -y python3-gpiozero python3-rpi.gpio
```

## Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 5: Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# If torch fails, install CPU version:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install system packages for GPIO
sudo apt-get install -y python3-gpiozero python3-rpi.gpio
```

## Step 6: Create Required Directories

```bash
# Create data directories
mkdir -p data/images
mkdir -p data/logs
mkdir -p models

# Set permissions
chmod -R 755 data/
```

## Step 7: Check Camera

```bash
# List video devices
v4l2-ctl --list-devices

# Test camera (common devices: /dev/video0 or /dev/video8)
v4l2-ctl --device=/dev/video0 --all
# or
v4l2-ctl --device=/dev/video8 --all

# Capture test image
ffmpeg -f v4l2 -i /dev/video0 -frames 1 test.jpg
```

## Step 8: Test Components

```bash
# Make test script executable
chmod +x test_components.py

# Run component tests
python3 test_components.py
```

The test will guide you through:
1. ✅ LED functionality test
2. ✅ Camera capture test
3. ✅ Continuous capture test (15 seconds)
4. ✅ Storage statistics
5. ✅ Button input test

## Step 9: Verify Hardware Connections

Before running tests, verify your GPIO connections:

| Component | GPIO Pin | Physical Pin | Connection |
|-----------|----------|--------------|------------|
| Button 1 (Call 999) | GPIO 17 | Pin 11 | Button → GND + 10kΩ pull-down |
| Button 2 (Stop Call) | GPIO 27 | Pin 13 | Button → GND + 10kΩ pull-down |
| LED 1 (Fall) | GPIO 22 | Pin 15 | GPIO → 220Ω → LED → GND |
| LED 2 (Emergency) | GPIO 23 | Pin 16 | GPIO → 220Ω → LED → GND |

## Troubleshooting

### Camera not found
```bash
# Check available cameras
ls -l /dev/video*

# Try different device numbers in config.yaml
# Common: /dev/video0, /dev/video8, /dev/video11
```

### GPIO permission denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot for changes to take effect
sudo reboot
```

### Import errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Check if modules are installed
pip list | grep gpiozero
pip list | grep opencv
```

### Camera quality issues
Edit `config/config.yaml`:
```yaml
camera:
  resolution: [1280, 720]  # Try [640, 480] for better performance
  image_quality: 85  # Reduce for smaller files
```

## Quick Test Commands

```bash
# Test GPIO independently
cd src
python3 gpio_handler.py

# Test camera independently
python3 camera_service.py

# Test database
python3 database.py

# Run full component test
cd ..
python3 test_components.py
```

## Expected Results

After running `test_components.py`, you should see:

1. **LED Test**: Both LEDs turn on/off and flash
2. **Camera Test**: Test image saved to `data/images/`
3. **Continuous Capture**: Multiple images captured automatically
4. **Storage Stats**: Shows total images and storage used
5. **Button Test**: Buttons trigger callbacks and LEDs respond

## Next Steps

Once all component tests pass:

1. ✅ GPIO handler working
2. ✅ Camera service working
3. ✅ Database working
4. ✅ Continuous capture working

Next we'll implement:
- Fall detection module (waiting for teammate's model)
- Breathing detection (SIFT algorithm)
- Emergency controller (state machine)
- Flask web interface

## Notes

- **RDK X5 specifics**: Uses Ubuntu, not Raspberry Pi OS
- **BPU acceleration**: Available for YOLO model optimization later
- **Power**: Ensure stable 12V DC power supply
- **Storage**: Monitor disk space with `df -h`

## Support Commands

```bash
# Check system info
uname -a

# Check Python version
python3 --version

# Check disk space
df -h

# Monitor system resources
htop

# View logs (when running as service)
tail -f data/logs/system.log
```

---

**Ready to test?** Run `python3 test_components.py` and follow the prompts!
