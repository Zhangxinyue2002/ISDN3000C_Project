# RDK X5 Specific Notes

## Platform Overview
This project is designed for **RDK X5** (Horizon Robotics Development Kit), not Raspberry Pi.

### Key Differences from Raspberry Pi

#### Hardware
- **Processor**: RDK X5 features Horizon Robotics' specialized AI processor
- **BPU (Brain Processing Unit)**: Dedicated neural network accelerator
- **Power**: 12V DC power supply (not 5V like Raspberry Pi)
- **Camera**: MIPI CSI interface or standard USB webcam
- **GPIO**: Compatible with standard GPIO libraries (RPi.GPIO, gpiozero)

#### Operating System
- **OS**: Ubuntu 20.04/22.04 (64-bit) for RDK X5
- **Not**: Raspberry Pi OS
- **Kernel**: Linux kernel optimized for RDK X5

#### Camera Interface
- **Primary**: MIPI CSI camera
- **Alternative**: USB webcam
- **Library**: OpenCV VideoCapture (not picamera2)
- **Device**: Usually `/dev/video0` or `/dev/video8`

#### AI Acceleration
- **BPU**: Can accelerate YOLO and other neural networks
- **Model Format**: May require model conversion for BPU optimization
- **Performance**: Significantly faster inference than Raspberry Pi CPU

---

## Setup Considerations

### 1. Camera Configuration
```python
# Use OpenCV for camera access on RDK X5
import cv2

# Open camera
cap = cv2.VideoCapture(0)  # or /dev/video8 depending on setup

# Set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

# Capture frame
ret, frame = cap.read()
```

### 2. Model Optimization
For best performance on RDK X5:
```yaml
# config/config.yaml
fall_detection:
  model_path: "models/fall_detection.pt"
  use_bpu: true  # Enable BPU acceleration
  model_format: "horizon"  # or "onnx" or "pytorch"
```

**Consider converting your YOLO model for BPU:**
- Use Horizon's model conversion tools
- Export to ONNX first, then convert for BPU
- Expect 3-5x speed improvement

### 3. GPIO Compatibility
RDK X5 GPIO is compatible with standard Python GPIO libraries:
```python
# Works on RDK X5
from gpiozero import LED, Button
import RPi.GPIO as GPIO

# Pin numbering is similar to Raspberry Pi
# Check RDK X5 documentation for exact pinout
```

### 4. Camera Device Detection
```bash
# List available video devices
ls -l /dev/video*

# Get camera capabilities
v4l2-ctl --list-devices

# Test camera
v4l2-ctl --device=/dev/video0 --all
```

### 5. System Resources
```bash
# Check CPU temperature
cat /sys/class/thermal/thermal_zone0/temp

# Monitor BPU usage (if tools available)
# Check Horizon Robotics documentation

# Check memory
free -h

# Monitor processes
htop
```

---

## Performance Optimization

### Use BPU for AI Inference
The RDK X5's BPU can dramatically accelerate neural network inference:

1. **Convert model to BPU-compatible format**
2. **Use Horizon's SDK** for optimal performance
3. **Benchmark**: Test inference time with and without BPU

Expected performance:
- **CPU-only YOLO**: 200-500ms per frame
- **BPU-accelerated YOLO**: 20-50ms per frame

### Camera Optimization
```python
# Use hardware-accelerated formats if available
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

# Reduce resolution for faster processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

## Installation Notes

### 1. System Preparation
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip python3-venv git \
    libopencv-dev python3-opencv \
    v4l-utils hostapd dnsmasq
```

### 2. Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Note: Some packages may need compilation
# Be patient during installation
```

### 3. Camera Setup
```bash
# No raspi-config needed on RDK X5
# Camera should be auto-detected

# Verify camera
python3 -c "import cv2; print('OpenCV:', cv2.__version__); cap=cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Error')"
```

---

## Troubleshooting RDK X5 Specific Issues

### Camera Not Detected
```bash
# Check kernel modules
lsmod | grep video

# Check device permissions
ls -l /dev/video*
sudo usermod -aG video $USER

# Reboot if needed
sudo reboot
```

### GPIO Not Working
```bash
# Check GPIO permissions
sudo usermod -aG gpio $USER

# Install GPIO library if missing
pip install RPi.GPIO gpiozero

# May need to reboot
sudo reboot
```

### Model Loading Issues
```bash
# Check PyTorch installation
python3 -c "import torch; print(torch.__version__)"

# For BPU usage, check Horizon SDK
# Consult RDK X5 documentation
```

### WiFi AP Issues
```bash
# Same as Raspberry Pi setup
# hostapd and dnsmasq work identically

# Check wireless interface name
ip link show

# May be wlan0 or wlan1
```

---

## Resources

### Official Documentation
- **Horizon Robotics**: Check official RDK X5 documentation
- **BPU SDK**: Model conversion and optimization tools
- **Community Forums**: RDK X5 developer community

### Comparison with Raspberry Pi

| Feature | Raspberry Pi 4/5 | RDK X5 |
|---------|-----------------|---------|
| CPU | ARM Cortex-A72 | ARM Cortex-A55 |
| AI Accelerator | None | BPU (Brain Processing Unit) |
| AI Performance | Low | High (5+ TOPS) |
| Power | 5V 3A | 12V DC |
| Camera | CSI via libcamera | MIPI CSI via V4L2 |
| OS | Raspberry Pi OS | Ubuntu |
| GPIO | 40-pin header | Similar GPIO |

---

## Recommended Workflow for RDK X5

1. **Initial Development**:
   - Develop on computer or Raspberry Pi
   - Test algorithms and logic
   - Use CPU-based inference

2. **RDK X5 Deployment**:
   - Port code to RDK X5
   - Replace camera library (picamera2 → OpenCV)
   - Test with real hardware

3. **Optimization**:
   - Convert model for BPU
   - Benchmark performance
   - Tune parameters

4. **Production**:
   - Enable BPU acceleration
   - Optimize camera settings
   - Deploy final system

---

## Contact

For RDK X5 specific issues:
- Check Horizon Robotics documentation
- Consult RDK X5 community forums
- Review example projects for RDK X5

**Note**: This project is designed to work on RDK X5 with minimal modifications from the general architecture. The main changes are:
1. Camera access via OpenCV instead of picamera2
2. Optional BPU acceleration for AI models
3. Ubuntu instead of Raspberry Pi OS

All other components (Flask, GPIO, database, web interface) work identically!

---

**Last Updated**: November 23, 2025  
**Platform**: RDK X5 (Horizon Robotics)
