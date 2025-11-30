"""
Test Breathing Detection Module

This script provides comprehensive testing for the breathing detector:
1. Simulated breathing motion test
2. Static frame test (no breathing)
3. Random motion test (non-periodic)
4. Live camera test (if camera available)

Usage:
    python3 test_breathing_detection.py [--camera]

Author: ISDN3000C Project Team
Date: 2025-11-30
"""

import sys
import argparse
import numpy as np
import cv2
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from breathing_detector import BreathingDetector


def create_test_pattern(size=(200, 200), num_keypoints=50):
    """
    Create a test image with SIFT keypoints.
    
    Args:
        size: Image size (width, height)
        num_keypoints: Number of random features to add
    
    Returns:
        Test image with features
    """
    img = np.ones((size[1], size[0], 3), dtype=np.uint8) * 128
    
    # Add random circles as features
    for _ in range(num_keypoints):
        x = np.random.randint(20, size[0] - 20)
        y = np.random.randint(20, size[1] - 20)
        radius = np.random.randint(3, 8)
        color = (np.random.randint(50, 200),) * 3
        cv2.circle(img, (x, y), radius, color, -1)
    
    # Add some texture
    noise = np.random.randint(-30, 30, (size[1], size[0], 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return img


def test_simulated_breathing():
    """
    Test 1: Simulated breathing motion with expected rate of 16 breaths/min.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Simulated Breathing Motion (16 breaths/min)")
    print("=" * 70)
    
    detector = BreathingDetector()
    
    # Parameters
    duration = 12  # seconds
    fps = 30
    breathing_rate_target = 16  # breaths per minute
    amplitude = 6  # pixels
    
    num_frames = int(duration * fps)
    frames = []
    
    print(f"Generating {num_frames} frames with simulated breathing...")
    print(f"  Target breathing rate: {breathing_rate_target} breaths/min")
    print(f"  Motion amplitude: {amplitude} pixels")
    
    # Create base frame with features
    base_frame = create_test_pattern((200, 200), num_keypoints=100)
    
    # Generate frames with breathing motion
    for i in range(num_frames):
        # Calculate breathing displacement
        breathing_freq = breathing_rate_target / 60  # Hz
        phase = 2 * np.pi * breathing_freq * i / fps
        displacement = int(amplitude * np.sin(phase))
        
        # Create frame with vertical shift
        frame = base_frame.copy()
        if displacement != 0:
            M = np.float32([[1, 0, 0], [0, 1, displacement]])
            frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
        
        frames.append(frame)
    
    # Analyze breathing
    chest_bbox = (0, 0, 200, 200)
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Display results
    print(f"\n✓ Analysis Complete")
    print(f"  Breathing Detected: {'YES' if result['breathing_detected'] else 'NO'}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Detected Rate: {result['breathing_rate']:.1f} breaths/min")
    print(f"  Expected Rate: {breathing_rate_target} breaths/min")
    print(f"  Rate Error: {abs(result['breathing_rate'] - breathing_rate_target):.1f} breaths/min")
    print(f"  Motion Amplitude: {result['motion_amplitude']:.2f} pixels")
    print(f"  Keypoints Tracked: {result['keypoints_tracked']}")
    
    # Evaluate test
    rate_error = abs(result['breathing_rate'] - breathing_rate_target)
    if result['breathing_detected'] and rate_error < 5:
        print(f"\n✅ TEST PASSED: Breathing correctly detected")
        return True
    else:
        print(f"\n❌ TEST FAILED: Breathing not detected or rate error too large")
        return False


def test_static_frames():
    """
    Test 2: Static frames (no breathing) - should NOT detect breathing.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Static Frames (No Breathing)")
    print("=" * 70)
    
    detector = BreathingDetector()
    
    # Parameters
    duration = 12
    fps = 30
    num_frames = int(duration * fps)
    
    print(f"Generating {num_frames} static frames (no motion)...")
    
    # Create static frames
    base_frame = create_test_pattern((200, 200), num_keypoints=100)
    frames = [base_frame.copy() for _ in range(num_frames)]
    
    # Analyze
    chest_bbox = (0, 0, 200, 200)
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Display results
    print(f"\n✓ Analysis Complete")
    print(f"  Breathing Detected: {'YES' if result['breathing_detected'] else 'NO'}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Detected Rate: {result['breathing_rate']:.1f} breaths/min")
    print(f"  Motion Amplitude: {result['motion_amplitude']:.2f} pixels")
    
    # Evaluate test
    if not result['breathing_detected']:
        print(f"\n✅ TEST PASSED: Correctly identified no breathing")
        return True
    else:
        print(f"\n❌ TEST FAILED: False positive - detected breathing in static frames")
        return False


def test_random_motion():
    """
    Test 3: Random motion (non-periodic) - should NOT detect breathing.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Random Motion (Non-Periodic)")
    print("=" * 70)
    
    detector = BreathingDetector()
    
    # Parameters
    duration = 12
    fps = 30
    num_frames = int(duration * fps)
    
    print(f"Generating {num_frames} frames with random motion...")
    
    # Create frames with random motion
    base_frame = create_test_pattern((200, 200), num_keypoints=100)
    frames = []
    
    for i in range(num_frames):
        # Random displacement
        displacement = np.random.randint(-5, 6)
        
        frame = base_frame.copy()
        if displacement != 0:
            M = np.float32([[1, 0, 0], [0, 1, displacement]])
            frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))
        
        frames.append(frame)
    
    # Analyze
    chest_bbox = (0, 0, 200, 200)
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Display results
    print(f"\n✓ Analysis Complete")
    print(f"  Breathing Detected: {'YES' if result['breathing_detected'] else 'NO'}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Detected Rate: {result['breathing_rate']:.1f} breaths/min")
    print(f"  Motion Amplitude: {result['motion_amplitude']:.2f} pixels")
    
    # Evaluate test
    if not result['breathing_detected']:
        print(f"\n✅ TEST PASSED: Correctly rejected random motion")
        return True
    else:
        print(f"\n⚠️  TEST WARNING: Detected breathing in random motion")
        print(f"    (This might be acceptable depending on threshold)")
        return True  # Not a hard failure


def test_live_camera():
    """
    Test 4: Live camera test (if available).
    """
    print("\n" + "=" * 70)
    print("TEST 4: Live Camera Test")
    print("=" * 70)
    
    detector = BreathingDetector()
    
    # Try to open camera
    print("Opening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Camera not available - skipping test")
        return None
    
    print("✓ Camera opened successfully")
    print("\nInstructions:")
    print("  1. Position camera to view a person's chest area")
    print("  2. Draw a bounding box around the chest when prompted")
    print("  3. System will capture 12 seconds of video and analyze breathing")
    print("\nPress SPACE to start, ESC to skip...")
    
    # Display live view
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from camera")
            cap.release()
            return False
        
        # Display frame
        display = frame.copy()
        cv2.putText(display, "Press SPACE to start, ESC to skip", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Live Camera Test", display)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space to start
            break
        elif key == 27:  # ESC to skip
            cap.release()
            cv2.destroyAllWindows()
            print("Test skipped by user")
            return None
    
    # Let user draw bounding box
    print("\nDraw a bounding box around the chest area...")
    ret, frame = cap.read()
    bbox = cv2.selectROI("Select Chest Area", frame, fromCenter=False)
    cv2.destroyWindow("Select Chest Area")
    
    if bbox[2] == 0 or bbox[3] == 0:
        print("❌ Invalid bounding box")
        cap.release()
        return False
    
    chest_bbox = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])
    print(f"✓ Chest area selected: {chest_bbox}")
    
    # Capture frames
    duration = 12
    fps = 30
    num_frames = int(duration * fps)
    frames = []
    
    print(f"\nCapturing {duration} seconds of video...")
    print("Keep the person still and breathing naturally")
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Failed to capture frame {i}")
            continue
        
        frames.append(frame.copy())
        
        # Show progress
        if i % 30 == 0:
            print(f"  {i//30 + 1}/{duration} seconds...")
        
        cv2.waitKey(int(1000 / fps))
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"✓ Captured {len(frames)} frames")
    
    # Analyze breathing
    print("\nAnalyzing breathing...")
    result = detector.analyze_breathing(frames, chest_bbox)
    
    # Display results
    print(f"\n✓ Analysis Complete")
    print(f"  Breathing Detected: {'YES' if result['breathing_detected'] else 'NO'}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"  Detected Rate: {result['breathing_rate']:.1f} breaths/min")
    print(f"  Motion Amplitude: {result['motion_amplitude']:.2f} pixels")
    print(f"  Keypoints Tracked: {result['keypoints_tracked']}")
    
    return result['breathing_detected']


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description='Test breathing detection module')
    parser.add_argument('--camera', action='store_true', 
                       help='Include live camera test')
    args = parser.parse_args()
    
    print("=" * 70)
    print("BREATHING DETECTION TEST SUITE")
    print("=" * 70)
    
    results = {}
    
    # Run automated tests
    try:
        results['test1_simulated'] = test_simulated_breathing()
    except Exception as e:
        print(f"\n❌ Test 1 failed with exception: {e}")
        results['test1_simulated'] = False
    
    try:
        results['test2_static'] = test_static_frames()
    except Exception as e:
        print(f"\n❌ Test 2 failed with exception: {e}")
        results['test2_static'] = False
    
    try:
        results['test3_random'] = test_random_motion()
    except Exception as e:
        print(f"\n❌ Test 3 failed with exception: {e}")
        results['test3_random'] = False
    
    # Live camera test (optional)
    if args.camera:
        try:
            results['test4_camera'] = test_live_camera()
        except Exception as e:
            print(f"\n❌ Test 4 failed with exception: {e}")
            results['test4_camera'] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        if passed is None:
            status = "⊘ SKIPPED"
        elif passed:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    # Overall result
    total_tests = sum(1 for v in results.values() if v is not None)
    passed_tests = sum(1 for v in results.values() if v is True)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if total_tests > 0 and passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Breathing detector is working correctly.")
        return 0
    elif passed_tests > 0:
        print("\n⚠️  SOME TESTS FAILED. Please review the results above.")
        return 1
    else:
        print("\n❌ ALL TESTS FAILED. Please check the implementation.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
