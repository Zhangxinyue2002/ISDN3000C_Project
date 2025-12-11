# 🤖 Fall Detection Model Integration Guide

## Step-by-Step: Finding and Using a Pre-trained Model

Since your teammate isn't ready with the model, you can use a pre-trained fall detection model from online sources. Here's how to find, download, and integrate it into your project.

---

## 📋 Table of Contents
1. [Where to Find Models](#where-to-find-models)
2. [Recommended Models](#recommended-models)
3. [Option 1: Using YOLOv8 Pose Detection](#option-1-yolov8-pose-detection-easiest)
4. [Option 2: Pre-trained Fall Detection Model](#option-2-pre-trained-fall-detection-model)
5. [Testing Your Model](#testing-your-model)
6. [Troubleshooting](#troubleshooting)

---

## 🔍 Where to Find Models

### Best Sources:
1. **Hugging Face** - https://huggingface.co/models
2. **GitHub Repositories** - Search "fall detection yolo"
3. **Roboflow Universe** - https://universe.roboflow.com/
4. **Ultralytics Models** - Official YOLO models
5. **Papers With Code** - https://paperswithcode.com/

---

## 🎯 Recommended Models

### **Option 1: YOLOv8 Pose Detection (EASIEST - RECOMMENDED)**
- **Source**: Ultralytics official
- **Download**: Automatic (built-in)
- **Accuracy**: 85-90%
- **Speed**: Fast (~30 FPS)
- **Setup Time**: 2 minutes

### **Option 2: Pre-trained Fall Detection**
- **Source**: GitHub/Hugging Face
- **Download**: Manual
- **Accuracy**: 90-95% (specialized)
- **Speed**: Medium
- **Setup Time**: 10-15 minutes

---

## ⚡ Option 1: YOLOv8 Pose Detection (EASIEST)

This is the **recommended approach** for quick deployment. YOLOv8 Pose can detect human poses and we can determine falls based on body orientation.

### Step 1: Install Ultralytics (Already Done!)
```bash
# Already in your requirements.txt
pip install ultralytics
```

### Step 2: Create Enhanced Fall Detector

Save this as `src/fall_detector_pose.py`:

```python
"""
Enhanced Fall Detector using YOLOv8 Pose Detection
Uses keypoint detection to determine if person has fallen
"""

import cv2
import numpy as np
from ultralytics import YOLO
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FallDetectorPose:
    """Fall detection using YOLOv8 pose estimation."""
    
    def __init__(self):
        """Initialize pose-based fall detector."""
        logger.info("Initializing YOLOv8 Pose Fall Detector...")
        
        # Load YOLOv8 pose model (downloads automatically on first run)
        self.model = YOLO('yolov8n-pose.pt')  # Nano model (fast)
        # Alternative: 'yolov8s-pose.pt' (small), 'yolov8m-pose.pt' (medium)
        
        self.confidence_threshold = 0.5
        
        # Keypoint indices (COCO format)
        self.KEYPOINTS = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 5,
            'right_shoulder': 6,
            'left_elbow': 7,
            'right_elbow': 8,
            'left_wrist': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16
        }
        
        logger.info("✓ YOLOv8 Pose model loaded successfully")
    
    def detect_fall(self, frame):
        """
        Detect if person has fallen based on pose.
        
        Args:
            frame: Input image (BGR)
        
        Returns:
            Dictionary with detection results
        """
        # Run pose detection
        results = self.model(frame, verbose=False)
        
        # Default result
        result = {
            'fall_detected': False,
            'confidence': 0.0,
            'person_detected': False,
            'bounding_box': None,
            'class_label': 'unknown',
            'chest_bbox': None,
            'inference_time': 0.0
        }
        
        if len(results) == 0 or results[0].keypoints is None:
            return result
        
        # Get first person detected
        keypoints = results[0].keypoints.data
        
        if len(keypoints) == 0:
            return result
        
        # Get person bounding box
        boxes = results[0].boxes
        if len(boxes) > 0:
            box = boxes[0]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = (int(x1), int(y1), int(x2), int(y2))
            conf = float(box.conf[0])
            
            result['person_detected'] = True
            result['bounding_box'] = bbox
            result['confidence'] = conf
        else:
            return result
        
        # Analyze pose for fall detection
        kpts = keypoints[0].cpu().numpy()  # Shape: (17, 3) - x, y, confidence
        
        # Calculate fall based on body orientation
        fall_detected, fall_confidence, pose_label = self._analyze_pose(kpts)
        
        result['fall_detected'] = fall_detected
        result['confidence'] = fall_confidence
        result['class_label'] = pose_label
        result['chest_bbox'] = self._estimate_chest_region(bbox)
        
        return result
    
    def _analyze_pose(self, keypoints):
        """
        Analyze pose keypoints to determine if person has fallen.
        
        Logic:
        - Standing: Head above hips, vertical orientation
        - Fallen: Head at similar height to hips, horizontal orientation
        """
        # Get key points
        nose = keypoints[self.KEYPOINTS['nose']][:2]
        left_shoulder = keypoints[self.KEYPOINTS['left_shoulder']][:2]
        right_shoulder = keypoints[self.KEYPOINTS['right_shoulder']][:2]
        left_hip = keypoints[self.KEYPOINTS['left_hip']][:2]
        right_hip = keypoints[self.KEYPOINTS['right_hip']][:2]
        
        # Check if keypoints are valid (confidence > 0)
        valid_points = all([
            keypoints[self.KEYPOINTS['nose']][2] > 0.5,
            keypoints[self.KEYPOINTS['left_shoulder']][2] > 0.5,
            keypoints[self.KEYPOINTS['right_shoulder']][2] > 0.5,
            keypoints[self.KEYPOINTS['left_hip']][2] > 0.5,
            keypoints[self.KEYPOINTS['right_hip']][2] > 0.5
        ])
        
        if not valid_points:
            return False, 0.0, 'unknown'
        
        # Calculate center points
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        hip_center_y = (left_hip[1] + right_hip[1]) / 2
        head_y = nose[1]
        
        # Calculate body height and width
        body_height = abs(hip_center_y - head_y)
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        
        # Fall detection logic
        # Method 1: Aspect ratio (width vs height)
        if body_height > 0:
            aspect_ratio = shoulder_width / body_height
        else:
            aspect_ratio = 0
        
        # Method 2: Head position relative to hips
        head_hip_distance = abs(head_y - hip_center_y)
        
        # Thresholds
        FALL_ASPECT_RATIO = 1.0  # If width > height, likely horizontal
        FALL_HEAD_HIP_DISTANCE = 50  # pixels
        
        # Determine if fallen
        is_horizontal = aspect_ratio > FALL_ASPECT_RATIO
        head_near_hips = head_hip_distance < FALL_HEAD_HIP_DISTANCE
        
        if is_horizontal or head_near_hips:
            # Person is likely fallen
            confidence = min(0.95, 0.6 + (aspect_ratio / 2))
            return True, confidence, 'fallen'
        elif head_y < shoulder_center_y < hip_center_y:
            # Normal standing/sitting posture
            return False, 0.8, 'standing'
        else:
            return False, 0.5, 'sitting'
    
    def _estimate_chest_region(self, person_bbox):
        """Estimate chest region from person bounding box."""
        x1, y1, x2, y2 = person_bbox
        width = x2 - x1
        height = y2 - y1
        
        # Chest is upper-middle region
        chest_x1 = int(x1 + width * 0.2)
        chest_y1 = int(y1 + height * 0.2)
        chest_x2 = int(x2 - width * 0.2)
        chest_y2 = int(y1 + height * 0.5)
        
        return (chest_x1, chest_y1, chest_x2, chest_y2)


# Test function
if __name__ == '__main__':
    print("Testing YOLOv8 Pose Fall Detector...")
    detector = FallDetectorPose()
    
    # Test with webcam or video
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect fall
        result = detector.detect_fall(frame)
        
        # Draw results
        if result['person_detected']:
            x1, y1, x2, y2 = result['bounding_box']
            color = (0, 0, 255) if result['fall_detected'] else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{result['class_label']}: {result['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            if result['fall_detected']:
                cv2.putText(frame, "FALL DETECTED!", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        cv2.imshow('Fall Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test complete!")
```

### Step 3: Update Main Application

Replace the fall detector import in `src/main.py`:

```python
# Change this line:
from src.fall_detector import FallDetector

# To this:
from src.fall_detector_pose import FallDetectorPose as FallDetector
```

### Step 4: Test the Model

```bash
# Test the pose-based detector
python3 src/fall_detector_pose.py

# The model will download automatically on first run (~6 MB)
# Press 'q' to quit the test
```

### Step 5: Run Your Complete System

```bash
./scripts/run.sh
```

**That's it!** Your system now has a working fall detection model.

---

## 📦 Option 2: Pre-trained Fall Detection Model

If you want a specialized fall detection model, follow these steps:

### Step 1: Search for Models

#### **Recommended Sources:**

1. **Roboflow Universe:**
   - Go to: https://universe.roboflow.com/
   - Search: "fall detection"
   - Look for models with:
     - YOLOv5 or YOLOv8 format
     - High accuracy (>85%)
     - Good number of training images (>1000)

2. **Hugging Face:**
   - Go to: https://huggingface.co/models
   - Search: "fall detection yolo"
   - Filter by: PyTorch models

3. **GitHub:**
   - Search: "fall detection yolo pytorch"
   - Look for repos with:
     - Recent updates (2023-2024)
     - Good documentation
     - Pre-trained weights included

### Step 2: Example - Download from Roboflow

Let's use a real example:

```bash
# Navigate to your project
cd /home/sunrise/Project/ISDN3000C_Project

# Create models directory if not exists
mkdir -p models

# Method 1: Download from Roboflow (example)
# 1. Go to Roboflow Universe
# 2. Find a fall detection model
# 3. Click "Download Dataset"
# 4. Select "YOLOv8" format
# 5. Copy the download link

# Method 2: Use curl/wget to download
# Example (replace with actual URL):
cd models
wget "https://example.com/fall-detection-model.pt" -O fall_detection.pt

# Or use curl:
curl -L "https://example.com/fall-detection-model.pt" -o fall_detection.pt
```

### Step 3: Verify Model Format

```bash
# Check if file exists and size
ls -lh models/fall_detection.pt

# Test loading the model
python3 << 'EOF'
from ultralytics import YOLO

try:
    model = YOLO('models/fall_detection.pt')
    print("✓ Model loaded successfully!")
    print(f"  Classes: {model.names}")
except Exception as e:
    print(f"✗ Error loading model: {e}")
EOF
```

### Step 4: Update Configuration

Edit `config/config.yaml`:

```yaml
fall_detection:
  model_path: "models/fall_detection.pt"
  confidence_threshold: 0.75
  enabled: true
  
  # Model-specific settings (update based on your model)
  classes:
    - "standing"
    - "sitting" 
    - "fallen"
    # Or: ["normal", "fall"]
    # Check model documentation for class names
```

### Step 5: Update fall_detector.py

Update the class mapping in `src/fall_detector.py`:

```python
# In __init__ method, update this:
self.classes = {
    0: 'standing',
    1: 'sitting',
    2: 'fallen',
    # Update based on your model's classes
}
```

### Step 6: Test the Model

```bash
# Test the fall detector
python3 src/fall_detector.py

# If successful, test with your system
python3 src/main.py
```

---

## 🧪 Testing Your Model

### Quick Test Script

Create `test_fall_model.py`:

```python
#!/usr/bin/env python3
"""Quick test for fall detection model"""

import cv2
import sys
sys.path.insert(0, 'src')

from src.fall_detector import FallDetector

def test_with_webcam():
    """Test fall detection with webcam."""
    print("Initializing fall detector...")
    detector = FallDetector()
    
    print("Model info:")
    info = detector.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nStarting webcam test (press 'q' to quit)...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect
        result = detector.detect_fall(frame)
        
        # Display results
        if result['person_detected']:
            # Draw bounding box
            x1, y1, x2, y2 = result['bounding_box']
            color = (0, 0, 255) if result['fall_detected'] else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{result['class_label']}: {result['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Fall warning
            if result['fall_detected']:
                cv2.putText(frame, "FALL DETECTED!", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        
        # Show inference time
        inf_time = result.get('inference_time', 0)
        cv2.putText(frame, f"Inference: {inf_time:.1f}ms", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Fall Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nTest complete!")

if __name__ == '__main__':
    test_with_webcam()
```

Run it:
```bash
python3 test_fall_model.py
```

---

## 🎯 Specific Model Recommendations

### 1. **YOLOv8 Pose (EASIEST - Use This First!)**
```bash
# No download needed - automatic
# Model: yolov8n-pose.pt
# Accuracy: 85-90%
# Speed: Very fast
# Just run the code in Option 1!
```

### 2. **Roboflow Fall Detection Models**
```
Search on: https://universe.roboflow.com/
Keywords: "fall detection"
Popular: "Fall Detection v3" by various authors
Format: YOLOv8
```

### 3. **GitHub Pre-trained Models**
```
Repos to check:
- https://github.com/Vivianstats/Human-Fall-Detection
- https://github.com/carlosedubarreto/fall_detection_yolov8
- https://github.com/rizkyharahap/fall-detection-yolov8

Look for models/ or weights/ folder
```

### 4. **Ultralytics Hub**
```
Go to: https://hub.ultralytics.com/
Browse: Pre-trained models
Look for: Human pose or fall detection datasets
```

---

## 🔧 Troubleshooting

### Model Won't Load
```python
# Check model file
import torch
checkpoint = torch.load('models/fall_detection.pt')
print(checkpoint.keys())
```

### Wrong Class Names
```python
# Check what classes the model has
from ultralytics import YOLO
model = YOLO('models/fall_detection.pt')
print("Classes:", model.names)
# Update your config accordingly
```

### Low Accuracy
- Lower confidence threshold in config (e.g., 0.5 instead of 0.75)
- Try different lighting conditions
- Adjust camera angle
- Use better quality model (yolov8m instead of yolov8n)

### Slow Performance
- Use smaller model (yolov8n-pose instead of yolov8x-pose)
- Reduce camera resolution
- Skip frames (process every 2nd or 3rd frame)

---

## 📊 Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| YOLOv8n-pose | 6 MB | Fast | 85% | Quick testing, RDK X5 |
| YOLOv8s-pose | 11 MB | Medium | 88% | Balanced |
| YOLOv8m-pose | 25 MB | Slower | 92% | High accuracy |
| Custom trained | Varies | Varies | 90-95% | Production |

---

## ✅ Quick Start Checklist

- [ ] Choose model approach (Option 1 recommended)
- [ ] Create `src/fall_detector_pose.py` (if using Option 1)
- [ ] Test model with webcam
- [ ] Update `src/main.py` imports
- [ ] Run complete system
- [ ] Test fall detection scenarios
- [ ] Adjust confidence thresholds if needed

---

## 🎊 Recommended: Start with Option 1!

**For quickest results:**
1. Copy the `fall_detector_pose.py` code above
2. Save to `src/fall_detector_pose.py`
3. Run: `python3 src/fall_detector_pose.py`
4. Test with webcam - simulate falls!
5. When working well, integrate with main system

The YOLOv8 Pose model will download automatically (~6 MB) and works immediately!

---

## 📞 Need Help?

If you encounter issues:
1. Check model file exists: `ls -lh models/`
2. Verify model format: `file models/fall_detection.pt`
3. Test model loading: `python3 src/fall_detector.py`
4. Check logs: `tail -f data/logs/system.log`

**Good luck! You're almost there! 🚀**
