"""
Breathing Detector Demo - Simple Usage Example

This script demonstrates how to use the breathing detector in a real scenario.

Usage:
    python demo_breathing.py

Author: ISDN3000C Project Team
Date: 2025-11-30
"""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from breathing_detector import BreathingDetector
    print("✓ Successfully imported BreathingDetector")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    print("Please install required packages:")
    print("  pip install opencv-python opencv-contrib-python numpy pyyaml")
    sys.exit(1)


def demo_basic_usage():
    """Demonstrate basic usage of breathing detector."""
    print("\n" + "=" * 70)
    print("BREATHING DETECTOR - BASIC USAGE DEMO")
    print("=" * 70)
    
    # Step 1: Initialize detector
    print("\n1. Initializing breathing detector...")
    detector = BreathingDetector()
    print(f"   ✓ Detector initialized")
    print(f"   - Breathing rate range: {detector.min_breathing_rate}-{detector.max_breathing_rate} breaths/min")
    print(f"   - Capture duration: {detector.capture_duration} seconds")
    print(f"   - FPS: {detector.fps}")
    
    # Step 2: Create sample data (simulating video frames)
    print("\n2. Creating sample video frames (simulating breathing)...")
    
    # Simulate 12 seconds of video at 30 fps
    num_frames = 360
    frame_width = 640
    frame_height = 480
    
    frames = []
    for i in range(num_frames):
        # Create a frame with some texture
        frame = np.random.randint(100, 150, (frame_height, frame_width, 3), dtype=np.uint8)
        
        # Add some features (simulating chest texture)
        for _ in range(50):
            x = np.random.randint(200, 400)
            y = np.random.randint(150, 300)
            size = np.random.randint(3, 10)
            color = np.random.randint(50, 200)
            frame[y:y+size, x:x+size] = color
        
        frames.append(frame)
    
    print(f"   ✓ Created {len(frames)} frames")
    
    # Step 3: Define chest region (normally from fall detection)
    print("\n3. Defining chest region...")
    # Chest bounding box: [x1, y1, x2, y2]
    chest_bbox = (200, 150, 400, 300)
    x1, y1, x2, y2 = chest_bbox
    print(f"   ✓ Chest region: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"   - Width: {x2-x1} pixels")
    print(f"   - Height: {y2-y1} pixels")
    
    # Step 4: Analyze breathing
    print("\n4. Analyzing breathing...")
    print("   This may take a few seconds...")
    
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Step 5: Display results
    print("\n5. Results:")
    print("   " + "-" * 60)
    print(f"   Breathing Detected:  {'YES ✓' if result['breathing_detected'] else 'NO ✗'}")
    print(f"   Confidence:          {result['confidence']:.1%}")
    print(f"   Breathing Rate:      {result['breathing_rate']:.1f} breaths/min")
    print(f"   Motion Amplitude:    {result['motion_amplitude']:.2f} pixels")
    print(f"   Frames Analyzed:     {result['num_frames_analyzed']}")
    print(f"   Keypoints Tracked:   {result['keypoints_tracked']}")
    
    if 'error' in result:
        print(f"   Error:               {result['error']}")
    print("   " + "-" * 60)
    
    # Step 6: Interpret results
    print("\n6. Interpretation:")
    
    if result['breathing_detected']:
        if result['confidence'] > 0.7:
            print("   ✅ High confidence - Person is breathing normally")
        elif result['confidence'] > 0.5:
            print("   ⚠️  Medium confidence - Breathing detected but unclear")
        else:
            print("   ⚠️  Low confidence - Breathing possibly detected")
        
        # Check breathing rate
        if 12 <= result['breathing_rate'] <= 20:
            print(f"   ✓ Breathing rate is normal ({result['breathing_rate']:.1f} breaths/min)")
        elif result['breathing_rate'] < 12:
            print(f"   ⚠️  Breathing rate is slow ({result['breathing_rate']:.1f} breaths/min)")
        else:
            print(f"   ⚠️  Breathing rate is fast ({result['breathing_rate']:.1f} breaths/min)")
    else:
        print("   ❌ No breathing detected!")
        print("   → This indicates a potential emergency situation")
        print("   → System should trigger emergency countdown")
        
        if 'error' in result:
            print(f"   → Error reason: {result['error']}")


def demo_integration_workflow():
    """Demonstrate how breathing detection fits into the full system."""
    print("\n" + "=" * 70)
    print("INTEGRATION WORKFLOW DEMO")
    print("=" * 70)
    
    print("""
This demonstrates how breathing detection integrates with the full system:

STEP 1: Fall Detection
    ↓
    [Camera captures image every 2 seconds]
    ↓
    [YOLO model detects fall]
    ↓
    Result: {
        'fall_detected': True,
        'confidence': 0.92,
        'bbox': [150, 100, 400, 450],  ← Person bounding box
        'class': 'fallen'
    }

STEP 2: Start Breathing Check
    ↓
    [LED 1 turns ON - Fall indicator]
    ↓
    [Extract chest region from fall bbox]
    ↓
    chest_y1 = bbox[1]  # Top of person
    chest_y2 = bbox[1] + (bbox[3] - bbox[1]) // 2  # Middle
    chest_bbox = [bbox[0], chest_y1, bbox[2], chest_y2]
    ↓
    [Capture 12 seconds of video]

STEP 3: Analyze Breathing
    ↓
    detector = BreathingDetector()
    result = detector.analyze_breathing(frames, chest_bbox)
    ↓
    ┌─────────────────────────────────────┐
    │ If breathing detected:              │
    │   - Turn OFF LED 1                  │
    │   - Return to normal monitoring     │
    │   - Log as false alarm              │
    └─────────────────────────────────────┘
    ↓
    ┌─────────────────────────────────────┐
    │ If NO breathing detected:           │
    │   - Keep LED 1 ON                   │
    │   - Start LED 2 flashing (countdown)│
    │   - Start 10-second countdown       │
    │   - Wait for Button 2 or timeout    │
    └─────────────────────────────────────┘

STEP 4: Emergency Response
    ↓
    ┌─────────────────────────────────────┐
    │ If countdown reaches 0:             │
    │   - LED 2 solid ON                  │
    │   - Log emergency event             │
    │   - Trigger 999 call                │
    │   - Send web alert                  │
    └─────────────────────────────────────┘
    """)


def demo_code_example():
    """Show code example for integration."""
    print("\n" + "=" * 70)
    print("CODE EXAMPLE - How to Use in Your System")
    print("=" * 70)
    
    code = '''
# In your main application:

from src.breathing_detector import BreathingDetector
from src.camera_service import CameraService
from src.gpio_handler import GPIOHandler

# Initialize components
breathing_detector = BreathingDetector()
camera = CameraService()
gpio = GPIOHandler()

# When fall is detected:
def on_fall_detected(fall_bbox):
    """Handle fall detection event."""
    print("Fall detected! Checking breathing...")
    
    # Turn on fall indicator LED
    gpio.led_fall_on()
    
    # Calculate chest region (upper half of person)
    x1, y1, x2, y2 = fall_bbox
    chest_height = (y2 - y1) // 2
    chest_bbox = (x1, y1, x2, y1 + chest_height)
    
    # Capture video and analyze breathing
    result = breathing_detector.capture_and_analyze(
        camera.cap, 
        chest_bbox,
        duration=12
    )
    
    # Check result
    if result['breathing_detected']:
        print(f"Breathing OK: {result['breathing_rate']:.1f} bpm")
        gpio.led_fall_off()
        return False  # No emergency
    else:
        print("NO BREATHING DETECTED!")
        start_emergency_countdown()
        return True  # Emergency!

def start_emergency_countdown():
    """Start 10-second emergency countdown."""
    gpio.led_emergency_flash()
    # ... countdown logic ...
'''
    
    print(code)


def main():
    """Run all demos."""
    try:
        # Demo 1: Basic usage
        demo_basic_usage()
        
        # Demo 2: Integration workflow
        demo_integration_workflow()
        
        # Demo 3: Code example
        demo_code_example()
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run the test suite: python test_breathing_detection.py")
        print("  2. Test with camera: python test_breathing_detection.py --camera")
        print("  3. Read the guide: BREATHING_DETECTION_GUIDE.md")
        print("  4. Integrate with your system using the code example above")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
