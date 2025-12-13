"""
Breathing Detection Test for RDK X5 Camera

This script tests the breathing detector using a camera connected to RDK X5.
It automatically detects the chest region using YOLOv8 pose detection.

Usage:
    On RDK X5:
    
    # Automatic chest detection (recommended)
    python3 test_breathing_rdk.py
    
    # Manual chest region (if automatic fails)
    python3 test_breathing_rdk.py --bbox X1,Y1,X2,Y2
    
    # Test camera only
    python3 test_breathing_rdk.py --test-capture

Options:
    --duration SECONDS    : Capture duration for breathing analysis (default: 12)
    --fps FPS            : Target FPS for capture (default: 30)
    --test-capture       : First test basic camera capture only
    --bbox X1,Y1,X2,Y2   : Manually specify chest bounding box (optional)

Features:
    - Automatic chest detection using pose estimation
    - Works with any person pose/position
    - No manual region selection needed
    - Falls back to manual bbox if needed

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


def test_camera_capture_direct():
    """Test camera capture directly without CameraService."""
    print("\n" + "=" * 70)
    print("CAMERA CAPTURE TEST (Direct)")
    print("=" * 70)
    
    # Try simple direct access first (like the main system does)
    print("\nTrying direct camera access...")
    
    camera_indices = [0, 1, 8, 10]
    
    for idx in camera_indices:
        print(f"Trying camera index {idx}...")
        cap = cv2.VideoCapture(idx)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Camera {idx} works! Resolution: {frame.shape}")
                
                # Test multiple frames
                print("  Testing frame capture...")
                success_count = 0
                for i in range(5):
                    ret, frame = cap.read()
                    if ret:
                        success_count += 1
                    time.sleep(0.1)
                
                print(f"  Successfully captured {success_count}/5 frames")
                
                if success_count >= 4:
                    print(f"\n✅ Camera {idx} is working properly!")
                    return cap, idx
                else:
                    print(f"  Camera {idx} unstable, trying next...")
                    cap.release()
            else:
                print(f"  Camera {idx} opened but can't read frames")
                cap.release()
        else:
            print(f"  Camera {idx} failed to open")
            if cap:
                cap.release()
    
    print("\n❌ No working camera found")
    return None, None


def test_camera_capture(camera_service):
    """Test basic camera capture functionality."""
    print("\n" + "=" * 70)
    print("CAMERA CAPTURE TEST")
    print("=" * 70)
    
    print("\nOpening camera...")
    if not camera_service.open_camera():
        print("❌ Failed to open camera with CameraService")
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


def capture_frames_for_analysis(cap, duration, fps):
    """
    Capture frames for breathing analysis.
    
    Args:
        cap: OpenCV VideoCapture object
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
        ret, frame = cap.read()
        
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


def get_chest_bbox_automatic(cap):
    """
    Automatically detect chest region using pose detection.
    
    Args:
        cap: OpenCV VideoCapture object
    
    Returns:
        Chest bounding box (x1, y1, x2, y2) or None if detection fails
    """
    print("\n" + "=" * 70)
    print("AUTOMATIC CHEST DETECTION")
    print("=" * 70)
    
    print("\nUsing YOLOv8 pose detection to find person and chest region...")
    
    # Import fall detector
    from fall_detector_enhanced import FallDetectorEnhanced
    
    # Initialize detector
    print("Loading pose detection model...")
    detector = FallDetectorEnhanced(debug_mode=False)
    
    # Capture a frame
    print("Capturing frame for pose analysis...")
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame")
        return None
    
    # Detect person and get chest region
    print("Detecting person pose...")
    result = detector.detect_fall(frame)
    
    if not result['person_detected']:
        print("❌ No person detected in frame")
        print("   Make sure person is visible to camera")
        
        # Save frame for debugging
        debug_file = "no_person_detected.jpg"
        cv2.imwrite(debug_file, frame)
        print(f"\n💡 Saved frame to: {debug_file}")
        print("   Download this to see what the camera sees:")
        print(f"   scp user@rdk-ip:~/ISDN3000C_Project/{debug_file} .")
        
        print("\n📋 Troubleshooting:")
        print("   1. Point camera at a person")
        print("   2. Make sure person is in frame (not too close/far)")
        print("   3. Ensure good lighting")
        print("   4. Or use manual bbox if needed:")
        print("      python3 test_breathing_rdk.py --bbox 200,150,450,350")
        
        return None
    
    if result['chest_bbox'] is None:
        print("⚠️  Person detected but chest region not available")
        print("   Using person bounding box to estimate chest...")
        
        if result['bounding_box'] is None:
            print("❌ No bounding box available")
            return None
        
        # Estimate chest from person bbox (same method as fall detector)
        person_bbox = result['bounding_box']
        chest_bbox = estimate_chest_from_person_bbox(person_bbox)
    else:
        chest_bbox = result['chest_bbox']
    
    print(f"✓ Chest region detected: {chest_bbox}")
    print(f"  Width: {chest_bbox[2] - chest_bbox[0]} pixels")
    print(f"  Height: {chest_bbox[3] - chest_bbox[1]} pixels")
    
    # Save original frame
    original_file = "captured_frame.jpg"
    cv2.imwrite(original_file, frame)
    print(f"\n📸 Saved original frame: {original_file}")
    
    # Create annotated frame with bounding boxes
    annotated_frame = frame.copy()
    
    # Draw person bounding box (blue)
    if result['bounding_box'] is not None:
        px1, py1, px2, py2 = result['bounding_box']
        cv2.rectangle(annotated_frame, (px1, py1), (px2, py2), (255, 0, 0), 2)
        cv2.putText(annotated_frame, "Person", (px1, py1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # Draw chest bounding box (green)
    cx1, cy1, cx2, cy2 = chest_bbox
    cv2.rectangle(annotated_frame, (cx1, cy1), (cx2, cy2), (0, 255, 0), 3)
    cv2.putText(annotated_frame, "Chest Region", (cx1, cy1 - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Add info text
    info_text = f"Resolution: {frame.shape[1]}x{frame.shape[0]}"
    cv2.putText(annotated_frame, info_text, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    chest_size = f"Chest: {cx2-cx1}x{cy2-cy1}px"
    cv2.putText(annotated_frame, chest_size, (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Save annotated frame
    annotated_file = "chest_detection_result.jpg"
    cv2.imwrite(annotated_file, annotated_frame)
    print(f"📸 Saved annotated frame: {annotated_file}")
    print(f"   → Blue box: Person")
    print(f"   → Green box: Chest region for breathing analysis")
    
    print(f"\n💾 Download images to view:")
    print(f"   scp user@rdk-ip:~/ISDN3000C_Project/{{{original_file},{annotated_file}}} .")
    
    return chest_bbox


def estimate_chest_from_person_bbox(person_bbox):
    """
    Estimate chest region from person bounding box.
    Uses same logic as fall detector.
    
    Args:
        person_bbox: (x1, y1, x2, y2) of person
    
    Returns:
        (x1, y1, x2, y2) of estimated chest region
    """
    x1, y1, x2, y2 = person_bbox
    
    width = x2 - x1
    height = y2 - y1
    
    # Chest region: upper 1/3, centered horizontally, 60% width
    chest_x1 = int(x1 + width * 0.2)
    chest_y1 = int(y1 + height * 0.2)
    chest_x2 = int(x2 - width * 0.2)
    chest_y2 = int(y1 + height * 0.5)
    
    return (chest_x1, chest_y1, chest_x2, chest_y2)


def get_chest_bbox_interactive(cap):
    """
    Let user select chest bounding box interactively.
    
    Args:
        cap: OpenCV VideoCapture object
    
    Returns:
        Chest bounding box (x1, y1, x2, y2) or None if cancelled
    """
    print("\n" + "=" * 70)
    print("CHEST REGION SELECTION")
    print("=" * 70)
    
    # Check if we can display (headless detection)
    import os
    if 'DISPLAY' not in os.environ or not os.environ['DISPLAY']:
        print("\n⚠️  No display detected (headless/SSH mode)")
        print("\nYou have two options:")
        print("\n1. Use manual bounding box:")
        print("   python3 test_breathing_rdk.py --bbox X1,Y1,X2,Y2")
        print("   Example: python3 test_breathing_rdk.py --bbox 200,150,450,350")
        print("\n2. Capture test frame to find coordinates:")
        print("   python3 capture_test_frame.py")
        print("   Download test_frame.jpg and identify chest region")
        print("   Then use those coordinates with --bbox")
        return None
    
    print("\nInstructions:")
    print("  1. A preview window will open")
    print("  2. Draw a box around the person's chest area")
    print("  3. Press SPACE or ENTER to confirm")
    print("  4. Press C to cancel and redraw")
    print("  5. Press ESC to skip this test")
    print("\nPress any key to continue...")
    input()
    
    # Capture a frame for ROI selection
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame for ROI selection")
        return None
    
    try:
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
    except Exception as e:
        print(f"\n❌ GUI selection failed: {e}")
        print("\nThis usually means no display is available (SSH/headless mode)")
        print("Use --bbox parameter instead:")
        print("  python3 test_breathing_rdk.py --bbox X1,Y1,X2,Y2")
        return None


def test_breathing_detection(cap, chest_bbox, duration, fps):
    """
    Test breathing detection with RDK camera.
    
    Args:
        cap: OpenCV VideoCapture object
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
    frames = capture_frames_for_analysis(cap, duration, fps)
    
    if len(frames) < 10:
        print(f"❌ Insufficient frames captured: {len(frames)}")
        return None
    
    # Analyze breathing
    print("\nAnalyzing breathing...")
    print("This may take a few seconds...")
    
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Save visualization of breathing analysis
    print("\nCreating visualization...")
    if len(frames) > 0:
        # Create a visualization showing chest region over time
        visualization_frame = frames[0].copy()
        
        # Draw chest bounding box
        x1, y1, x2, y2 = chest_bbox
        cv2.rectangle(visualization_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(visualization_frame, "Chest Region (Breathing Analysis)", 
                   (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add analysis results on image
        result_text = f"Breathing: {'YES' if result['breathing_detected'] else 'NO'}"
        cv2.putText(visualization_frame, result_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                   (0, 255, 0) if result['breathing_detected'] else (0, 0, 255), 2)
        
        rate_text = f"Rate: {result['breathing_rate']:.1f} bpm"
        cv2.putText(visualization_frame, rate_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        conf_text = f"Confidence: {result['confidence']:.1%}"
        cv2.putText(visualization_frame, conf_text, (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Save visualization
        viz_file = "breathing_analysis_result.jpg"
        cv2.imwrite(viz_file, visualization_frame)
        print(f"📸 Saved breathing analysis: {viz_file}")
    
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
    
    # Test 1: Try direct camera access first
    print("\nStep 1: Testing direct camera access...")
    cap, working_idx = test_camera_capture_direct()
    
    if cap is None:
        print("\n❌ Cannot access camera directly")
        print("\nMost likely cause: Another process is using the camera!")
        print("\nCheck if main system is running:")
        import subprocess
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            main_processes = [line for line in result.stdout.split('\n') 
                            if 'main.py' in line and 'grep' not in line]
            if main_processes:
                print("\n⚠️  FOUND RUNNING PROCESSES:")
                for proc in main_processes:
                    print(f"  {proc}")
                print("\n🔴 STOP THE MAIN SYSTEM FIRST:")
                print("  pkill -f 'python.*main.py'")
                print("  or press Ctrl+C in the terminal running main.py")
            else:
                print("\nNo main.py process found. Other debugging steps:")
                print("  1. Check camera devices: ls -l /dev/video*")
                print("  2. Check permissions: groups (need 'video' group)")
                print("  3. Check if camera is in use: lsof /dev/video*")
                print("  4. Try: sudo usermod -aG video $USER && newgrp video")
        except Exception as e:
            print(f"  Could not check for running processes: {e}")
        return 1
    
    print(f"\n✅ Camera index {working_idx} is working!")
    
    if args.test_capture:
        print("\n✅ Camera test complete. Camera is accessible.")
        print(f"    Use camera index: {working_idx}")
        print(f"    Run without --test-capture to test breathing detection.")
        cap.release()
        return 0
    
    # Continue with breathing detection using the working camera
    print("\nStep 2: Proceeding with breathing detection test...")
    
    # We already have a working camera, so we'll use it directly
    # instead of going through CameraService
    
    # Test 2: Breathing detection
    try:
        # Get chest bounding box
        if args.bbox:
            # Parse manual bbox
            bbox_parts = args.bbox.split(',')
            if len(bbox_parts) != 4:
                print("❌ Invalid bbox format. Use: X1,Y1,X2,Y2")
                cap.release()
                return 1
            chest_bbox = tuple(map(int, bbox_parts))
            print(f"\nUsing manual chest bbox: {chest_bbox}")
        else:
            # Use automatic detection via fall detector
            print("\n✅ Using automatic chest detection via pose estimation...")
            chest_bbox = get_chest_bbox_automatic(cap)
            if chest_bbox is None:
                print("\n❌ Could not automatically detect chest region")
                print("Please use manual bbox: python3 test_breathing_rdk.py --bbox X1,Y1,X2,Y2")
                cap.release()
                return 1
            print(f"✓ Chest region detected: {chest_bbox}")
        
        # Run breathing detection
        result = test_breathing_detection(cap, chest_bbox, args.duration, args.fps)
        
        if result is None:
            print("\n❌ Breathing detection test failed")
            cap.release()
            return 1
        
        # Success
        print("\n✅ Breathing detection test complete!")
        
        if result['breathing_detected']:
            print("🎉 Breathing was successfully detected!")
            cap.release()
            return 0
        else:
            print("⚠️  No breathing detected (may need to adjust conditions)")
            cap.release()
            return 0
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        cap.release()
        return 0
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        return 1


if __name__ == "__main__":
    sys.exit(main())
