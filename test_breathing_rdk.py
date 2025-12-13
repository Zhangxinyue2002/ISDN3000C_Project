"""
Breathing Detection Test for RDK X5 Camera

This script tests the breathing detector using a camera connected to RDK X5.
It uses the CameraService class which handles RDK camera configuration.

Usage:
    On RDK X5:
    python3 test_breathing_rdk.py [--duration SECONDS] [--test-capture]

Options:
    --duration SECONDS    : Capture duration for breathing analysis (default: 12)
    --test-capture        : First test basic camera capture only
    --bbox X1,Y1,X2,Y2   : Manually specify chest bounding box (e.g., 200,100,400,300)

Author: ISDN3000C Project Team
Date: 2025-12-13
"""

import sys
import argparse
import time
import numpy as np
from pathlib import Path
import cv2
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from breathing_detector import BreathingDetector
    from camera_service import CameraService
    from database import Database
    print("✓ Successfully imported modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def load_config():
    """Load configuration."""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def test_camera_capture(camera_service):
    """Test basic camera capture functionality."""
    print("\n" + "=" * 70)
    print("CAMERA CAPTURE TEST")
    print("=" * 70)
    
    print("\nOpening camera...")
    if not camera_service.open_camera():
        print("❌ Failed to open camera")
        return False
    
    print("✓ Camera opened successfully")
    
    # Capture a few test frames
    print("\nCapturing 5 test frames...")
    for i in range(5):
        ret, frame = camera_service.cap.read()
        if ret:
            print(f"  Frame {i+1}: {frame.shape} - ✓")
        else:
            print(f"  Frame {i+1}: Failed - ✗")
            return False
        time.sleep(0.1)
    
    print("\n✅ Camera capture test PASSED")
    return True


def capture_frames_for_analysis(camera_service, duration, fps):
    """
    Capture frames for breathing analysis.
    
    Args:
        camera_service: CameraService instance
        duration: Capture duration in seconds
        fps: Target frames per second
    
    Returns:
        List of captured frames
    """
    num_frames = int(duration * fps)
    frames = []
    
    print(f"\nCapturing {num_frames} frames over {duration} seconds...")
    print("Keep the person still and breathing normally...")
    
    start_time = time.time()
    frame_interval = 1.0 / fps
    
    for i in range(num_frames):
        # Calculate target time for this frame
        target_time = start_time + (i * frame_interval)
        
        # Capture frame
        ret, frame = camera_service.cap.read()
        
        if not ret:
            print(f"  Warning: Failed to capture frame {i+1}")
            continue
        
        frames.append(frame.copy())
        
        # Progress update every second
        if (i + 1) % fps == 0:
            elapsed = time.time() - start_time
            print(f"  {int(elapsed)}/{duration} seconds... ({len(frames)} frames)")
        
        # Sleep to maintain target FPS
        current_time = time.time()
        sleep_time = target_time - current_time
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    total_time = time.time() - start_time
    actual_fps = len(frames) / total_time
    
    print(f"\n✓ Captured {len(frames)} frames in {total_time:.2f} seconds")
    print(f"  Actual FPS: {actual_fps:.1f}")
    
    return frames


def get_chest_bbox_interactive(camera_service):
    """
    Let user select chest bounding box interactively.
    
    Args:
        camera_service: CameraService instance
    
    Returns:
        Chest bounding box (x1, y1, x2, y2) or None if cancelled
    """
    print("\n" + "=" * 70)
    print("CHEST REGION SELECTION")
    print("=" * 70)
    print("\nInstructions:")
    print("  1. A preview window will open")
    print("  2. Draw a box around the person's chest area")
    print("  3. Press SPACE or ENTER to confirm")
    print("  4. Press C to cancel and redraw")
    print("  5. Press ESC to skip this test")
    print("\nPress any key to continue...")
    input()
    
    # Capture a frame for ROI selection
    ret, frame = camera_service.cap.read()
    if not ret:
        print("❌ Failed to capture frame for ROI selection")
        return None
    
    # Let user select ROI
    print("\nSelect the chest region...")
    roi = cv2.selectROI("Select Chest Area", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select Chest Area")
    
    if roi[2] == 0 or roi[3] == 0:
        print("Selection cancelled")
        return None
    
    # Convert to (x1, y1, x2, y2) format
    chest_bbox = (roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3])
    print(f"✓ Chest area selected: {chest_bbox}")
    print(f"  Width: {roi[2]} pixels")
    print(f"  Height: {roi[3]} pixels")
    
    return chest_bbox


def test_breathing_detection(camera_service, chest_bbox, duration, fps):
    """
    Test breathing detection with RDK camera.
    
    Args:
        camera_service: CameraService instance
        chest_bbox: Chest bounding box (x1, y1, x2, y2)
        duration: Capture duration
        fps: Target FPS
    
    Returns:
        Analysis result dictionary
    """
    print("\n" + "=" * 70)
    print("BREATHING DETECTION TEST")
    print("=" * 70)
    
    # Initialize breathing detector
    print("\nInitializing breathing detector...")
    detector = BreathingDetector()
    print(f"✓ Detector initialized")
    print(f"  Breathing rate range: {detector.min_breathing_rate}-{detector.max_breathing_rate} bpm")
    print(f"  Minimum motion: {detector.min_motion_amplitude} pixels")
    
    # Capture frames
    frames = capture_frames_for_analysis(camera_service, duration, fps)
    
    if len(frames) < 10:
        print(f"❌ Insufficient frames captured: {len(frames)}")
        return None
    
    # Analyze breathing
    print("\nAnalyzing breathing...")
    print("This may take a few seconds...")
    
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Display results
    print("\n" + "=" * 70)
    print("BREATHING DETECTION RESULTS")
    print("=" * 70)
    
    print(f"\n  Breathing Detected:  {'YES ✓' if result['breathing_detected'] else 'NO ✗'}")
    print(f"  Confidence:          {result['confidence']:.1%}")
    print(f"  Breathing Rate:      {result['breathing_rate']:.1f} breaths/min")
    print(f"  Motion Amplitude:    {result['motion_amplitude']:.2f} pixels")
    print(f"  Frames Analyzed:     {result['num_frames_analyzed']}")
    print(f"  Keypoints Tracked:   {result['keypoints_tracked']}")
    
    if 'error' in result:
        print(f"  Error:               {result['error']}")
    
    # Interpretation
    print("\n" + "-" * 70)
    print("INTERPRETATION:")
    
    if result['breathing_detected']:
        if result['confidence'] > 0.7:
            print("  ✅ High confidence - Person is breathing normally")
            print(f"  ✓ Breathing rate of {result['breathing_rate']:.1f} bpm is within normal range")
        elif result['confidence'] > 0.5:
            print("  ⚠️  Medium confidence - Breathing detected but signal unclear")
            print("  → May need better lighting or less background movement")
        else:
            print("  ⚠️  Low confidence - Breathing possibly detected")
            print("  → Consider recapturing with better conditions")
    else:
        print("  ❌ No breathing detected!")
        
        if result['breathing_rate'] < detector.min_breathing_rate:
            print(f"  → Breathing rate too low: {result['breathing_rate']:.1f} bpm")
        elif result['breathing_rate'] > detector.max_breathing_rate:
            print(f"  → Motion too fast (not breathing): {result['breathing_rate']:.1f} bpm")
            print("  → Possible causes: camera shake, person moving, etc.")
        
        if result['motion_amplitude'] < detector.min_motion_amplitude:
            print(f"  → Motion amplitude too small: {result['motion_amplitude']:.2f} pixels")
            print("  → Person may be too still or too far from camera")
        
        if result.get('keypoints_tracked', 0) < 10:
            print(f"  → Insufficient keypoints: {result.get('keypoints_tracked', 0)}")
            print("  → Need more texture in chest area (avoid plain clothing)")
    
    print("=" * 70)
    
    return result


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test breathing detection with RDK camera')
    parser.add_argument('--duration', type=int, default=12,
                       help='Capture duration in seconds (default: 12)')
    parser.add_argument('--test-capture', action='store_true',
                       help='Test basic camera capture only')
    parser.add_argument('--bbox', type=str,
                       help='Manually specify chest bbox as X1,Y1,X2,Y2')
    parser.add_argument('--fps', type=int, default=30,
                       help='Target FPS for capture (default: 30)')
    args = parser.parse_args()
    
    print("=" * 70)
    print("RDK X5 BREATHING DETECTION TEST")
    print("=" * 70)
    print(f"\nTest Configuration:")
    print(f"  Duration: {args.duration} seconds")
    print(f"  Target FPS: {args.fps}")
    
    # Load config and initialize services
    print("\nLoading configuration...")
    config = load_config()
    
    print("Initializing database...")
    db = Database()
    
    print("Initializing camera service...")
    camera_service = CameraService(config, db)
    
    # Test 1: Basic camera capture
    if args.test_capture or True:  # Always test capture first
        if not test_camera_capture(camera_service):
            print("\n❌ Camera capture test failed")
            return 1
    
    if args.test_capture:
        print("\n✅ Camera test complete. Run without --test-capture to test breathing detection.")
        camera_service.cap.release()
        return 0
    
    # Test 2: Breathing detection
    try:
        # Get chest bounding box
        if args.bbox:
            # Parse manual bbox
            bbox_parts = args.bbox.split(',')
            if len(bbox_parts) != 4:
                print("❌ Invalid bbox format. Use: X1,Y1,X2,Y2")
                return 1
            chest_bbox = tuple(map(int, bbox_parts))
            print(f"\nUsing manual chest bbox: {chest_bbox}")
        else:
            # Interactive selection
            chest_bbox = get_chest_bbox_interactive(camera_service)
            if chest_bbox is None:
                print("\nTest cancelled by user")
                camera_service.cap.release()
                return 0
        
        # Run breathing detection
        result = test_breathing_detection(camera_service, chest_bbox, args.duration, args.fps)
        
        if result is None:
            print("\n❌ Breathing detection test failed")
            camera_service.cap.release()
            return 1
        
        # Success
        print("\n✅ Breathing detection test complete!")
        
        if result['breathing_detected']:
            print("🎉 Breathing was successfully detected!")
            camera_service.cap.release()
            return 0
        else:
            print("⚠️  No breathing detected (may need to adjust conditions)")
            camera_service.cap.release()
            return 0
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        camera_service.cap.release()
        return 0
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        camera_service.cap.release()
        return 1


if __name__ == "__main__":
    sys.exit(main())
